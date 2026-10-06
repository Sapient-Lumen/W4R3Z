# Product profile matrix (A–D)

> Generated from `spec/examples/product.profiles.json`. Do not hand-edit; run `python3 tools/gen_product_profile_matrix.py --write`.

**Tier:** A (Core meta-doc)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, isolation, supply-chain, operability

## Defaults snapshot

| Profile | Default posture (selected knobs) |
|---|---|
| A — A) Secure fleet host (`fleet_host`) | `backups=state-replication-with-restore-drills`, `data_at_rest=encrypted-state-attested-or-brokered-unlock`, `destructive_reprovision=target-bound-digest-breakglass-or-maintenance`, `device_authority=compiled-minimal-maintenance-leased`, `dns_resolution=brokered-required-when-hostnames-appear`, `evidence=always-on`, `evidence_exports=brokered-ticketed-encrypted-external-two-person`, `firmware_updates=policy-gated`, `fuzzing=required-classes-uapi-parser-driver-zero-open-reproducible-cases-flake-triage`, `high_risk_approvals=digest-bound-role-separated-quorum`, `home_identity=host-operator-accounts-no-portable-home-default`, `installation_recovery=target-bound-additive-breakglass`, `interactive_ui=off-by-default`, `kernel_mutation=activation-first-maintenance-leased`, `network_egress=brokered-policy-derived-noninteractive`, `network_ingress=brokered-service-classes-noninteractive`, `networking=activation-first-commit-confirmed-maintenance-leased`, `operator_access=brokered-jit-cert-role-shell-escalation-separate`, `platform_provenance=measured-receipted-and-sensitive-gating`, `private_keys=brokered-nonexportable-headless-policy-gated`, `remote_assistance=brokered-tty-console-recorded-no-gui-control`, `removable_media=deny-or-quarantine-only`, `runtime=microvm-first`, `store_retention=rollback-floor-policy-gated`, `time_authority=authenticated-quorum-lkgt-required-noninteractive`, `trust_bundles=purpose-scoped-diff-gated-shadow-trust-blocking`, `updates=health-gated`, `usb_isolation=prefer-device-domain-no-host-automount`, `workload_identity=brokered-short-lived-digest-bound-headless` |
| B — B) Secure workstation (`workstation`) | `backups=exports-or-home-replication`, `data_at_rest=lost-device-default-login-bound-user-state`, `destructive_reprovision=trusted-ui-target-confirm-digest-bound`, `device_authority=portal-first-host-owned-trusted-ui-exceptions`, `dns_resolution=brokered-required`, `evidence=exportable`, `evidence_exports=user-mediated-redacted-recipient-visible-encrypted-external`, `firmware_updates=interactive-consent`, `fuzzing=required-classes-importer-broker-parser-zero-open-reproducible-cases-flake-triage`, `high_risk_approvals=trusted-ui-user-consent-first`, `home_identity=portable-home-preferred-login-mounted-no-whole-home-appvm-default`, `installation_recovery=guided-consent-encrypted-default`, `interactive_ui=on`, `kernel_mutation=activation-first-trusted-ui-maintenance`, `network_egress=brokered-consent-with-durable-policy-landing`, `network_ingress=loopback-by-default-brokered-exceptions-with-lease`, `networking=trusted-ui-local-first-commit-confirmed`, `operator_access=local-user-presence-preferred-jit-remote-admin-exceptional`, `platform_provenance=measured-exportable-user-visible`, `private_keys=brokered-nonexportable-user-presence-vault-preferred`, `remote_assistance=visible-user-mediated-view-or-control-with-lease`, `removable_media=quarantine-first-no-automount`, `runtime=appvm-first-with-host-ui-control-plane`, `store_retention=trusted-ui-visible-space-pressure-rollback-floor`, `time_authority=authenticated-preferred-visible-degraded-state-sensitive-ops-gated`, `trust_bundles=system-visible-trusted-ui-extra-roots`, `updates=health-gated`, `usb_isolation=device-domain-required-when-supported`, `workload_identity=brokered-short-lived-appvm-preferred-user-identity-separate` |
| C — C) General-purpose OS (`general_os`) | `backups=user-choice`, `compat=bounded-adapters`, `data_at_rest=encrypted-preferred-explicit-compatibility-fallback`, `destructive_reprovision=explicit-admin-or-trusted-ui-digest-bound`, `device_authority=compiled-minimal-preferred-explicit-compatibility-fallback`, `devshells=first-class`, `dns_resolution=brokered-preferred-explicit-fallback`, `evidence=local-retained-explicit-export`, `evidence_exports=brokered-preferred-ticketed-explicit-adapter-fallback`, `firmware_updates=user-choice`, `fuzzing=required-shipped-host-and-importer-classes-advisory-elsewhere`, `high_risk_approvals=single-principal-default-explicit-quorum-lane`, `home_identity=host-accounts-default-portable-home-optional`, `installation_recovery=guided-choice-explicit-destructive`, `kernel_mutation=derived-default-explicit-admin-fallback`, `network_egress=brokered-by-default-explicit-adapter-fallback`, `network_ingress=brokered-service-classes-explicit-adapter-fallback`, `networking=derived-preferred-explicit-admin-fallback`, `operator_access=local-admin-default-jit-remote-preferred-explicit-static-key-adapter`, `platform_provenance=optional-exportable-explicit-gates`, `private_keys=brokered-preferred-explicit-file-key-adapter`, `remote_assistance=brokered-explicit-lease-no-ambient-agent`, `removable_media=quarantine-first-local-fallback`, `runtime=jails-first-with-microvm-lanes`, `store_retention=pins-and-generations-explicit-admin`, `time_authority=authenticated-preferred-explicit-fallback`, `trust_bundles=system-preferred-explicit-local-override`, `updates=transactional`, `usb_isolation=prefer-device-domain-fallback-to-local-policy`, `workload_identity=brokered-preferred-explicit-static-token-adapter` |
| D — D) Appliance factory / regulatory (`appliance_factory`) | `backups=replication-and-restore-drills`, `data_at_rest=encrypted-production-state-attested-or-quorum-maintenance-unlock`, `destructive_reprovision=offline-signed-authority-plus-reset-marker`, `device_authority=compiled-minimal-sealed-offline-maintenance`, `dns_resolution=brokered-or-none-fixed-policy`, `evidence=bundled-and-redacted`, `evidence_exports=minimal-redacted-encrypted-two-person-transparency-required`, `firmware_updates=offline-staged`, `fuzzing=approved-target-set-zero-open-production-cases-retained-corpora`, `high_risk_approvals=offline-oob-role-separated-quorum`, `home_identity=no-human-homes-in-production-maintenance-identities-separate`, `installation_recovery=target-bound-offline-resettable`, `kernel_mutation=preload-only-lockdown-offline-maintenance`, `network_egress=deny-by-default-offline-or-approved-brokered`, `network_ingress=deny-by-default-offline-or-approved-brokered-service`, `networking=sealed-offline-windowed-commit-confirmed`, `operator_access=maintenance-window-jit-cert-quorum-no-standing-admin-keys`, `platform_provenance=measured-retained-and-production-gating`, `private_keys=offline-or-hsm-quorum-nonexportable`, `remote_assistance=disabled-by-default-maintenance-only-recorded`, `removable_media=offline-ingest-quarantine-first`, `runtime=sealed-workload-images`, `store_retention=offline-auditable-rollback-floor`, `time_authority=offline-bounded-bootstrap-signed-time-or-authenticated-quorum`, `trust_bundles=fixed-purpose-offline-quorum-bundles`, `updates=offline-bundles`, `usb_isolation=device-domain-or-ingest-station`, `workload_identity=brokered-attested-short-lived-no-static-production-secrets` |

