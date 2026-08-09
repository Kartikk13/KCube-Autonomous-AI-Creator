def test_init_returns_200_and_agent_id(client):
    response = client.post("/api/agent/init")

    assert response.status_code == 200
    body = response.json()
    assert "agentId" in body
    assert isinstance(body["agentId"], str)
    assert body["agentId"]


def test_init_returns_different_agent_ids(client):
    first = client.post("/api/agent/init")
    second = client.post("/api/agent/init")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["agentId"] != second.json()["agentId"]
