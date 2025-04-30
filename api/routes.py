"""
routes.py

FastAPI routes for the DIL API.
"""

from typing import Union, Optional, List
import re

from fastapi import (APIRouter,
                     Depends,
                     Query)
from fastapi.responses import JSONResponse
from fastapi_pagination import (Page,
                                set_page)
from fastapi_pagination.ext.sqlalchemy import (paginate)
from fastapi_pagination.customization import CustomizedPage

import bleach

from sqlalchemy import (or_,
                        and_,
                        func,
                        asc,
                        desc,
                        select)
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from api.database import get_db
from api.crud import (get_printer,
                      get_patent,
                      get_city,
                      get_address)
from api.schemas import (Message,
                         PatentMinimalOut,
                         AddressMinimalOut,
                         PersonPatentsImages,
                         CityOut,
                         AddressOut,
                         PrinterMinimalResponseOut,
                         CityOutMinimal,
                         PrinterOut,
                         PatentOut)
from api.models.models import (Person,
                               Patent,
                               City,
                               Address)
from api.index_fts.search_utils import search_whoosh

api_router = APIRouter()


# -- infos routes -- #
"""
return 
-> total persons
-> total patents
"""

@api_router.get(
    "/infos",
    include_in_schema=True,
    responses={500: {"model": Message}},
    summary='Get API information',
    tags=['Infos']
)
def get_infos(db: Session = Depends(get_db)):
    try:
        # Nombre total de personnes
        total_persons = db.query(Person).count()

        # Nombre total de brevets
        total_patents = db.query(Patent).count()

        # Nombre total de villes
        total_cities = db.query(City).count()

        # Nombre total d'adresses
        total_addresses = db.query(Address).count()

        return {
            "total_persons": total_persons,
            "total_patents": total_patents,
            "total_cities": total_cities,
            "total_addresses": total_addresses
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"It seems the server have trouble: {e}"})

@api_router.get(
    "/map/places",
    include_in_schema=True,
    responses={500: {"model": Message}},
    summary='Get map data: cities with geolocation and linked printers',
    tags=['Map']
)
def get_cities_with_printers(db: Session = Depends(get_db)):
    try:
        results = db.query(
            City.id,
            City.label,
            City.long_lat,
            City._id_dil,
            Patent.person_id
        ).join(
            Patent, City.id == Patent.city_id
        ).filter(
            City.long_lat.isnot(None)
        ).all()

        # Organiser les résultats
        cities_dict = {}
        for city_id, city_label, city_long_lat, city_dil, person_id in results:
            if city_id not in cities_dict:
                cities_dict[city_id] = {
                    "city_label": city_label,
                    "city_long_lat": city_long_lat,
                    "city_dil": city_dil,
                    "printer_ids": set()
                }
            cities_dict[city_id]["printer_ids"].add(person_id)

        # Transformer en liste pour l'API
        cities_list = [
            {
                "city_label": data["city_label"],
                "city_long_lat": data["city_long_lat"],
                "city_dil": data["city_dil"],
                "printer_ids": list(data["printer_ids"])
            }
            for data in cities_dict.values()
        ]

        return cities_list

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"It seems the server have trouble: {e}"})


@api_router.get("/places/autocomplete", response_model=List[CityOutMinimal])
def autocomplete_city(
        q: Optional[str] = Query(None, description="Recherche partielle sur le nom de la ville"),
        db: Session = Depends(get_db)
):
    query = db.query(Patent)

    if q:
        query = query.filter(Patent.city_label.ilike(f"%{q}%"))

    results = query.order_by(Patent.city_label.asc()).limit(20).all()
    results = [
        {
            "label": result.city_label
        }
        for result in results
    ]
    # deduplicate results dict
    if len(results) > 0:
        results = {result["label"]: result for result in results}
        results = list(results.values())
        # Sort results by label
        results.sort(key=lambda x: x["label"])
        # Limit results to 20
        results = results[:20]

    return results


# routes utils

