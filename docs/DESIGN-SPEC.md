# Civics — Design Spec

Version 1.0 · September 2026 · Owner: Product & UX

## 1. Principles

1. **Studying in 5 seconds.** The first screen has one obvious primary action: *Start studying*. No onboarding, no sign‑up, no modal on first launch.
2. **Calm.** Quiet greys, one accent color (system blue), with color used only for meaning: green = knew it or passed, orange = still learning, red = failed.
3. **Native feel.** Large titles, grouped inset lists, frosted bars, spring‑like but short motion, 44 pt targets, and safe‑area aware.
4. **Honest content.** Official USCIS wording is always shown verbatim. Friendly explanations are visually separate ("Remember it"), and anything that changes over time is clearly labelled.

## 2. Information architecture & navigation

```
Tab bar (mobile, bottom) / Sidebar (≥ 900 px, left)
 ├─ Home ──────────── Continue studying → Study
 │                    Category card     → Study (deck = category)
 │                    Practice test     → Test
 │                    "Set up your state" nudge → Settings › My State
 ├─ Study   (flashcards, Leitner spaced repetition)
 ├─ Test    (start → question → … → results)
 ├─ Review  (search + filters; rows expand inline)
 └─ Settings
      ├─ My State & Officials
      ├─ Study options (65/20 mode, read aloud)
      ├─ Reset progress (confirm)
      └─ About  → About screen (back chevron returns to Settings)
```

* Hash routing: `#home`, `#study`, `#test`, `#review`, `#settings`, `#about`. The browser back button works, and the last screen is restored on reload.
* Only one screen is visible at a time. Switching screens moves focus to that screen's `<h1>` for screen‑reader users.

## 3. Screens

### 3.1 Home
* Frosted header with the app name (small, centered), which turns into a large title on scroll (iOS pattern). The large title is a greeting based on the time of day: "Good morning / afternoon / evening."
* Subtitle: "Let's get you ready for your citizenship interview."
* **Progress card**: a 120 px ring showing % mastered, with three stats beside it: *Mastered*, *Learning*, *New*. A mastered card is in Leitner box ≥ 3.
* **Primary button** (full width, 50 px, accent): "Start studying", or "Continue studying" once any card has been seen.
* **Secondary button**: "Take a practice test".
* **Categories**: one card for each of the three categories. Each shows its name, question count, % mastered, and a thin progress bar. Tapping a card studies that deck.
* **Nudge card** (only while no local officials are saved): "Add your state's officials. 4 questions depend on where you live." → Settings.
* **Reminder**: "Some answers change after elections. Check uscis.gov/citizenship/testupdates before your interview."
* When 65/20 mode is on, a pill appears under the title: "65/20 mode · 20 questions."

### 3.2 Study (flashcards)
* Header: the deck picker as a horizontally scrolling chip row (*All*, *Still learning*, *★ 65/20*, and the three categories), and a counter: "Card 7 · 34 of 128 mastered" with a 4 px progress bar.
* **Card**: ≥ 320 px tall, 24 px radius, elevated shadow, flips in 3D (rotateY, 450 ms, `cubic-bezier(.2,.8,.2,1)`).
  * Front: eyebrow (`Q12 · American Government`, plus `★ 65/20`, `Changes over time`, or `Depends on where you live` badges), the question (title2, 22 px/28, semibold), a speaker button (44 px circle, top right), and the hint "Tap to see the answer."
  * Back: "Answer" or "Name any 2" label, the official answers as a list (the first answer emphasized), and time‑sensitive blocks:
    * Official officials: "Current answer (USCIS, as of Sep 18, 2025)" with the name. If the user entered their own, "Your answer" is shown instead, with a link to *testupdates*.
    * Local: the user's saved value, or an inline "Add yours" button → Settings, plus a lookup link (senate.gov, house.gov, usa.gov).
    * "Remember it" callout (a tinted rounded box, with a lightbulb glyph) containing the explanation.
