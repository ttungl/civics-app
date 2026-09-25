-- Feedback sent from the app. No IP address or device fingerprint is stored.
CREATE TABLE IF NOT EXISTS feedback (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
  type        TEXT    NOT NULL,              -- suggestion | question | bug | other
  message     TEXT    NOT NULL,
  email       TEXT,                          -- only if the person chose to give one
  question_id INTEGER,                       -- 1–128 when reporting a problem with a question
  app_version TEXT,
  status      TEXT    NOT NULL DEFAULT 'new' -- new | read | done (for your own tracking)
);
CREATE INDEX IF NOT EXISTS feedback_created ON feedback (created_at);
