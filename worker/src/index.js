// n400practice.com feedback API (Cloudflare Worker + D1).
// POST /feedback  {type, message, email?, questionId?, appVersion?, website?(honeypot)}
// Stores the feedback in D1. No IP address or device fingerprint is stored.

const ALLOWED_ORIGINS = ['https://n400practice.com', 'https://www.n400practice.com', 'null']; // 'null' = the app opened as a local file
const TYPES = ['suggestion', 'question', 'bug', 'other'];
const MAX_MESSAGE = 2000;

function cors(origin) {
  const allow = ALLOWED_ORIGINS.includes(origin) || /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin || '');
  return {
    'Access-Control-Allow-Origin': allow ? origin : ALLOWED_ORIGINS[0],
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    Vary: 'Origin',
  };
}

const json = (body, status, headers) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', ...headers } });

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get('Origin');
    const h = cors(origin);

    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: h });
    if (url.pathname === '/health') return json({ ok: true }, 200, h);
    if (url.pathname !== '/feedback' || request.method !== 'POST') return json({ error: 'Not found' }, 404, h);

    // Only accept requests from the app (browsers always send Origin on cross-site POST).
    if (origin && !ALLOWED_ORIGINS.includes(origin) && !/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin)) {
      return json({ error: 'Forbidden' }, 403, h);
    }

    // Rate limit per sender (the IP is used only as a transient counter key, never stored).
    if (env.LIMITER) {
      const { success } = await env.LIMITER.limit({ key: request.headers.get('CF-Connecting-IP') || 'unknown' });
      if (!success) return json({ error: 'Too many messages. Please try again in a minute.' }, 429, h);
    }

    let body;
    try {
      if (Number(request.headers.get('Content-Length') || 0) > 10000) throw new Error('too large');
      body = await request.json();
    } catch (e) {
      return json({ error: 'Invalid request' }, 400, h);
    }

    // Honeypot: real people never fill this hidden field. Pretend success so bots move on.
    if (body.website) return json({ ok: true }, 200, h);

    const type = TYPES.includes(body.type) ? body.type : 'other';
    const message = String(body.message || '').trim();
    const email = String(body.email || '').trim().slice(0, 254);
    const qid = Number.isInteger(body.questionId) && body.questionId >= 1 && body.questionId <= 128 ? body.questionId : null;
    const version = String(body.appVersion || '').slice(0, 20);

    if (message.length < 3) return json({ error: 'Please write a little more.' }, 400, h);
    if (message.length > MAX_MESSAGE) return json({ error: `Please keep it under ${MAX_MESSAGE} characters.` }, 400, h);
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json({ error: 'That email address looks incomplete.' }, 400, h);

    await env.DB.prepare(
      'INSERT INTO feedback (type, message, email, question_id, app_version) VALUES (?1, ?2, ?3, ?4, ?5)'
    ).bind(type, message, email || null, qid, version || null).run();

    return json({ ok: true }, 201, h);
  },
};
