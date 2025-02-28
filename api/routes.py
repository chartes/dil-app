from fastapi import (APIRouter,
                     Depends)
from fastapi.responses import JSONResponse
from fastapi_pagination import (Page,
                                paginate)
from fastapi_pagination.utils import disable_installed_extensions_check

from sqlalchemy.orm import Session

from api.database import get_db
from api.crud import get_user, get_printer
from api.schemas import (Message,
                         PrinterOut)

api_router = APIRouter()

"""
- récupérer un imprimeur et ses adresses perso et ses brevets
- récupérer tous les imprimeurs et leurs adresses ids brevet perso paginés
- récupérer tous les brevets et leurs adresses pro paginés
- récupérer les brevets d'un imprimeur et leurs adresses pro paginés
- récupérer les images associées aux brevets d'un imprimeur (caché)
"""

@api_router.get("/printers/{printer_id}",
                include_in_schema=True,
                responses={404: {"model": Message}, 500: {"model": Message}},
                summary='',
                tags=['Persons'],
                response_model=PrinterOut)
async def read_printer(printer_id: str, db: Session = Depends(get_db)):
    try:
        printer = get_printer(db, {"id": printer_id})
        if printer is None:
            return JSONResponse(status_code=404,
                            content={"message": f"Printer with id {printer_id} not found"})
        return printer
    except Exception as e:
        return JSONResponse(status_code=500,
                            content={"message": "It seems the server have trouble: "
                                                f"{e}"})