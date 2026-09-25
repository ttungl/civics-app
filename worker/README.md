# Feedback API

Feedback from the app (Settings › *Send feedback*, and *Report a problem with this question*) goes to a small **Cloudflare Worker** at `https://api.n400practice.com/feedback`, which stores it in a **Cloudflare D1** database (SQLite) called `n400-feedback`. Both are on Cloudflare's free plan.

**What's stored:** time, type (`suggestion`, `question`, `bug`, `other`), the message, the question number (for question reports), the app version, and an email **only if the person typed one**. No IP address, browser details, or anything else. Spam protection: a hidden honeypot field and a rate limit of about 5 messages per minute per sender (the IP is used only as a short-lived counter key, never saved).

## Reading feedback

**In the browser (easiest):** [dash.cloudflare.com](https://dash.cloudflare.com) → **Storage & Databases** → **D1 SQL Database** → **n400-feedback** → **Console**, then run:

```sql
SELECT id, created_at, type, question_id, email, message FROM feedback ORDER BY id DESC;
```

Useful queries:

```sql
-- New messages only
SELECT * FROM feedback WHERE status = 'new' ORDER BY id DESC;
-- Reports about a specific question
SELECT * FROM feedback WHERE question_id = 23;
-- Mark one as read or done
UPDATE feedback SET status = 'done' WHERE id = 12;
```

**From a terminal** (after `npx wrangler login`, from this folder):

```
npx wrangler d1 execute n400-feedback --remote --command "SELECT * FROM feedback ORDER BY id DESC LIMIT 50"
./export-feedback.sh            # saves feedback.csv
```

## Deploying changes

```
cd worker
npx wrangler deploy                                     # the Worker
npx wrangler d1 execute n400-feedback --remote --file=schema.sql   # only for a brand-new database
```

## Adding Cloudflare Turnstile later (only if spam appears)

Create a Turnstile widget for `n400practice.com` in the Cloudflare dashboard, save its secret with `npx wrangler secret put TURNSTILE_SECRET`, verify the token in `src/index.js`, and render the widget in the feedback form. It isn't enabled now because it would add a third-party script and stop feedback from working when the app is opened as a local file.