## Required invariants

### A — A) Secure fleet host (`fleet_host`)
- Atomic activation + rollback
- Receipts/evidence for privileged ops
- Remote recovery story (break-glass, logged)
- Strong supply-chain verification by default
- Local removable-media workflows remain explicit, receipted, and quarantine-shaped
- Outbound network authority remains policy-derived and non-interactive by default
- Inbound exposure remains policy-derived and non-interactive by default
- Support sessions stay brokered, receipted, and console/TTY-shaped rather than becoming ambient GUI remoting
- Private-key use stays brokered, non-exportable, and headless/policy-gated by default
- Human state stays separately governed from workload state; operator homes are exceptional and login-bounded rather than ambient
- State datasets have receipted replication and periodic restore drills; full-host image backups are not the primary recovery contract
- Mutable state remains encrypted by default; unattended unlock stays attested or brokered rather than image-baked
- Evidence export stays brokered, ticket-shaped, and encrypted for external recipients; high-risk boundary expansion requires stronger review
- Operator access stays JIT/leased and revocable; escalation remains separate from login rather than hiding in standing credentials.
- Expiry-sensitive host gates use authenticated time with quorum/LKGT posture by default; degraded time stays explicit and non-interactive rather than waived silently.
- Measured platform posture remains receipted and can gate sensitive admissions (identity issuance, secret release, rollout, or recovery) by policy rather than by dashboard folklore.
- Service/workload authentication stays short-lived, receipted, and digest-bound by default; static shared tokens remain out of bounds except via explicit reviewed adapters.
- Firmware and UEFI trust-root changes require explicit plans, maintenance authority, post-reboot receipts, and health/promotion gates; stage is not success.
- Update offer/finalization for A stays health-gated, rollout-aware, and receipted; signed channels remain byte authority and local health/promotion gates remain authoritative for commit.
- Install/recovery on A stays target-device-bound and additive by default; destructive disk mutation requires breakglass/maintenance approval and recovery media remains verifiable and ready.
- High-risk shared-trust mutations stay digest-bound and role-separated by default; publish/trust-root/breakglass approvals require distinct principals and emit auditable receipts.
- Kernel mutation on A stays activation-first and receipted: boot tunables are generation-bound, risky runtime sysctl writes require maintenance leases/receipts, and module loading is preload-first with lockdown after apply.
- Device authority stays compiled-minimal and lease-shaped: raw block/input/capture/packet nodes do not appear ambiently in ordinary service compartments, and any expansion is receipted and reviewable.
- Evidence collection on A stays always-on, bounded, and policy-governed; richer diagnostics or wider export scope remains explicit and receipted rather than ambient.
- Host network topology on A stays activation-first and commit-confirmed: links/addresses/routes/pf root state are planned and receipted, risky live mutation requires maintenance leases, and remote-brick rollback remains ready.
- Trust bundles remain explicit, purpose-scoped, diff-gated artifacts; official fleet lanes block shadow trust unless explicitly waived.
- GC on A preserves an explicit bootable rollback floor and never silently trades away cohort rollback safety for reclaimed bytes.

