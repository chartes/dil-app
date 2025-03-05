"""
routes.py

FastAPI routes for the DIL API.
"""

from fastapi import (APIRouter,
                     Depends,
                     Query)
from fastapi.responses import JSONResponse
from fastapi_pagination import (Page,
                                set_page)
from fastapi_pagination.ext.sqlalchemy import (paginate)
from fastapi_pagination.customization import CustomizedPage

from sqlalchemy import (or_,
                        asc)
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
                         PrinterOut,
                         PatentOut)
from api.models.models import (Person,
                               Patent,
                               City,
                               Address)

api_router = APIRouter()

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

@api_router.get("/persons",
                response_model=Page[PrinterMinimalResponseOut],
                include_in_schema=True,
                responses={400: {"model": Message}, 500: {"model": Message}},
                summary='Retrieve all persons (printers) with optional filters',
                tags=['Persons'])
def read_printers(db: Session = Depends(get_db),
                  patent_city_query: str = Query(None,
                                                 description="Filtrer des personnes par le nom de la ville des brevets."),
                  patent_date_start: str = Query(None,
                                                 description="Filtrer des personnes par la date de début des brevets. Forme requise : `YYYY`, `YYYY-MM`, `YYYY-MM-DD`"),
                  exact_patent_date_start: bool = Query(False,
                                                        description="Recherche exacte sur la date de début des brevets.")) -> \
        JSONResponse | Page:
    """
       🔍 **Rechercher des personnes (imprimeurs et/ou lithographes) avec filtres**

       Par défaut cette route retourne tous les personnes avec leur nom, prénoms et nombre de brevets associés par ordre alphabétique.

       - **Filtre sur la ville de l'enregistrement des brevets** (`patent_city_query`).
       - **Filtre sur la date des brevets** : Recherche des brevets commençant à `patent_date_start` soit à l'année ou année et mois ou année, mois et jour. Forme requise : `YYYY`, `YYYY-MM`, `YYYY-MM-DD`.
       - **Mode Exact** : Si `exact_patent_date_start=True`, recherche uniquement les brevets correspondant à l'année ou année et mois ou année, mois et jour.

       📌 **Exemples :**
       - `/persons?patent_city_query=Paris`
       - `/persons?patent_date_start=1900`
       - `/persons?patent_date_start=1900-10-01`
       - `/persons?patent_date_start=1900&exact_patent_date_start=True`
       """
    try:
        query = db.query(
            Person
        ).join(
            Patent, Patent.person_id == Person.id
        ).join(
            City, City.id == Patent.city_id, isouter=True
        )

        if patent_city_query:
            query = query.filter(
                or_(
                    City.label.like(f"%{patent_city_query}%"),
                    Patent.city_label.like(f"%{patent_city_query}%")
                )
            )

        if patent_date_start:
            if len(patent_date_start) >= 4:
                normalized_date = normalize_date(patent_date_start)
                if exact_patent_date_start:
                    query = query.filter(Patent.date_start == patent_date_start)
                else:
                    query = query.filter(or_(
                        Patent.date_start.like(f"{patent_date_start}%"),
                        Patent.date_start >= normalized_date
                    ))
                query = query.order_by(asc(Patent.date_start))

        paginated_printers = paginate(query)

        if not paginated_printers.items:
            return JSONResponse(status_code=404,
                                content={"message": "No printers found"})

        transformed_items = [
            PrinterMinimalResponseOut(
                _id_dil=str(printer.id_dil) if printer.id_dil else None,
                lastname=printer.lastname,
                firstnames=printer.firstnames,
                total_patents=int(len(get_printer(
                    db, {"_id_dil": str(printer.id_dil)}, enhance=False).patents))
                if printer.id_dil else 0
            ) for printer in paginated_printers.items if printer.id_dil
        ]

        return Page(
            page=paginated_printers.page,
            total=paginated_printers.total,
            items=transformed_items,
            size=paginated_printers.size,
            pages=paginated_printers.pages,
        )
    except Exception as e:
        return JSONResponse(status_code=500,
                            content={"message": f"It seems the server has trouble: {e}"})


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
def read_cities():
    pass


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
        print(get_city(db, {"id": int(address.city_id)})._id_dil)
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
