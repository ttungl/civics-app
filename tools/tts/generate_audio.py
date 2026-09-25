#!/usr/bin/env python3
"""Pre-record read-aloud audio with Microsoft Azure neural text-to-speech.

For each voice this writes, next to index.html:
    audio/<voice>/q001.mp3 … q128.mp3   the question
    audio/<voice>/a001.mp3 … a128.mp3   the default spoken answer
    audio/<voice>/sample.mp3            a short "Hi, I'm Ava…" preview
Each file name carries a hash of its text (e.g. a038-1f2e3d4c.mp3).
Existing clips are skipped and out-of-date ones deleted, so after editing an answer
(for example a new Speaker of the House) only the changed clips are re-recorded.

Setup (once):
    1. In the Azure portal create a "Speech" resource (the Free F0 tier is enough).
    2. Copy one of its Keys and its Location/Region (e.g. eastus).
Run from the repo root:
    AZURE_SPEECH_KEY=... AZURE_SPEECH_REGION=eastus python3 tools/tts/generate_audio.py
Options:
    --voices ava,emma   only these voices        --force   re-record everything
    --dry-run           show what would be recorded, no API calls

The key is only used on your computer; it is never written into the app.
"""
import argparse, json, os, re, time, urllib.error, urllib.request
from xml.sax.saxutils import escape

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
AUDIO = os.path.join(ROOT, 'audio')
FORMAT = 'audio-24khz-48kbitrate-mono-mp3'

# Keep in sync with VOICES in index.html.
VOICES = {
    'ava': 'en-US-AvaNeural',
    'andrew': 'en-US-AndrewNeural',
    'emma': 'en-US-EmmaNeural',
    'christopher': 'en-US-ChristopherNeural',
}
SAMPLE = "Hi, I'm {name}. I'll read your civics test questions out loud."


def load_questions():
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    arr = re.search(r'const QUESTIONS = (\[.*?\n\]);', html, re.S).group(1)
    return json.loads(re.sub(r',\n\]$', '\n]', arr))


# Same rules as speechText() / defaultSpokenAnswer() in index.html.
def speech_text(s):
    s = re.sub(r'\s*\(\d+\)', '', str(s))
    s = re.sub(r'[()\[\]]', '', s)
    return re.sub(r'\s+', ' ', s).strip()


def default_answer(q):
    if q.get('currentAnswers'):
        return q['currentAnswers'][0]
    if q.get('localKey'):
        return 'Answers will vary.'
    n = q.get('answersNeeded')
    return ', '.join(q['answers'][:n]) if n else q['answers'][0]


def text_hash(t):
    """FNV-1a (32-bit) of the UTF-8 text; must match textHash() in index.html."""
    h = 0x811c9dc5
    for byte in t.encode('utf-8'):
        h = ((h ^ byte) * 0x01000193) & 0xffffffff
    return f'{h:08x}'


def clips(questions):
    """(file name without .mp3, text). The text hash in the name means an edited answer
    gets a new file name, so the app never plays an out-of-date recording."""
    out = []
    for q in questions:
        qt, at = speech_text(q['question']), speech_text(default_answer(q))
        out.append((f"q{q['id']:03d}-{text_hash(qt)}", qt))
        out.append((f"a{q['id']:03d}-{text_hash(at)}", at))
    return out


def synthesize(key, region, voice, text):
    ssml = (f"<speak version='1.0' xml:lang='en-US'><voice name='{voice}'>"
            f"<prosody rate='-4%'>{escape(text)}</prosody></voice></speak>")
    req = urllib.request.Request(
        f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1',
        data=ssml.encode('utf-8'), method='POST',
        headers={'Ocp-Apim-Subscription-Key': key, 'Content-Type': 'application/ssml+xml',
                 'X-Microsoft-OutputFormat': FORMAT, 'User-Agent': 'n400practice-audio-builder'})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                wait = int(e.headers.get('Retry-After') or 0) or min(60, 4 * 2 ** attempt)
                print(f'    {e.code}: waiting {wait}s (free tier allows ~20 requests/minute)')
                time.sleep(wait)
                continue
            raise SystemExit(f'Azure returned {e.code}: {e.read().decode(errors="ignore")[:300]}')
    raise SystemExit('Azure kept rate-limiting; try again later.')


def check_voices(key, region):
    req = urllib.request.Request(f'https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list',
                                 headers={'Ocp-Apim-Subscription-Key': key})
    with urllib.request.urlopen(req, timeout=30) as r:
        names = {v['ShortName'] for v in json.load(r)}
    missing = [v for v in VOICES.values() if v not in names]
    if missing:
        raise SystemExit(f'These voices are not available in {region}: {missing}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--voices', default=','.join(VOICES))
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    key, region = os.environ.get('AZURE_SPEECH_KEY'), os.environ.get('AZURE_SPEECH_REGION')
    if not args.dry_run and not (key and region):
        raise SystemExit('Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION first (see the top of this file).')

    items = clips(load_questions())
    if not args.dry_run:
        check_voices(key, region)

    total_chars = recorded = removed = 0
    for vid in args.voices.split(','):
        vname = VOICES[vid]
        folder = os.path.join(AUDIO, vid)
        os.makedirs(folder, exist_ok=True)
        todo = items + [('sample', SAMPLE.format(name=vid.capitalize()))]
        wanted = {f'{name}.mp3' for name, _ in todo}
        for name, text in todo:
            path = os.path.join(folder, f'{name}.mp3')
            if not args.force and os.path.exists(path):
                continue
            total_chars += len(text)
            if args.dry_run:
                print(f'would record {vid}/{name}.mp3: {text[:70]}')
                continue
            open(path, 'wb').write(synthesize(key, region, vname, text))
            recorded += 1
            if recorded % 25 == 0:
                print(f'  {recorded} clips recorded…')
        for f in os.listdir(folder):          # recordings of text that no longer exists
            if f.endswith('.mp3') and f not in wanted:
                if args.dry_run:
                    print(f'would delete {vid}/{f}')
                else:
                    os.remove(os.path.join(folder, f))
                removed += 1
    verb = 'Would record' if args.dry_run else 'Recorded'
    print(f'{verb} {recorded if not args.dry_run else "the clips above"}; {total_chars} characters; {removed} stale clips {"to delete" if args.dry_run else "deleted"}.')


if __name__ == '__main__':
    main()
