# 🧴 Nat Habit Moisturisers Dashboard — deployment guide

This zip contains the complete, final dashboard:

- `index.html` — the entire app (styles, engine, charts, bundled 655-customer sample). Self-contained: no server, no libraries, no build step.

## ⚠️ Why you saw a 404 and how to fix it

GitHub Pages serves the file at the **root of the branch** it publishes from. A 404 means there was no `index.html` at that root. The common causes (and fixes):

1. **You uploaded a .zip or a folder to GitHub.** The web uploader does **not** unzip anything — you must upload the *extracted* `index.html` file itself.
2. **The file landed in a subfolder** (e.g. `dashboard/index.html`). It must sit at the repository root, next to `.git`, so the URL `https://<user>.github.io/<repo>/` finds it.
3. **The old index.html was deleted but the commit didn't finish**, or the new file has a different name (`index (1).html`). Exactly the name `index.html` is required.
4. **Pages source setting** — in *Settings → Pages*, Source must be *Deploy from a branch*, branch `main` (or `master`), folder `/ (root)`.

## ✅ Upload steps (GitHub web UI)

1. Unzip this archive on your computer.
2. Open your repository → make sure you are on the `main` branch.
3. If an old `index.html` exists, open it, click the trash icon, and commit the deletion. *(Skip if not present.)*
4. Click **Add file → Upload files**, drag the extracted `index.html` (the file, not the zip) into the box.
5. Click **Commit changes** to `main`.
6. *Settings → Pages*: Source = *Deploy from a branch*, Branch = `main`, Folder = `/ (root)` → Save.
7. Wait ~1–2 minutes (the first deploy after a fresh source can take a few more), then hard-refresh the site (Ctrl/Cmd + Shift + R).

## ▶️ Using the dashboard

- Opens instantly with a bundled sample (655 customers / 835 orders).
- Click **📂 Load your CSV** and pick your original order dump (100k+ rows fine). It auto-detects the format (order-level rows *or* journey-wide export), keeps only moisturiser SKUs (`FC-…`), rebuilds every journey, and reports the kept/skipped counts in the header chip.
- Everything is computed in your browser — nothing is uploaded anywhere.
- Charts are clickable filters; journey rows expand; table headers sort; ⚡ insights recompute per filter.

## 🛠️ If the loader ever rejects your file

It alerts with the header row it saw. Keep those headers and share them with your developer/AI assistant to pin the column mapping exactly.
