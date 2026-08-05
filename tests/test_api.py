from fastapi.testclient import TestClient
from infrastructure.web.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "architecture" in response.json()

def test_chat_creates_new_session():
    payload = {
        "message": "Hello, this is a test message!"
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "session_id" in data
    assert "response" in data
    assert "Hello, this is a test message!" in data["response"]

def test_chat_persists_session():
    # 1. Create a session first
    payload1 = {
        "message": "First message"
    }
    response1 = client.post("/chat", json=payload1)
    assert response1.status_code == 200
    session_id = response1.json()["session_id"]
    
    # 2. Send another message with same session_id
    payload2 = {
        "session_id": session_id,
        "message": "Second message"
    }
    response2 = client.post("/chat", json=payload2)
    assert response2.status_code == 200
    data2 = response2.json()
    
    assert data2["session_id"] == session_id
    assert "Second message" in data2["response"]

def test_preset_sessions_exist():
    payload = {
        "session_id": "session-2",
        "message": "Continuing conversation..."
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "session-2"
    assert "Continuing conversation..." in data["response"]

