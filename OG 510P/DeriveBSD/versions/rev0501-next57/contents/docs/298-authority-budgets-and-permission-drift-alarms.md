# Authority budgets + permission drift alarms (stop capability creep early)

Most systems die by a thousand paper-cuts:
a capability here, a device grant there, a “temporary” exception that never leaves.

Even with great sandbox primitives, permission creep happens unless we make it **visible and enforceable**.

DeriveBSD already has:
- explicit grants (`caproute.json`)
- blast-radius diffs (`docs/106-blast-radius-diff.md`)
- authority diffs (`docs/374-authority-diff-schema-and-review-workflows.md`)
- multiparty approvals (`docs/288-multiparty-approvals-and-separation-of-duties.md`)

The missing primitive is a **budget**: an explicit, reviewable limit that makes drift fail fast **without** becoming a second giant authority meta-system.

## Prior art worth stealing

- Flatpak / portal model makes permissions explicit, but still depends on careful permission review.
- Flathub linter turns recurring permission smells into machine-checkable feedback.
- systemd's `systemd-analyze security` shows the value of a generated exposure summary, but it is heuristic rather than authoritative.

The meta-lesson: *permissions need budgets + review surfaces + narrow exceptions, not just mechanisms.*

## DeriveBSD target

Each component (service/app) can declare an **authority budget** that is evaluated against compiled runtime IR.

The trilogy is now explicit:

- `authority.budget` = authoritative least-authority policy object
- `authority.budget.check` = evidence-only comparison result
- `authority.exception` = authoritative, timeboxed, field-scoped waiver

Budgets may be:
- authored by the component owner (self-restraint),
- imposed by platform policy (hard limit),
- or tightened automatically over time (ratchet).

But the generic budget lane is intentionally **small**.
It covers component-runtime posture, not every privileged action in DeriveBSD.

## What we budget in v0

Budget dimensions align with runtime surfaces that already compile naturally from descriptor intent.

### Filesystem
- number of writable roots
- number of read roots
- hard failure for ambient roots (`/`, full home, equivalent broad exposure)
- whether metadata enumeration is allowed

Inputs: `preopen.map`, `mount.view`, state footprints.
See: `docs/294-oblivious-sandboxing-launchers.md`, `docs/152-store-view-minimization.md`.

### Network
- number of allowed egress destinations / classes
- whether raw sockets are permitted
- number of inbound listeners
- whether DNS must remain brokered

Inputs: compiled network policy, egress broker state, inbound listen manifests.
See: `docs/281-network-egress-broker-and-consent.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`.

### Devices
- allowed device classes
- whether grants must be timeboxed leases

Inputs: device-grant receipts and compiled `devfs.view.*` artifacts.
See: `docs/323-devfs-views-plans-and-receipts.md`, `docs/278-device-grants-and-devfs-rulesets.md`.

### Trust
- number of trust bundles a unit depends on
- whether private / enterprise roots are in scope
- whether the unit ships its own CA bundle

Inputs: compiled PKI profile + trust bundle mapping.
See: `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`.

### Observability
- whether tracing is allowed
- whether screen / remote-assistance style observation is allowed
- how many inspect namespaces are exposed
- how many flight-recorder classes are retained

Inputs: diagnostics profiles, observability leases, remote assistance envelopes.
See: `docs/192-observability-as-capability.md`, `docs/302-structured-diagnostics-inspect-trees.md`, `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`.

## What this lane does **not** own

The generic authority-budget lane does **not** replace already-distinct higher-authority lanes.

These remain governed by their own authoritative objects and posture docs:

- kernel mutation
- host network-topology mutation
- firmware / UEFI mutation
- destructive reprovision / reset
- workload identity issuance
- operator-session policy

That boundary matters because otherwise `authority.budget` would quietly duplicate accepted decisions from `docs/467-operator-access-posture-by-profile.md`, `docs/470-workload-identity-and-credential-issuance-posture-by-profile.md`, `docs/471-firmware-update-posture-by-profile.md`, `docs/475-kernel-mutation-posture-by-profile.md`, `docs/477-network-topology-posture-by-profile.md`, and `docs/483-destructive-reprovisioning-and-reset-authority.md`.

## Enforcement points

1) **Plan time (preferred):**
   budget checks run during compilation / review; broadening beyond budget blocks by default.

2) **Runtime drift alarms:**
   if reality diverges from compiled manifests, emit an incident-grade `authority.budget.check`.

3) **Review UX:**
   `derive diff --blast-radius` and `authority.diff` summarize which field crossed which limit and why.

## Evidence + exception objects

- `authority.budget` = authoritative least-authority budget
- `authority.budget.check` = evidence-only comparison result
- `authority.exception` = authoritative scoped waiver

The canonical pattern is intentionally narrow:

- a failing check does **not** become policy
- an exception waives one field at a time
- exceptions expire instead of silently rewriting the baseline budget

## Failure modes

- Budgets that are too strict create bypass pressure → design must allow scoped exceptions with receipts.
- Budgets that are too broad recreate “permission dashboards” → keep the v0 dimension set small.
- Budgets that absorb every privileged lane become incoherent → preserve accepted lane-specific authority contracts.

## What remains open

The hard boundary is now decided.
What remains open is implementation detail:

- how aggressively budgets ratchet by default for new components,
- which review UI is best for budget deltas,
- and whether future dimensions deserve promotion into the generic budget lane.

See: `adrs/ADR-0084-authority-budgets-and-exception-boundary.md`, `docs/494-authority-budget-policy-check-and-exception-boundary.md`.

Last updated: 2026-03-07r223
