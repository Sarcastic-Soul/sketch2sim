from backend.meta import cache


def test_json_cache_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", str(tmp_path))
    payload = b"same request"
    assert cache.get_json("unit", payload) is None
    cache.put_json("unit", payload, {"value": 42})
    assert cache.get_json("unit", payload) == {"value": 42}
    assert cache.cache_path("unit", payload, "json").parent == tmp_path
