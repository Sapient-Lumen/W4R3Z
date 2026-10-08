# Archive session receipt discipline — 2026-03-24

This note exists to add one more **amnesia resistor** for future archive passes.

The archive now has enough moving pieces that a future assistant can easily:
- forget which revision it started from,
- silently change the practical queue,
- duplicate an already-covered seam under new wording,
- or rewrite old conclusions without saying what changed.

The fix is simple:

Every archive refresh should publish a small **session receipt** inside its new entry.

## Minimum session receipt fields

Each refresh entry should say:
1. **baseline revision** — which zip / repo snapshot it extended,
2. **main judgment** — what changed and what did not,
3. **frontier delta** — rerank, no rerank, or queue-only reinterpretation,
4. **files added** — new docs / schemas / scenarios,
5. **files updated** — repo bookkeeping touched,
6. **sources consulted** — exact URLs,
7. **watchlist** — unresolved seams worth reopening later,
8. **non-actions** — high-salience lanes intentionally not changed.

## Why this matters specifically for LLM work

LLM-driven archive maintenance is especially vulnerable to:
- paraphrase drift,
- duplicate idea creation,
- collapsing lane boundaries,
- and claiming freshness without naming a source route.

A session receipt keeps the pass narrow and inspectable.

## Required hygiene rules

### 1. Say what the baseline was

Never act as if the archive is being edited from memory.
Always name the prior revision or repo snapshot.

### 2. Say what did *not* change

The archive becomes noisy when every pass sounds like a rerank.
If salience did not change, say that plainly.

### 3. Name non-actions explicitly

Examples:
- “did not add a new frontier lane”
- “did not promote P-0538 in the practical queue”
- “did not treat docs.rs download archives as solved offline docs”

### 4. Keep source route truth visible

A refresh should record whether evidence came from:
- Rust blog / project-goals posts,
- Cargo docs,
- docs.rs reference pages,
- or registry/package surfaces.

### 5. Preserve review ceilings

A session receipt should name at least one thing the new pass still cannot honestly claim.

## Practical benefit

This discipline helps future passes:
- extend instead of restart,
- deepen instead of duplicate,
- and preserve the repo’s strongest asset: **tight explanations with visible basis and visible limits**.

## Connection to the top crates

This is not just repo process trivia.
It mirrors the same discipline the archive now asks from the leading crates:
- basis locks,
- trigger intake,
- recheck tickets,
- intake receipts,
- materialization plans,
- and visible ceilings.

The archive should model the behavior it wants the crates to have.
