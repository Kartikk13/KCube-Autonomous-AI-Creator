PROMPT:1 (08-08-26 9:10AM) [Kirtika]

   Create this exact folder and file structure inside the current project.
   Create every folder and every file listed, even if some files are empty
   for now:
   app/main.py
   app/api/__init__.py
   app/core/config.py
   app/agent/__init__.py
   app/db/__init__.py
   app/services/__init__.py
   app/utils/__init__.py
   tests/__init__.py
   scripts/init_db.py
   postman/collection.json
   docs/HANDOVER_KITTU.md
   docs/HANDOVER_K7.md
   docs/BUG_TRACKER.md
   docs/DEPLOYMENT_CHECKLIST.md
   docs/TESTING_CHECKLIST.md
   docs/DEMO_SCRIPT.md
   docs/SUBMISSION_CHECKLIST.md
   data/.gitkeep
   .gitignore
   requirements.txt
   .env.example


PROMPT-2 (08-08-26 9:15AM) [Kirtika]

   In .gitignore add these lines exactly:
   data/
   .env
   __pycache__/
   *.db
   *.pyc

   In requirements.txt add these lines exactly:
   fastapi
   uvicorn[standard]
   apscheduler
   sqlalchemy
   sentence-transformers
   httpx
   google-generativeai
   python-dotenv
   pytest
   pytest-asyncio

   In .env.example add these lines exactly:
   GEMINI_API_KEY=
   OPENROUTER_API_KEY=
   DATABASE_URL=sqlite:///./data/agent.db
   PERSONA_NAME=Ada
   PERSONA_DOMAIN=AI Security
   PORT=8000
   ENV=development


PROMPT-3 (08-08-26 9:20AM) [Kirtika]
   In app/main.py, create a basic FastAPI app with one route:
   GET /healthz that returns {"status": "ok"}


