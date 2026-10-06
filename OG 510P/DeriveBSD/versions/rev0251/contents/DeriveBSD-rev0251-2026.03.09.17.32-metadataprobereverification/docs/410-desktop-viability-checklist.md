# Desktop viability checklist (profile B must remain real)

**Tier:** C (Optional lane)  
**Profiles:** B
**Pillars:** isolation, operability
**Patterns:** Registry→Diff→Gate  

DeriveBSD must keep “secure workstation” (profile **B**) viable even if v0 ships as a fleet host.
This checklist exists to prevent accidental design choices that make B impossible later.

This is **not** a desktop roadmap. It is a constraint list.

Baseline boundary: the workstation host remains the trusted UI / broker control plane, and general interactive apps are AppVM-first (see `adrs/ADR-0047-workstation-host-ui-and-appvm-boundary.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`).

## Trusted UI boundary

- define a **trusted UI / secure attention** path (how the user knows “this prompt is real”)
- define what is in the trusted computing base for UI:
  - compositor? small “trusted shell”? minimal window manager?
- define how prompts are mediated when apps are isolated (AppVMs / microVMs)

## Portals / powerbox (mandatory for B)

Portal-mediated access for:

- file open/save
- clipboard
- URL handling
- notifications
- screenshots/recording
- printing
- device access (USB, cameras, microphones)
- secrets (credential prompts)

Rules:

- no ambient “read the whole home directory” by default
- portal decisions must be receipted and explainable (“why does app X have access?”)

## GUI transport across isolation boundaries

- Wayland/X11 strategy (and the security implications)
- display protocol boundary (host compositor vs guest compositor)
- GPU acceleration boundary (software fallback vs mediated GPU)
- input method boundary (HID, IME, key logging risk)

## Device mediation

Baseline posture is now decided: no trusted-plane automount, quarantine-first removable-media flows, and device-domain use when hardware supports it cleanly (see `adrs/ADR-0048-removable-media-and-usb-posture-by-profile.md`, `docs/458-removable-media-and-usb-posture-by-profile.md`).

The raw-device boundary is now also decided: general interactive apps on B should not inherit ambient raw host `/dev` authority; camera/mic/HID/block access should stay portal-first or trusted-UI-mediated, with explicit exception lanes when compatibility really demands them (see `adrs/ADR-0066-device-authority-posture-by-profile.md`, `docs/476-device-authority-posture-by-profile.md`).

B still requires a coherent implementation plan for:

- USB/HID pass-through (policy-gated, time-bounded leases)
- webcam/mic access (indicator lights, revocation UX)
- Bluetooth
- smart cards / FIDO keys
- printing/scanning

## “Daily ergonomics” integration points

