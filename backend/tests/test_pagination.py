def test_list_testimonies_pagination(client_factory):
    items = [
        {
            "id": i,
            "recorded_at": f"2024-01-{i:02d}",
            "church_id": "Lausanne",
            "transcript_status": "completed",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        for i in range(10)
    ]
    client = client_factory(items)

    resp = client.get("/testimonies", params={"page": 1, "size": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["size"] == 5
    assert data["total"] == 10
    assert len(data["items"]) == 5