* **Answer buttons** under the card (always visible, so users can grade without flipping; reachable by keyboard and by swipe): "Still learning" (orange tint) and "I knew it" (green tint), each ≥ 52 px tall.
* **Gestures**: drag horizontally. The card follows the finger and rotates up to ±12°, and an orange or green stamp fades in. Releasing past 30% of the width commits the answer, and the card flies out (220 ms). Otherwise it springs back.
* **Keyboard**: Space or Enter flips, → means *I knew it*, ← means *Still learning*, and S speaks the question.
* **Empty deck state** (e.g. *Still learning* with nothing in it): a checkmark glyph, the message "Nothing to review here. Questions you mark 'Still learning' will show up here.", and a "Study all questions" button.

### 3.3 Practice Test
* **Start**: an illustration glyph and the rules: "The officer asks up to 20 questions. Answer 12 correctly to pass. The test ends as soon as you pass or can no longer pass." In 65/20 mode the rules are 10 questions from the starred 20, with 6 needed to pass. Buttons: *Start test*, plus a "Read questions aloud" toggle mirroring the setting.
* **Question**: "Question 3 of 20", a score line ("2 correct · 0 missed"), and a dot row (20 dots filling green or red). The question card shows the question and a speaker button, and is read aloud automatically when read‑aloud is on. The user answers out loud, then taps **Show answer**. The accepted answers are revealed, and the user grades themselves with **I got it wrong** / **I got it right**.
* **Stops early**: passing at 12 correct, or failing at 9 missed (the point where 12 is no longer reachable). For 65/20 it passes at 6 correct and fails at 5 missed.
* **Results**: a big status icon (green check seal for passed, orange for not yet) and a headline ("You passed!" / "Not quite yet"), the score "12 of 14 correct", and a list of every asked question with ✓/✗ that expands to show its answers. Buttons: *Study missed questions* (only if any were missed), *Take another test*, and *Done*. Missed questions move to Leitner box 1, and correct ones move up a box.

### 3.4 Review
* A sticky search field (iOS search style, with a clear button) that matches question text, answers, and question number.
* A segmented control: *All · Still learning · ★ 65/20*, and a category chip row.
* A list grouped by subcategory with inset grouped section headers. Each row shows the number, the question, and a status dot (green mastered, orange learning, grey new). Tapping a row expands its answers and the explanation inline (a disclosure with `aria-expanded`).
* A result count, announced politely, e.g. "14 questions".
* **Empty**: "No matching questions", with a *Clear filters* button.

### 3.5 Settings (iOS grouped inset lists)
* **My State & Officials**: State, U.S. Senator, second U.S. Senator (optional), U.S. Representative, Governor, and State capital. Each has a lookup link. A footnote explains the D.C. and territory rules from USCIS.
* **Current national officials** (optional overrides): President, Vice President, Speaker of the House, and Chief Justice. The placeholder shows the USCIS answer. Footnote: "Leave blank to use the USCIS answer as of Sep 18, 2025."
* **Study**: *65/20 mode* switch (with its footnote explaining eligibility), *Read questions aloud* switch, and *Speaking speed* (Slow / Normal).
* **Data**: *Reset progress*, which opens a confirm dialog with a destructive red button. Officials are kept unless the user also checks "Also clear my officials."
* **About Civics** row with a chevron.
* If storage is unavailable, a notice: "Your browser is blocking storage, so progress won't be saved after you close this page."

### 3.6 About
* The app icon (72 px), name, and version.
* Source: "Official USCIS 2025 Civics Test: 128 Questions and Answers (M‑1778, 09/25)." Content verified September 24, 2026, against the PDF and uscis.gov/citizenship/testupdates.
* Links: uscis.gov/citizenship and the test updates page.
* Privacy: "No accounts, ads, cookies, tracking, or analytics. Your progress stays on this device."
* The disclaimer in a highlighted card: **"Free study tool. Not affiliated with or endorsed by USCIS or the U.S. government."**

