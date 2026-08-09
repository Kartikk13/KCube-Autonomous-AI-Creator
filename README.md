# KCube Autonomous AI Creator

An autonomous AI agent that discovers topics, applies editorial judgment, writes research-backed posts, and serves them through a simple FastAPI feed for evaluation.

## Architecture

```
Evaluator
   |
   v
POST /api/agent/init
   |
   v
FastAPI
   |
   v
Scheduler (every 20 min)
   |
   v
Discover Topics
   |
   v
Editorial Judgment
   |
   v
Research
   |
   v
Write Post
   |
   v
Save to Database
   |
   v
GET /api/agent/feed
   |
   v
Evaluator
```

## Setup

1. Clone the repo:

   ```bash
   git clone <https://github.com/kirtika-0102/KCube-Autonomous-AI-Creator.git>
   cd KCube-Autonomous-AI-Creator
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate it:

   ```bash
   # macOS / Linux
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env` and fill in the API keys:

   ```bash
   cp .env.example .env
   ```

6. Initialize the database:

   ```bash
   python scripts/init_db.py
   ```

7. Start the server:

   ```bash
   uvicorn app.main:app --reload
   ```

## API Contract

### POST /api/agent/init

Initializes a new agent. The request body is optional; missing persona fields fall back to defaults.

**Request**

```json
{
  "persona": {
    "name": "Ada",
    "domain": "AI Security"
  }
}
```

**Response**

```json
{
  "agentId": "a1b2c3d4"
}
```

### GET /api/agent/feed

Returns posts for an agent, newest first. Always responds with HTTP 200.

**Request**

```
GET /api/agent/feed?agentId=a1b2c3d4
```

**Response**

```json
{
  "posts": [
    {
      "id": "post-uuid",
      "createdAt": "2026-08-08T10:30:00+00:00",
      "text": "Post content here.",
      "rationale": "Why this topic was chosen and written this way.",
      "sources": [
        "https://example.com/article-1",
        "https://example.com/article-2"
      ]
    }
  ]
}
```

If `agentId` is missing, unknown, or has no posts yet:

```json
{
  "posts": []
}
```

## Persona

**Ada** is the default AI Security Researcher persona. She focuses on timely developments in AI security — threats, defenses, policy, and research — and writes in a professional, concise voice suited for a technical audience. You can override her name and domain when initializing an agent, or configure defaults via `PERSONA_NAME` and `PERSONA_DOMAIN` in `.env`.

## Deployment

Live URL: http://65.1.91.169:8000/docs
