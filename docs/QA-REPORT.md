# QA & Post-Launch Sign-off

**Live URL:** https://n400practice.com/  ·  **Release:** 1.0.4  ·  **Date:** September 24, 2026  
*(Originally launched at ttungl.github.io/civics-app/, which now redirects to the custom domain.)*
**Verdict:** ✅ **Ship.** There are 0 open critical or major issues. The items in §6 are manual device checks that automation can't do, and they're listed so the owner can tick them off.

---

## 1. Content QA (vs. the USCIS PDF)
| Check | Result |
|---|---|
| Exactly 128 questions, numbered 1–128 | ✅ |
| Every question's text matches the PDF verbatim | ✅ 0 mismatches |
| Every accepted answer present, in PDF order (410 of 410 bullets) | ✅ 0 mismatches |
| 65/20 asterisk flags (20) | ✅ exact match |
| Time-sensitive (7) and location-dependent (4) flags present | ✅ |
| Current officials match uscis.gov/citizenship/testupdates (09/18/2025) | ✅ Trump · Vance · Johnson · Roberts |
| Reminder to check testupdates is shown on Home, on every time-sensitive card, and in Settings | ✅ |

Re-run any time with `python3 tools/verify_content.py`. Details are in [DATASET-REPORT.md](DATASET-REPORT.md).

## 2. Functional QA (automated, headless Chrome, `tools/qa/browser-qa.js`): 75 of 75 pass
* **Study:** tap and Space flip; → / ← grade; mouse-drag swipe commits the grade; cards follow the Leitner boxes (a missed card comes back after 3 others); decks for Still learning, 65/20, and each category; empty-deck state.
* **Persistence:** progress, the current card, the current screen, settings, and officials all restore after reload.
* **Practice test:** 20 unique random questions. It **stops at 12 correct (pass)** and **stops at 9 missed (fail)**. A score of 11 right plus 8 missed continues to Q20 and then passes. Keyboard (Space, →) works. In **65/20 mode** it draws 10 starred questions and fails at 5 missed.
* **Review:** text search across questions and answers, the All / Still learning / 65/20 segments, category chips, the empty state, and *Clear filters*.
* **Settings:** local officials appear on Q23, Q61, and others. National overrides work. Reset keeps officials unless the user asks to clear them.
* **localStorage blocked** (the getter throws): the app works fully, shows the "can't be saved" notice, and logs **no errors**.
* **file://:** loads and runs with **zero console errors** (the manifest and service worker are only attached over HTTPS).

## 3. Accessibility & responsive QA
* **axe-core 4 (WCAG 2.0/2.1 A + AA, plus best practices):** 0 violations on all six screens, in light and dark mode, and on the flipped card.
* **Widths 320, 375, 390, 768, 1024, and 1440 px, light and dark:** no horizontal scroll on any screen. The layout moves to a sidebar at ≥ 900 px.
* **200% text size:** no horizontal scroll on any screen, because all type is in `rem`.
* **Keyboard only:** the skip link comes first, then the tab bar, then content. There's a visible focus ring. Focus moves to the screen title on navigation. `scroll-padding` keeps focused controls from hiding under the fixed bars.
* **prefers-reduced-motion:** the 3D flip becomes a cross-fade, and the fly-out animations are removed.
* **Contrast:** every text token is ≥ 4.6:1 against the card, the background, and its own tint, in both modes (these were fixed during QA; see §5).

## 4. Post-launch verification (live URL, `tools/qa/live-check.js`): 11 of 11 pass
| Check | Result |
|---|---|
| HTTPS, 200; http:// → 301 → https | ✅ |
| All assets served with correct MIME types; unknown paths → 404 page | ✅ |
| Service worker active, scoped to the site root, 8 files precached | ✅ |
| Manifest parsed without errors; **Chrome installability errors: none** | ✅ |
| **Airplane mode:** reload works, a cold open in a new tab works, icons come from the cache, progress is kept | ✅ |
| OG and Twitter tags: title, description, absolute 1200×630 `og:image` (reachable, image/png) | ✅ |
| No console errors on the live site | ✅ |
| **Update rollout:** a returning visitor with v1.0.2 cached saw **v1.0.3 on their first visit** after the deploy. The old cache was deleted, the new version works offline, and progress was kept | ✅ |

### Lighthouse 12.8.2 (live URL, https://n400practice.com)
| | Performance | Accessibility | Best Practices | SEO | FCP | LCP | CLS | TBT |
|---|---|---|---|---|---|---|---|---|
| Mobile | **100** | **100** | **100** | **100** | 1.0 s | 1.1 s | 0 | 10 ms |
| Desktop | **100** | **100** | **100** | **100** | 0.3 s | 0.3 s | 0 | 0 ms |