PROMPT-4 (08-08-26 11:30AM) [Kirtika]

   In app/db/schema.sql, create exactly these 5 SQLite tables:

   CREATE TABLE IF NOT EXISTS agent (
      agent_id        TEXT PRIMARY KEY,
      persona_name    TEXT NOT NULL,
      persona_domain  TEXT NOT NULL,
      persona_voice   TEXT NOT NULL,
      initialized_at  TEXT NOT NULL
   );

   CREATE TABLE IF NOT EXISTS topics (
      topic_id        TEXT PRIMARY KEY,
      agent_id        TEXT NOT NULL REFERENCES agent(agent_id),
      title           TEXT NOT NULL,
      summary         TEXT,
      source_url      TEXT,
      discovered_at   TEXT NOT NULL,
      status          TEXT NOT NULL CHECK(status IN ('pending','accepted','rejected','published')),
      rejection_reason TEXT,
      embedding       BLOB
   );

   CREATE TABLE IF NOT EXISTS posts (
      id              TEXT PRIMARY KEY,
      agent_id        TEXT NOT NULL REFERENCES agent(agent_id),
      topic_id        TEXT REFERENCES topics(topic_id),
      text            TEXT NOT NULL,
      rationale       TEXT NOT NULL,
      sources         TEXT NOT NULL,
      created_at      TEXT NOT NULL,
      embedding       BLOB
   );

   CREATE TABLE IF NOT EXISTS editorial_log (
      log_id          INTEGER PRIMARY KEY AUTOINCREMENT,
      agent_id        TEXT NOT NULL REFERENCES agent(agent_id),
      topic_id        TEXT REFERENCES topics(topic_id),
      decision        TEXT NOT NULL CHECK(decision IN ('accept','reject')),
      reasoning       TEXT NOT NULL,
      logged_at       TEXT NOT NULL
   );

   CREATE TABLE IF NOT EXISTS scheduler_state (
      agent_id        TEXT PRIMARY KEY REFERENCES agent(agent_id),
      last_tick_at    TEXT,
      next_tick_at    TEXT,
      tick_count      INTEGER DEFAULT 0
   );

   Then in app/db/database.py, using SQLAlchemy, create:
   - an engine connected to the DATABASE_URL environment variable
   (default sqlite:///./data/agent.db if not set)
   - a function init_db() that reads schema.sql and runs it, creating the
   tables if they don't already exist
   - a function get_db() that gives a safe connection to use and closes it
   properly afterward

   Then in app/db/models.py create simple helper functions:
   - insert_agent(agent_id, persona_name, persona_domain, persona_voice)
   - insert_topic(topic_id, agent_id, title, summary, source_url, discovered_at, status, rejection_reason=None)
   - insert_post(id, agent_id, topic_id, text, rationale, sources, created_at)
   - get_posts_for_feed(agent_id) — returns posts ordered by created_at, newest first
   - get_recent_topics(agent_id, limit=20) — returns most recent topics

   Then in scripts/init_db.py, write a small script that calls init_db() and
   prints "Database ready."


PROMPT-5 (08-08-26 11:47AM) [Kirtika]
   python scripts/init_db.py


PROMPT-6 (08-08-26 12:10PM) [Kripa]
   In app/agent/persona.py, create a Python dictionary called PERSONA with
   these exact keys and values:

   name: "Ada"
   domain: "AI Security"
   voice_rules: a list of these 5 short rules —
   "precise and specific, never vague"
   "skeptical of hype, calls out overclaiming"
   "always references where information came from"
   "no emojis, no exclamation marks"
   "writes in first person, analytical tone"
   stable_interests: a list of these 6 tags —
   "model alignment", "red-teaming", "prompt injection",
   "AI supply-chain risk", "eval gaming", "deployment incidents"
   publishing_standards: a list of these 4 rules —
   "the claim must be verifiable, not rumor"
   "it must be genuinely new compared to the last 20 posts"
   "it must connect to at least one of the stable_interests"
   "it must have at least one credible source URL"

   Then write a function called render_system_prompt() with no arguments that
   takes this PERSONA dictionary and turns it into one long text paragraph
   that can be given to an AI model as its instructions — mentioning the name,
   domain, voice rules, interests, and standards clearly. Return that text as
   a string.


PROMPT-7 (08-08-26 12:14PM) [Kirtika]

   In app/api/init_route.py, create a FastAPI router with one route:
   POST /api/agent/init
   It should:
   1. Accept an optional JSON body like {"persona": {"name": "Ada", "domain": "AI Security"}}
   2. If no body or partial body is sent, fall back to the PERSONA dictionary
      from app.agent.persona
   3. Generate a new unique agent_id using Python's uuid.uuid4(), just use the
      first 8 characters as a string
   4. Save this agent into the database using insert_agent() from app.db.models
   5. Call start_scheduler(agent_id) from app.core.scheduler (this function
      might not exist yet — write a simple placeholder version of it in
      app/core/scheduler.py that just prints "scheduler started for {agent_id}"
      for now, we will replace it properly later)
   6. Return JSON: {"agentId": agent_id}
   This must respond fast, in under 1 second — don't do any heavy work here.
   Then in app/main.py, register this router so the route is active.


PROMPT-8 (08-08-26 12:47PM) [Kirtika]
   In app/api/feed_route.py, create a FastAPI router with one route:
   GET /api/agent/feed
   It should:
   1. Read a query parameter called agentId (example: /api/agent/feed?agentId=a1b2c3d4)
   2. Call get_posts_for_feed(agentId) from app.db.models
   3. Turn each database row into this exact JSON shape:
      {
      "id": "...",
      "createdAt": "...",
      "text": "...",
      "rationale": "...",
      "sources": [...]
      }
      (sources is stored as a JSON text string in the database — parse it back
      into a real list before returning)
   4. Return them newest first as: {"posts": [...]}
   5. If agentId is missing, unknown, or has zero posts yet — still return
      HTTP 200 with {"posts": []}. NEVER return an error for this case.

   Then register this router in app/main.py.


PROMPT-9 (08-08-26 02:45 - 02:50 PM) [Kripa]
   In app/core/scheduler.py, using the apscheduler library's AsyncIOScheduler:

   1. Create one scheduler object.
   2. Write a function start_scheduler(agent_id: str) that adds a repeating
      job which runs a function called run_agent_tick(agent_id) every 20
      minutes, and then starts the scheduler if it isn't already running.
      Set max_instances=1 and coalesce=True on the job (this means: if a
      previous tick is still running, don't pile up a second one on top of it).
   3. Write a function run_agent_tick(agent_id) that for now just prints
      "tick for {agent_id}" — we will fill in the real logic in a later step.
   4. Write a function stop_scheduler() that stops the scheduler cleanly, for
      testing purposes.
   5. Important: do NOT start the scheduler automatically when this file is
      imported — it should only start when start_scheduler() is actually called.


   The scheduler.py file has a bug: calling start_scheduler() outside of a
   running asyncio event loop raises "RuntimeError: no running event loop"
   because AsyncIOScheduler.start() requires one.

   Fix start_scheduler(agent_id) so it works safely whether or not an event
   loop is already running:
   - If there's a running event loop, use it as before.
   - If there isn't one (e.g. being called directly from a script for testing),
   create and run one temporarily just to call scheduler.start(), without
   blocking forever.

   Keep run_agent_tick(agent_id) and stop_scheduler() unchanged.


PROMPT-10 (08-08-26 04:10 PM) [Kripa]
   In app/agent/topic_discovery.py, write an async function:

   async def discover_topics(persona: dict) -> list[dict]

   It should:
   1. Fetch news from 2 free, no-login-required sources: the Hacker News
      "AI" front page RSS feed, and the arXiv cs.AI recent papers listing.
      Use the httpx library with an AsyncClient for the network calls.
   2. Turn each item into a dictionary with keys: title, summary, source_url,
      discovered_at (use the current time in ISO 8601 UTC format, meaning
      like "2026-08-08T10:30:00Z")
   3. Keep only up to 8 items, roughly filtered to match words from
      persona["stable_interests"] if possible, but don't be too strict — some
      items are fine even if the match isn't perfect
   4. If the network call fails for any reason, catch the error and return an
      empty list [] instead of crashing. This function must NEVER raise an
      error — a scheduler tick should never break because of a bad network call.


PROMPT-11 (08-08-26 04:26 PM) [Kripa]
   In app/agent/editorial.py, write an async function:

   async def judge_topic(topic: dict, persona: dict, recent_topics: list[dict]) -> dict

   It should:
   1. Call the Gemini AI model (create a helper file app/services/gemini_client.py
      with a function generate(system_prompt: str, user_prompt: str) -> str
      that uses the google-generativeai library and the GEMINI_API_KEY
      environment variable to call Gemini 2.5 Flash and return its text reply)
   2. Give Gemini the persona's system prompt (from render_system_prompt())
      plus a clear instruction: "decide accept or reject for this topic based
      on these publishing_standards rules: [list them], and check this topic
      isn't too similar to these recent topics: [list recent_topics titles].
      Reply ONLY with JSON in this exact shape: {"decision": "accept" or
      "reject", "reasoning": "one or two sentences explaining why"}"
   3. Parse Gemini's reply as JSON. If parsing fails for any reason (bad
      format, empty reply, anything), do NOT crash — instead return
      {"decision": "reject", "reasoning": "unparseable model output, defaulting to reject"}
   4. This function must NEVER raise an error under any circumstance — always
      return a valid dictionary with "decision" and "reasoning" keys.


PROMPT-12 (08-08-26 04:49PM) [Kirtika]

   Rewrite README.md with these sections:
   1. One-sentence description of the project
   2. A simple text diagram showing: Evaluator -> POST /init -> FastAPI ->
      Scheduler (every 20 min) -> Discover Topics -> Editorial Judgment ->
      Research -> Write Post -> Save to Database -> GET /feed -> Evaluator
   3. Setup instructions: clone the repo, create a venv, activate it, run
      pip install -r requirements.txt, copy .env.example to .env and fill in
      the API keys, run python scripts/init_db.py, then run
      uvicorn app.main:app --reload
   4. The API contract: show the exact request/response JSON for both
      POST /api/agent/init and GET /api/agent/feed
   5. A short "Persona" section describing Ada, the AI Security Researcher persona
   6. A placeholder line "Live URL: [will be added after deployment]"


PROMPT-13 (08-08-26 05:20 PM) [Kripa]
   In app/agent/research.py, write an async function:

   async def research_topic(topic: dict) -> dict

   It should:
   1. Fetch the webpage at topic["source_url"] using httpx, with a 10 second
      timeout
   2. Strip out the HTML tags to get plain readable text (basic stripping is
      fine, no need for a heavy library)
   3. Cut the text down to about 4000 characters if it's longer
   4. Return a new dictionary: the original topic's keys, PLUS a new key
      "research_context" (the text you extracted) and a new key "sources"
      (a list containing at least topic["source_url"])
   5. If the fetch fails for any reason (dead link, timeout, anything), do NOT
      crash — instead set "research_context" to topic["summary"] and still
      return "sources": [topic["source_url"]]


PROMPT-14 (08-08-26 05:26 PM) [Kripa]
   In app/agent/writer.py, write an async function:

   async def write_post(topic: dict, persona: dict) -> dict | None

   It should:
   1. Call Gemini (using the generate() function from app.services.gemini_client)
      with the persona's system prompt plus the topic's research_context, and
      ask it to write a social-media-style post between 150 and 280 words in
      the persona's voice, plus a short rationale (2-3 sentences) explaining
      why this topic was picked and why it matters right now. Ask for the
      reply as JSON only: {"text": "...", "rationale": "..."}
   2. Parse this JSON reply. Before parsing, strip any markdown code fences
      (```json, ```, or similar) and surrounding whitespace from the reply,
      since Gemini often wraps JSON responses in fences.
   3. If Gemini fails or the reply can't be parsed, try ONE more time using a
      backup AI service — create app/services/openrouter_client.py with a
      generate(system_prompt, user_prompt) function using the
      OPENROUTER_API_KEY environment variable and OpenRouter's free API,
      calling any free model available there.
   4. If BOTH Gemini and OpenRouter fail, return None instead of crashing —
      the caller will just skip publishing this time.


PROMPT-15 (08-08-26 05:40 PM) [Kripa]
   In app/services/embeddings.py, using the sentence-transformers library with
   the "all-MiniLM-L6-v2" model, create:
   - a function embed(text: str) that returns the sentence's embedding (a
   vector of numbers)
   - a function cosine_sim(a, b) that returns how similar two embeddings are,
   as a number between 0 and 1

   In app/agent/memory.py, create:
   - a function is_duplicate(candidate_embedding, existing_embeddings, threshold=0.87)
   that returns True if the candidate is too similar to anything already
   published
   - a function load_recent(agent_id, limit=20) that pulls the most recent
   topics from the database using get_recent_topics() from app.db.models

   Then EDIT app/core/scheduler.py's run_agent_tick(agent_id) function to do
   this, in this exact order, every time it runs:

   1. Call discover_topics(persona) to get candidate topics
   2. For each candidate topic:
      a. Turn its title+summary into an embedding, check is_duplicate() against
         recent topics' embeddings — skip this candidate if it's a duplicate
      b. Call judge_topic() to get accept/reject
      c. Save the decision into the editorial_log table no matter what
      d. If accepted: call research_topic(), then write_post()
      e. If write_post() succeeded: turn the new post's text into an
         embedding, check is_duplicate() against existing posts too — skip
         saving if too similar
      f. If it passed both duplicate checks: save it into the posts table
         using insert_post(), with a unique id, and save the topic into the
         topics table too
   3. Only publish AT MOST 1 new post per tick, even if multiple topics passed
   4. Wrap this entire function's body in a try/except so that ANY unexpected
      error is logged but never crashes the scheduler — the next tick in 20
      minutes should always still happen


PROMPT-16 (08-08-26 21:40 PM) [Kartik]
   In tests/test_init.py, using pytest and FastAPI's TestClient, write tests:
   1. Calling POST /api/agent/init returns HTTP 200 and a JSON body with a
      non-empty string "agentId"
   2. Calling it twice gives two DIFFERENT agentIds

   In tests/test_feed.py, write tests:
   1. Calling GET /api/agent/feed with a brand new agentId (that has never
      published anything) returns HTTP 200 and {"posts": []}
   2. Calling GET /api/agent/feed with a completely made-up/unknown agentId
      ALSO returns HTTP 200 and {"posts": []} — never an error

   Use a pytest fixture that points DATABASE_URL to a temporary test database
   file, so these tests never touch or mess up our real data/agent.db file.


PROMPT-17 (09-08-26 12:25 PM) [Kirtika]
   Create render.yaml for a Render.com web service:
   - environment: python
   - build command: pip install -r requirements.txt
   - start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   - plan: free
   - health check path: /healthz
   - list GEMINI_API_KEY and OPENROUTER_API_KEY as environment variables with
   sync set to false (this means: don't put the real key in this file,
   Render will ask for it separately in their website)

   Also create a Procfile with this one line:
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
