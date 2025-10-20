"""
routes.py

FastAPI routes for the DIL API.
"""
from bdb import effective
from typing import Union, Optional, List

from fastapi import (APIRouter,
                     Depends,
                     Query)
from fastapi.responses import JSONResponse
from fastapi_pagination import (Page,
                                set_page)
from fastapi_pagination.ext.sqlalchemy import (paginate)
from fastapi_pagination.customization import CustomizedPage



from sqlalchemy import (or_,
                        and_,
                        func,
                        asc,
                        desc,
                        distinct)
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from cachetools import TTLCache, cached
import hashlib

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
from api.api_utils import (normalize_firstnames,
                           normalize_date,
                           year_bounds,
                           period_bounds)

api_router = APIRouter()

# -- infos routes -- #
cache = TTLCache(maxsize=1024, ttl=300)  # 5 minutes

@api_router.get(
    "/infos",
    include_in_schema=False,
    responses={500: {"model": Message}},
    summary='Get generic API information about data (e.g. total)',
)
def get_infos(db: Session = Depends(get_db)):
    """Retrieve generic information about the API data."""
    try:
        # filter only patents with date start between 1817–1870
        effective_patents_subquery = db.query(Patent).filter(
            Patent.date_start >= normalize_date("1817-01-01"),
            Patent.date_start <= normalize_date("1870-12-31")
        ).subquery()
        return {
            "total_persons": db.query(Person).count(),
            "total_patents": db.query(Patent).count(),
            "total_effective_patents": db.query(effective_patents_subquery).count(),
            "total_cities": db.query(City).count(),
            "total_addresses": db.query(Address).count()
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"It seems the server have trouble: {e}"})


@api_router.get(
    "/map/places",
    include_in_schema=False,
    responses={500: {"model": Message}},
    summary='Get map data: cities with geolocation and linked printers',
    tags=['Map']
)
def get_cities_with_printers(
        db: Session = Depends(get_db),
        patent_city_query: Optional[List[str]] = Query(None),
        patent_date_start: Optional[str] = Query(None),
        exact_patent_date_start: Optional[str] = Query(None)
):
    try:
        query = db.query(Patent.person_id).join(City)

        if patent_city_query:
            query = query.filter(City._id_dil.in_(patent_city_query))

        if patent_date_start:
            pstart, pend = period_bounds(patent_date_start)
            if pstart and pend:
                if bool(exact_patent_date_start):
                    query = query.filter(
                        and_(Patent.date_start >= pstart, Patent.date_start <= pend)
                    )
                else:
                    query = query.filter(
                        or_(
                            and_(
                                Patent.date_end.is_(None),
                                Patent.date_start >= pstart,
                                Patent.date_start <= pend
                            ),
                            and_(
                                Patent.date_end.is_not(None),
                                Patent.date_start <= pend,
                                Patent.date_end >= pstart
                            )
                        )
                    )

        if patent_city_query:
            query = query.group_by(Patent.person_id)
            query = query.having(
                func.count(distinct(City._id_dil)) == len(patent_city_query)
            )

        matching_person_ids = [row[0] for row in query.all()]
        if not matching_person_ids:
            return []

        query2 = db.query(
            City.id.label("city_id"),
            City.label.label("city_label"),
            City.insee_fr_department_label.label("city_dept_label"),
            City.long_lat.label("city_long_lat"),
            City._id_dil.label("city_dil"),
            Patent.city_label.label("patent_city_label"),
            Person.id.label("person_id"),
            Person._id_dil.label("person_dil"),
            Person.lastname,
            Person.firstnames,
        ).join(
            Patent, City.id == Patent.city_id
        ).join(
            Person, Person.id == Patent.person_id
        ).filter(
            City.long_lat.isnot(None),
            Person.id.in_(matching_person_ids)
        )

        results = query2.all()

        city_map = {}
        for row in results:
            city_id = row.city_id
            person_key = row.person_dil

            if city_id not in city_map:
                city_map[city_id] = {
                    "city_id": city_id,
                    "city_label": row.city_label,
                    "city_dept_label": row.city_dept_label,
                    "city_long_lat": row.city_long_lat,
                    "city_dil": row.city_dil,
                    "persons": {}
                }

            if person_key not in city_map[city_id]["persons"]:
                city_map[city_id]["persons"][person_key] = {
                    "id": person_key,
                    "firstnames": normalize_firstnames(row.firstnames),
                    "lastname": row.lastname,
                    "city_patent": row.patent_city_label
                }

        return [
            {
                "city_id": c["city_id"],
                "city_label": c["city_label"],
                "city_dept_label": c["city_dept_label"],
                "city_long_lat": c["city_long_lat"],
                "city_dil": c["city_dil"],
                "persons": list(c["persons"].values())
            }
            for c in city_map.values()
        ]

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Erreur serveur: {e}"})


