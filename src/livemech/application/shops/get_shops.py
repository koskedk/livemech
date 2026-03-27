from uuid import UUID
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from livemech.domain.shop import Shop
from livemech.infrastructure.models import ShopEntity
from livemech.infrastructure.database.session import get_db_context

class GetShopsQuery(BaseModel):
    pass

class ShopResponse(BaseModel):
    id: str
    name: str
    description: str | None = None

class GetShopsQueryHandler:
    def __init__(self, context: AsyncSession):
        self.db = context

    async def handle(self, query: GetShopsQuery) -> list[ShopResponse]:
        from sqlalchemy import select
        from livemech.infrastructure.models import ShopEntity

        result = await self.db.execute(select(ShopEntity))
        shops = result.scalars().all()

        return [
            ShopResponse(
                id=str(shop.id),
                name=shop.name,
                description=shop.description
            )
            for shop in shops
        ]

def provide_get_shops_query_handler(
    context: AsyncSession = Depends(get_db_context)
) -> GetShopsQueryHandler:
    return GetShopsQueryHandler(context=context)
