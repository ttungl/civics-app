#!/usr/bin/env python3
"""Pre-record read-aloud audio for every question and answer.

Default engine: Kokoro (open-source, Apache-2.0; runs locally, no account or key).
For each voice this writes, next to index.html:
    audio/<voice>/q001-<hash>.mp3 …   the question
    audio/<voice>/a001-<hash>.mp3 …   the default spoken answer
    audio/<voice>/sample.mp3          a short "Hi, I'm Heart…" preview
Each file name carries a hash of its text. Existing clips are skipped and
out-of-date ones deleted, so after editing an answer (for example a new Speaker
of the House) only the changed clips are re-recorded. The app never plays an
old recording: a missing clip falls back to the device voice.

Setup (once, ~350 MB download):
    python3 -m venv .ttsenv && .ttsenv/bin/pip install kokoro-onnx soundfile
    mkdir -p .kokoro && cd .kokoro && \\
      curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx && \\
      curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
    (ffmpeg with libmp3lame must be installed, e.g. `brew install ffmpeg`)
Run from the repo root:
    KOKORO_DIR=.kokoro .ttsenv/bin/python tools/tts/generate_audio.py
Options:
    --voices heart,michael   only these voices    --force   re-record everything
    --dry-run                list what would be recorded
    --engine azure           use Microsoft Azure instead (needs AZURE_SPEECH_KEY / AZURE_SPEECH_REGION)
"""
import argparse, json, os, re, subprocess, time, urllib.error, urllib.request
from xml.sax.saxutils import escape

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
AUDIO = os.path.join(ROOT, 'audio')

# App voice id -> engine voice. Keep in sync with VOICES in index.html.
KOKORO_VOICES = {'heart': 'af_heart', 'bella': 'af_bella', 'michael': 'am_michael', 'fenrir': 'am_fenrir'}
AZURE_VOICES = {'ava': 'en-US-AvaNeural', 'andrew': 'en-US-AndrewNeural',
                'emma': 'en-US-EmmaNeural', 'christopher': 'en-US-ChristopherNeural'}
SAMPLE = "Hi, I'm {name}. I'll read your civics test questions out loud."
KOKORO_SPEED = 0.95


def load_questions():
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    arr = re.search(r'const QUESTIONS = (\[.*?\n\]);', html, re.S).group(1)
    return json.loads(re.sub(r',\n\]$', '\n]', arr))


# Same rules as speechText() / defaultSpokenAnswer() / textHash() in index.html.
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
    """FNV-1a (32-bit) of the UTF-8 text."""
    h = 0x811c9dc5
    for byte in t.encode('utf-8'):
        h = ((h ^ byte) * 0x01000193) & 0xffffffff
    return f'{h:08x}'


def clips(questions):
    out = []
    for q in questions:
        qt, at = speech_text(q['question']), speech_text(default_answer(q))
        out.append((f"q{q['id']:03d}-{text_hash(qt)}", qt))
        out.append((f"a{q['id']:03d}-{text_hash(at)}", at))
    return out


# ---------- engines ----------
class KokoroEngine:
    def __init__(self):
        from kokoro_onnx import Kokoro
        d = os.environ.get('KOKORO_DIR', os.path.join(ROOT, '.kokoro'))
        self.k = Kokoro(os.path.join(d, 'kokoro-v1.0.onnx'), os.path.join(d, 'voices-v1.0.bin'))

    def mp3(self, voice, text):
        samples, sr = self.k.create(text, voice=voice, speed=KOKORO_SPEED, lang='en-us')
        return subprocess.run(
            ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', '-',
             '-af', 'afade=t=in:d=0.01', '-codec:a', 'libmp3lame', '-b:a', '48k', '-f', 'mp3', '-'],
            input=samples.astype('float32').tobytes(), capture_output=True, check=True).stdout


class AzureEngine:
    FORMAT = 'audio-24khz-48kbitrate-mono-mp3'

    def __init__(self):
        self.key, self.region = os.environ.get('AZURE_SPEECH_KEY'), os.environ.get('AZURE_SPEECH_REGION')
        if not (self.key and self.region):
            raise SystemExit('Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION first.')

    def mp3(self, voice, text):
        ssml = (f"<speak version='1.0' xml:lang='en-US'><voice name='{voice}'>"
                f"<prosody rate='-4%'>{escape(text)}</prosody></voice></speak>")
        req = urllib.request.Request(
            f'https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1', data=ssml.encode(), method='POST',
            headers={'Ocp-Apim-Subscription-Key': self.key, 'Content-Type': 'application/ssml+xml',
                     'X-Microsoft-OutputFormat': self.FORMAT, 'User-Agent': 'n400practice-audio-builder'})
        for attempt in range(8):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    return r.read()
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504):
                    time.sleep(int(e.headers.get('Retry-After') or 0) or min(60, 4 * 2 ** attempt))
                    continue
                raise SystemExit(f'Azure returned {e.code}: {e.read().decode(errors="ignore")[:300]}')
        raise SystemExit('Azure kept rate-limiting; try again later.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', choices=['kokoro', 'azure'], default='kokoro')
    ap.add_argument('--voices')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    table = KOKORO_VOICES if args.engine == 'kokoro' else AZURE_VOICES
    voices = args.voices.split(',') if args.voices else list(table)
    engine = None if args.dry_run else (KokoroEngine() if args.engine == 'kokoro' else AzureEngine())

    items = clips(load_questions())
    chars = recorded = removed = 0
    t0 = time.time()
    for vid in voices:
        folder = os.path.join(AUDIO, vid)
        os.makedirs(folder, exist_ok=True)
        todo = items + [('sample', SAMPLE.format(name=vid.capitalize()))]
        wanted = {f'{name}.mp3' for name, _ in todo}
        for name, text in todo:
            path = os.path.join(folder, f'{name}.mp3')
            if not args.force and os.path.exists(path):
                continue
            chars += len(text)
            if args.dry_run:
                print(f'would record {vid}/{name}.mp3: {text[:70]}')
                continue
            data = engine.mp3(table[vid], text)
            with open(path + '.part', 'wb') as f:
                f.write(data)
            os.replace(path + '.part', path)
            recorded += 1
            if recorded % 50 == 0:
                print(f'  {recorded} clips recorded ({time.time() - t0:.0f}s)', flush=True)
        for f in os.listdir(folder):
            if f.endswith('.mp3') and f not in wanted:
                if not args.dry_run:
                    os.remove(os.path.join(folder, f))
                removed += 1
    print(f'{"Dry run" if args.dry_run else "Recorded " + str(recorded) + " clips"}; {chars} characters; '
          f'{removed} out-of-date clips {"would be " if args.dry_run else ""}removed; {time.time() - t0:.0f}s.')


if __name__ == '__main__':
    main()