### B — B) Secure workstation (`workstation`)
- Clear trusted UI boundary / secure attention path
- Portal-mediated file/clipboard/device flows
- Data-at-rest protection appropriate for lost-device threat model
- Explainers for 'why does this app have access?'
- No trusted-plane automount for removable media; USB/media flows stay quarantine-first
- Network prompts create leases or durable policy edits rather than invisible one-off exceptions
- General interactive apps stay loopback-only unless a lease or policy grants broader exposure
- No ambient LAN/WAN listeners for general interactive apps; inbound sharing/support stays brokered and timeboxed
- Remote assistance stays visible, secure-attention-gated for control, and revocable by lease
- Human key use stays user-presence-gated and risky apps get crypto operations rather than raw key bytes by default
- Human home state unlocks on login and can relock/unmount on logout; whole-home AppVM mounts stay exceptional, explicit, and leased
- User recovery remains explicit and exportable; when replication exists it is scoped to home/state datasets rather than ambient whole-device cloning
- Ordinary private user state stays login-bounded for the lost-device threat model; boot-available state is minimal and explicit
- Evidence sharing stays user-mediated, recipient-visible, and redaction-aware; remembered authority lands in leases/policy rather than ambient upload helpers
- Local admin/elevation stays secure-attention and user-presence gated; remote shell admin, if it exists, is exceptional and leased rather than standing.
- Time health is visible to the human; expiry-sensitive operations gate on authenticated time or surface explicit degraded state rather than silently proceeding.
- Measured platform posture is visible/exportable and may gate sensitive operations, but ordinary local use does not silently depend on remote attestation infrastructure.
- Workload identity for apps/dev services stays separate from human login/account authority; static cloud/API token sprawl is not the default compatibility lane.
- Firmware and Secure Boot trust-root changes are trusted-UI-visible, consented, receipted, and power-safety checked; stage is not success.
- Host-generation update apply/reboot stays trusted-UI-visible, health/rollback-aware, and leased or consented when disruptive; silent unattended finalization is not the workstation baseline.
- Install/recovery on B stays trusted-UI-guided: destructive disk mutation requires explicit disk identity confirmation, encrypted-root posture is the default, and a verified local recovery path remains available.
- Ordinary personal-risk actions stay trusted-UI-visible and user-consented; shared-trust/org-wide mutations never hide behind the same prompt surface and require an explicit admin lane when enabled.
- Kernel mutation on B stays activation-first and trusted-UI-mediated: boot tunables are generation-bound, risky runtime sysctl/module changes require visible consent or maintenance workflow, and silent background kernel mutation is out of bounds.
- General interactive apps do not get ambient raw host device-node authority by default; HID/camera/mic/block access stays portal-first or trusted-UI-mediated and reviewable.
- Evidence on B stays locally useful and user-exportable with trusted-UI-visible redaction/share; richer capture or upload is explicit rather than ambient.
- Host topology changes on B stay trusted-UI-visible and commit-confirmed: local networking remains humane, but exposure-expanding or remote-risky mutations are rollbackable and receipted.
- System trust remains visible and reviewable; extra roots land through trusted UI and silent shadow trust stays out of bounds by default.
- GC on B is space-aware but preserves current/recent rollback points and explicit pins unless the human reviews a stronger cleanup in trusted UI.

