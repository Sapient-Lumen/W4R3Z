# Archive refresh loop — 2026-03-23

This note is for future maintainers and future LLM passes.
It exists to reduce amnesia, repetition, and vague churn.

## Main judgment

Every future refresh should explicitly choose one of three modes:

- **deepen** — sharpen existing high-salience lanes,
- **re-rank** — change frontier order or portfolio bands,
- **append** — add genuinely new proposal territory.

Do not silently mix all three.
If a pass does mix them, say which mode is primary.

## Mandatory refresh sequence

1. Read the latest `entries/` file.
2. Read the most recent frontier-salience note.
3. Read the latest repo-level operator/hygiene/memory notes.
4. Decide whether the pass is `deepen`, `re-rank`, or `append`.
5. Name the exact lanes being changed before writing new files.
6. Prefer updating the practical implementation queue before opening new sector territory.
7. After edits, update:
   - `README.md`
   - `INDEX.md`
   - `meta/prioritization.md`
   - `meta/roadmap.md`
   - `meta/research-ledger.md`
   - `meta/decision-log.md`
   - `meta/llm-hygiene.md`
   - `meta/archive-memory-anchor-2026-03-22.md`
8. Write one new entry summarizing the pass.

## Default anti-drift rules

### Keep “what changed” explicit
Every pass should list files added and files updated.

### Keep “what did not change” explicit
If the top frontier stayed intact, say so.
If only the practical build queue changed, say that instead of implying a full rerank.

### Prefer deeper product planning over more raw proposal sprawl
Unless a truly new seam appeared, refine artifact sets, boundaries, proving grounds, and adoption staircases for the top lanes.

### Prefer horizontal gaps over narrow novelty
Before adding a new sector proposal, ask whether the real missing layer is still one of:
- pathfinding,
- debuggability,
- docs/build parity,
- dependency transition,
- target/toolchain support,
- knowledge-pack handoff,
- compile iteration,
- or concurrency/runtime truth.

### Preserve refusal zones
If a product plan gains a new claim ceiling or manual-review zone, update hygiene and memory notes.

## Minimal pass template

Each new entry should answer:

1. Why this pass existed.
2. Whether it was deepen, re-rank, or append.
3. Main judgment.
4. Files added.
5. Files updated.
6. New portfolio stance.
7. Sources consulted.

## Source-grounding rule

Do not let the archive drift into uncited atmosphere.
For any repo-level rerank or product-plan shift tied to current Rust ecosystem reality, record the source URLs in the entry.

## LLM-specific guardrails

- Do not rephrase earlier work as new insight unless the artifact set, boundary model, or ranking actually changed.
- Do not create five new documents where one tighter document plus one entry would suffice.
- Do not silently resurrect rejected or deprioritized ideas.
- Do not treat a current official post as permanent truth without preserving dates.
- Do not flatten “local success”, “hosted success”, “imported evidence”, and “manual review” into one green status.

## Preferred growth pattern for the next few passes

1. deepen the practical implementation queue,
2. improve proving grounds / fixtures where justified,
3. only then reopen broad territory expansion.
