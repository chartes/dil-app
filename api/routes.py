from fastapi import (APIRouter,
                     Depends)

from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.crud import get_user

api_router = APIRouter()


"""example for async post
@api_router.post('/user')
async def index(user, db: AsyncSession = Depends(get_db)):
    db_user = User(username=user.username)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
"""

@api_router.get('/user')
async def get_user(db: AsyncSession = Depends(get_db)):
    res = await get_user({"username": "test"}, sync=False)
    return {
        "id": res.id,
        "username": res.username,
    }