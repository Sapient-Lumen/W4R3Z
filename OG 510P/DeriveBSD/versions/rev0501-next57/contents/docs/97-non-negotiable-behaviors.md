# Non-negotiable behaviors (day-0 defaults)

This file is the *behavioral contract* for DeriveBSD: the things that must be **true by default** so that
(1) the supply chain is verifiable, and (2) the runtime blast radius is minimized.

Each behavior maps to:
- **where it is enforced** in the pipeline (Spec→Lock→Plan→Artifact→Activate/Launch)
- **what evidence object exists** (digestable, signable)
- **where to read** in this archive

> Rule: If a behavior cannot be backed by **verifiable evidence**, `derive explain` must report it as `unverified`.

---

## Supply-chain defaults

### Pin inputs
- Enforced at: **Spec→Lock**
- Evidence: `derive.lock` (source identities + hashes), Spec digest
- Read: `docs/02-derive-core.md`, `docs/14-supply-chain.md`

### Prove closure
- Enforced at: **Artifact→Closure→Activate/Launch**
- Evidence: `closure.manifest` + `closure.proof` (signature)
- Read: `docs/90-closure-proof.md`, `spec/closure.manifest.schema.json`, `spec/closure.proof.schema.json`

### Sandbox builds
- Enforced at: **Plan→Artifact**
- Evidence: sandbox policy hash bound into Plan digest (+ logs/metadata)
- Read: `docs/04-sandbox.md`, `docs/45-build-sandbox-jails.md`, `docs/16-sandbox-hardening.md`

### Deny network (build-time)
- Enforced at: **Plan→Artifact**
- Evidence: sandbox policy includes `network=never` unless an explicit fetch step is declared
- Read: `docs/04-sandbox.md`, `docs/91-hostile-builders.md`

### Minimize build read scope (hide non-required store paths)
- Enforced at: **Plan→Artifact**
- Evidence: `storeview.manifest` (declared store objects visible to this build step)
- Read: `docs/152-store-view-minimization.md`, `docs/91-hostile-builders.md`

### Enforce store immutability (no post-check mutation)
- Enforced at: **Store import/consume + Activate/Launch**
- Evidence: store mounted read-only from snapshots; optional store-integrity reporting
- Read: `docs/153-store-immutability-and-toc-tou.md`, `docs/56-store-layout-and-digests.md`

### Sign artifacts (distribution-time)
- Enforced at: **Cache/Consume**
- Evidence: signature over artifact digest (per trust policy)
- Read: `docs/46-cache-trust-model.md`, `adrs/ADR-0009-artifact-verification.md`, `spec/trust.policy.schema.json`

### Keep signing keys out of risky compartments (split crypto domain)
- Enforced at: **Plan→Artifact**, **Cache/Consume**
- Evidence: `crypto.op.receipt` objects binding signature operations to an approved crypto-domain + policy decision digest
- Read: `docs/164-split-crypto-domains.md`, `docs/151-factotum-style-credential-broker.md`

### Attest provenance
- Enforced at: **Plan→Artifact** (emit), **Consume** (verify if policy requires)
- Evidence: DSSE/in-toto attestation bound to artifact digest (optional transparency log)
- Read: `docs/71-attestations-dsse-in-toto-slsa.md`, `docs/31-provenance-and-sbom.md`, `adrs/ADR-0004-attestations-intoto-dsse.md`

### Make test results evidence-addressable (test receipts)
- Enforced at: **Plan→Artifact** (emit), **Consume/Promote** (verify if policy requires)
- Evidence: a digest-bound test receipt bound to artifact digest + runner identity; policy may require it for promotion
- Read: `docs/166-test-receipts-and-promotion-gates.md`

### Enforce policy
- Enforced at: **Lock→Plan**, **Plan→Artifact**, **Runtime launch**
- Evidence: `policy.decision` record (PDR) digest bound into Plan/closure
- Read: `docs/30-policy-engine.md`, `docs/93-policy-decision-records.md`, `spec/policy.decision.schema.json`