@api_router.get("/places/autocomplete",
                response_model=List[CityOutMinimal],
                include_in_schema=False)
def autocomplete_city(
        q: Optional[str] = Query(None),
        selected: Optional[List[str]] = Query(None),
        db: Session = Depends(get_db)
):
    selected = list(set(selected or []))

    person_query = db.query(Patent.person_id).join(City)
    if selected:
        person_query = person_query.filter(City._id_dil.in_(selected))
        person_query = person_query.group_by(Patent.person_id)
        person_query = person_query.having(func.count(distinct(City._id_dil)) == len(selected))

    matching_person_ids = [row[0] for row in person_query.all()]
    if not matching_person_ids:
        return []

    city_query = db.query(
        City._id_dil.label("id_dil"),
        City.label,
        City.insee_fr_department_label.label("department_label_fr"),
        func.count(Patent.id).label("total_patents_if_selected"),
        func.count(distinct(Patent.person_id)).label("total_persons_if_selected")
    ).join(Patent).filter(
        Patent.person_id.in_(matching_person_ids)
    ).group_by(
        City._id_dil, City.label, City.insee_fr_department_label
    )

    if q:
        city_query = city_query.filter(City.label.ilike(f"{q}%"))

    if selected:
        city_query = city_query.filter(City._id_dil.notin_(selected))

    city_query = city_query.order_by(desc("total_patents_if_selected")).limit(20)

    results = []
    for row in city_query.all():
        results.append({
            "id": row.id_dil,
            "id_dil": row.id_dil,
            "label": row.label,
            "department_label_fr": row.department_label_fr,
            "total_patents_if_selected": row.total_patents_if_selected,
            "total_persons_if_selected": row.total_persons_if_selected
        })

    return results

# -- IMAGE ROUTES -- #
@api_router.get(
    "/persons/person/{id}/images",
    include_in_schema=False,
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
def make_cache_key(name: str, content: str):
    raw = f"{name or ''}|{content or ''}"
    return hashlib.sha256(raw.encode()).hexdigest()


@cached(cache=cache, key=lambda name, content: make_cache_key(name, content))
def cached_search(name, content):
    return search_whoosh(query_firstnames_lastname=name, query_content=content)


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
        search_head_info: Optional[str] = Query(None),
        search_extra_info: Optional[str] = Query(None),
        patent_city_query: Optional[List[str]] = Query(None),
        patent_date_start: Optional[str] = Query(None),
        exact_patent_date_start: bool = Query(False),
        sort: Optional[str] = Query("asc")
) -> Union[JSONResponse, Page]:
    """
    Recherche de personnes (imprimeurs), avec filtres facultatifs.

    - `search`: Terme recherché
    - `search_head_info`: Active la recherche sur nom/prénom
    - `search_extra_info`: Active la recherche sur contenu (brevets, infos)
    """
    try:
        filters = []
        if not search_head_info and not search_extra_info:
            whoosh_ids = None
            whoosh_hits = {}
        else:
            whoosh_hits = cached_search(
                name=search_head_info,
                content=search_extra_info
            )
            if not whoosh_hits:
                return Page(page=1, total=0, items=[], size=20, pages=0)
            whoosh_ids = list(whoosh_hits.keys())

        query = db.query(
            Person._id_dil,
            Person.lastname,
            Person.firstnames,
            func.count(Patent.id).label("total_patents")
        ).outerjoin(
            Patent, Patent.person_id == Person.id
        ).outerjoin(
            City, City.id == Patent.city_id
        ).group_by(
            Person._id_dil, Person.lastname, Person.firstnames
        )

        if whoosh_ids is not None:
            query = query.filter(Person._id_dil.in_(whoosh_ids))

        if patent_city_query:
            query = query.filter(City._id_dil.in_(set(patent_city_query)))
            query = query.having(func.count(func.distinct(City._id_dil)) == len(set(patent_city_query)))

        if patent_date_start:
            pstart, pend = period_bounds(patent_date_start)
            if pstart and pend:
                if exact_patent_date_start:
                    query = query.filter(
                        and_(Patent.date_start >= pstart, Patent.date_start <= pend)
                    )
                else:
                    # Argument :
                    # - if NULL -> start inside the interval
                    # - if not NULL -> overlaps the interval
                    query = query.filter(
                        or_(
                            and_(
                                Patent.date_end.is_(None),
                                Patent.date_start >= pstart,
                                Patent.date_start <= pend
                            ),
                            and_(
                                Patent.date_end.is_not(None),
                                Patent.date_start <= pend,
                                Patent.date_end >= pstart
                            )
                        )
                    )

        if filters:
            query = query.filter(and_(*filters))

        if sort == "desc":
            query = query.order_by(desc(func.replace(func.replace(Person.lastname, "É", "E"), "È", "E")))
        else:
            query = query.order_by(asc(func.replace(func.replace(Person.lastname, "É", "E"), "È", "E")))

        paginated = paginate(db, query)

        transformed_items = []
        for p in paginated.items:
            highlight = whoosh_hits.get(str(p.id_dil), {}).get("highlight")
            firstnames = normalize_firstnames(p.firstnames)

            transformed_items.append(
                PrinterMinimalResponseOut(
                    _id_dil=str(p.id_dil),
                    lastname=p.lastname,
                    firstnames=firstnames,
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
        print(e)
        import traceback
        return JSONResponse(status_code=500, content={"message": f"Erreur serveur: {e}"})


@api_router.get("/persons/person/{id}",
                include_in_schema=True,
                responses={404: {"model": Message}, 500: {"model": Message}},
                summary='Retrieve a specific person (printer) by ID',
                tags=['Persons'],
                response_model=PrinterOut)
async def read_printer(id: str,
                       html: bool = False,
                       db: Session = Depends(get_db)):
    """
    Retrieve a specific person (printer) by DIL ID.
    - `id`: The DIL ID of the person (printer). e.g., "person_dil_2QO3gEnU".
    """
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
                summary='Retrieve all patents with pagination',
                tags=['Patents'])
def read_patents(db: Session = Depends(get_db)):
    """
    Retrieve all patents with pagination.
    """
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
                summary='Retrieve a specific patent by ID',
                tags=['Patents'])
