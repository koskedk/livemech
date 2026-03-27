import logging
import pytest
from uuid import UUID

from livemech.domain.shop import Shop


logger = logging.getLogger(__name__)

def test_should_create():

    shop=Shop(name="Auto world",description="Your No.1 Garage for German cars")

    assert shop.name=="Auto world"
    assert shop.description=="Your No.1 Garage for German cars"
    assert isinstance(shop.id,UUID)

    logger.info(shop)
