# Denial-driven policy suggestions: make least-authority iteration cheap

Least-authority systems fail when *iteration* is painful.
If tightening authority requires hand-authoring every rule, people stop.

DeriveBSD already has the right primitive (`spec/policy.suggestion.schema.json`):
**learning produces reviewable patches**.

This note tightens the workflow by emphasizing a specific high-signal input:
**denials** (and near-denials) are the best teaching moments.

## Prior art (denials → candidate policy)

- AppArmor: `aa-logprof` proposes policy from audit denials.
- SELinux: `audit2allow` (dangerous if used blindly, still a useful iteration tool).
- macOS sandbox profiles (Seatbelt/SBPL): historically supported tracing denials to help converge on a profile.
  - reverse-engineering guide (historical but still useful model): https://reverse.put.as/wp-content/uploads/2011/09/Apple-Sandbox-Guide-v1.0.pdf

The pattern:
1) run with a restrictive baseline
2) capture denials with context
3) propose a minimal additive patch
4) require explicit review

## DeriveBSD mapping

### Denials are structured evidence

Every broker/portal/sandbox boundary should emit denial events with:
- **what was requested**
- **why it was denied** (which rule)
- **what authority would be required** to allow it
- a stable target id (unit/service/jail/microVM)

Denials become a first-class input to:
- `policy.suggestion` generation
- the Permission Center / consent ledger (review + revoke + expire)

See: `docs/326-learned-promise-profiles-and-observation-mode.md`, `docs/371-permission-center-and-authority-introspection.md`.

### “Minimal patch” defaults

Denial-driven suggestions should be conservative by construction:
- never propose wildcard “allow all” rules
- prefer narrow path rules over broad filesystem grants
- map network attempts into *classes* (egress/listen classes), not raw IPs
- require a justification string (human-written) for every suggested widening

### A practical UX loop

Introduce a workflow that turns “it failed” into a reviewable patch:

- `derive run --complain <unit>`
  - runs with the baseline promise profile
  - collects broker receipts + denial events

- `derive suggest --from-denials <session>`
  - emits `policy.suggestion` objects targeting:
    - `sandbox.profile`
    - `net.egress.policy` / `net.listen.policy`
    - portal permission store deltas

- `derive apply-suggestion <file>`
  - applies the patch in a branch/PR-style flow
  - produces a receipt that ties the change to the denial evidence

## Why this matters

- Makes least-authority convergence a **workflow**, not heroics.
- Prevents “temporary exceptions” from becoming permanent folklore.
- Turns policy changes into explainable diffs: *the system asked; policy said no; we changed policy because…*

Last updated: 2026-02-27r107
