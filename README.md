# Civics: U.S. Citizenship Test Flashcards (2025)

A free, private web app for studying all **128 questions of the official USCIS 2025 Civics Test**. It has flashcards with spaced repetition, a practice test that works like the real interview, and a searchable review list, and it works offline.

**Live app:** https://n400practice.com/

> Free study tool. Not affiliated with or endorsed by USCIS or the U.S. government.

---

## Using the app

| Screen | What it does |
|---|---|
| **Home** | Your progress ring, *Continue studying*, and per-category progress. Tap a category to study just that one. |
| **Study** | Tap the card (or press **Space**) to flip it. Swipe right or press **→** for *I knew it*. Swipe left or press **←** for *Still learning*. The speaker button (or **S**) reads the card aloud. Cards you miss come back sooner (Leitner spaced repetition). |
| **Test** | Like the real interview: 20 random questions, 12 correct to pass, and it stops as soon as you pass or can no longer pass. Say each answer out loud, tap *Show answer*, and grade yourself honestly. |
| **Review** | Search all 128 questions and answers. Filter by *Still learning*, *★ 65/20*, or category. Tap a question to see its answers. |
| **Settings** | Enter your state's senators, representative, governor, and capital (they then appear on your cards). You can also override the national officials if they change, turn on 65/20 mode, turn on read-aloud, or reset your progress. |

**65/20 mode:** if you are 65 or older and have been a permanent resident for 20+ years, turn this on in Settings. You'll study only the 20 ★ questions, and the practice test becomes 10 questions with 6 needed to pass.

**Your privacy:** there are no accounts, ads, cookies, tracking, or analytics. Progress is saved only in your browser (localStorage) on your device. If your browser blocks storage (for example, some private windows), the app still works but won't remember your progress.

## Installing on your phone

* **iPhone / iPad (Safari):** open the link → tap **Share** → **Add to Home Screen** → **Add**.
* **Android (Chrome):** open the link → tap **⋮** → **Install app** (or **Add to Home screen**).
* **Mac / PC (Chrome or Edge):** click the install icon in the address bar.

After your first visit the app works **offline**, including in airplane mode.

## Keeping time-sensitive answers current

Some answers change after elections or appointments (the President, the Vice President, the Speaker of the House, and the Chief Justice). The app shows the names from **uscis.gov/citizenship/testupdates**, with the date they were checked.

* **Users** should always check https://www.uscis.gov/citizenship/testupdates before their interview. If a name has changed, they can type the new one in *Settings › Current national officials*.
* **The owner** can update the name for everyone. See [docs/HOW-TO-UPDATE.md](docs/HOW-TO-UPDATE.md). It's a 3-minute edit.

## Hosting it yourself

Everything is static. Upload the files anywhere that serves HTTPS:

* **GitHub Pages:** fork or push this repo → *Settings › Pages* → deploy from the `main` branch, `/ (root)` folder.
* **Netlify or Cloudflare Pages:** drag and drop this folder onto their dashboard.
* **No server:** `index.html` works on its own. Double-click it to open it from your computer (`file://`). Offline caching and "install" need HTTPS hosting, but everything else works.

If you host at a different address, update the `og:url`, `og:image`, `twitter:image`, and `canonical` URLs near the top of `index.html` so link previews point to your copy.

## Files

```
index.html             the whole app (HTML + CSS + JS + the 128-question dataset)
manifest.webmanifest   app name, colors, and icons for "install"
sw.js                  service worker (offline cache; bump VERSION to publish updates)
favicon.svg            browser tab icon
apple-touch-icon.png   iPhone home-screen icon (180×180)
icon-192.png, icon-512.png, icon-maskable-512.png   Android/desktop install icons
og-image.png           link preview image (1200×630)
404.html               "page not found" page
docs/                  design spec, dataset report, QA report, update guide
tools/                 source PDF text, parser, dataset builder, content verifier, icon artwork
```

## For developers

* There's no build step for the app itself: no frameworks and no external requests.
* The dataset in `index.html` is generated from the official PDF:
  `python3 tools/parse_pdf.py && python3 tools/build_data.py`
  (explanations live in `tools/explanations.json`, and flags and current officials live in `tools/build_data.py`).
* Check content against the PDF: `python3 tools/verify_content.py`

## Sources

* USCIS, *128 Civics Questions and Answers (2025 version)*, M-1778 (09/25): https://www.uscis.gov/sites/default/files/document/questions-and-answers/2025-Civics-Test-128-Questions-and-Answers.pdf
* USCIS civics test updates: https://www.uscis.gov/citizenship/testupdates
* The study tips were informed by this explainer video: https://www.youtube.com/watch?v=J28m1AFnIRQ (official wording always comes from the PDF).

Content last verified: **September 24, 2026**.
