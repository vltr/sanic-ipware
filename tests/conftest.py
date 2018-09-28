import pytest
from multidict import CIMultiDict
from sanic.request import Request


@pytest.fixture
def create_request():
    def _create_request(headers=None):
        headers = headers or {}
        return Request(
            url_bytes=b"/",
            headers=CIMultiDict(headers),
            version=None,
            method="GET",
            transport=None,
        )

    return _create_request