### C — C) General-purpose OS (`general_os`)
- Derive pipeline remains the primary interface
- Adapters remain killable and tiered
- Explainability of system state remains intact
- Removable-media use remains explicit and quarantine-aware even when using local fallback policy
- Legacy networking fallbacks stay explicit, adapter-shaped, and reviewable
- Non-loopback listeners stay explicit, brokered, and adapter-shaped when needed
- Broader service exposure stays explicit and reviewable rather than ambient
- Remote assistance stays explicit, leased, and reviewable rather than ambient
- Brokered/non-exportable key use remains preferred; file-backed keys stay an explicit adapter fallback
- Human home state remains explicit and explainable; compatibility defaults must not silently redefine workstation whole-home sharing rules
- Backup choice stays explicit and reviewable; Derive-managed backup lanes remain receipted rather than ambient sync folklore
- Encryption stays preferred and explainable; compatibility fallbacks remain explicit and do not silently inherit into stricter product shapes
- Evidence export remains reviewable and receipted; compatibility adapters stay explicit rather than becoming the ambient default
- Remote admin stays explicit and reviewable; JIT/leased access is preferred and static-key compatibility remains adapter-shaped.
- Authenticated time remains preferred and explainable; compatibility fallback stays explicit and must not silently redefine stricter product-shape defaults.
- Optional attestation gates stay explicit and reviewable; compatibility/default installs do not silently depend on TPM/verifier presence.
- Workload identity remains the preferred default for derived services, while static-token or file-credential compatibility stays explicit, killable, and reviewable.
- If firmware tooling exists on C, outcomes stay planned/receipted and classic vendor utilities remain explicit adapters rather than hidden ambient mutation lanes.
- Transactional update viability stays standalone on C; stronger rollout, health-gate, or offline-bundle lanes remain explicit, killable, and do not become hidden coordinator dependencies.
- Install/recovery on C keeps guided and compatibility paths explicit, keeps encryption preferred with explicit fallback, and never hides destructive repartitioning behind ambient convenience.
- Ordinary local admin/install/update flows remain viable without central approver reachability; quorum and separation-of-duties stay explicit optional policy or adapter lanes.
- Kernel mutation on C remains derive-managed by default, while explicit local-admin fallback stays possible; risky sysctl or module changes remain reviewable/receipted and do not become ambient service authority.
- Compiled-minimal and mediated device authority remain preferred; raw device-node compatibility stays explicit, local, and reviewable rather than ambient.
- Evidence on C stays local-retained and explicit-export by default; remote collectors, richer tracing, and support agents remain optional, killable, and never hidden prerequisites.
- Host network topology on C prefers derived plans and receipts, while explicit local-admin fallback remains viable and reviewable; compatibility paths do not silently redefine A/B/D defaults.
- Governed system trust remains preferred; explicit local CA / app-specific trust overrides stay adapter-shaped rather than ambient baseline behavior.
- GC on C keeps pins and recent generations understandable/queryable by default; aggressive reclamation is explicit local-admin policy, not ambient surprise.