### Explain dependencies (“why/what/where-from”)
- Enforced at: **Explain surfaces**
- Evidence: verified digests + closure manifest + PDR trace + provenance pointers
- Read: `docs/95-explainability-contract.md`, `docs/38-structured-outputs.md`, `docs/92-verification-matrix.md`

---

## Developer UX defaults

### Provide fast, reproducible dev environments (nix-shell parity)
- Enforced at: **Plan→Activate (DevShell)**
- Evidence: `devshell.plan.json`, `devshell.env.json`, `devshell.sandbox.json`
- Read: `docs/159-devshells.md`, `adrs/ADR-0039-devshells-first-class.md`

### Keep dev environments sandboxed (hostile code posture)
- Enforced at: **DevShell runtime**
- Evidence: jail/microVM profile digest; deny-network default unless policy grants
- Read: `docs/159-devshells.md`, `docs/91-hostile-builders.md`, `docs/150-jail-profiles-and-allowlist-knobs.md`

---

## Runtime defaults (blast-radius)

### Launch microVMs (microVM-first)
- Enforced at: **Runtime**
- Evidence: `runtime.manifest` digest + VM bundle digest
- Read: `docs/23-hypervisor-centric-derivebsd.md`, `docs/33-runtime-manifest-schema.md`, `docs/34-microvm-bundle-format.md`

### Compose pf (per-instance networking)
- Enforced at: **Runtime**
- Evidence: per-instance pf anchor name + generated ruleset digest
- Read: `docs/26-virtual-networking-pf.md`, `docs/67-pf-anchors-per-instance.md`, `adrs/ADR-0017-pf-anchors-unit.md`


### `/dev` views are derived + receipted (device nodes are authority)
- Enforced at: **Runtime launch / jail activation**
- Evidence: `devfs.view.plan` + `devfs.view.receipt` (+ drift `devfs.view.event`); device attach grants/receipts for cross-domain attachments
- Read: `docs/323-devfs-views-plans-and-receipts.md`, `docs/278-device-grants-and-devfs-rulesets.md`, `spec/devfs.view.plan.schema.json`, `spec/devfs.view.receipt.schema.json`, `spec/devfs.view.event.schema.json`


### Host network topology is derived + receipted (no rc.conf folklore)
- Enforced at: **Activate/Apply** (or maintenance leases)
- Evidence: `net.topology.plan` + `net.topology.receipt` (+ drift `net.topology.event`)
- Read: `docs/322-network-topology-and-firewall-as-derived-operations.md`, `spec/net.topology.plan.schema.json`, `spec/net.topology.receipt.schema.json`, `spec/net.topology.event.schema.json`

### Snapshot ZFS (generations + images)
- Enforced at: **Activate/Launch**
- Evidence: ZFS BE name + dataset snapshot ids bound into deployment refs
- Read: `docs/69-host-generations-bectl.md`, `docs/27-vm-storage-zfs.md`, `docs/100-deployments-are-commits.md`

### Switch atomically
- Enforced at: **Host activation**
- Evidence: generation pointer update is atomic; tentative until health gate passes
- Read: `docs/06-system-activation.md`, `docs/17-secure-activation.md`, `docs/112-health-gated-updates.md`


### Preflight hardware compatibility before switching (no remote bricks by default)
- Enforced at: **Host activation / change-set preflight**
- Evidence: `hw.inventory.receipt` + `hw.compat.report` digests recorded in the change receipt; failures block switch unless breakglass
- Read: `docs/319-hardware-inventory-and-driver-binding-as-evidence.md`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `spec/hw.inventory.receipt.schema.json`, `spec/hw.compat.report.schema.json`

### Firmware updates and UEFI variable writes are derived + receipted
- Enforced at: **Host activation / maintenance leases**
- Evidence: `fw.inventory.receipt` + `fw.update.plan`/`fw.update.receipt` (spanning reboot stages); `uefi.var.set.plan`/`uefi.var.set.receipt` for boot/capsule/secureboot variables
- Read: `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `spec/fw.inventory.receipt.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`, `spec/uefi.var.set.plan.schema.json`, `spec/uefi.var.set.receipt.schema.json`

### Rollback instantly
- Enforced at: **Host + workload rollout**
- Evidence: prior generation/closure proofs remain addressable + selectable
- Read: `docs/69-host-generations-bectl.md`, `docs/35-workload-rollout-rollback.md`

### Kernel mutation is derived and auditable (no mystery knobs)
- Enforced at: **Activate/Apply**, **Runtime drift monitoring**
- Evidence: `sysctl.plan` + `sysctl.receipt` (+ drift `sysctl.event`); `kmod.load.plan` + `kmod.load.receipt` (+ live `kmod.event`)
- Read: `docs/318-kernel-tunables-and-sysctls-as-evidence.md`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/230-lockdown-levels-and-securelevel.md`

