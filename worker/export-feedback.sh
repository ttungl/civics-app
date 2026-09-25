#!/bin/sh
# Export all feedback to feedback.csv (run from this folder after `npx wrangler login`).
set -e
npx wrangler d1 execute n400-feedback --remote --json \
  --command "SELECT id, created_at, type, question_id, email, app_version, status, message FROM feedback ORDER BY id" \
  | python3 -c '
import csv, json, sys
rows = json.load(sys.stdin)[0]["results"]
cols = ["id", "created_at", "type", "question_id", "email", "app_version", "status", "message"]
with open("feedback.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
print(f"Saved {len(rows)} messages to feedback.csv")
'