### D — D) Appliance factory / regulatory (`appliance_factory`)
- Airgap-friendly update and provenance workflow
- Long-term rebuildability / source availability plan
- Strict admission gates and stable audit evidence exports
- Deterministic retention / evidence redaction controls
- Offline/removable-media ingest stays quarantine→promote with retained evidence
- Outbound network use is absent or explicitly approved; prompts are not the authority model
- Inbound exposure is absent or explicitly approved; prompts are not the authority model
- Inbound exposure is absent by default or explicitly approved through stable brokered service policy
- Remote assistance is absent by default in production images or explicitly enabled only in maintenance-shaped workflows with retained evidence
- Production/manufacturing key use stays offline or hardware-backed and quorum-gated by default
- Human maintenance identity stays separate from production workload state and is absent from production-image defaults
- State recovery claims are backed by receipted replication and recurring restore drills
- Production/factory state remains encrypted by default; unattended or maintenance unlock stays attested, brokered, or quorum-shaped rather than image-secret convenience
- Evidence export remains minimal/redacted, encrypted, and strongly approved; high-assurance lanes retain transparency records for the act of sharing
- Maintenance/operator access stays maintenance-window-shaped, JIT, and strongly approved; shipped standing admin keys remain out of bounds.
- Offline/bootstrap time remains bounded and evidentiary; signed time or authenticated quorum replaces internet dependency without collapsing expiry/freshness checks.
- Measured platform posture is retained and can gate production enrollment, maintenance access, or secret release by default; weakening those gates requires explicit review.
- Production/service authentication stays short-lived and brokered by default; shipped static shared secrets remain out of bounds and stronger admissions may gate issuance.
- Firmware and UEFI trust-root changes for D use approved offline-staged artifacts, strong review/approval, and retained post-reboot receipts; live convenience flashing is out of bounds for production posture.
- Production update delivery for D stays offline-bundle or mirror-kit shaped with quarantine→promote, retained receipts, and local approval policy rather than live upstream reachability.
- Install/recovery on D stays target-device-bound and offline-capable by default; destructive reprovisioning uses signed reset bundles/markers with retained approval/receipts and verified recovery media remains available.
- Production publish/trust-root/reset/exposure-expanding lanes stay digest-bound, role-separated, and quorum-gated by default; offline or OOB approval remains workable.
- Kernel mutation on D stays preload-only and lockdown-shaped in production: boot tunables are generation-bound, required modules are preloaded, and runtime sysctl/kmod mutation is limited to offline or strongly approved maintenance workflows with receipts.
- Production/factory device authority stays compiled-minimal and sealed: raw block/input/capture/debug nodes are absent by default and stronger expansion is offline or strongly approved with receipts.
- Evidence on D stays bundle-oriented, minimal/redacted, and retention-bounded by default; live diagnostic streaming or open-ended telemetry remains absent from production posture unless explicitly approved.
- Production topology on D stays sealed and maintenance-window-shaped: links/addresses/routes/pf root state do not drift via ad-hoc shell edits, and exposure-expanding changes require approved rollbackable workflows with retained receipts.
- Production/manufacturing trust roots remain fixed-purpose, digest-bound, and offline/strongly-approved; live CA edits are not the production default.
- Destructive reprovision on D stays offline-capable, target-device-bound, and digest-bound, with signed reset authority plus physical or attended-station presence and retained receipts.
- GC on D preserves approved rollback and audit floors with retained receipts and never silently prunes required production recovery coverage.

## Forbidden by default

### A — A) Secure fleet host (`fleet_host`)
- Desktop session on host
- Unreceipted mutable config
- Opaque binary update channels
- Automount of removable media into host
- Interactive outbound network approvals on the host
- Interactive inbound exposure approvals on the host
- Ad-hoc permanent firewall openings during incidents
- Stealth or always-on remote support agents on the host
- Long-lived exportable private-key files on hosts or workloads
- Image-baked static unlock keys for host mutable state
- Ad-hoc external evidence export outside brokered export policy / receipt lanes
- Standing operator SSH keys or permanent bastion access on hosts
- Silent unauthenticated time fallback for expiry-sensitive host gates
- Routine destructive disk reprovisioning without target-device identity and breakglass/maintenance approval
- Single-principal self-approval for release publish, trust-root mutation, or destructive breakglass on fleet hosts
- Unbounded or unreceipted always-on diagnostic capture outside compiled budget / policy lanes
- Unconfirmed live host-topology mutation that can strand remote nodes or silently broaden exposure
- Embedded or per-app trust stores in official fleet lanes that bypass governed trust bundles

