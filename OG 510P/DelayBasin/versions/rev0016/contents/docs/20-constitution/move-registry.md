# Move registry

This registry records **certified move classes**.
The point is not to bureaucratize every revision.
The point is to keep the archive honest about **what kind of transition** it is claiming to have made.

## Certified move classes

- `MV-0001` — `read-reopen`
  - Class: certified-move
  - Meaning: re-enter the latest archive revision as source of truth before claiming new progress.
  - Admission notes: current canon surfaces must be read or refreshed enough to avoid drifting from stale state.
  - Dereference: `START_HERE.md`, `docs/00-meta/llm-runbook.md`

- `MV-0002` — `research-cite`
  - Class: certified-move
  - Meaning: use current external sources to pressure, sharpen, or challenge the archive, while preserving only compact load-bearing trace.
  - Admission notes: cite current sources; do not retain bulky non-crucial artifacts in the release bundle.
  - Dereference: `docs/00-meta/archive-policy.md`, `docs/50-promptcraft/prompt-pairs.md`

- `MV-0003` — `refine-compress`
  - Class: certified-move
  - Meaning: reduce entropy, clarify an existing distinction, or compress repeated structure into a better canonical surface.
  - Admission notes: wire the refined surface into discovery so compression does not become disappearance.
  - Dereference: `docs/10-method/method-overview.md`, `docs/00-meta/trajectory-map.md`

- `MV-0004` — `quarantine`
  - Class: certified-move
  - Meaning: keep a risky or weakly supported idea live without laundering it into canon.
  - Admission notes: preserve consequences-if-true and what-would-count-against-it hooks.
  - Dereference: `docs/90-quarantine/wild-speculations-2026-03-08.md`, `docs/50-promptcraft/prompt-pairs.md`

- `MV-0005` — `promote`
  - Class: certified-move
  - Meaning: elevate a loose pattern or risky idea into canon with explicit status and wiring.
  - Admission notes: identify what changed status and where the new canonical surface lives.
  - Dereference: `docs/20-constitution/claim-registry.md`, `docs/00-meta/trajectory-map.md`

- `MV-0006` — `recertify`
  - Class: certified-move
  - Meaning: confirm that a term, prompt, surface, or distinction still deserves trusted status after drift pressure.
  - Admission notes: say what remained stable enough to keep trusting or what was demoted/renegotiated.
  - Dereference: `docs/10-method/certified-core-vocabulary-and-recertification.md`, `docs/20-constitution/core-lexicon-registry.md`

- `MV-0007` — `package-handoff`
  - Class: certified-move
  - Meaning: emit a compact release object that future sessions can reopen as the current handoff artifact.
  - Admission notes: `make lint` passes and release packaging stays compact and inspectable.
  - Dereference: `Makefile`, `tools/package_release.py`

- `MV-0008` — `ratify-demote`
  - Class: certified-move
  - Meaning: explicitly raise or lower the trusted status of an archive term, claim, or surface under a preserved promotion contract or demotion reason.
  - Admission notes: promotion may not occur by repetition alone; preserve evidence family, temporal validity posture, and what would force reversal.
  - Dereference: `docs/10-method/promotion-contracts-and-staged-ratification.md`, `docs/20-constitution/promotion-contract-registry.md`

- `MV-0009` — `review-decay`
  - Class: certified-move
  - Meaning: explicitly re-evaluate whether a canon-level claim still deserves its status under temporal drift pressure.
  - Admission notes: preserve what triggered review and whether the result was keep, shrink, recertify, demote, or quarantine.
  - Dereference: `docs/10-method/temporal-demotion-and-decay-patrol.md`, `docs/20-constitution/decay-watch-registry.md`


- `MV-0010` — `recover-resync`
  - Class: certified-move
  - Meaning: re-establish legitimate continuation after suspected transient corruption, stale reopen, or procedurally invalid local progress.
  - Admission notes: reopen the recovery kernel, regenerate bounded handoff state, run deterministic checks, and quarantine or demote ambiguous material before ordinary revision resumes.
  - Dereference: `docs/10-method/self-stabilizing-recovery-and-legitimacy-kernel.md`, `docs/20-constitution/recovery-kernel.md`


- `MV-0011` — `issue-receipt`
  - Class: certified-move
  - Meaning: emit or update a compact revision receipt showing what transition occurred, what status moved, which refs materially mattered, and which checks made the transition admissible.
  - Admission notes: receipt must stay small, machine-readable, and aligned with current revision surfaces.
  - Dereference: `docs/10-method/revision-receipts-and-audit-objects.md`, `docs/20-constitution/revision-receipt-contract.md`, `REVISION-RECEIPT.json`


- `MV-0012` — `shadow-compare`
  - Class: certified-move
  - Meaning: preserve one nearby rejected move and why it was not admitted, so the accepted revision does not rewrite its local decision boundary into inevitability.
  - Admission notes: use only when a real near-admitted alternative existed; keep the shadow tiny and point to quarantine or open questions if the rejected move remains live.
  - Dereference: `docs/10-method/counterfactual-shadow-and-nearby-rejected-moves.md`, `docs/20-constitution/counterfactual-shadow-contract.md`, `REVISION-RECEIPT.json`