- networking UX (VPNs, Wi‑Fi secrets) without leaking ambient authority; app-facing egress remains brokered and trusted-UI prompts must land in leases/policy (see `docs/459-outbound-network-posture-by-profile.md`)
- risky host-topology changes should stay trusted-UI-visible and commit-confirmed so laptops do not get stranded by invisible route/firewall edits (see `docs/477-network-topology-posture-by-profile.md`, `docs/322-network-topology-and-firewall-as-derived-operations.md`)
- host-generation switches on B should run trusted-UI-visible hardware compatibility preflight, block on boot/display/input/storage floor failures, and require explicit consent plus a verified local recovery path for warnings rather than surprising the user after reboot (see `docs/479-hardware-compatibility-posture-by-profile.md`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`)
- trustworthy-time UX should keep degraded time visible in the trusted UI; expiry-sensitive operations should gate or ask for repair rather than silently trusting weak time (see `docs/468-trustworthy-time-posture-by-profile.md`, `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`)
- firmware updates on B should remain trusted-UI-visible, consented, and power-safety checked; silent unattended firmware or Secure Boot trust-root mutation is not acceptable workstation baseline behavior (see `docs/471-firmware-update-posture-by-profile.md`, `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`)
- trust roots on B should stay visible and reviewable in the trusted UI; enterprise/developer extra roots are allowed, but silent app-local or shell-folklore CA injection is not the workstation baseline (see `docs/480-trust-bundle-posture-by-profile.md`, `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`)
- measured/attestation posture should be visible and exportable for support or verification, but ordinary local use should not become a surprise hard-fail when remote verifier lanes are absent; attestation gates on B belong to sensitive operations and reviewable policy (see `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md`)
- local developer servers and remote/share workflows should stay loopback-first; non-local listeners for general apps must go through trusted-UI-mediated leases/policy instead of ambient firewall edits (see `docs/460-inbound-listen-posture-by-profile.md`)
- remote assistance must stay a visible, trusted-UI-mediated lane; remote control requires secure attention and support sessions must be leased/revocable rather than ambient helpers (see `docs/461-remote-assistance-posture-by-profile.md`, `docs/291-remote-assistance-sessions-as-evidence.md`)
- evidence on B should stay locally useful and user-exportable, but richer capture or external sharing must remain trusted-UI-visible; ambient background diagnostic uploaders are not acceptable workstation baseline behavior (see `docs/478-evidence-collection-posture-by-profile.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/302-structured-diagnostics-inspect-trees.md`)
- password manager / secret store (brokered capabilities)
- human key use (SSH/GPG/code-signing/passkey-adjacent flows) should prefer split-key vaults or platform keystores; risky apps should request crypto ops instead of holding raw private-key bytes by default (see `docs/462-private-key-and-crypto-op-posture-by-profile.md`)
- local admin/elevation should prefer secure-attention / user-presence-gated flows; remote shell admin should remain exceptional and leased rather than becoming a standing workstation default (see `docs/467-operator-access-posture-by-profile.md`, `docs/311-operator-access-leases-and-ssh-certs.md`)
- trusted-UI user consent should remain the default for personal-risk actions on B; org/shared-trust mutations must use an explicit admin lane instead of smuggling quorum prompts into ordinary desktop UX (see `docs/474-high-risk-approval-posture-by-profile.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`)
- service/dev auth on B should prefer short-lived workload identity for AppVMs or local service-like tools, while human login/OIDC/account authority stays separate; general interactive apps should not normalize long-lived cloud/API tokens by default (see `docs/470-workload-identity-and-credential-issuance-posture-by-profile.md`, `docs/181-workload-identity-and-secretless-deploys.md`)
- home identity / portable-home UX: login-bounded unlock, relock/unmount on logout, and no whole-home mount into general interactive AppVMs by default (see `docs/463-human-identity-and-home-state-posture-by-profile.md`)
- lost-device posture should be real: ordinary private user state unlocks with the human, while boot-available state stays minimal and explicit (see `docs/465-data-at-rest-posture-by-profile.md`, `docs/409-zfs-encryption-and-key-management.md`)
- updates/rollback UX that non-experts can understand, with trusted-UI-visible apply/reboot finalization and no surprise host-generation changes by default (see `docs/472-update-delivery-and-release-posture-by-profile.md`, `docs/112-health-gated-updates.md`)
- install/recovery UX should keep destructive storage changes trusted-UI-mediated with explicit disk identity confirmation, encrypted-root default for ordinary private state, and a local verified recovery path (see `docs/473-installation-and-recovery-posture-by-profile.md`, `docs/309-installation-and-recovery-as-derived-operations.md`)
- host kernel mutation should stay activation-first and trusted-UI-visible on B: risky sysctl/debug changes or runtime module loads belong to visible maintenance workflows, not background helpers or support agents (see `docs/475-kernel-mutation-posture-by-profile.md`, `docs/318-kernel-tunables-and-sysctls-as-evidence.md`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`)
- backups and portable homes UX should prefer explicit exports or home-area replication rather than ambient whole-device clone assumptions (see `docs/464-backup-and-restore-posture-by-profile.md`, `docs/463-human-identity-and-home-state-posture-by-profile.md`)

## Forensics and support bundles (user-safe)

- support bundles must avoid leaking secrets
- user-controlled redaction + deterministic export
- export/share UI should keep recipient and redaction posture visible rather than growing invisible remembered upload helpers (see `docs/466-export-boundary-posture-by-profile.md`)
- “explain my system state” should work without privileged spelunking

## How to keep this viable now (even before desktop work)

When making core decisions, ensure we do not foreclose:

- portal services as capability-brokered ops
- per-app isolation boundaries that can still render UI safely
- a stable policy vocabulary for “user intent” approvals

Last updated: 2026-03-06r209
