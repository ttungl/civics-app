#!/usr/bin/env python3
"""Check every recorded clip by transcribing it back to text (a listening test without ears).

Needs: pip install faster-whisper num2words   (in the same environment as generate_audio.py)
Run from the repo root:  .ttsenv/bin/python tools/tts/verify_audio.py [--voices heart,bella]
Prints clips whose transcript doesn't match the intended text, and exits 1 if any fail.
"""
import argparse, difflib, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_audio import AUDIO, KOKORO_VOICES, SAMPLE, clips, load_questions  # noqa: E402
from faster_whisper import WhisperModel  # noqa: E402
from num2words import num2words  # noqa: E402


def norm(t):
    t = t.lower().replace('’', "'").replace('&', ' and ')
    t = re.sub(r'\b(\d+)(st|nd|rd|th)\b', lambda m: num2words(int(m.group(1)), to='ordinal'), t)
    t = re.sub(r'\b(1[0-9]{3}|20[0-9]{2})\b', lambda m: num2words(int(m.group(1)), to='year'), t)
    t = re.sub(r'\d+', lambda m: num2words(int(m.group(0))), t)
    t = re.sub(r"[^a-z' ]+", ' ', t.replace('-', ' '))
    t = re.sub(r'\band\b', ' ', t)                  # "four hundred (and) thirty-five"
    t = re.sub(r'\b(\w)\s(?=\w\b)', r'\1', t)       # "u s" -> "us", "d c" -> "dc"
    return re.sub(r'\s+', ' ', t).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--voices', default=','.join(KOKORO_VOICES))
    ap.add_argument('--threshold', type=float, default=0.80)
    args = ap.parse_args()
    model = WhisperModel('base.en', device='cpu', compute_type='int8')
    items = clips(load_questions())
    fails, scores = [], []
    for vid in args.voices.split(','):
        todo = items + [('sample', SAMPLE.format(name=vid.capitalize()))]
        for name, text in todo:
            path = os.path.join(AUDIO, vid, f'{name}.mp3')
            if not os.path.exists(path):
                fails.append((vid, name, 0.0, text, '(missing file)'))
                continue
            segs, _ = model.transcribe(path, beam_size=1, language='en', vad_filter=False)
            heard = ' '.join(s.text.strip() for s in segs)
            score = difflib.SequenceMatcher(None, norm(text), norm(heard)).ratio()
            scores.append(score)
            if score < args.threshold:
                fails.append((vid, name, score, text, heard))
        print(f'{vid}: checked {len(todo)} clips', flush=True)
    avg = sum(scores) / max(1, len(scores))
    print(f'\nAverage match {avg:.3f} over {len(scores)} clips; {len(fails)} below {args.threshold}:')
    for vid, name, score, text, heard in fails:
        print(f'  {vid}/{name} ({score:.2f})\n     want: {text}\n     heard: {heard}')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
