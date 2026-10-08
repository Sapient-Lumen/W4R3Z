# Revision REV0268 — live-proof plumbing for evidence lanes

This revision fixes a broader plumbing class than the one closed in REV0267:
several host-aware commands were successfully probing live session/host facts,
but then failed to forward those facts into the lower-level pack/audit writers
that actually decide whether the current machine is believable proof for a
selected desktop lane.

## What changed

- fixed `plan-project` so its live readiness snapshot is passed into
  `build_claim_plan()` instead of being collected and dropped
- fixed `gen-host-contract-pack` so live host snapshots reach
  `write_host_contract_pack()` / `build_host_contract_plan()`
- fixed `gen-claim-pack` so live host snapshots reach `write_claim_pack()`
- fixed `audit-target-claims` so live host snapshots reach the audit engine
- fixed `gen-capability-audit-pack` so both live host snapshots and explicit
  `--evidence-lane` selections reach the generated audit pack
- fixed `gen-promotion-pack` so claim-witness review is built from the real
  host snapshot instead of a hostless fallback
- host/session review scripts now preserve explicit `--evidence-lane` reruns
- host/session builders now materialize a selected evidence lane even when the
  upstream planner did not already populate one, keeping the selected lane
  visible in generated pack JSON/docs

## Why it matters

For VHK, Linux-native support claims are only honest if the review packs keep
the proof context intact. A sway box being evaluated as GNOME evidence should
show up as drifted everywhere, not only in one command path. These fixes make
that proof posture survive across planner, claim, promotion, host-contract,
session-fit, and capability-audit workflows.

## Validation

Focused coverage now passes for:
- `tests/test_host_contract_pack_cli.py`
- `tests/test_session_fit_pack_cli.py`
- `tests/test_claim_pack_cli.py`
- `tests/test_capability_audit_pack_cli.py`
- `tests/test_plan_project_cli.py`
- `tests/test_promotion_pack_cli.py`

The full suite was started more than once, but in this environment I only got a
reliable full signal from the focused CLI slices above before the run stopped
reporting progress.