def normalize_date(date_str):
    date_str = date_str.replace("~", "")
    parts = date_str.split("-")
    if len(parts) == 1:
        return f"{parts[0]}-01-01"
    elif len(parts) == 2:
        return f"{parts[0]}-{parts[1]}-01"
    return date_str


# -- IMAGE ROUTES -- #
@api_router.get(
    "/persons/person/{id}/images",
    include_in_schema=True,
    response_model=PersonPatentsImages,
    responses={404: {"model": Message}, 500: {"model": Message}},
    summary='',
    tags=['Images']
)
def read_images(id: str, db: Session = Depends(get_db)):
    try:
        printer = get_printer(db, {"_id_dil": id})
        if not printer:
            return JSONResponse(status_code=404, content={"message": f"Printer with id {id} not found"})

        patent_images = []
        images_pinned = []

        for patent in printer.patents:
            images = [
                {
                    "image_id": getattr(image_rel, "_id_dil", None),
                    "label": getattr(image_rel.image_patents, "label", None),
                    "reference_url": getattr(image_rel.image_patents, "reference_url", None),
                    "img_name": getattr(image_rel.image_patents, "img_name", None),
                    "iiif_url": getattr(image_rel.image_patents, "iiif_url", None),
                    "is_pinned": image_rel.is_pinned,
                }
                for image_rel in patent.images_relations
            ]
            images_pinned.extend(filter(lambda img: img["is_pinned"], images))
            patent_images.append({
                "patent_id": getattr(patent, "_id_dil", None),
                "images": images
            })
        response = {
            "person_id": getattr(printer, "_id_dil", None),
            "patent_images": patent_images,
            "total_images": sum(len(p["images"]) for p in patent_images),
            "total_images_pinned": len(images_pinned),
            "images_pinned": images_pinned
        }
        return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


# -- ROUTES PERSONS -- #


@api_router.get(
    "/persons",
    response_model=Page[PrinterMinimalResponseOut],
    include_in_schema=True,
    responses={400: {"model": Message}, 500: {"model": Message}},
    summary='Retrieve all persons (printers) with optional filters',
    tags=['Persons']
)
def read_printers(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None),

    mode: Optional[str] = Query("all", description="Mode de recherche : all / head_info / extra_info"),
    patent_city_query: Optional[List[str]] = Query(None),
    patent_date_start: Optional[str] = Query(None),
    exact_patent_date_start: bool = Query(False),
    sort: Optional[str] = Query("asc"),
) -> Union[JSONResponse, Page]:
    try:
        whoosh_hits = {}
        filters = []
        search_on_content = False

        if search:
            if mode not in ["all", "head_info", "extra_info"]:
                return JSONResponse(status_code=400, content={"message": "Mode de recherche invalide"})

            fields = {
                "all": ["lastname", "firstnames", "content"],
                "head_info": ["lastname", "firstnames"],
                "extra_info": ["content"]
            }[mode]

            search_on_content = "content" in fields

            sql_filters = []
            whoosh_ids = []

            if search_on_content:
                # Recherche Whoosh
                hits = search_whoosh(keyword=search, fields=fields)
                if not hits:
                    return Page(page=1, total=0, items=[], size=20, pages=0)

                whoosh_hits = {hit["id_dil"]: hit["highlight"] for hit in hits}
                whoosh_ids = list(whoosh_hits.keys())

            if mode in ["all", "head_info"]:
                # Recherche classique SQL sur lastname + firstnames
                terms = search.strip().split()
                for term in terms:
                    pattern = f"%{term}%"
                    sql_filters.append(
                        or_(
                            Person.lastname.ilike(pattern),
                            Person.firstnames.ilike(pattern)
                        )
                    )


            if whoosh_ids and sql_filters:
                # filtrage restrictif sur ID obtenus via whoosh
                filters.append(
                    and_(
                        Person._id_dil.in_(whoosh_ids),
                        or_(*sql_filters)
                    )
                )
            elif whoosh_ids:
                filters.append(Person._id_dil.in_(whoosh_ids))
            elif sql_filters:
                filters.append(or_(*sql_filters))

        # Requête SQL de base
        query = db.query(
            Person._id_dil,
            Person.lastname,
            Person.firstnames,
            func.count(Patent.id).label("total_patents")
        ).join(
            Patent, Patent.person_id == Person.id
        ).join(
            City, City.id == Patent.city_id, isouter=True
        ).group_by(
            Person._id_dil, Person.lastname, Person.firstnames
        )



        if patent_city_query:
            selected_villes = list(set(patent_city_query))
            ville_match = or_(*[Patent.city_label.ilike(q) for q in selected_villes])
            query = query.filter(ville_match)
            query = query.having(func.count(func.distinct(Patent.city_label)) >= len(selected_villes))

        if patent_date_start:
            normalized_date = normalize_date(patent_date_start)
            if exact_patent_date_start:
                query = query.filter(Patent.date_start == patent_date_start)
            else:
                query = query.filter(
                    or_(
                        Patent.date_start.like(f"{patent_date_start}%"),
                        Patent.date_start >= normalized_date
                    )
                )

        if search and whoosh_hits:
            filters.append(Person._id_dil.in_(list(whoosh_hits.keys())))

        if filters:
            query = query.filter(or_(*filters))

        if sort == "desc":
            query = query.order_by(desc(func.replace(func.replace(Person.lastname, "É", "E"), "È", "E")))
        else:
            query = query.order_by(asc(func.replace(func.replace(Person.lastname, "É", "E"), "È", "E")))

        paginated = paginate(db, query)

        # Construction de la réponse
        transformed_items = []
        for p in paginated.items:
            highlight = None
            if search and str(p.id_dil) in whoosh_hits:
                highlight = whoosh_hits.get(str(p.id_dil))

            transformed_items.append(
                PrinterMinimalResponseOut(
                    _id_dil=str(p.id_dil),
                    lastname=p.lastname,
                    firstnames=p.firstnames,
                    total_patents=p.total_patents,
                    highlight=highlight
                )
            )

        return Page(
            page=paginated.page,
            total=paginated.total,
            items=transformed_items,
            size=paginated.size,
            pages=paginated.pages,
        )

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"message": f"Erreur serveur: {e}"})

