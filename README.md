# 🧠 Mohit's Knowledge Base

One place for everything you look up, study, and want to remember — so you
never have to recall it all from memory again.

## 📑 Index

| Section | What lives here | Open |
|---|---|---|
| 🔎 Searches | Things you looked up / researched / useful links | [knowledge/searches.md](knowledge/searches.md) |
| 📚 Studies | Topics you're learning, courses, study notes | [knowledge/studies.md](knowledge/studies.md) |
| 💡 Notes | General knowledge, facts, ideas, references | [knowledge/notes.md](knowledge/notes.md) |

> The sections start empty and fill up as you add things. Everything you add
> lands here — never scattered anywhere else.

## ➕ How to add new content (this is the "automatic" part)

Two easy ways. Both always land in the **same place**.

**1. Just tell Claude Code** (recommended)

Open this repo with Claude Code and say things like:

- "Save this search: …"
- "Add to my studies: …"
- "Remember this: …"

Claude reads [CLAUDE.md](CLAUDE.md) and automatically files it under the right
section, dates it, and keeps this index tidy. You never have to decide where it
goes.

**2. From the terminal**

```bash
./capture.sh searches "React hooks"  "useEffect runs after every render..."
./capture.sh studies  "Spanish"      "Learned past-tense conjugations"
./capture.sh notes    "Book idea"    "A short story about ..."
```

## 🗂 How it's organized

- Each entry is dated: `## YYYY-MM-DD — Title`, so you can see *when* you learned it.
- **Newest entries sit at the top** of each file.
- Add `#tags` inside entries, then use your editor's or GitHub's search to find
  anything in seconds.

That's the whole system. Simple on purpose.
