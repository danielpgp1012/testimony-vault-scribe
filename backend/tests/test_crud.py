from app.crud import check_duplicate_testimony


class FakeResult:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, items):
        self.items = items
        self.filters = {}

    def select(self, *_):
        return self

    def eq(self, key, value):
        self.filters[key] = value
        return self

    def execute(self):
        data = [i for i in self.items if all(i.get(k) == v for k, v in self.filters.items())]
        return FakeResult(data)


class FakeSupabase:
    def __init__(self, items):
        self.items = items

    def table(self, name):
        assert name == "testimonies"
        return FakeQuery(self.items)


def test_check_duplicate_with_church_id():
    data = [
        {"id": 1, "audio_hash": "h1", "church_id": "A"},
        {"id": 2, "audio_hash": "h1", "church_id": "B"},
    ]
    sb = FakeSupabase(data)
    assert check_duplicate_testimony(sb, "h1", church_id="A") == 1
    assert check_duplicate_testimony(sb, "h1", church_id="B") == 2
    assert check_duplicate_testimony(sb, "h1", church_id="C") is None
    assert check_duplicate_testimony(sb, "h1") == 1
