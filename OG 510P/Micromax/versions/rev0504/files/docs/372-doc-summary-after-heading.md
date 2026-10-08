# Rev430: docs summaries prefer heading-first content

## What changed

- `_scan_docs()` now prefers the first meaningful non-heading line *after* the primary heading when extracting a docs summary.
- `doc_prompt_rows()` / `ed.doc-rows` / `ed.doc-section-rows` therefore surface the document's actual topic sentence more often.
- `helppick` and doc prompt preview/status now inherit the same cleaner summary automatically.

## Why this is worth doing

Micromax's docs archive now carries lots of small rev-note breadcrumbs at the top of many files. That is useful for continuity, but it made searchable docs discovery less pleasant: the summary extractor kept grabbing top-of-file archive bookkeeping instead of the document's real topic sentence.

That was a tiny problem, but it mattered right where humans and future LLMs browse the archive:

- `helppick` preview text often led with revision churn instead of the document's subject
- `ed.doc-rows` / `ed.doc-section-rows` gave scripts the same noisier summary signal
- repo guidance was doing the right archival thing while docs discovery quietly became less legible

Rev430 keeps the fix deliberately small. The docs files keep their rev-note history exactly as-is; only summary extraction gets a better default.

## New summary rule

When a docs file has a primary heading, Micromax now prefers:

1. the first meaningful non-heading line after that heading
2. otherwise, the old fallback of the first meaningful non-heading line anywhere in the file

That keeps heading-backed docs previews honest without breaking tiny note files that do not have a normal heading/body shape.

## Design intent

The goal is simple: searchable docs discovery should summarize the document, not the archive bookkeeping wrapped around it.
