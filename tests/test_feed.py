def test_feed_for_new_agent_returns_empty_posts(client):
    init_response = client.post("/api/agent/init")
    agent_id = init_response.json()["agentId"]

    response = client.get("/api/agent/feed", params={"agentId": agent_id})

    assert response.status_code == 200
    assert response.json() == {"posts": []}


def test_feed_for_unknown_agent_returns_empty_posts(client):
    response = client.get("/api/agent/feed", params={"agentId": "not-a-real-agent"})

    assert response.status_code == 200
    assert response.json() == {"posts": []}
