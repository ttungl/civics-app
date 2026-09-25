import re, json
lines = open(__import__('os').path.join(__import__('os').path.dirname(__file__),'uscis-2025-source.txt'), encoding='utf-8').read().split('\n')
start = next(i for i,l in enumerate(lines) if 'AMERICAN GOVERNMENT' in l)
cat = sub = None
qs = []; cur = None; last = None  # last: 'q' or 'a'
catmap = {'AMERICAN GOVERNMENT':'American Government','AMERICAN HISTORY':'American History','SYMBOLS AND HOLIDAYS':'Symbols and Holidays'}
for raw in lines[start:]:
    s = raw.strip()
    if not s or re.search(r'\d+ of 19', s) or s == '*': continue
    if s in catmap: cat = catmap[s]; continue
    m = re.match(r'^[A-C]: (.+)$', s)
    if m: sub = m.group(1); continue
    m = re.match(r'^(\d{1,3})\. (.+)$', s)
    if m:
        cur = {'id':int(m.group(1)),'category':cat,'subcategory':sub,'question':m.group(2),'answers':[],'note':None}
        qs.append(cur); last='q'; continue
    if s.startswith('•'):
        cur['answers'].append(s[1:].strip()); last='a'; continue
    if s.startswith('For a complete list'):
        cur['note'] = s; continue
    # continuation
    if last=='q': cur['question'] += ' ' + s
    else: cur['answers'][-1] += ' ' + s
for q in qs:
    star = q['question'].rstrip().endswith('*')
    q['question'] = re.sub(r'\s*\*\s*$','',q['question']).strip()
    q['question'] = re.sub(r'\s+',' ',q['question'])
    q['answers'] = [re.sub(r'\s+',' ',a) for a in q['answers']]
    q['isSpecialConsideration'] = star
json.dump(qs, open(__import__('os').path.join(__import__('os').path.dirname(__file__),'parsed.json'),'w'), ensure_ascii=False, indent=1)
print(len(qs), [q['id'] for q in qs] == list(range(1,129)))
print('stars', [q['id'] for q in qs if q['isSpecialConsideration']], sum(q['isSpecialConsideration'] for q in qs))
from collections import Counter
print(Counter((q['category'],q['subcategory']) for q in qs))
print('answers total', sum(len(q['answers']) for q in qs))
for i in (23,29,62,97,113,115,117,120): print(i, qs[i-1]['question'], qs[i-1]['answers'][-1], qs[i-1]['note'])
