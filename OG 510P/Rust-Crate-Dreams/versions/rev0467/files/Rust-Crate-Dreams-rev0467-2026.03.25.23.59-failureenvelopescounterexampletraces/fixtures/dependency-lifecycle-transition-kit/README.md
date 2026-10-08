# Dependency Lifecycle Transition Kit fixtures

This fixture family gives **P-0535** concrete `0.1` review artifacts.

Also consult `meta/dependency-lifecycle-transition-lane-boundaries-2026-03-22.md` and `meta/dependency-lifecycle-transition-seam-proof-plan-2026-03-22.md` so lane assignment, seam proof, transition posture, source-aware boundaries, imported signals, and exceptions stay separate.

## First-class schemas

- `dependency-lane.snapshot.schema.json`
- `criticality-boundary.report.schema.json`
- `abstraction-seam.receipt.schema.json`
- `replacement-readiness.report.schema.json`
- `transition-plan.manifest.schema.json`
- `override-authority.receipt.schema.json`
- `dependency-exception.ledger.schema.json`
- `imported-signal.receipt.schema.json`
- `signal-freshness.report.schema.json`
- `exception-reevaluation.report.schema.json`
- `selection-anchor.receipt.schema.json`
- `reresolution-risk.report.schema.json`
- `lifecycle-drift.diff.schema.json`
- `lifecycle-support-bundle.manifest.schema.json`

## Scenario themes

1. a broad prototype/tooling lane coexisting with a restricted control core,
2. a real trait-facade seam that makes replacement plausible,
3. an owned-fork or restricted-lane exception that still needs typed policy and reevaluation,
4. release drift that widens direct third-party exposure into a restricted lane,
5. override visibility that distinguishes checked-in transition policy from local-only config,
6. stale imported context or expired exceptions that should force review instead of silent carry-forward,
7. lockfile-only or local-only routes that keep today green without proving future clean-resolve durability.

## What these fixtures are trying to protect

They protect against flattening all of the following into one fake lifecycle answer:

- “the graph exists”,
- “the dependency is trusted enough”,
- “we can replace it later”,
- “there is a local patch”,
- “we forked or vendored it”,
- “there is a security tab”,
- or “the lane has few dependencies”.

Those are useful facts, but **P-0535** is stronger only when lane, seam, override authority, selection anchor, clean-resolve risk, exception status, imported context freshness, and transition drift remain reviewable as separate objects.


## 2026-03-23 refresh / transition additions

### New first-class schema

- `transition-review-packet.manifest.json`

### New scenario themes

#### `fresh_advisory_and_new_release_force_transition_recheck_not_silent_keep`
Proves that a previously accepted posture needs one explicit transition review packet when both advisory and release facts change.

#### `alternate_registry_and_lock_only_anchor_need_shared_transition_packet`
Proves that an alternate registry plus an old lockfile can keep today green without proving a shared future posture.



## 2026-03-23 trigger-intake addendum

This family now also needs to prove:
- which imported signals were observed before posture changed,
- how alternate-registry and anchor-sharedness facts stay separate from the imported signal itself,
- and when the correct next step is to open a transition packet rather than silently assume one.

### New first-class schema
- `trigger-intake.receipt.json`

### `alternate_registry_trigger_intake_distinguishes_signal_from_posture`
Proves that imported registry/security signals should first become a typed intake receipt before they become a new architectural answer.