## 4. Components
| Component | Spec |
|---|---|
| Nav bar | 52 px plus the safe‑area top, `backdrop-filter: saturate(180%) blur(20px)`, bg `--bar`, hairline bottom border |
| Tab bar | 50 px plus the safe‑area bottom, 5 items (icon 24 px + 10 px label), selected = accent |
| Sidebar (≥ 900 px) | 240 px wide, same items as the tab bar, 44 px rows, selected row tinted |
| Card | `--card` bg, radius 20, shadow `--shadow-1`, padding 20 |
| Button: filled | accent bg, white text, radius 14, min height 50, weight 600 |
| Button: tinted | 12% accent bg, accent text |
| Chip | height 36 (target padded to 44), radius 999, 15 px text, selected = label‑color bg with inverted text |
| Segmented control | track `--fill`, selected thumb `--card` + shadow, 36 px |
| Switch | 51×31 iOS switch built on `<input type=checkbox role=switch>` |
| List row | min 44 px, 16 px inset, hairline separators inset 16 px |
| Progress ring | SVG, 10 px stroke, round caps, track `--fill` |
| Toast | bottom center above the tab bar, frosted, 2.4 s, `role=status` |
| Dialog | native `<dialog>`, radius 20, frosted backdrop |

## 5. Color tokens (WCAG AA verified for text use)
| Token | Light | Dark |
|---|---|---|
| `--bg` (grouped background) | `#F2F2F7` | `#000000` |
| `--card` | `#FFFFFF` | `#1C1C1E` |
| `--card-2` (elevated/inset) | `#F2F2F7` | `#2C2C2E` |
| `--label` | `#1D1D1F` | `#F5F5F7` |
| `--label-2` (secondary) | `#5E5E63` | `#AEAEB2` |
| `--label-3` (tertiary, non‑text) | `#8E8E93` | `#636366` |
| `--sep` | `rgba(60,60,67,.18)` | `rgba(84,84,88,.6)` |
| `--fill` | `rgba(120,120,128,.14)` | `rgba(120,120,128,.32)` |
| `--accent` | `#0058B0` | `#66B2FF` |
| `--green` | `#186B2B` | `#32D74B` |
| `--orange` | `#9C4700` | `#FF9F0A` |
| `--red` | `#C00013` | `#FF6961` (text on red: black) |
| `--bar` | `rgba(249,249,251,.78)` | `rgba(22,22,24,.72)` |

Measured contrast (QA pass 1 tightened these values): every text color is ≥ 4.6:1 against the card, the background, *and* its own 10–16% tint in both modes. Label‑2 on bg is 5.8:1 (light) and 9.5:1 (dark). White on accent is 6.9:1, and black on dark accent is 9:1.

