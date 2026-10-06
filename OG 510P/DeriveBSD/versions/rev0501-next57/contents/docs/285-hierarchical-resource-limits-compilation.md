# Hierarchical resource limits (rctl/racct) compilation details

This file is a deeper companion to `docs/247-resource-budgets-and-limits-as-evidence.md`.

DeriveBSD wants “resource governance” to be:

- **typed** (not shell snippets)
- **compiled** into enforcement backends
- **receipted** when applied
- **explainable** when violated

FreeBSD’s `racct` + `rctl(8)` are unusually good primitives for this because they were designed to
support *hierarchical* subjects (jails, users, login classes, etc.) rather than only per-process ulimits.

(see `docs/32-curated-references.md`)

## Lessons to steal

- `rctl(8)` has a precise rule syntax, but admins often treat it as “that weird config file”.
  Greenfield advantage: wrap it in a typed policy that can be linted, diffed, and replayed.
- `racct` makes “who used what” answerable without bolting on a separate accounting daemon.
- The hard part is rarely enforcement; it’s *coordination*: making budgets consistent across services,
  packaging, and incident workflows.

## DeriveBSD stance

### 1) Resource governance policy is the source of truth

A deployment’s resource governance should be captured as `resource.policy`:

- `spec/resource.policy.schema.json`
- example: `spec/examples/resource.policy.json`

It should be possible to answer “what budgets existed?” without reading host-local state.

### 2) Budgets are leased capabilities, not permanent exemptions

For operations, a budget is often temporarily raised (e.g. incident response).
That should be modeled as a short-lived **budget grant** with an audit trail:

- `spec/resource.budget.grant.schema.json`
- `spec/resource.budget.receipt.schema.json`

This mirrors the pattern used elsewhere in the archive (breakglass grants, device grants, egress leases).

### 3) Compile policy into backend-specific rulesets with receipts

The policy compiler should target a small set of backends initially:

- `rctl` / `racct` for host and jails (hierarchical limits + accounting)
- `cpuset` for CPU topology binding (where needed)
- (optionally) bhyve caps for VM-level ceilings

Applying the compiled ruleset produces a `resource.budget.receipt` that includes:
- the policy digest
- the backend(s) touched
- the effective rule identifiers
- any non-fatal mismatches (e.g. unsupported resource type on a backend)

### 4) Violations are first-class events

When a limit triggers, record an explainable violation event:

- `spec/resource.violation.event.schema.json`

A violation should include:
- subject identity (jail/service/appvm id)
- which budget/rule triggered
- measured usage at the time
- the enforced action (deny, kill, log, notify, etc.)

This prevents “resource incidents” from turning into guesswork.

## Recommended v0 constraints (keep it boring)

To avoid a sprawling policy language, start with a constrained vocabulary:

- Subject selectors: `{kind: jail|service|uid|loginclass|appvm, id: ...}`
- Resources: align with `rctl(8)`’s common resources (cpu, memoryuse, nproc, openfiles, swapuse, etc.)
- Actions: `{deny, log, throttle, kill}` (even if `rctl` itself expresses these differently)

Then make backend mappings explicit and linted.

## Cross-links

- High-level philosophy and evidence spine: `docs/247-resource-budgets-and-limits-as-evidence.md`, `docs/222-resource-governance-as-evidence.md`
- Existing profiles and per-service contracts: `docs/143-resource-controls-rctl-racct-cpuset.md`, `docs/232-service-promise-profiles.md`
- Observation-mode learning loop for right-sized budgets: `docs/329-learned-resource-budgets-and-observation-mode.md`
- Incident workflows and timeboxed authority: `docs/223-secrets-and-key-management-as-evidence.md`, `docs/281-network-egress-broker-and-consent.md`

