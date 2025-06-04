import os
import sys

# Ensure the application package is on the path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Default environment variables required by the app during import
os.environ.setdefault("SUPABASE_URL", "http://test")
os.environ.setdefault("SUPABASE_KEY", "key")

from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
import pytest

from app.main import app
from app.deps import get_supabase


class FakeResult:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, items):
        self.items = items
        self.filters = {}
        self._order_key = None
        self._desc = False

    def select(self, *_):
        return self

    def eq(self, key, value):
        self.filters[key] = value
        return self

    def order(self, key, desc=False):
        self._order_key = key
        self._desc = desc
        return self

    def execute(self):
        data = [i for i in self.items if all(i.get(k) == v for k, v in self.filters.items())]
        if self._order_key:
            data = sorted(data, key=lambda x: x.get(self._order_key), reverse=self._desc)
        return FakeResult(data)


class FakeSupabase:
    def __init__(self, items):
        self.items = items

    def table(self, name):
        assert name == "testimonies"
        return FakeQuery(self.items)


@pytest.fixture
def client_factory():
    """Return a TestClient with dependencies overridden."""

    def _factory(items):
        app.dependency_overrides[get_supabase] = lambda: FakeSupabase(items)
        add_pagination(app)
        return TestClient(app)

    yield _factory
    app.dependency_overrides.clear()

