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
