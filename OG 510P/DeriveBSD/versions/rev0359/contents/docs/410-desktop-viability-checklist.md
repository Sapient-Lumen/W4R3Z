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

Baseline boundary is now also decided: the trusted host owns composition, window-origin markers, focus policy, and trusted prompts; isolated apps cross into the desktop through remoted GUI; software-rendered or 2D guest output is acceptable workstation floor behavior; and raw host X11/DRM/render-node access plus direct guest GPU passthrough are **not** baseline workstation plumbing (see `adrs/ADR-0126-workstation-display-composition-and-gpu-boundary.md`, `docs/536-workstation-display-composition-and-gpu-boundary.md`).
The next hard cut is now made too: the workstation viability floor is **session-surface-first**, not seamless per-window host-native windows, so a compartment enters the desktop as one labeled remoted session surface and ergonomics should prefer small-role or single-app AppVMs (see `adrs/ADR-0127-workstation-remoted-session-surface-boundary.md`, `docs/537-workstation-remoted-session-surface-boundary.md`).

B still requires a coherent implementation plan for:

- the exact remoting transport / damage-tracking model for the session surface
- audio/video forwarding and screencast composition details
- IME/accessibility behavior across the boundary
- whether any future accelerated lane is worth shipping without weakening the trusted host boundary
- whether any future seamless per-window lane is worth the extra complexity
- clipboard/file movement must stay **explicit, directional, no ambient shared cross-domain sync**; the baseline is brokered transfer with typed receipts rather than ambient shared state (see `docs/538-workstation-cross-domain-datatransfer-floor.md`)
- URI opening must stay **intent-routed, compartment-preserving**; the baseline sends `http` / `https` into a designated browsing compartment, `mailto` into a designated communications compartment, keeps `file://` out of the cross-domain lane, keeps chooser/default-app UX on trusted host-managed role slots rather than arbitrary app discovery or first-open default rewrites, keeps remembered defaults in typed `intent.role.binding` state instead of desktop-registry folklore, reviews remembered-role changes through `intent.role.binding.diff` rather than raw settings blobs, leaves a durable `intent.role.binding.event` trail for remembered-role mutation evidence, keeps interactive remembered-role changes on the generic consent lane with non-`auto` approval evidence rather than ambient trusted-settings writes, and keeps non-interactive reconcile/import changes joined to `policy.decision` via `policy_decision_digest`, keeps `trigger` reserved for authority lanes rather than admin transport folklore, keeps `trigger = support-import` mutations joined back to typed import evidence via `import_receipt_digest` rather than restore-log folklore, and denies stale remembered-role writes with typed `precondition-failed` evidence instead of silently rebasing over newer state (see `docs/539-workstation-intent-routed-uri-opening-floor.md`, `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`, `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`, `docs/542-role-binding-diff-as-review-surface.md`, `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`, `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md`)
- cross-compartment document open/view/edit must stay **import-shaped first, route-shaped second**; imported files should land in bounded `document_viewing` / `document_editing` compartments rather than the host, `intent.route.receipt.import_receipt_digest` should point back to the exact `content.import.receipt` that produced the artifact, and imported foreign originals should stay **view-first** so baseline workstation behavior is **work on a copy** rather than **edit in place**; that copy act should now be typed as `content.working-copy.receipt`, allow-path edit routes should carry `working_copy_receipt_digest`, and ordinary save on that lane should stay scoped to the working-copy output rather than silently writing back to the imported source (see `docs/605-workstation-file-open-import-and-bounded-document-roles.md`, `docs/606-workstation-imported-foreign-documents-stay-view-first.md`, `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`, `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`, `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`, `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`); when those locally edited bytes should count as the next version, the official lane should produce `content.reintegrate.receipt` as an immutable successor candidate instead of letting an app or cloud adapter define source replacement implicitly, later edits should require a new candidate rather than silently mutating the old one, and if several immutable candidates exist, recency alone should not decide which one is current; explicit supersession by `supersedes_receipt_digest` should decide when one candidate displaces another, and that supersession should remain same-authoritative-origin-only while carrying `superseded_candidate_digest` so the displaced snapshot stays detached-bundle-queryable (see `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md`, `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md`)

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
- host-generation switches on B should run trusted-UI-visible hardware compatibility preflight, join any applicable `hw.support.matrix`, block on boot/display/input/storage floor failures, and require explicit consent plus a verified local recovery path for warnings rather than surprising the user after reboot (see `docs/479-hardware-compatibility-posture-by-profile.md`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`)
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

## Trusted UI floor must be typed, not vibes

B needs a small stable vocabulary for “this laptop is supported enough to trust the host UI after reboot.”
That means:

- `hw.support.matrix` should be able to declare `trusted-display`, `trusted-input`, and `boot-storage` roles for known-supported machine classes
- those positive entries should carry a typed `qualification` summary so trusted-UI support is not just a label
- that summary should include `qualification.receipt_digest` so trusted-UI-visible warnings and support bundles can point at a typed evidence object instead of vague release-team memory
- those receipts should now also carry a concrete `fresh_until` so the workstation trusted-UI floor can stop counting as fresh in a typed way instead of through vague “recently tested” claims
- those receipts should now also carry `status_effective_at`, and positive workstation support entries should only point at an `accepted` receipt instead of a historically interesting but non-current proof
- `hw.compat.report` should emit `trusted-ui-floor-risk` when those roles are only conditionally supported for the target generation
- workstation support entries that are less than fully supported should now publish typed `conditions[]` with stable `condition_id`, `reason_code`, and `required_posture` instead of burying caveats in notes; the common workstation posture answer is `trusted-ui-consent` when the machine stays within a verified recovery-capable path
- workstation trusted-UI floor claims should also publish `qualification.target_binding`; `same-release-train-and-boot-manifest` is the honest default when display/input trust depends on the exact boot/kmod lineage rather than just the broad machine class
- preflight should surface `qualification-target-mismatch` when an older workstation proof does not cover the target `release_train`, instead of collapsing that problem into a generic warning
- `hw.compat.report` should emit `support-condition-triggered` and surface `matched_condition_ids` when one of those published caveats/prerequisites is part of the review outcome
- `hw.compat.report` should emit `recovery-path-missing` when the warning posture assumes a verified local recovery path that the machine does not currently have
- `hw.compat.report` should emit `qualification-stale` when the matched workstation support claim is backed by a receipt whose `fresh_until` has elapsed or whose typed `reverify_on` trigger has landed
- `hw.compat.report` should emit `qualification-superseded` when the matched workstation proof was replaced by a newer receipt, and `qualification-revoked` when the matched proof was actively withdrawn
- workstation-grade support promotion should require `qualification.evidence_floor` to include `trusted-ui-basic` and `rollback-or-recovery` for entries that claim the trusted UI floor

Without those typed findings, workstation compatibility drift collapses back into vague “might work” warnings that humans cannot reason about.
The archive now also expects the support matrix to say whether the trusted UI floor is only `lab-validated`, merely `canary-observed`, or genuinely `release-qualified` / `field-sustained`.
When a workstation preflight matched that catalog entry, `matched_qualification_receipt_digests` should make the backing receipt visible to the consent/review surface.
Those receipts now also carry `qualification.profile_digest`, `check_results[]`, `fresh_until`, and publication-state fields such as `decision.status` / `status_effective_at`, so the consent surface can say which typed qualification standard was satisfied, when that support proof expires, and when `qualification-stale`, `qualification-superseded`, or `qualification-revoked` should replace vague “recently tested” wording.

- whether bounded drag&drop or clipboard-history lanes are worth adding later without drifting back into ambient shared state

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

Last updated: 2026-03-20r342
