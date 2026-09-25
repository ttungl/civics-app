#!/usr/bin/env python3
"""Check index.html's QUESTIONS against the official USCIS PDF text.
Run from anywhere:  python3 tools/verify_content.py   (exit code 0 = all good)"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
flat = re.sub(r'\s+', ' ', re.sub(r'\d+ of 19\s+uscis\.gov/citizenship', ' ',
       open(os.path.join(HERE, 'uscis-2025-source.txt'), encoding='utf-8').read()))
html = open(os.path.join(HERE, '..', 'index.html'), encoding='utf-8').read()
Q = json.loads(re.sub(r',\n\]$', '\n]', re.search(r'const QUESTIONS = (\[.*?\n\]);', html, re.S).group(1)))
errs = []
if len(Q) != 128: errs.append(f'expected 128 questions, found {len(Q)}')
for q in Q:
    head = f"{q['id']}. {q['question']}"
    pos = flat.find(head)
    if pos < 0: errs.append(f"Q{q['id']}: question text differs from PDF"); continue
    seg = flat[pos:flat.find('•', pos)]
    if ('*' in seg) != q['isSpecialConsideration']: errs.append(f"Q{q['id']}: 65/20 flag differs from PDF")
    for a in q['answers']:
        p = flat.find('• ' + a, pos)
        if p < 0: errs.append(f"Q{q['id']}: answer not in PDF: {a}")
        else: pos = p
n = sum(len(q['answers']) for q in Q)
print(f"{len(Q)} questions, {n} answers, {sum(q['isSpecialConsideration'] for q in Q)} marked 65/20")
print('\n'.join(errs) if errs else 'OK: every question and answer matches the USCIS PDF.')
sys.exit(1 if errs else 0)
