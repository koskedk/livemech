from fastapi import APIRouter
from fastapi import Depends
from livemech.application.shops.create_shop import CreateShopCommand
from livemech.application.shops.create_shop import CreateShopCommandHandler
from livemech.application.shops.create_shop import provide_create_shop_command_handler
from livemech.application.shops.get_shops import GetShopsQuery, GetShopsQueryHandler, ShopResponse, provide_get_shops_query_handler

router=APIRouter(prefix="/shops",tags=["Shops"])

@router.post("/",status_code=200)
async def create_shop(
    command:CreateShopCommand,
    handler:CreateShopCommandHandler=Depends(provide_create_shop_command_handler)
):
    new_shop_id=await handler.handle(command)
    return {"id": new_shop_id}

@router.get("/",response_model=list[ShopResponse] ,status_code=200 )
async def get_shops(
    handler:GetShopsQueryHandler=Depends(provide_get_shops_query_handler)
):
    query=GetShopsQuery()
    shops=await handler.handle(query)
    return shops