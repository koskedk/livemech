import logging
import socket
from fastapi.testclient import TestClient
from livemech.main import app

logger = logging.getLogger(__name__)

client = TestClient(app)


def test_root():
    expected_hostname = socket.gethostname()

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "Hello": "Maun",
        "Host": expected_hostname
    }

    logger.info(f"Response received: {response.json()}")
