# How to update the app

*For the owner. No coding knowledge needed. Everything happens in your web browser on github.com.*

The whole app lives in one file, **`index.html`**. To change an answer you:
**1) edit the answer → 2) bump the version number → 3) save. Done.**

---

## Example: a new Speaker of the House

### Step 1: Edit the answer
1. Go to **https://github.com/ttungl/civics-app** and sign in.
2. Click **`index.html`**, then click the **pencil icon ✏️** (top right of the file, "Edit this file").
3. Press **Ctrl+F** (Windows) or **⌘+F** (Mac) and search for the old name, for example **`Mike Johnson`**.
   You'll find a line like this:
   ```
   "currentAnswers": ["Mike Johnson", "Johnson", "James Michael Johnson (birth name)"], "currentAsOf": "2025-09-18"
   ```
4. Replace the names with the new ones, copying **exactly** what USCIS lists at
   https://www.uscis.gov/citizenship/testupdates. Put the full name first:
   ```
   "currentAnswers": ["Jane Doe", "Doe"], "currentAsOf": "2027-01-05"
   ```
   * Keep the quotation marks `"` and the commas.
   * Change `currentAsOf` to the "Last Reviewed/Updated" date shown on the USCIS page (year-month-day).
5. Search for **`CONTENT_VERIFIED`** and change the date to today, e.g. `'January 5, 2027'`.
6. Scroll down and click **Commit changes…** → **Commit changes**.

| To change… | Search `index.html` for… |
|---|---|
| President (Q38) | `Donald J. Trump` |
| Vice President (Q39) | `JD Vance` |
| Speaker of the House (Q30) | `Mike Johnson` |
| Chief Justice (Q57) | `John Roberts` |

### Step 2: Bump the version number (so phones get the update)
1. Go back to the repository and click **`sw.js`** → **pencil icon ✏️**.
2. On line 4, change the number, for example:
   `const VERSION = '1.0.0';` → `const VERSION = '1.0.1';`
   (Any change works. Just make it bigger each time.)
3. Click **Commit changes…** → **Commit changes**.

> **Why?** Phones keep a saved copy of the app so it works offline. Changing this number tells every phone "there's a new version, download it."

### Step 3: Wait, then check
* GitHub publishes your change in about **1–2 minutes**. You can watch the progress under the **Actions** tab (a green ✓ means it's live).
* Open https://ttungl.github.io/civics-app/ and go to *Review*. Search for the question and confirm the new name.
* Users get the update the **next time they open the app** while online.

---

## Other common edits

**Fix wording in a "Remember it" tip:** search for a few words of the tip and edit the text inside the quotes after `"explanation":`.

**USCIS changes an official answer or question:** edit the text inside `"question":` or `"answers": [...]` so it matches the PDF **exactly**, including curly quotes and parentheses. Then bump `sw.js` (Step 2).

**Something broke?** Every change is saved in history. In the repository, click **`index.html`** → **History** to see older versions. Open the last good one, click **⋯ → View file**, copy its contents, and paste them back with the pencil editor. You can also ask a developer to "revert the last commit."

## Rules to remember
1. Official wording must match the USCIS PDF and test-updates page **exactly**.
2. **Always** bump the version in `sw.js` after any change.
3. Don't delete quotation marks `"`, commas `,`, or brackets `[ ]` in the question list.

*(Developers: after editing, you can run `python3 tools/verify_content.py` to confirm the official text still matches the PDF.)*
