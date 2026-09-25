# Dataset Verification Report

Source: **USCIS, *128 Civics Questions and Answers (2025 version)*, form M-1778 (09/25)**. The PDF was downloaded on September 24, 2026, from the official URL (PDF metadata: created Sep 26, 2025, modified Oct 14, 2025, 19 pages).  
Current officials come from **uscis.gov/citizenship/testupdates** (page last updated **09/18/2025**, checked September 24, 2026).

## Method

1. `pdftotext -layout` extracted the PDF text (saved as `tools/uscis-2025-source.txt`).
2. `tools/parse_pdf.py` parsed the numbered questions and bulleted answers straight from that text, so nothing was retyped by hand. Curly quotes, apostrophes, parentheses, and bracketed notes are kept exactly as printed.
3. `tools/build_data.py` added flags and explanations, and embedded `const QUESTIONS = [...]` in `index.html`.
4. **Independent check:** a separate script reloaded the array *from `index.html`* and, for each of the 128 questions, confirmed three things against the whitespace-normalized PDF text: that `N. question` appears; that every answer appears as a `• answer` bullet, in order; and that an asterisk follows the question only where `isSpecialConsideration` is true.

## Results

| Check | Result |
|---|---|
| Questions | **128** (IDs 1–128, contiguous) ✅ |
| Accepted answers | **410**, which equals the 410 `•` bullets in the PDF ✅ |
| Question/answer text mismatches | **0** ✅ |
| 65/20 (asterisk) questions | **20**, matching the PDF's “20 questions” ✅ |
| Schema fields present on every item | ✅ |
| Explanations | 128 (1–2 sentences each; max 135 characters) ✅ |

## Counts by category

| Category | Subcategory | Questions |
|---|---|---|
| American Government | Principles of American Government | 15 |
| American Government | System of Government | 47 |
| American Government | Rights and Responsibilities | 10 |
| American History | Colonial Period and Independence | 17 |
| American History | 1800s | 10 |
| American History | Recent American History and Other Important Historical Information | 19 |
| Symbols and Holidays | Symbols | 6 |
| Symbols and Holidays | Holidays | 4 |

Note: the PDF splits *Symbols and Holidays* into **A: Symbols** (Q119–124) and **B: Holidays** (Q125–128). Those official subsection names are used.

## 65/20 special consideration questions (20)

| # | Question |
|---|---|
| 2 | What is the supreme law of the land? |
| 7 | How many amendments does the U.S. Constitution have? |
| 12 | What is the economic system of the United States? |
| 20 | Name one power of the U.S. Congress. |
| 30 | What is the name of the Speaker of the House of Representatives now? |
| 36 | The President of the United States is elected for how many years? |
| 38 | What is the name of the President of the United States now? |
| 39 | What is the name of the Vice President of the United States now? |
| 44 | Who vetoes bills? |
| 52 | What is the highest court in the United States? |
| 61 | Who is the governor of your state now? |
| 66 | What do we show loyalty to when we say the Pledge of Allegiance? |
| 74 | Who lived in America before the Europeans arrived? |
| 78 | Who wrote the Declaration of Independence? |
| 86 | George Washington is famous for many things. Name one. |
| 94 | Abraham Lincoln is famous for many things. Name one. |
| 113 | Martin Luther King, Jr. is famous for many things. Name one. |
| 115 | What major event happened on September 11, 2001 in the United States? |
| 121 | Why does the flag have 13 stripes? |
| 126 | Name three national U.S. holidays. |

## Time-sensitive questions (answer changes with elections/appointments)

| # | Question | Current answer shown in app |
|---|---|---|
| 23 | Who is one of your state’s U.S. senators now? | User enters their own (Settings › My State & Officials) |
| 29 | Name your U.S. representative. | User enters their own (Settings › My State & Officials) |
| 30 | What is the name of the Speaker of the House of Representatives now? | Mike Johnson · Johnson · James Michael Johnson (birth name) (USCIS, 2025-09-18) |
| 38 | What is the name of the President of the United States now? | Donald J. Trump · Donald Trump · Trump (USCIS, 2025-09-18) |
| 39 | What is the name of the Vice President of the United States now? | JD Vance · Vance (USCIS, 2025-09-18) |
| 57 | Who is the Chief Justice of the United States now? | John Roberts · John G. Roberts, Jr. · Roberts (USCIS, 2025-09-18) |
| 61 | Who is the governor of your state now? | User enters their own (Settings › My State & Officials) |

## Location-dependent questions

| # | Question | Lookup |
|---|---|---|
| 23 | Who is one of your state’s U.S. senators now? | https://www.senate.gov/senators/senators-contact.htm |
| 29 | Name your U.S. representative. | https://www.house.gov/representatives/find-your-representative |
| 61 | Who is the governor of your state now? | https://www.usa.gov/states-and-territories |
| 62 | What is the capital of your state? | https://www.usa.gov/states-and-territories |

## Additional fields (beyond the required schema)

* `answersNeeded`: set when the question asks for several answers (Q10, 48, 67, 69 → 2; Q65, 126 → 3; Q81 → 5).
* `currentAnswers` / `currentAsOf`: the names listed on the USCIS test-updates page for Q30, 38, 39, 57.
* `lookup`, `localKey`: the official lookup site, and which saved local answer to show.
* `note`: the PDF's note under Q117 (“For a complete list of tribes, please visit bia.gov.”).

## Discrepancies noted

* The USCIS test-updates **web page** shows an asterisk on Q23 (“Who is one of your state’s U.S. Senators now?\*”), but the **PDF does not**, and the PDF says exactly 20 questions are marked. Following the rule that the PDF is authoritative, Q23 is **not** flagged 65/20. It stays flagged as time-sensitive and location-dependent, so it can't be missed.
* The reference video's answers are shortened paraphrases (e.g. “Russia” for Q108, “Answers depends on where you live”). They were used **only** for the “Remember it” tips and never for official answer text. Where the video names officials (Donald Trump, JD Vance, Mike Johnson, John Roberts), those names match the USCIS updates page.
