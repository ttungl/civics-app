#!/usr/bin/env python3
"""Build the QUESTIONS array and embed it in index.html.

Inputs (all in this folder):
  uscis-2025-source.txt  pdftotext -layout output of the official USCIS PDF
  parsed.json            produced by parse_pdf.py (verbatim questions/answers)
  explanations.json      plain-language "Remember it" notes, keyed by id

Run:  python3 parse_pdf.py && python3 build_data.py
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, '..', 'index.html')

qs = json.load(open(os.path.join(HERE, 'parsed.json'), encoding='utf-8'))
expl = json.load(open(os.path.join(HERE, 'explanations.json'), encoding='utf-8'))

# Answers change after elections/appointments (USCIS: "now" questions).
TIME_SENSITIVE = {23, 29, 30, 38, 39, 57, 61}
# Answers depend on where the applicant lives.
LOCATION = {23, 29, 61, 62}
# Current accepted answers from uscis.gov/citizenship/testupdates.
CURRENT_AS_OF = '2025-09-18'
CURRENT = {
    30: ['Mike Johnson', 'Johnson', 'James Michael Johnson (birth name)'],
    38: ['Donald J. Trump', 'Donald Trump', 'Trump'],
    39: ['JD Vance', 'Vance'],
    57: ['John Roberts', 'John G. Roberts, Jr.', 'Roberts'],
}
LOOKUP = {
    23: ['senate.gov', 'https://www.senate.gov/senators/senators-contact.htm'],
    29: ['house.gov', 'https://www.house.gov/representatives/find-your-representative'],
    61: ['usa.gov', 'https://www.usa.gov/states-and-territories'],
    62: ['usa.gov', 'https://www.usa.gov/states-and-territories'],
}
# Key in "My State & Officials" that answers each local question.
LOCAL_KEY = {23: 'senator', 29: 'representative', 61: 'governor', 62: 'capital'}
# Questions that ask for more than one answer.
NEED = {10: 2, 48: 2, 65: 3, 67: 2, 69: 2, 81: 5, 126: 3}

out = []
for q in qs:
    i = q['id']
    item = {
        'id': i,
        'category': q['category'],
        'subcategory': q['subcategory'],
        'question': q['question'],
        'answers': q['answers'],
        'isSpecialConsideration': q['isSpecialConsideration'],
        'isTimeSensitive': i in TIME_SENSITIVE,
        'isLocationDependent': i in LOCATION,
        'explanation': expl[str(i)],
    }
    if i in NEED: item['answersNeeded'] = NEED[i]
    if q.get('note'): item['note'] = q['note']
    if i in CURRENT:
        item['currentAnswers'] = CURRENT[i]
        item['currentAsOf'] = CURRENT_AS_OF
    if i in LOOKUP: item['lookup'] = {'label': LOOKUP[i][0], 'url': LOOKUP[i][1]}
    if i in LOCAL_KEY: item['localKey'] = LOCAL_KEY[i]
    out.append(item)

assert len(out) == 128 and [q['id'] for q in out] == list(range(1, 129))
assert sum(q['isSpecialConsideration'] for q in out) == 20

lines = ['const QUESTIONS = [']
for q in out:
    lines.append('  ' + json.dumps(q, ensure_ascii=False) + ',')
lines.append('];')
block = '\n'.join(lines)

html = open(INDEX, encoding='utf-8').read()
new = re.sub(r'(// BEGIN QUESTIONS\n).*?(\n\s*// END QUESTIONS)',
             lambda m: m.group(1) + block + m.group(2), html, flags=re.S)
assert new != html or block in html, 'markers not found'
open(INDEX, 'w', encoding='utf-8').write(new)
json.dump(out, open(os.path.join(HERE, 'questions.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('Embedded', len(out), 'questions into index.html')
