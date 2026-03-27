from uuid import UUID
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from livemech.domain.shop import Shop
from livemech.infrastructure.models import ShopEntity
from livemech.infrastructure.database.session import get_db_context



class CreateShopCommand(BaseModel):
    name: str
    description: str | None = None

class CreateShopCommandHandler:
    def __init__(self,context:AsyncSession):
        self.db=context

    async def handle(self,command:CreateShopCommand)->UUID:
        shop=Shop(
            name=command.name,
            description=command.description
        )

        shop_entity=ShopEntity(
            id=shop.id,
            name=shop.name,
            description=shop.description
        )

        self.db.add(shop_entity)
        
        await self.db.commit()

        return shop.id

        
def provide_create_shop_command_handler(
        context:AsyncSession=Depends(get_db_context)
)->CreateShopCommandHandler:
    return CreateShopCommandHandler(context=context)