### B — B) Secure workstation (`workstation`)
- Implicit ambient authority across apps
- Direct device passthrough without policy + receipts
- General-purpose app execution on host outside trusted UI / broker set
- Automount of removable media into trusted host UI plane
- Ambient direct-socket egress for general interactive apps
- Ambient non-loopback listeners for general interactive apps
- Ambient LAN/WAN listeners for general interactive apps
- Stealth remote view/control outside the trusted UI path
- Raw exportable private-key files for general interactive apps by default
- Whole portable home mounted into general interactive AppVMs by default
- Image-baked or ambient file-backed unlock keys for ordinary user state
- Invisible remembered export/support upload authority outside trusted UI lease / policy paths
- Standing remote shell admin for workstation management by default
- Invisible unauthenticated time fallback for expiry-sensitive operations
- Long-lived cloud/API tokens for general interactive apps by default
- Silent unattended firmware or Secure Boot trust-root updates outside trusted UI consent / maintenance path
- Silent unattended host-generation apply/reboot outside trusted UI policy / maintenance path
- Destructive reinstall or repartition on the wrong disk via weak/no trusted-UI disk identity confirmation
- Silent background kernel-mutation writes or module loads outside trusted UI / maintenance path
- Ambient raw host device nodes for general interactive apps outside portal or trusted-UI-mediated exception paths
- Ambient background diagnostic upload or always-on high-detail support capture outside trusted UI / policy lanes
- Silent host-topology mutation that can strand the machine or silently broaden exposure outside trusted UI / confirm window
- Silent enterprise / custom trust-root injection outside trusted UI / review path
- App-shipped shadow trust stores for general interactive apps by default

### C — C) General-purpose OS (`general_os`)
- Forked 'classic' configuration pathways that bypass the derive pipeline
- Ambient always-on remote support agents outside brokered or adapter lanes
- Ambient unrestricted private-key agents or silent file-key sprawl
- Ambient remote admin static-key access outside an explicit adapter lane
- Mandatory central approver dependency for ordinary local admin, install, or update flows
- Ambient off-box diagnostic collection or support-agent dependency by default

### D — D) Appliance factory / regulatory (`appliance_factory`)
- Network-dependent updates without mirror-kit fallback
- Undocumented debug backdoors
- Unreceipted removable-media ingest into trusted update or evidence lanes
- Interactive outbound network approvals in production or evidence lanes
- Interactive inbound exposure approvals in production or evidence lanes
- Interactive exposure approvals in production or evidence lanes
- Ambient or always-on remote support agents in production images
- Exportable production or manufacturing private-key files in shipped/factory images
- Shipped production or factory images with static file-backed unlock keys
- Opaque or convenience evidence export to external recipients without minimal/redacted policy, encryption, and approval
- Standing vendor or admin keys in factory or shipped images
- Ignoring freshness/expiry because the site is offline or air-gapped
- Shipped production or factory images with static shared service/API credentials
- Live network-fetched firmware or Secure Boot trust-root mutation in production outside approved offline staging / maintenance approval
- Factory or production destructive reprovisioning from ad-hoc live rescue media without signed reset authority or target-device binding
- Self-approval or same-principal decide-and-ship for production publish, trust-root, reset, or exposure-expanding mutations
- Runtime kernel mutation in production outside approved preload/lockdown or offline maintenance workflow
- Ambient live production diagnostic streaming or open-ended vendor telemetry in shipped/factory images
- Ad-hoc live production topology mutation outside approved maintenance window / rollback path
- Live production trust-root injection or ad-hoc CA edits outside approved offline bundle / quorum lane

## Notes

- Profiles are compilation targets for defaults and gates; they are not forks.
- Letter aliases A–D are defined in `spec/product.profile_aliases.json` (tools normalize to canonical ids).
- Features should declare **Tier** and applicable **Profiles** in their doc metadata.

Last updated: 2026-03-22r409