@api_router.get("/persons/person/{id}",
                include_in_schema=True,
                responses={404: {"model": Message}, 500: {"model": Message}},
                summary='',
                tags=['Persons'],
                response_model=PrinterOut)
async def read_printer(id: str,
                       html: bool = False,
                       db: Session = Depends(get_db)):
    try:
        printer = get_printer(db, {"_id_dil": id, "html": html}, enhance=True)
        if printer is None:
            return JSONResponse(status_code=404,
                                content={"message": f"Printer with id {id} not found"})
        return printer
    except Exception as e:
        return JSONResponse(status_code=500,
                            content={"message": "It seems the server have trouble: "
                                                f"{e}"})


# -- ROUTES PATENTS -- #

@api_router.get("/patents",
                response_model=Page[PatentMinimalOut],
                include_in_schema=True,
                responses={404: {"model": Message}, 500: {"model": Message}},
                summary='',
                tags=['Patents'])
def read_patents(db: Session = Depends(get_db)):
    try:
        paginated_patents = paginate(db.query(Patent))

        if not paginated_patents.items:
            return JSONResponse(status_code=404,
                                content={"message": "No patents found"})

        return paginated_patents
    except Exception as e:
        return JSONResponse(status_code=500,
                            content={"message": f"It seems the server have trouble: {e}"})


@api_router.get("/patents/patent/{id}",
                response_model=PatentOut,
                include_in_schema=True,
                responses={404: {"model": Message}, 500: {"model": Message}},
                summary='',
                tags=['Patents'])
def read_patent(id: str, db: Session = Depends(get_db), html: bool = False):
    try:
        patent = get_patent(db, {"_id_dil": id, "html": html}, enhance=True)
        if patent is None:
            return JSONResponse(status_code=404,
                                content={"message": f"Patent with id {id} not found"})
        return patent
    except Exception as e:
        return JSONResponse(status_code=500,
                            content={"message": f"It seems the server have trouble: {e}"})