## 6. Typography
Font stack: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif`. All sizes are in `rem` (1 rem = 16 px) so text follows browser zoom and the user's font size.

| Style | Size / line | Weight |
|---|---|---|
| Large title | 2.125rem / 1.2 | 700 |
| Title 2 (card question) | 1.375rem / 1.3 | 600 |
| Title 3 | 1.25rem / 1.3 | 600 |
| Headline | 1.0625rem / 1.35 | 600 |
| Body | 1.0625rem / 1.45 | 400 |
| Subhead | 0.9375rem / 1.4 | 400 |
| Footnote | 0.8125rem / 1.35 | 400 |
| Caption | 0.75rem / 1.3 | 500 |

## 7. Spacing, radius, elevation
* A 4 pt grid: 4, 8, 12, 16, 20, 24, 32, 44. Screen gutter 16 px (20 px ≥ 600 px). Content max‑width 720 px, centered.
* Radius: 12 (small), 14 (buttons), 20 (cards), 24 (flashcard).
* Shadows: `--shadow-1: 0 1px 2px rgba(0,0,0,.04), 0 4px 16px rgba(0,0,0,.06)`, and `--shadow-2` for the flashcard: `0 2px 6px rgba(0,0,0,.06), 0 16px 40px rgba(0,0,0,.10)`. In dark mode, shadows are replaced by a 1 px `--sep` border.

## 8. Motion
* Screen change: 250 ms fade + 8 px rise.
* Flip: 450 ms rotateY with `cubic-bezier(.2,.8,.2,1)`. Swipe fly‑out: 220 ms. Spring back: 300 ms.
* Buttons: scale .97 on press (100 ms).
* `prefers-reduced-motion: reduce`: no 3D flip (a cross‑fade instead), no fly‑out, and every transition ≤ 1 ms except opacity.

## 9. Accessibility
* Semantic landmarks: `header`, `nav` (tabs, with `aria-current="page"`), `main`, and `h1` per screen.
* The flashcard is a `button` with `aria-pressed` reflecting the flipped state. The answer side is in an `aria-live="polite"` region when revealed.
* Every icon‑only button has an `aria-label`. SVGs are `aria-hidden`.
* A focus ring of `0 0 0 3px` accent at 60% on `:focus-visible`, on every interactive element.
* A skip link, "Skip to content."
* Status changes (answer recorded, test result, search count) are announced through a visually hidden `role=status` region.
* Layout is tested at 320 px width and 200% zoom, with no horizontal scrolling.

## 10. Empty & edge states
| Where | State | Treatment |
|---|---|---|
| Study | Deck empty | Glyph + message + "Study all questions" |
| Review | No results | "No matching questions" + Clear filters |
| Card back (local Q) | No value saved | Inline "Add yours" tinted button |
| Settings | Storage blocked | Orange notice at the top |
| Speech | No speechSynthesis | Speaker buttons hidden; read‑aloud switch disabled with a footnote |
| Test | Finished | Results screen; the progress and answers are recorded |

## 11. App icon
* A 1024 master drawn in SVG: a rounded square (iOS squircle is applied by the OS, so the PNG is full‑bleed) with a vertical gradient `#1A5FD0 → #0B3A8C`. It shows a white flashcard, rotated −8°, with radius 10% and a soft shadow. On the card are a navy five‑point star and three short red "stripe" lines under it.
* The maskable variant keeps all artwork inside the central 80% safe zone.
* favicon.svg is the same artwork, simplified: a gradient square plus a white star.

## 12. Link preview (og-image, 1200×630)
* The background is the same blue gradient with a subtle large star watermark at the right.
* On the left: the icon (160 px), then "Civics" (96 px bold white), then "Study all 128 USCIS citizenship test questions." (40 px, 85% white), then a pill "Free · No sign-up · Works offline."
* Title tag: "Civics — U.S. Citizenship Test Flashcards (2025)". Description: "Free, private flashcards and practice tests for all 128 questions of the 2025 USCIS civics test. Works offline, no sign-up."

## 13. Color & motion update (v1.1)
Inspired by the soft-gradient, animated style of modern AI product sites (e.g. ElevenLabs). The base stays calm and Apple-like: color is added to headings, key actions, and progress, never to body text or answers.

| Element | Treatment |
|---|---|
| Home hero | New headline, "Pass your **citizenship test** with confidence.", with the phrase in animated gradient text. The words blur in one by one (80 ms stagger, 700 ms). Four pastel gradient orbs drift behind it (18–26 s loops), masked to fade on every edge. The greeting sits above it as a small line. |
| Gradient text | `--grad-text`: blue → violet → pink → orange → blue. It shimmers slowly (14 s loop) on screen titles, the hero phrase, and test results, and stays static on the progress %. It's used only at large sizes, where every stop is ≥ 3:1 (light orange darkened to `#C2410C`). |
| Light / dark stops | `#2563EB #7C3AED #DB2777 #C2410C` / `#60A5FA #A78BFA #F472B6 #FB923C` |
| Primary buttons, selected chips, selected sidebar tab | `--grad-btn`: `#2563EB → #7C3AED → #A21CAF` with white text (≥ 4.7:1), a soft violet glow, and a one-time light sweep (on load and on hover) |
| Tab bar (mobile) | The selected icon is stroked with the brand gradient |
| Progress | The ring and progress bars use the gradient |
| Category cards | Each has its own colored icon tile (blue/indigo, orange/rose, violet/pink). They lift on hover and fade up on scroll. |
| Flashcard & test card | A 1.5 px conic-gradient edge that spins once when the card flips |
| Passing a test | A confetti burst (110 pieces, about 3 s, removed afterwards) |
| Scroll reveals | Cards and notices below the fold fade up as they enter the view |

