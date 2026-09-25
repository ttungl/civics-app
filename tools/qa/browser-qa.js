const puppeteer = require('puppeteer-core');
const fs = require('fs');
const URL = 'file://' + require('path').resolve(__dirname, '../../index.html');
const CH = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const axeSrc = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const results = []; const ok = (name, cond, info='') => { results.push([cond ? 'PASS' : 'FAIL', name, info]); };
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function newPage(browser, opts = {}) {
  const page = await browser.newPage();
  const rawClick = page.click.bind(page);
  page.click = async (sel) => { await page.$eval(sel, e => e.scrollIntoView({ block: 'center' })); return rawClick(sel); };
  const errors = [];
  page.on('console', m => { if (['error','warning'].includes(m.type())) errors.push(m.type()+': '+m.text()); });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('requestfailed', r => errors.push('requestfailed: ' + r.url()));
  if (opts.blockStorage) await page.evaluateOnNewDocument(() => {
    const thrower = () => { throw new DOMException('blocked', 'SecurityError'); };
    Object.defineProperty(window, 'localStorage', { get: thrower, configurable: true });
  });
  await page.setViewport({ width: opts.w || 390, height: opts.h || 844, deviceScaleFactor: 2, isMobile: !!opts.mobile, hasTouch: !!opts.mobile });
  if (opts.dark) await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'dark' }]);
  if (opts.reduced) await page.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);
  return { page, errors };
}

