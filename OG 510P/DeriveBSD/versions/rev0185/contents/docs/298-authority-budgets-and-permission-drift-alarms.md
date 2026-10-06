# Authority budgets + permission drift alarms (stop capability creep early)

Most systems die by a thousand paper-cuts:
a capability here, a device grant there, a “temporary” exception that never leaves.

Even with great sandbox primitives, permission creep happens unless we make it **visible and enforceable**.

DeriveBSD already has:
- explicit grants (`caproute.json`)
- blast radius diffs (`docs/106-blast-radius-diff.md`)
- promise vocabulary + lint (`docs/271-promise-profile-vocabulary-and-lint.md`)
- multiparty approvals (`docs/288-multiparty-approvals-and-separation-of-duties.md`)

The missing primitive is a **budget**: an explicit, reviewable limit that makes drift fail fast.

## Prior art worth stealing

- **Flatpak / portal model** makes permissions explicit, but ecosystems still needed tooling to flag bad patterns.  
  References: https://docs.flatpak.org/en/latest/sandbox-permissions.html

- **Flathub linter** encodes “permission smell” rules (filesystem access, background operation, etc.) and blocks submissions.  
  Reference: https://docs.flathub.org/docs/for-app-authors/linter

The meta-lesson: *permissions need budgets + lints, not just mechanisms.*

## DeriveBSD target

Each component (service/app) can declare an **authority budget** that is evaluated against compiled runtime IR.

Budgets can be:
- authored by the component owner (self-restraint),
- imposed by a platform policy (hard limits),
- tightened automatically over time (ratchet).

Budgets are **policy objects**, not “best-effort warnings”.

## What we budget (v0)

Budget dimensions should align with the things we already compile:

### Filesystem / handles
- number of writable roots
- number of read-only roots
- presence of “ambient” roots (e.g., `/` or full home) is always a hard failure
- whether any handle grants metadata enumeration vs specific subdir

Inputs: `preopen.map`, `mount.view`, state footprints.  
See: `docs/294-oblivious-sandboxing-launchers.md`, `docs/152-store-view-minimization.md`.

### Network
- number of allowed egress destinations (by name/category)
- whether raw sockets are permitted
- inbound listeners count (and whether brokered)
- whether hostname rules require brokered DNS, and DNS evidence retention budgets

- whether host network topology mutation is allowed (links/routes/pf root ruleset), and whether it requires maintenance leases + commit-confirmed semantics
Inputs: egress broker leases, inbound listen broker manifests.  ; net.topology plans/receipts
See: `docs/281-network-egress-broker-and-consent.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`., `docs/322-network-topology-and-firewall-as-derived-operations.md`

### Trust / PKI
- number of trust bundles a unit depends on
- whether private/enterprise CAs are in scope
- whether the unit ships its own CA bundle (should be a lint failure by default)

Inputs: compiled PKI profile + trust bundle mapping.
See: `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`.


### Crypto operations / key use
- which key ids a unit may request operations for (sign/decrypt)
- whether user presence is required for key use
- rate limits (ops/minute) and export posture for outputs
- receipt retention/redaction class (avoid privacy-toxic audit trails)

Inputs: compiled crypto profile + per-op receipts.
See: `docs/306-crypto-operations-portal-and-split-keys.md`, `spec/crypto.op.receipt.schema.json`.

### Devices
- device grants by class (HID, USB storage, camera/mic, GPU)
- whether grants are timeboxed leases (should be the default)

Inputs: device-grant receipts and compiled devfs views (`devfs.view.plan`/`devfs.view.receipt`/`devfs.view.event`) (and any rendered devfs rulesets).  
See: `docs/323-devfs-views-plans-and-receipts.md`, `docs/278-device-grants-and-devfs-rulesets.md`, `docs/279-usb-quarantine-and-removable-media-workflow.md`.