Full reports: [lighthouse/mobile.html](lighthouse/mobile.html) and [lighthouse/desktop.html](lighthouse/desktop.html). Lighthouse 12 no longer has a "PWA" category, so installability was verified directly through Chrome's installability check (§4). The remaining advisory items are GitHub Pages' fixed 10-minute cache headers (the host controls these) and optional image-format hints.

## 5. Issues found and fixed during QA
| # | Severity | Owner | Issue | Fix | Re-verified |
|---|---|---|---|---|---|
| 1 | **Critical** | Engineer | On long answers the flipped card overflowed and covered the grade buttons (the grid row didn't size to the back face) | The card now measures both faces and sizes to the taller; this re-runs on resize and zoom | ✅ screenshot + measurement |
| 2 | Major | Designer | Tinted buttons and badges were at 3.9–4.4:1 contrast in light mode (AA fail); dark-mode red button text was 2.6:1 | New tokens (accent `#0058B0`, green `#186B2B`, orange `#9C4700`, red `#C00013`, dark accent `#66B2FF`; black text on dark red) | ✅ axe 0 violations |
| 3 | Major | Engineer | Keyboard focus could scroll controls underneath the fixed tab bar (WCAG 2.4.11) | `scroll-padding-top/bottom` on the page | ✅ |
| 4 | Minor | Engineer | Category cards' `aria-label` didn't include their visible text (voice control) | Removed the override; the visible text is the name | ✅ Lighthouse |
| 5 | Minor | Engineer | After a deploy, the first visit could still show the previous page (browser HTTP cache) | Service worker revalidates pages with `cache: 'no-cache'` | ✅ v1.0.2 → 1.0.3 test |
| 6 | Minor | Designer | Focus ring drawn around the large title after navigation; back-face header row not full width; grade button labels wrapping at 375 px | CSS polish | ✅ screenshots |

## 6. Manual device checklist (needs real hardware; not possible to automate here)
These use the same web standards that passed above, but they should be confirmed by hand once:
- [ ] **iPhone Safari:** open the link, then Share → *Add to Home Screen*. It should open full-screen with the Civics icon, and the speaker button should talk.
- [ ] **iPhone:** turn on airplane mode and open the home-screen app. It should still work.
- [ ] **VoiceOver (iPhone or Mac):** swipe through Home and Study; flip a card and hear the answer announced.
- [ ] **Android Chrome:** use ⋮ → *Install app*. It opens standalone with the maskable icon.
- [ ] **Desktop Safari and Firefox:** load the page, flip, swipe with the trackpad, and take a test.
- [ ] **Link previews:** paste the URL into iMessage, WhatsApp, and a social post. You should see the blue "Civics" card, the title, and the description. (The tags and image are verified; the apps cache previews, so the first share may take a moment.)

## 7. Known limitations
* Read-aloud voices come from the device. Very old Android browsers without `speechSynthesis` hide the speaker buttons.
* Progress lives in one browser on one device, by design (no accounts). Clearing site data resets it.
* GitHub Pages sets a 10-minute cache on files. The service worker bypasses this for pages, but a brand-new visitor may see an update up to 10 minutes late.

## How to re-run QA
```
cd tools/qa && npm install
node browser-qa.js          # 75 functional, accessibility and responsive checks against index.html
node live-check.js          # 11 checks against the live URL
python3 ../verify_content.py
```

## Custom domain: n400practice.com ✅
The site is hosted on GitHub Pages, with DNS at Cloudflare (the domain is registered there too).

| Cloudflare DNS record | Value | Proxy |
|---|---|---|
| A `@` ×4 | `185.199.108.153`, `.109.153`, `.110.153`, `.111.153` | DNS only |
| AAAA `@` ×4 | `2606:50c0:8000::153` … `8003::153` | DNS only |
| CNAME `www` | `ttungl.github.io` | DNS only |

Keep these records **DNS only (grey cloud)**. When proxied, GitHub can't renew its HTTPS certificate, and Cloudflare's cache can delay app updates.

| Post-switch check | Result |
|---|---|
| GitHub Pages custom domain `n400practice.com`, certificate **approved** (covers the root and www) | ✅ |
| Enforce HTTPS on; `http://n400practice.com` → 301 → `https://n400practice.com/` | ✅ |
| `https://www.n400practice.com` → 301 → `https://n400practice.com/` | ✅ |
| Old `https://ttungl.github.io/civics-app/` → 301 → `https://n400practice.com/` | ✅ |
| Live checks (11/11) and Lighthouse 100 ×4 on the new domain | ✅ |

Note: progress is stored per web address, so anyone who studied on the github.io address before the switch starts fresh on n400practice.com.