def read_patent(id: str, db: Session = Depends(get_db), html: bool = False):
    """
    Retrieve a specific patent by DIL ID. e.g., "patent_dil_20XQCaDr".
    """
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
                summary='Retrieve all cities with pagination',
                tags=['Referential'])
def read_cities(db: Session = Depends(get_db)):
    """Retrieve all cities with pagination.
    """
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
                summary='Retrieve a specific city by ID',
                tags=['Referential'])
def read_city(db: Session = Depends(get_db), id: str = None):
    """Retrieve a specific city by DIL ID. e.g., "city_dil_I11CRwcK".
    """
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
                summary='Retrieve all addresses with pagination',
                tags=['Referential'])
def read_addresses(db: Session = Depends(get_db)):
    """Retrieve all addresses with pagination.
    """
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
                summary='Retrieve a specific address by ID',
                tags=['Referential'])
def read_address(db: Session = Depends(get_db), id: str = None):
    """Retrieve a specific address by DIL ID. e.g., "address_dil_k5VNb151".
    """
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

@api_router.get("/graph", tags=["Graph"])
def get_graph_data(year: int = Query(..., description="Filtrer les brevets dont date_start <= année"),
                   db: Session = Depends(get_db)):

    patents = db.query(Patent).all()



    nodes = {}
    edges = {}
    edge_id = 0

    for patent in patents:
        patent_id = patent._id_dil
        person = patent.person
        city = patent.city

        # -- Brevet node --
        nodes[patent_id] = {
            "name": f"Brevet {patent_id[-5:]}",
            "type": "brevet",
            "year": int(patent.date_start.split('-')[0]) if patent.date_start else None
        }

        # -- Imprimeur node --
        if person:
            person_id = person._id_dil
            if person_id not in nodes:
                nodes[person_id] = {
                    "name": f"{person.lastname} {person.firstnames or ''}",
                    "type": "imprimeur"
                }

            edges[f"e{edge_id}"] = {
                "source": person_id,
                "target": patent_id,
                "type": "a_obtenu"
            }
            edge_id += 1

        # -- Ville node --
        if city:
            city_id = city._id_dil
            if city_id not in nodes:
                nodes[city_id] = {
                    "name": city.label,
                    "type": "ville"
                }

            edges[f"e{edge_id}"] = {
                "source": patent_id,
                "target": city_id,
                "type": "localise_a"
            }
            edge_id += 1

        # -- printer relations via patent --
        for rel in patent.patent_relations:
            src = rel.person
            tgt = rel.person_related
            if not (src and tgt):
                continue

            src_id = src._id_dil
            tgt_id = tgt._id_dil

            for p in [src, tgt]:
                if p._id_dil not in nodes:
                    nodes[p._id_dil] = {
                        "name": f"{p.lastname} {p.firstnames or ''}",
                        "type": "imprimeur"
                    }

            edges[f"e{edge_id}"] = {
                "source": src_id,
                "target": tgt_id,
                "type": rel.type  # parrain, successeur, etc.
            }
            edge_id += 1


    return {"nodes": nodes, "edges": edges}