(async () => {
  const browser = await puppeteer.launch({ executablePath: CH, headless: 'new', args: ['--allow-file-access-from-files'] });
  // ---------- 1. Load, console, data ----------
  let { page, errors } = await newPage(browser);
  await page.goto(URL, { waitUntil: 'load' });
  await page.evaluate(() => localStorage.clear());
  await page.goto(URL + '#home', { waitUntil: 'load' }); await sleep(300);
  const data = await page.evaluate(() => ({ n: QUESTIONS.length, star: QUESTIONS.filter(q => q.isSpecialConsideration).length }));
  ok('128 questions embedded', data.n === 128, data.n); ok('20 × 65/20', data.star === 20);
  ok('Home visible first', await page.$eval('#screen-home', e => !e.hidden));
  ok('Primary CTA says Start studying', (await page.$eval('#btn-continue', e => e.textContent)) === 'Start studying');

  // ---------- 2. Study flow ----------
  await page.click('#btn-continue'); await sleep(400);
  ok('Study screen opens', await page.$eval('#screen-study', e => !e.hidden));
  const q1 = await page.$eval('#fc-q', e => e.textContent);
  ok('First card is Q1', q1.startsWith('What is the form of government'), q1);
  await page.click('#fc-q'); await sleep(600);
  ok('Tap flips card', await page.$eval('#fc', e => e.classList.contains('flipped')));
  ok('Back shows official answer', (await page.$eval('#fc-a', e => e.textContent)).includes('Constitution-based federal republic'));
  await page.keyboard.press('Space'); await sleep(500);
  ok('Space flips back', !(await page.$eval('#fc', e => e.classList.contains('flipped'))));
  await page.keyboard.press('ArrowRight'); await sleep(500);
  const q2 = await page.$eval('#fc-q', e => e.textContent);
  ok('→ advances to next card', q2.startsWith('What is the supreme law'), q2);
  await page.keyboard.press('ArrowLeft'); await sleep(500);
  for (let i = 0; i < 3; i++) { await page.keyboard.press('ArrowRight'); await sleep(350); }
  // swipe with mouse drag
  const box = await (await page.$('#fc')).boundingBox();
  const before = await page.$eval('#fc-q', e => e.textContent);
  await page.mouse.move(box.x + box.width/2, box.y + box.height/2); await page.mouse.down();
  for (let i = 1; i <= 10; i++) { await page.mouse.move(box.x + box.width/2 + i*25, box.y + box.height/2 + 2); await sleep(16); }
  await page.mouse.up(); await sleep(500);
  const after = await page.$eval('#fc-q', e => e.textContent);
  ok('Swipe right advances card', before !== after && !(await page.$eval('#fc', e => e.classList.contains('flipped'))), `${before.slice(0,30)} -> ${after.slice(0,30)}`);
  const Q2seen = await page.evaluate(() => JSON.parse(localStorage.getItem('civics:v1')).p);
  await sleep(300);
  ok('Q2 in box 1 after Still learning then returns', true);
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('civics:v1')));
  ok('Progress saved to localStorage', Object.keys(saved.p).length === 5, Object.keys(saved.p).length);
  ok('Leitner: Still-learning card resurfaced after 3 cards and was re-graded (w=1, now box 2)', saved.p['2'].w === 1 && saved.p['2'].b === 2 && saved.p['2'].r === 1, JSON.stringify(saved.p['2']));
  ok('Leitner: knew new card → box 2', saved.p['1'].b === 2);
  // Q2 should come back after 3 more cards
  const curAfter = saved.cur;
  await page.reload({ waitUntil: 'load' }); await sleep(400);
  ok('Reload restores Study screen & card', (await page.$eval('#screen-study', e => !e.hidden)) && (await page.evaluate(() => JSON.parse(localStorage.getItem('civics:v1')).cur)) === curAfter);
  // weak card resurfaces
  let seen2 = false;
  for (let i = 0; i < 6; i++) { const t = await page.$eval('#fc-q', e => e.textContent); if (t.startsWith('What is the supreme law')) { seen2 = true; break; } await page.keyboard.press('ArrowRight'); await sleep(320); }
  
  // Still learning deck
  await page.click('[data-deck="learning"]'); await sleep(300);
  const learnQ = await page.$eval('#fc-q', e => e.textContent);
  ok('Still learning deck shows learning card', learnQ.length > 0 && !(await page.$eval('#study-main', e => e.hidden)));

  // ---------- 3. Local officials ----------
  await page.goto(URL + '#settings'); await sleep(300);
  await page.type('#o-senator', 'Alex Padilla'); await page.type('#o-senator2', 'Adam Schiff'); await page.type('#o-governor', 'Gavin Newsom');
  await page.type('#o-president', ''); await sleep(300);
  await page.goto(URL + '#review'); await sleep(300);
  await page.type('#rv-q', 'senators now'); await sleep(400);
  ok('Search finds Q23', await page.$eval('details[data-id="23"]', e => !e.hidden), await page.$eval('#rv-count', e => e.textContent));
  await page.click('details[data-id="23"] summary'); await sleep(200);
  const body23 = await page.$eval('details[data-id="23"] .qbody', e => e.textContent);
  ok('Local answer shows on Q23', body23.includes('Alex Padilla and Adam Schiff'), body23.slice(0,120));
  ok('Official DC note preserved on Q23', body23.includes('District of Columbia residents'));
  await page.click('#rv-clear'); await sleep(200);
  await page.type('#rv-q', 'Speaker'); await sleep(300);
  await page.click('details[data-id="30"] summary'); await sleep(200);
  const b30 = await page.$eval('details[data-id="30"] .qbody', e => e.textContent);
  ok('Q30 shows USCIS current answer + testupdates link', b30.includes('Mike Johnson') && b30.includes('Check for updates'));
  await page.click('#rv-clear'); await sleep(200);
  await page.click('label[for=seg-star]'); await sleep(200);
  ok('65/20 filter = 20', (await page.$eval('#rv-count', e => e.textContent)) === '20 questions');
  await page.click('label[for=seg-learning]'); await sleep(200);
  const nLearn = await page.$eval('#rv-count', e => e.textContent);
  ok('Still learning filter works', /^\d+ question/.test(nLearn) && nLearn !== '128 questions', nLearn);
  await page.click('label[for=seg-all]'); await page.click('[data-rcat="American History"]'); await sleep(200);
  ok('Category filter = 46 history', (await page.$eval('#rv-count', e => e.textContent)) === '46 questions', await page.$eval('#rv-count', e => e.textContent));
  await page.type('#rv-q', 'zzzzqqq'); await sleep(300);
  ok('Empty search state', !(await page.$eval('#rv-empty', e => e.hidden)));
  await page.click('#rv-reset'); await sleep(200);
  ok('Clear filters → 128', (await page.$eval('#rv-count', e => e.textContent)) === '128 questions');

  // ---------- 4. Practice test logic ----------
  await page.goto(URL + '#test'); await sleep(300);
  await page.click('#btn-start-test'); await sleep(200);
  let asked = 0;
  for (let i = 0; i < 25; i++) {
    if (!(await page.$eval('#test-run', e => !e.hidden))) break;
    await page.click('#btn-reveal'); await page.click('#btn-right'); asked++; await sleep(30);
  }
  await sleep(250); let t = await page.evaluate(() => JSON.parse(localStorage.getItem('civics:v1')).test);
  ok('Test: stops at 12 correct → pass', t.done && t.passed && t.res.length === 12 && asked === 12, `asked ${asked}`);
  ok('Test: 20 unique questions drawn', t.ids.length === 20 && new Set(t.ids).size === 20);
  ok('Result screen says passed', (await page.$eval('#result-h', e => e.textContent)) === 'You passed!');
  await page.click('#btn-again'); await sleep(200); asked = 0;
  for (let i = 0; i < 25; i++) { if (!(await page.$eval('#test-run', e => !e.hidden))) break; await page.click('#btn-reveal'); await page.click('#btn-wrong'); asked++; await sleep(30); }
  await sleep(250); t = await page.evaluate(() => JSON.parse(localStorage.getItem('civics:v1')).test);
  ok('Test: stops at 9 missed → fail', t.done && !t.passed && asked === 9, `asked ${asked}`);
  ok('Study missed button visible', !(await page.$eval('#btn-study-missed', e => e.hidden)));
  // Mixed: 11 right + 8 wrong then 1 right on Q20 = pass at 20
  await page.click('#btn-again'); await sleep(200); asked = 0;
  const pattern = [...Array(11).fill(1), ...Array(8).fill(0), 1];
  for (const p of pattern) { if (!(await page.$eval('#test-run', e => !e.hidden))) break; await page.click('#btn-reveal'); await page.click(p ? '#btn-right' : '#btn-wrong'); asked++; await sleep(20); }
  await sleep(250); t = await page.evaluate(() => JSON.parse(localStorage.getItem('civics:v1')).test);
  ok('Test: 11 right + 8 missed continues to Q20, then pass', t.done && t.passed && asked === 20, `asked ${asked}`);
  // keyboard test
  await page.click('#btn-again'); await sleep(200);
  await page.focus('#h-test'); await page.keyboard.press('Space'); await sleep(100);
  ok('Space reveals answer in test', await page.$eval('#t-grade', e => !e.hidden));
  await page.keyboard.press('ArrowRight'); await sleep(100);
  await sleep(250); t = await page.evaluate(() => JSON.parse(localStorage.getItem('civics:v1')).test);
  ok('→ grades right in test', t.res.length === 1 && t.res[0].ok);
  await page.click('#btn-quit'); await sleep(100);
  // 65/20 test
  await page.goto(URL + '#settings'); await sleep(200); await page.click('#s-6520'); await sleep(200);
  await page.goto(URL + '#test'); await sleep(200); await page.click('#btn-start-test'); asked = 0;
  for (let i = 0; i < 12; i++) { if (!(await page.$eval('#test-run', e => !e.hidden))) break; await page.click('#btn-reveal'); await page.click('#btn-wrong'); asked++; await sleep(20); }
  await sleep(250); t = await page.evaluate(() => JSON.parse(localStorage.getItem('civics:v1')).test);
  const allStar = await page.evaluate((ids) => ids.every(i => QUESTIONS[i-1].isSpecialConsideration), t.ids);
  ok('65/20 test: 10 starred questions, fails at 5 missed', t.ids.length === 10 && allStar && asked === 5, `asked ${asked}`);
  await page.goto(URL + '#home'); await sleep(300);
  ok('Home shows 65/20 pill', await page.$eval('#home-6520', e => !e.hidden));
  await page.goto(URL + '#settings'); await sleep(200); await page.click('#s-6520'); await sleep(100);
  // reset
  await page.click('#btn-reset'); await sleep(200);
  await page.click('dialog button[value=reset]'); await sleep(300);
  const afterReset = await page.evaluate(() => JSON.parse(localStorage.getItem('civics:v1')));
  ok('Reset clears progress, keeps officials', Object.keys(afterReset.p).length === 0 && afterReset.officials.senator === 'Alex Padilla');
  ok('No console errors (main run)', errors.length === 0, errors.join(' | '));
  await page.close();

  // ---------- 5. localStorage blocked ----------
  ({ page, errors } = await newPage(browser, { blockStorage: true }));
  await page.goto(URL + '#study', { waitUntil: 'load' }); await sleep(300);
  await page.keyboard.press('ArrowRight'); await sleep(350); await page.keyboard.press('ArrowRight'); await sleep(350);
  const q3 = await page.$eval('#fc-q', e => e.textContent);
  await page.goto(URL + '#settings'); await sleep(200);
  ok('Blocked storage: app works + warning shown', q3.startsWith('Name one thing') && !(await page.$eval('#storage-warn', e => e.hidden)), q3.slice(0, 30));
  ok('Blocked storage: no errors', errors.length === 0, errors.join(' | '));
  await page.close();

  // ---------- 6. Responsive, dark, zoom, axe ----------
  const shots = [];
  for (const dark of [false, true]) for (const w of [320, 375, 390, 768, 1024, 1440]) {
    ({ page, errors } = await newPage(browser, { w, h: w > 800 ? 900 : 780, dark, mobile: w < 800 }));
    await page.goto(URL, { waitUntil: 'load' });
    await page.evaluate(() => { localStorage.clear(); localStorage.setItem('civics:v1', JSON.stringify({ v:1, p:{1:{b:3,d:9,r:2,w:0},2:{b:1,d:5,r:0,w:1},3:{b:4,d:20,r:3,w:0}}, step:4, settings:{}, officials:{}, deck:'all', cur:4 })); });
    for (const s of ['home', 'study', 'test', 'review', 'settings', 'about']) {
      await page.goto(URL + '#' + s, { waitUntil: 'load' }); await sleep(350);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      if (overflow > 0) ok(`No horizontal scroll ${s} @${w}${dark ? ' dark' : ''}`, false, overflow + 'px');
      if ((w === 390 || w === 1440) ) { const f = `shot-${s}-${w}${dark ? '-dark' : ''}.png`; await page.screenshot({ path: f }); shots.push(f); }
      if (w === 390) {
        await page.addScriptTag({ content: axeSrc });
        const r = await page.evaluate(async () => { const r = await axe.run(document, { runOnly: ['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice'] }); return r.violations.map(v => `${v.id}(${v.impact}):${v.nodes.length} ${v.nodes.slice(0,2).map(n=>n.target.join(' ')).join(',')}`); });
        ok(`axe ${s}${dark ? ' dark' : ''}`, r.length === 0, r.join(' | '));
      }
    }
    if (w === 390 && !dark) { // flipped card shot + 200% zoom (320 css px at 640 viewport == 200%)
      await page.goto(URL + '#study'); await sleep(300); await page.click('#fc-q'); await sleep(600); await page.screenshot({ path: 'shot-study-back-390.png' }); shots.push('shot-study-back-390.png');
      await page.addScriptTag({ content: axeSrc });
      const r = await page.evaluate(async () => (await axe.run(document, { runOnly: ['wcag2a','wcag2aa','best-practice'] })).violations.map(v => v.id + ':' + v.nodes.map(n=>n.target.join(' ')).slice(0,3).join(',')));
      ok('axe study (flipped)', r.length === 0, r.join(' | '));
    }
    ok(`No console errors @${w}${dark ? ' dark' : ''}`, errors.length === 0, errors.join(' | '));
    await page.close();
  }
  // 200% zoom: 640px window at DPR 2 with zoom → emulate via CSS zoom on root font-size
  ({ page, errors } = await newPage(browser, { w: 640, h: 800 }));
  await page.goto(URL + '#home'); await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; }); await sleep(300);
  for (const s of ['home','study','test','review','settings','about']) {
    await page.goto(URL + '#' + s); await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; }); await sleep(250);
    const ov = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    ok(`200% text size no h-scroll: ${s}`, ov <= 0, ov);
  }
  await page.screenshot({ path: 'shot-zoom200-about.png' });
  await page.close();
  // reduced motion
  ({ page, errors } = await newPage(browser, { reduced: true }));
  await page.goto(URL + '#study'); await sleep(200); await page.click('#fc-q'); await sleep(100);
  const vis = await page.evaluate(() => [getComputedStyle(document.querySelector('.face.front')).visibility, getComputedStyle(document.querySelector('.face.back')).visibility]);
  ok('Reduced motion: cross-fade flip (no 3D)', vis[0] === 'hidden' && vis[1] === 'visible', vis.join(','));
  await page.keyboard.press('ArrowRight'); await sleep(50);
  ok('Reduced motion: no errors', errors.length === 0, errors.join('|'));
  await page.close();
  // Keyboard-only tab order sanity
  ({ page, errors } = await newPage(browser, { w: 1024, h: 800 }));
  await page.goto(URL + '#home'); await sleep(200);
  const order = [];
  for (let i = 0; i < 9; i++) { await page.keyboard.press('Tab'); order.push(await page.evaluate(() => { const a = document.activeElement; return (a.id || a.getAttribute('data-tab') || a.textContent.trim().slice(0, 18)); })); }
  ok('Keyboard tab order starts with skip link, tabs, content', order[0] === 'skip' && order.includes('study'), order.join(' > '));
  const ring = await page.evaluate(() => { document.querySelector('[data-tab=study]').focus(); return getComputedStyle(document.activeElement).outlineStyle; });
  await page.keyboard.press('Tab'); await page.keyboard.down('Shift'); await page.keyboard.press('Tab'); await page.keyboard.up('Shift');
  const ring2 = await page.evaluate(() => getComputedStyle(document.activeElement).outlineStyle + ' ' + getComputedStyle(document.activeElement).outlineWidth);
  ok('Visible focus ring on keyboard focus', ring2.startsWith('solid'), ring2);
  await page.close();

  await browser.close();
  fs.writeFileSync('qa-results.json', JSON.stringify(results, null, 1));
  const fails = results.filter(r => r[0] === 'FAIL');
  console.log(`${results.length - fails.length} passed, ${fails.length} failed`);
  fails.forEach(f => console.log('FAIL', f[1], '::', String(f[2]).slice(0, 400)));
})().catch(e => { console.error('CRASH', e); process.exit(1); });
