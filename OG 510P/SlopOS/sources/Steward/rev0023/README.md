# Steward living archive

**One-line summary:** Steward is SlopOS's component lifecycle and activation fabric, keeping services explicit, restartable, and policy-bounded without ambient Unix folklore.

Revision notes: [`CHANGELOG.md`](CHANGELOG.md)

This repo is a **living archive** for designing Steward while SlopOS itself is still in design. The goal is to preserve the best parts of the SlopOS datacube discipline—explicit claims, source locks, context packs, packaged revisions, and narrow posture docs—without prematurely freezing a giant service-manager worldview.

## How to navigate
0. Mile-high map: [`docs/00-meta/trajectory-map.md`](docs/00-meta/trajectory-map.md)
0.5 Editing runbook: [`docs/00-meta/llm-runbook.md`](docs/00-meta/llm-runbook.md)
1. Threat model: [`docs/10-threat-model/`](docs/10-threat-model/)
2. Assurance: [`docs/20-assurance/`](docs/20-assurance/)
3. Architecture: [`docs/30-architecture/`](docs/30-architecture/)
4. Research / inspirations: [`docs/90-inspirations/`](docs/90-inspirations/)
5. Decisions: [`adrs/`](adrs/) and proposals: [`rfcs/`](rfcs/)

## Current posture
- Steward is **not** a systemd clone.
- Steward is **not yet** a final architecture; it is a research-and-posture archive with a small set of deliberately chosen seams.
- Phase 1 emphasis is on:
  - explicit component identity,
  - foreground, accountable lifecycle roots,
  - supervisor-owned activation,
  - deterministic restart and stop semantics,
  - lifecycle observations, compact status, and bounded subscription views that stay separate from logs,
  - explicit readiness, narrow activity accounting, and cooperative quiesce,
  - bounded continuity escrow,
  - shell/terminal integration that uses semantic side channels rather than PTY folklore,
  - command-frame observations with explicit trust/confidence rather than buffer-guess magic,
  - optional runtime-cycle witnesses for correlating concrete runs and avoiding stale shell actions,
  - compact end-of-cycle / termination-cause observations that explain why a concrete run ended without a giant host-specific failure API,
  - explicit repeated-failure cooldown / repair-gate semantics so crash loops become visible and bounded instead of ambient retry folklore,
  - explicit precision fences so shell/terminal affordances can admit when hops or fallback paths downgraded what they really know,
  - explicit capability handshakes so richer shell/terminal features come from fresh observed support instead of `TERM` folklore,
  - explicit shell/terminal hop lineage so remote-aware semantics stay scoped to the actual path instead of collapsing into flat PTY folklore,
  - explicit provisional-state semantics so predictive local echo, incomplete frame metadata, and later refinements can stay useful without masquerading as confirmed lifecycle truth,
  - explicit attention hints so command-finished, needs-input, warning, and progress-like shell/terminal cues can stay user-filterable, freshness-scoped, and non-authoritative,
  - explicit target anchors so shell/terminal affordances can bind to exact frames, receipts, transcript spans, and concrete runs without visible-text scraping or raw-capability leakage,
  - explicit bounded context handoff so exact command frames, output slices, receipts, and concrete runs can be attached or exported without ambient whole-scrollback sharing,
  - explicit repair-gate semantics so repeated failures can cool down, become repair-required, and stay explainable without a giant retry-policy language.

## Archive discipline
- Cite external work with **reference IDs** from [`docs/00-meta/bibliography.md`](docs/00-meta/bibliography.md).
- Register local evidence/process artifacts as **evidence IDs** in [`docs/00-meta/evidence-index.md`](docs/00-meta/evidence-index.md).
- Prefer **posture docs and open questions** over prematurely multiplying detailed singleton docs.
- Keep `out/context_pack.md` fresh using `make context-pack`.
- Refresh the external-source review queue using `make source-review-queue`.
- Ship revisions using `make handoff-release STAMP=YYYY.MM.DD.HH.MM SLUG=<slug>`.

## What the latest revision adds
- a repair-gate posture so repeated failures can cool down, become repair-required, and stay explainable instead of looping forever behind retry folklore,
- sharper shell/terminal direction around attach-last-failure, repair bundles, exact recent-cycle context, and safer clear/retry affordances,
- refreshed external research and repo hygiene around CrashLoopBackOff resets, restart intensity and respawn limits, launchd throttle intervals, maintenance/clear semantics, updated source locks, and regenerated review/context artifacts.
