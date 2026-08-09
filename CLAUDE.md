# Knowledge Base — Auto-Filing Rules

This repository is **Mohit's personal knowledge base**. Its only job is to be
the single, organized home for everything Mohit searches, studies, and wants to
remember.

## Your job in this repo

Whenever Mohit shares a search result, study material, fact, idea, link, or
anything worth remembering, **file it automatically** — do not ask where it
should go. Put it in the right file, stamp it with today's date, and keep the
index current.

## Where things go

| If it's… | Put it in |
|---|---|
| Something looked up / researched / a search result / a useful link | `knowledge/searches.md` |
| Something being learned / a course / study notes / practice | `knowledge/studies.md` |
| A general fact, idea, reference, or miscellaneous note | `knowledge/notes.md` |

If it's ambiguous, pick the closest match. Do **not** create new top-level files
unless Mohit explicitly asks.

## Entry format

Add each new entry **at the top** of the section's file, right under the
`<!-- ENTRIES -->` marker:

```
## YYYY-MM-DD — Short title

Body / notes in clear, simple language.

- Source: <link if any>
- Tags: #topic #topic2
```

Use today's real date. Rewrite dense material into short, skimmable notes —
simplifying is part of the job.

## After adding

- Confirm the entry is under the correct file and directly below the
  `<!-- ENTRIES -->` marker (newest first).
- Remove the "_Nothing here yet…_" placeholder line the first time a file gets a
  real entry.
- Run `./build_home.sh` so the homepage (`README.md`) shows the exact new
  content. Never hand-edit the block between `<!-- HOME:START -->` and
  `<!-- HOME:END -->` — it is generated.
- If Mohit asked for a brand-new section, add a row to the table in `README.md`.
- Commit with a short message like `kb: add <title>`.

## Principles

- **One place, always.** Never scatter notes into other files.
- **Simplify.** Turn long/complex material into clear, short notes.
- **Never delete** existing entries unless Mohit explicitly asks.
