# پردازش زبان‌های طبیعی — وب‌سایت درس

Static, bilingual (Persian-first + English) course-notes site for the NLP course at
Shahid Beheshti University, taught by Dr. Mehrnoush Shamsfard.

- **Live:** https://soheilnazari2001.github.io/nlp-sbu/
- **Repo:** https://github.com/soheilnazari2001/nlp-sbu

The site is plain HTML/CSS/JS with no build dependencies and no CDN. It is designed for
GitHub Pages and can be served from any static host.

## Contributing via pull requests

Pull requests are welcome. The notes live in `content/sessions/*.md`; the HTML pages
are generated, so edit the Markdown — never the generated HTML.

1. **Fork** the repo and create a branch (e.g. `improve-session-04`).
2. **Edit** the Markdown source in `content/sessions/`. Follow the existing style:
   - Front matter with `session`, `title_fa`, `title_en`, `summary_fa`, `lecturer`, `tags`.
   - Bilingual headings: `## ۱. فارسی | English`.
   - Callouts (`::: tip`, `::: warning`, `::: definition`, `::: example`, …), tables,
     and the `::: qa` self-check block.
   - Formulas in `math` code fences or inline `$...$` — supported syntax: `\frac{a}{b}`,
     `_{...}` / `^{...}`, `\mid`, `\prod`, `\sum`, `\hat{T}`, `\lambda`, `\text{...}`,
     `\dots`, `\times`, `\approx`, `\ge`, `\le`.
   - Content policy above: only what the session notes actually say — no invented
     syllabus, dates, or exam claims.
3. **Build and check** locally:
   ```bash
   python3 tools/build.py --check   # validate without writing
   python3 tools/build.py           # render pages + inject cards
   python3 -m http.server 8000      # preview at http://127.0.0.1:8000/
   ```
   Commit the regenerated `sessions/*.html` (and `index.html` / `notes.html` /
   `exercises.html` when the session count or cards changed) together with the
   Markdown change.
4. **Push** your branch and open a pull request against `main`. Describe what you
   changed and which part of the notes it improves.

## Content policy

- All substantive course content on the public pages is derived from the supplied
  session notes.
- The site does **not** publish an official syllabus, class schedule, deadlines,
  exam coverage, or project rules unless those are explicitly present in the notes.
- Where the notes do not specify something, the page says so instead of guessing.
- Session dates and slide numbers are omitted because the supplied notes do not include them.
- Official instructor announcements always take precedence over this site.

## Pages

| File | Purpose |
|---|---|
| `index.html` | Course home: published session topics, instructor, grading from the notes, references |
| `notes.html` | Searchable archive of published session notes |
| `exercises.html` | Suggested practice sets + the project facts stated in the notes |
| `sessions/session-01.html` … `session-06.html` | Generated session pages |

## Session notes pipeline

Source files live in `content/sessions/*.md`. Each file starts with front matter:

```yaml
---
session: 1
title_fa: بنیادها، کاربردها و چالش‌های زبان فارسی
title_en: Foundations, Applications & Persian Challenges
summary_fa: یک یا دو جمله خلاصه.
lecturer: دکتر مهرنوش شمس‌فرد
tags: [مبانی, کاربردها]
---
```

Supported Markdown: headings, paragraphs, bold/italic, links, inline code, fenced code,
lists, tables, blockquotes, and horizontal rules. Bilingual direction is resolved per
block (`dir="auto"` / `dir="rtl"`).

### Callouts

```markdown
::: definition عنوان اختیاری
متن تعریف.
:::
```

Types: `question`, `answer`, `tip`, `important`, `definition`, `example`, `warning`,
`note`, `persian` (alias `fa`).

### Self-check Q&A

```markdown
::: qa
Q | پرسش اول؟
A | پاسخ اول.
Q | پرسش دوم؟
A | پاسخ دوم.
:::
```

### Build

```bash
python3 tools/build.py          # render sessions, inject cards + session table
python3 tools/build.py --check  # validate without writing
```

The build also injects the published-session table into `index.html` and the note cards
into `notes.html`. Do not edit the generated blocks between the `START`/`END` markers by
hand.

## Logo

The header and footer use the Shahid Beheshti University seal to identify the institution.
Source file: [Sbu-logo.svg on Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Sbu-logo.svg).
The logo is used only for institutional identification; it is not part of the site's content license.

## Local preview

```bash
python3 -m http.server 8000
# open http://127.0.0.1:8000/
```

## Deploy to GitHub Pages

1. Push the repository to GitHub.
2. Open **Settings → Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Select branch `main` and folder `/ (root)`.
5. Save; the site appears at `https://<user>.github.io/<repo>/`.

`.nojekyll` is included so GitHub Pages serves the files without Jekyll processing.

## Structure

```text
index.html                 course home
notes.html                 notes archive
exercises.html             suggested practice + project facts
sessions/                  generated session pages
content/sessions/*.md      editable notes sources
assets/css/site.css        design system (blue/white, RTL, dark mode)
assets/js/site.js          theme, nav, search, TOC, progress
assets/fonts/              local Vazirmatn + JetBrains Mono (no CDN)
assets/img/favicon.svg     site icon
tools/build.py             Markdown → HTML builder
.nojekyll                  GitHub Pages marker
```
