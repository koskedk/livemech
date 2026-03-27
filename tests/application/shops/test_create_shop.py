import pytest
import logging
from unittest.mock import MagicMock, AsyncMock
from uuid import UUID

from livemech.application.shops.create_shop import CreateShopCommandHandler
from livemech.application.shops.create_shop import CreateShopCommand
from livemech.infrastructure.models import ShopEntity


logger=logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_create_shop_hander_saves():

    mock_context=MagicMock()
    mock_context.commit=AsyncMock()

    handler=CreateShopCommandHandler(context=mock_context)

    command=CreateShopCommand(
        name="Auto X world",
        description="Your Only Garage for German cars"
    )

    new_id=await handler.handle(command)

    assert isinstance(new_id,UUID)

    mock_context.add.assert_called_once()

    saved=mock_context.add.call_args[0][0]

    assert isinstance(saved, ShopEntity)
    assert saved.name=="Auto X world"
    assert saved.description=="Your Only Garage for German cars"

    mock_context.commit.assert_awaited_once()

    logger.info(f"Saved: {new_id}")