### Inventory / fingerprinting
- whether a unit can read full hardware inventory vs only filtered device-class facts
- whether any raw serial/asset identifiers are accessible (should be deny by default; hashed-only under explicit policy)
- export posture and retention class for inventory receipts

Inputs: `hw.inventory.receipt` digests, device topology facts, support bundle policies.
See: `docs/319-hardware-inventory-and-driver-binding-as-evidence.md`, `docs/251-export-policies-and-support-bundle-portal.md`.

### Firmware / boot-policy mutation
- whether firmware updates are allowed at all without explicit maintenance leases
- allowed firmware classes (system/bmc/nic/storage) and whether downgrades are ever permitted
- whether UEFI variable writes are allowed; which classes (boot/capsule/secureboot)
- Secure Boot key database mutation (`PK/KEK/db/dbx`) should require quorum approvals by default
- retention/export class for firmware and UEFI-var receipts (avoid privacy-toxic blobs)

Inputs: `fw.inventory.receipt` digests, `fw.update.plan`/`fw.update.receipt`, `uefi.var.set.plan`/`uefi.var.set.receipt`, consent/maintenance leases.
See: `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `docs/256-consent-ux-contract.md`, `docs/236-breakglass-and-recovery-mode.md`.

### Kernel mutation (sysctls + kmods)
- whether runtime sysctl writes are allowed at all
- maximum number of sysctl keys a unit/domain may write
- whether any runtime kernel module loads are allowed
- allowed kmod classes (network/storage/virtualization) and whether loads must be mediated

Inputs: `sysctl.plan`/`sysctl.receipt`/`sysctl.event`, `kmod.load.receipt`/`kmod.event`, lockdown/securelevel posture outputs.
See: `docs/318-kernel-tunables-and-sysctls-as-evidence.md`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/230-lockdown-levels-and-securelevel.md`.

### Observability / debug authority
- whether trace/log/screen capture is allowed by default
- whether remote assistance sessions can attach
- whether inspect trees / flight recorder buffers are accessible, and what retention budgets apply

Inputs: observability leases, diagnostics profiles, and remote assistance envelopes.  
See: `docs/192-observability-as-capability.md`, `docs/302-structured-diagnostics-inspect-trees.md`, `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`, `docs/291-remote-assistance-sessions-as-evidence.md`.


### Operator access / shells
- whether interactive operator sessions are allowed at all for a host/service domain
- maximum session TTL and concurrency
- whether SSH certificate auth is required (no static keys)
- whether output-only recording is required for privileged roles

Inputs: access broker policy and `operator.session` envelopes.
See: `docs/311-operator-access-leases-and-ssh-certs.md`, `spec/operator.session.schema.json`, `docs/292-terminal-session-recording-as-evidence.md`.

## Enforcement points

1) **Plan time (preferred):**  
   budgets are checked during Plan compilation; exceeding them blocks activation unless policy grants an exception.

2) **Runtime drift alarms:**  
   if reality diverges from compiled manifests (unexpected opens, new sockets), emit an incident-grade receipt.  
   (This pairs naturally with exec-integrity policy.)  
   See: `docs/289-exec-integrity-policy-and-verified-execution.md`.

3) **Review UX:**  
   `derive diff --blast-radius` summarizes “budget delta”: who crossed which threshold and why.

## Evidence objects

- `authority.budget` (policy object)
- `authority.budget.check` (result: pass/fail, deltas, top contributors)
- `authority.exception` (explicit, timeboxed waiver with approvers)

These should be first-class evidence nodes so we can answer:
“when did this service become scary?”

## Failure modes

- Budgets that are too strict create bypass pressure → design must allow *scoped exceptions* with receipts.
- Budgets that are too permissive are just dashboards → require ratcheting + ownership.

## Open questions

- How do we set sane defaults for “new components” without blocking experimentation?
- Do we budget *complexity* (e.g., number of distinct capability kinds) in addition to counts?
- What’s the minimum granularity that’s useful without becoming a paper exercise?

Last updated: 2026-02-26