### Breakglass is explicit, time-bounded, and receipted
- Enforced at: **Recovery / emergency operations**
- Evidence: `breakglass-grant`, `breakglass-receipt`, `breakglass-event`
- Read: `docs/236-breakglass-and-recovery-mode.md`, RFC-0168

### High-risk operations require explicit approvals (quorum if policy requires)
- Enforced at: **portals and brokers** (export, breakglass entry, networking grants, release publish, etc.)
- Evidence: `consent.request` + `consent.receipt` (digest-bound approvals)
- Read: `docs/256-consent-ux-contract.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`, `docs/107-two-person-integrity.md`

### Bind boot chain to deployed generation (Secure Boot-ready; measured boot optional)
- Enforced at: **Boot/Activation**
- Evidence: boot artifact digests recorded in the boot manifest; optional measured-boot attestation
- Read: `docs/51-secure-boot-integration.md`, `adrs/ADR-0019-tpm-optional.md`, `docs/61-channel-metadata-tuf-inspired.md`

### Limit authority (least privilege)
- Enforced at: **Every daemon and tool**
- Evidence: process topology + capability profile + restricted privileges (documented and testable)
- Read: `docs/96-process-topology.md`, `docs/49-capsicum-casper-hardening.md`, `adrs/ADR-0018-resource-limits-os-primitives.md`

### Minimize TCB
- Enforced at: **Design and packaging**
- Evidence: “control plane closure” is small and reviewable; workloads are replaceable images
- Read: `docs/23-hypervisor-centric-derivebsd.md`, `docs/94-runtime-blast-radius-contract.md`

### No mystery bytes (origin labels + quarantine metadata for inbound content)
- Enforced at: **Import/portal surfaces** (downloads, removable media, shares)
- Evidence: `content.origin` + `content.import.receipt` (plus a filesystem quarantine/origin pointer that is cache-only, not the authority)
- Read: `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/267-sanitization-portal-and-disposable-sandboxes.md`, `docs/279-usb-quarantine-and-removable-media-workflow.md`


### No stealth remote control (remote assistance is consented + visible)
- Enforced at: **Screen sharing / remote control**
- Rule: remote view/control is always portal/broker mediated, always timeboxed, always revocable, and always user-visible.
- Evidence: UI grants/receipts + a session envelope (`support.session`) when composed into a support workflow.
- Read: `docs/208-screencast-and-remote-desktop-portals.md`, `docs/291-remote-assistance-sessions-as-evidence.md`, `spec/support.session.schema.json`

### No unverified execution (exec integrity policy)
- Enforced at: **Activate/Launch**
- Evidence: `exec.integrity.receipt` (policy/plan/runtime-composition digests + backend state), plus optional `exec-verify-event` observations
- Read: `docs/289-exec-integrity-policy-and-verified-execution.md`, `docs/486-exec-integrity-authority-and-verified-execution-boundary.md`, `spec/exec.integrity.policy.schema.json`, `spec/exec.integrity.receipt.schema.json`

### Treat builders hostile
- Enforced at: **Plan→Artifact**
- Evidence: no secrets in builders; network denied; outputs verified against expected digests
- Read: `docs/91-hostile-builders.md`, `docs/92-verification-matrix.md`

---

## Notes

- Some behaviors are **policy-upgradable** (e.g., requiring attestations, transparency logs, witness rebuilders), but the default posture must remain secure without them.
- If we ever relax a default, we must do it via a **policy decision record** and make the relaxation visible in `derive explain`.

Last updated: 2026-03-07r215
