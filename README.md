# 🧠 Mohit's Knowledge Base

One place for everything you look up, study, and want to remember — so you
never have to recall it all from memory again.

## 📑 Jump to a section

| Section | What lives here | Full file |
|---|---|---|
| [🔎 Searches](#-searches) | Things you looked up / researched / useful links | [knowledge/searches.md](knowledge/searches.md) |
| [📚 Studies](#-studies) | Topics you're learning, courses, study notes | [knowledge/studies.md](knowledge/studies.md) |
| [💡 Notes](#-notes) | General knowledge, facts, ideas, references | [knowledge/notes.md](knowledge/notes.md) |

The full content of every section is shown right below, so this page alone gives
you everything. The links above jump you down the page; the "Full file" links
open each section on its own.

---

<!-- HOME:START -->
<!-- This block is generated from knowledge/*.md by ./build_home.sh — do not edit by hand. -->

## 🔎 Searches

_Nothing here yet._

## 📚 Studies

_Nothing here yet._

## 💡 Notes

### 2026-08-09 — Welcome

This is your knowledge base. Add anything worth remembering here — searches, study notes, or facts — and it all stays in one place. #getting-started
<!-- HOME:END -->

---

## ➕ How to add new content (this is the "automatic" part)

Two easy ways. Both always land in the **same place**, and both refresh this
homepage automatically.

**1. Just tell Claude Code** (recommended)

Open this repo with Claude Code and say things like:

- "Save this search: …"
- "Add to my studies: …"
- "Remember this: …"

Claude reads [CLAUDE.md](CLAUDE.md) and files it under the right section, dates
it, and rebuilds this homepage. You never have to decide where it goes.

**2. From the terminal**

```bash
./capture.sh searches "React hooks"  "useEffect runs after every render..."
./capture.sh studies  "Spanish"      "Learned past-tense conjugations"
./capture.sh notes    "Book idea"    "A short story about ..."
```

## 🗂 How it's organized

- Each entry is dated: `## YYYY-MM-DD — Title`, so you can see *when* you learned it.
- **Newest entries sit at the top** of each section.
- Add `#tags` inside entries, then use your editor's or GitHub's search to find
  anything in seconds.
- This homepage is rebuilt from the section files by `./build_home.sh`, so what
  you see here is always the exact current content.

That's the whole system. Simple on purpose.
