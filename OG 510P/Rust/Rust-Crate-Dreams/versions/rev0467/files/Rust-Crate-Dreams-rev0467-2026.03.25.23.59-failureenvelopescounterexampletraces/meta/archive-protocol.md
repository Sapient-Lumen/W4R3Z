# Archive protocol

## What goes where

- `entries/YYYY-MM-DD.md` — weekly/monthly snapshots of ecosystem signals & new ideas.
- `proposals/*.md` — “epic crate” proposals with real planning.
- `meta/*` — policies, templates, decision logs, rubrics.

## Evidence and citations

Every proposal must list:
- **at least 3 external sources** (links in `evidence:`) supporting the pain point.
- a **"Related work"** section naming existing crates/projects and why they are insufficient.

Avoid uncited claims about the ecosystem.

## Review cadence

- New proposals: `status: idea`
- After one concrete prototype spike is completed: `status: incubating`
- After public repo exists and early adopters confirmed: `status: building`
- After 1 stable release and documentation: `status: shipped`

## LLM interaction hygiene

- Never overwrite older entries; append new dated entries.
- Separate **facts** (with sources) from **hypotheses** (clearly marked).
- If unsure, add a TODO and a search query suggestion instead of guessing.

Last updated: 2026-03-01


## Proposal minimum bar (enforced)
- Include a **What it provides** section with concrete deliverables.
- Include an **adoption path**: MVP → v1 → stabilization, plus migration story.
- Include at least 2 sources for the problem statement when non-obvious.
