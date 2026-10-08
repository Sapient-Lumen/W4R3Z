# Archive refresh checklist — 2026-03-22

This note is an amnesia resistor for future humans and LLMs working on broad archive refreshes.
It is about how to update **this repository**, not about what any proposed crate should do.

## Before adding anything new

1. Read `README.md`, `INDEX.md`, and the latest entry in `entries/`.
2. Read the newest frontier-salience note.
3. Read `meta/epic-crate-rubric-2026-03-22.md`.
4. Search the proposal set for obvious overlaps before inventing a new lane.
5. Check whether the sharper move is **ranking**, **synthesis**, or **lane-boundary cleanup** instead of proposal count.

## During a broad scan

Keep at least one frontier from each of these families visible:

- support / stability / toolchain
- debugging / productivity / diagnosis
- interop / portability / conformance
- async / runtime / operations
- safety / assurance / verification
- API / release / maintenance / trust

That prevents the archive from drifting into one fashionable domain only.

## For every serious candidate, answer seven questions

1. What recurring pain does it solve?
2. What substrate already exists?
3. Why is the missing value a middle layer rather than new substrate?
4. What artifacts should the crate emit?
5. What should it provide other people?
6. What are the explicit non-goals?
7. What neighboring proposals must remain separate?

If those answers are weak, do not add a new lane yet.

## Repository update discipline

A high-quality pass should usually touch **all** of these, even briefly:

- one new entry in `entries/`
- `INDEX.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- at least one ranking or mapping note (`prioritization`, `territory-map`, `roadmap`, or frontier-salience)

That keeps the archive navigable instead of turning it into an append-only dump.

## Preferred outcomes of a broad refresh

### Best outcome
A ranked, cited rerank plus one sharpened existing proposal.

### Good outcome
A ranked rerank plus one new rubric / checklist / hygiene note that makes future passes better.

### Acceptable outcome
One genuinely new lane, but only if it exports explicit artifacts and does not duplicate an existing frontier.

## Failure modes to avoid

- adding multiple overlapping lanes in one pass
- treating all support problems as one giant “doctor” crate
- treating all safety/trust/assurance problems as one score or dashboard
- updating the proposal without updating the archive navigation docs
- forgetting to explain what the crate provides **other people**
- forgetting to record why this pass happened **now**

## When in doubt

Prefer **synthesis over proliferation**.
The archive is already large enough that curation quality matters at least as much as idea count.