# -- ROUTES REFERENTIAL -- #

@api_router.get("/referential/cities",
                response_model=Page[CityOut],
                include_in_schema=True,
                responses={404: {"model": Message}, 500: {"model": Message}},
                summary='',
                tags=['Referential'])
def read_cities(db: Session = Depends(get_db)):
    try:
        paginated_cities = paginate(db.query(City))

        if not paginated_cities.items:
            return JSONResponse(status_code=404,
                                content={"message": "No cities found"})

        return paginated_cities
    except Exception as e:
        return JSONResponse(status_code=500,
                            content={"message": f"It seems the server have trouble: {e}"})


@api_router.get("/referential/cities/city/{id}",
                response_model=CityOut,
                include_in_schema=True,
                responses={404: {"model": Message}, 500: {"model": Message}},
                summary='',
                tags=['Referential'])
def read_city(db: Session = Depends(get_db), id: str = None):
    try:
        city = get_city(db, {"_id_dil": id})
        if city is None:
            return JSONResponse(status_code=404,
                                content={"message": f"Address with id {id} not found"})
        transformed_address = CityOut(
            _id_dil=str(city._id_dil) if city._id_dil else None,
            label=city.label,
            country_iso_code=city.country_iso_code,
            long_lat=city.long_lat,
            insee_fr_code=city.insee_fr_code,
            insee_fr_department_code=city.insee_fr_department_code,
            insee_fr_department_label=city.insee_fr_department_label,
            geoname_id=city.geoname_id,
            wikidata_item_id=city.wikidata_item_id,
            dicotopo_item_id=city.dicotopo_item_id,
            databnf_ark=city.databnf_ark,
            viaf_id=city.viaf_id,
            siaf_id=city.siaf_id
        )
        return transformed_address
    except Exception as e:
        return JSONResponse(status_code=500,
                            content={"message": f"It seems the server have trouble: {e}"})


@api_router.get("/referential/addresses",
                response_model=Page[AddressMinimalOut],
                include_in_schema=True,
                responses={404: {"model": Message}, 500: {"model": Message}},
                summary='',
                tags=['Referential'])
def read_addresses(db: Session = Depends(get_db)):
    try:
        customPage = CustomizedPage[Page[AddressOut]]
        set_page(customPage)
        paginated_addresses = paginate(db.query(Address))

        if not paginated_addresses.items:
            return JSONResponse(status_code=404,
                                content={"message": "No addresses found"})

        transformed_addresses = [
            AddressMinimalOut(
                _id_dil=str(address.id_dil) if address.id_dil else None,
                label=address.label,
                city_label=address.city_label if address.city_label else None,
                city_id=str(get_city(db, {"id": int(address.city_id)})._id_dil) if address.city_id else None
            ) for address in paginated_addresses.items
        ]

        return Page(
            page=paginated_addresses.page,
            total=paginated_addresses.total,
            items=transformed_addresses,
            size=paginated_addresses.size,
            pages=paginated_addresses.pages,
        )

    except Exception as e:
        return JSONResponse(status_code=500,
                            content={"message": f"It seems the server has trouble: {e}"})


@api_router.get("/referential/addresses/address/{id}",
                response_model=AddressMinimalOut,
                include_in_schema=True,
                responses={404: {"model": Message}, 500: {"model": Message}},
                summary='',
                tags=['Referential'])
def read_address(db: Session = Depends(get_db), id: str = None):
    try:
        address = get_address(db, {"_id_dil": id})
        if address is None:
            return JSONResponse(status_code=404,
                                content={"message": f"Address with id {id} not found"})
        transformed_address = AddressMinimalOut(
            _id_dil=str(address._id_dil) if address._id_dil else None,
            label=address.label,
            city_label=address.city_label if address.city_label else None,
            city_id=get_city(db, {"id": int(address.city_id)})._id_dil if address.city_id else None
        )
        return transformed_address
    except Exception as e:
        return JSONResponse(status_code=500,
                            content={"message": f"It seems the server have trouble: {e}"})
