import pytest
from datetime import timedelta
from security import create_access_token

def test_create_access_token():
    """Test access token creation."""
    data = {"sub": "user@example.com"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))
    assert isinstance(token, str)
    assert len(token) > 0