**Motion controls (WCAG 2.2.2 / 2.3.3):** a *Settings › Motion effects* switch (on by default) stops every decorative animation: orbs, shimmer, word reveal, sweep, card spin, and confetti. The same "calm" mode turns on automatically when the device has Reduce Motion enabled, and it updates live if that setting changes. Gradient text falls back to solid text where `background-clip: text` isn't supported and in Windows High Contrast (forced colors).

## 14. Logo & brand (v1.2)
The app now uses the **n400practice.com** logo (supplied by the owner; the source is kept in `tools/art/logo-source.png`). The display name is **n400practice.com**, and the installed app name is **N-400 Practice**.

| Where | Treatment |
|---|---|
| Home (phone and tablet) | A brand row above the greeting: the emblem (40 px) and the wordmark (19 px) on a white rounded tile. It links to About. |
| Sidebar (≥ 900 px) | The full logo on a **transparent** background at the top of the sidebar, using the same light/dark pair as About. It links to Home. The Home brand row is hidden at this width. |
| About | The full logo with its tagline, on a **transparent** background straight on the page; this is the page's `h1`, and the image alt text carries the name. It uses two files: `logo-clear.webp` (light) and `logo-clear-dark.webp` (dark mode, navy recolored to `#6F9BFF`, about 7.5:1 on black), chosen automatically with `<picture>`. |
| App icons | The emblem centered on white: 180 (apple-touch), 192, 512, a maskable 512 (with a 20% safe zone), and a 64 px favicon. |
| Link preview | White card with soft color orbs, the full logo on the left, "Pass your citizenship test" on the right, and the "Free · No sign-up · Works offline" pill. The template is `tools/art/og.html`. |

On the Home brand row and in app icons, the logo is navy and red on a **white tile**; About and the sidebar use the transparent versions. That keeps it readable in dark mode, and matches how app icons appear. The tiled assets are flattened onto white. The transparent About versions drop the faint edge haze from the source and paint the see-through Q/A letters white. Every logo file is generated by `tools/art/make_logo_assets.py`.

## 15. Voices (v1.3)
**Settings › Voice** is an iOS-style radio list: Heart, Bella, Michael, Fenrir (Kokoro open-source voices, Apache-2.0, recorded locally with no account), and Device voice. Each row shows a colored initial, the name, a short description, a check mark when selected, and a 40 px ▶ button that plays a sample. Choosing a voice plays its sample. Below the list there's *Download this voice for offline use* (with progress and "ready offline ✓"), shown only on the hosted HTTPS site.

* **Playback:** a recorded clip plays when one exists; otherwise the device voice reads the text (and Device voice never fetches clips). *Speaking speed › Slow* plays clips at 0.8× (pitch preserved).
* **iPhone/iPad:** audio may only start from a tap, so the first tap anywhere plays a silent clip to unlock the app's audio player; auto read-aloud works after that.
* **Offline:** clips are cached in a separate `n400-audio-*` cache that survives app updates.
* **Accuracy:** clip file names include a hash of their text. An answer edited without re-recording falls back to the device voice, so a recording can never read an old answer.
* **Privacy & cost:** no API key, no account, and no speech service at runtime; the audio is ordinary files on the same site, free to host.
