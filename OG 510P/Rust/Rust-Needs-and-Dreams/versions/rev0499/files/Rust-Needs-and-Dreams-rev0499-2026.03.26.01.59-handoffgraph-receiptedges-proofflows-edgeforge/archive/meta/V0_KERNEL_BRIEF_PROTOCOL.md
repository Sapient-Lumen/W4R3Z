# V0 kernel-brief protocol (rev0483)

Use this protocol when the archive needs a **first honest repo shape** for a worthy candidate.
Read it with:
- `design/epic-contribution-v0-kernel-briefs-2026Q1.md`
- `design/epic-contribution-live-decision-packets-2026Q1.md`
- `design/epic-contribution-candidate-dossiers-2026Q1.md`
- `design/epic-contribution-reference-architectures-2026Q1.md`
- `design/epic-contribution-stage-gates-and-proof-budgets-2026Q1.md`
- `meta/LIVE_DECISION_PACKET_PROTOCOL.md`
- `meta/CANDIDATE_DOSSIER_PROTOCOL.md`
- `meta/PROGRAM_STAGE_GATE_PROTOCOL.md`

## Default rule
A v0 kernel brief is the archive's **first-build artifact**.
It should only be written when the repo can honestly answer:
- what gets built first,
- what repo shape it wants,
- what public seams it imports,
- and what bigger launch form is still refused.

If a revision says a top candidate is ready for a bounded next move but leaves no kernel brief, treat the revision as build-shape-lossy.

## Required fields
Every v0 kernel brief should say:
1. **identity** — candidate, macro-program, verdict context;
2. **kernel choice** — why this bounded first build is the honest next step;
3. **repo shape** — packages, corpora, schemas, fixtures, docs, or validators;
4. **user surfaces** — commands, cards, packs, or generated artifacts;
5. **import seams** — exact upstream/public interfaces or document families relied on;
6. **proof assets** — what evidence this kernel emits;
7. **proving grounds** — the first real environments where it should be tried;
8. **owner shape / upkeep** — who carries drift and renewal;
9. **refused expansions** — what bigger or more magical build is still not allowed;
10. **exit criteria** — what would justify graduating to a wider stage.

## When to write a v0 kernel brief
Prefer a kernel brief when:
- the candidate already has a live packet or dossier;
- the verdict is `advance` or `deepen` and a bounded shipset is visible;
- the archive wants to stop re-inventing repo trees or command surfaces from scratch;
- or a future contributor could plausibly use the brief as a starting implementation guide.

## When not to write a v0 kernel brief
Do not write one when:
- the candidate is still a `hold` because renewal burden, not build imagination, is the blocker;
- the right shape is still too speculative to bound honestly;
- or the repo would only be producing platform theater.

## Kernel discipline
A kernel brief must say why its first build is smaller than the program's eventual shape.
Examples:
- if it is a companion Cargo tool, say why it is not an upstream request yet;
- if it is a commons, say why it is not a portal or certification layer;
- if it is a document corpus, say what validation and proof assets keep it from becoming freeform prose.

## Scope discipline
The first corpus should stay small.
Default scope is the current top band, minus candidates that are still rightly on hold.
Do not create kernel briefs for every attractive seam in one pass.

## Same-revision updates
A kernel-brief revision should usually also refresh:
- `kernels/README.md`
- `kernels/top-band-v0/README.md`
- `AGENTS.md`
- `INDEX.md`
- `PRIORITIES.md`
- `STRATEGIC_FRONTIER.md`
- `meta/ACTIVE_FRONTIER.md`
- `meta/CANONICAL_WORKING_SET.md`
- `meta/LATEST_REVISION_FILESET.md`
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
- `meta/REVISION_OPERATING_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`
- `RESEARCH_LOG.md`

If source use became load-bearing, refresh the source atlas too.

## Non-goals
This protocol does not authorize:
- silent reranking;
- treating a `hold` candidate as launch-ready;
- treating a kernel brief as product-market proof;
- or treating one plausible repo tree as the only acceptable implementation forever.

