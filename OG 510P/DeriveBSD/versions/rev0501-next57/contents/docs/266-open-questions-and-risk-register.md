# Open questions and risk register (v0)

This archive is intentionally ambitious. To avoid “design tourism”, we keep a short list of the highest-leverage unknowns.

When an item moves from “open” → “decided”, capture it in an ADR.

## Conventions

- Each numeric heading is an item.
- If an item is decided, append the tag **[DECIDED]** to the heading and include an ADR link in the section.
- Generated surfaces (context pack + risk register index) treat **[DECIDED]** items as historical context and exclude them from the "top open questions" list.

## 1) Package recipe surface: how much language is allowed? [DECIDED]

The archive now fixes the package-recipe authority boundary in `adrs/ADR-0289-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md`:

- no general-purpose evaluator becomes part of the Derive core or the blessed in-tree package recipe surface
- the only native follow-on lane under consideration is the restricted typed pipeline lane from `rfcs/RFC-0091-declarative-image-pipelines.md`
- richer recipe ecosystems (ports/pkgsrc importers, apko/melange bridges, Starlark/Nix-like authoring, shell-heavy external systems) remain adapter/compiler lanes that must emit canonical Derive objects and evidence instead of becoming hidden product semantics
- shell may still exist inside bounded tool capsules or compiled plan steps, but it stays backend execution detail rather than reviewed recipe authority

What remains open is implementation detail, not the language boundary:

- the exact restricted step vocabulary and schema now that `adrs/ADR-0290-native-restricted-pipelines-reject-generic-run-steps-and-stay-registry-backed.md` has already ruled out a generic authoritative `run` / `script` escape hatch
- the exact adapter/import depth worth supporting
- the exact explain/provenance surfaces for compiled recipe steps

Risk: without this boundary, a rich language or imported recipe runtime becomes the real product and the typed Spec/Plan objects become a veneer.

See: `adrs/ADR-0289-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md`, `adrs/ADR-0290-native-restricted-pipelines-reject-generic-run-steps-and-stay-registry-backed.md`, `docs/699-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md`, `docs/700-native-restricted-pipelines-reject-generic-run-steps-and-stay-registry-backed.md`, `rfcs/RFC-0091-declarative-image-pipelines.md`, `docs/134-declarative-image-pipelines-apko-melange.md`, `docs/83-evaluator-minimalism.md`, `docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md`.

## 2) Cross compilation and multi-arch closures [DECIDED]

The archive now fixes the cross-compilation platform-identity boundary in `adrs/ADR-0291-cross-compilation-platform-identity-stays-build-host-target-shaped-and-not-store-path-encoded.md`:

- store paths stay content-addressed and digest-first rather than becoming a target-triple namespace
- platform truth stays on explicit `build_platform` / `host_platform` / optional `target_platform` metadata
- target triples, GNU-config strings, and FreeBSD `TARGET` / `TARGET_ARCH` stay adapter aliases rather than the authority object
- runtime closure and activation bind `host_platform`, so build-host tools do not silently become runtime closure authority

What remains open is implementation detail, not the authority boundary:

- exact cache/index projections for platform-role metadata
- exact compat/emulation adapter semantics for foreign-runtime lanes
- exact migration breadth for older schemas that still carry simpler platform selectors

Risk: subtle non-reproducible builds and broken caches.

See: `adrs/ADR-0291-cross-compilation-platform-identity-stays-build-host-target-shaped-and-not-store-path-encoded.md`, `docs/701-cross-compilation-platform-identity-stays-build-host-target-shaped-and-not-store-path-encoded.md`, `docs/03-store.md`, `docs/90-closure-proof.md`, `docs/526-derived-base-sets-and-pkgbase-adapter-boundary.md`, `spec/platform.identity.schema.json`, `spec/platform.roles.schema.json`.

## 3) Kernel/userland split: pkgbase vs “derive base” [DECIDED]

The archive now fixes the **base-system authority boundary** in `adrs/ADR-0116-derived-base-sets-and-pkgbase-adapter-boundary.md`:

- `base.set` is the canonical native base artifact.
- `pkgbase` remains an explicit adapter lane, not the source of truth.
- The native v0 split stays intentionally small: `kernel`, `userland`, `toolchain`.
- Host generations and patchsets bind to `base.set` digests rather than to pkg metadata.

What remains open is implementation detail, not the authority boundary:

- the exact bootstrap path for the first trusted native toolchain/base sets,
- the final per-file ownership map inside each set,
- and whether future optional native classes (for example `debug` or `rescue`) are worth the entropy cost.

Risk: if this boundary drifts, base becomes a special snowflake lane again and adapter/package folklore quietly becomes deployment authority.

See: `adrs/ADR-0116-derived-base-sets-and-pkgbase-adapter-boundary.md`, `docs/526-derived-base-sets-and-pkgbase-adapter-boundary.md`, `docs/111-packaged-base-pkgbase.md`, `rfcs/RFC-0079-packaged-base-and-sets.md`.

## 4) MicroVM orchestration boundary [DECIDED]

This is now a decided boundary in v0:

- `derive-vmmd` is **host-local** and owns the local authority boundary (verify → enforce → receipt).
- Any distributed scheduling/reconciliation is **external** and must integrate via a killable adapter lane.

ADR:
- `adrs/ADR-0040-microvm-orchestration-host-local.md`

Risk: we build Kubernetes accidentally.
See: v0 cutline discipline (`docs/401-v0-cutline-and-feature-tiers.md`).

## 5) Update distribution strategy [DECIDED]

The product-shape default is now decided in `adrs/ADR-0062-update-delivery-and-release-posture-by-profile.md`:

- A (`fleet_host`) defaults to `health-gated`: signed channels stay byte authority, while rollout/assignment/finalization remain policy-derived and receipted.
- B (`workstation`) also defaults to `health-gated`, but apply/reboot finalization must stay trusted-UI-visible and deferrable rather than silently disruptive.
- C (`general_os`) defaults to `transactional`: atomic apply/rollback is baseline, while rollout graphs, assignment services, and offline bundle lanes remain optional rather than hidden prerequisites.
- D (`appliance_factory`) defaults to `offline-bundles`: approved offline bundles or mirror kits with quarantine→promote import are the normal production delivery path.

What remains open is implementation detail, not the product-default boundary:

- exact key-rotation and operator-ceremony ergonomics,
- the concrete mirror-kit / offline-bundle envelope,
- and the depth/budget of long-term source-retention policy.

Risk: without a stable default, fleets drift toward opaque updater folklore, workstations inherit surprise reboots, general-purpose installs become coordinator-dependent by accident, and regulated/offline deployments quietly depend on live channels they cannot actually govern.

## 6) Human-scale debugging handoff contract [DECIDED]

The archive now fixes the **official support handoff contract** in `adrs/ADR-0071-support-bundle-contract-and-timeline-first-handoff.md`:

- the default one-page orientation surface is a typed `incident.timeline`,
- the official support handoff is `incident.timeline` + `incident.bundle` + `bundle.plan` + `bundle.payload.manifest` + `bundle.build.receipt`,
- the canonical payload format is `tar.zst`, while `zip` remains an explicit compatibility adapter,
- and raw dumps remain explicit opt-in rather than the default support posture.

What remains open is implementation detail, not the support-handoff contract:

- timeline rendering UX,
- exact bundle-min selection heuristics,
- and the concrete CLI / service implementation path for generating the handoff objects.

Risk: without a stable handoff contract, the archive drifts back to mystery tarballs, ticket comments, and non-reproducible support scripts even if the underlying evidence model is strong.

See: `adrs/ADR-0071-support-bundle-contract-and-timeline-first-handoff.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/419-incident-timelines-as-derived-artifacts.md`, `docs/253-bundle-plans-and-deterministic-exports.md`.

## 7) Desktop/interactive workload stance (if any) [DECIDED]

Decision:
- profile **B** does **not** treat the host as a general-purpose desktop app surface
- the host is the trusted UI / broker control plane
- general interactive apps are AppVM-first, with host integration through portals/brokers/leases

This narrows the workstation stance without pretending the full desktop stack is solved.
Remaining implementation questions (GUI transport, GPU, audio/video details, some device mediation details) stay open elsewhere.

See: `adrs/ADR-0047-workstation-host-ui-and-appvm-boundary.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`, `docs/268-desktop-appvms-and-portalized-apps.md`.

Risk: if this boundary is forgotten or softened, the workstation story collapses back into ad-hoc host execution and B diverges from A/D.

## 8) Store growth + GC + long-lived fleets [DECIDED]

The product-shape default is now fixed in `adrs/ADR-0086-store-retention-and-gc-posture-by-profile.md`:

- A (`fleet_host`) defaults to `rollback-floor-policy-gated`: preserve a hard bootable rollback floor first, then reclaim bytes through dry-run-first, policy-shaped GC.
- B (`workstation`) defaults to `trusted-ui-visible-space-pressure-rollback-floor`: space-pressure cleanup can be humane, but obvious rollback points and pins stay protected unless the human reviews a stronger cleanup.
- C (`general_os`) defaults to `pins-and-generations-explicit-admin`: roots/pins/generations remain explicit, while stronger cleanup stays a viable explicit local-admin action.
- D (`appliance_factory`) defaults to `offline-auditable-rollback-floor`: production cleanup preserves approved rollback/audit windows and stays maintenance/offline/receipted.

What remains open is implementation detail, not the product-default boundary:

- exact numeric rollback floors for specific host classes,
- exact workstation cleanup UX under disk pressure,
- cohort-wide fleet rollback budgeting heuristics,
- and the exact archival budget for long-lived regulated evidence.

Risk: fleets silently fall out of rollback coverage.

See: `adrs/ADR-0086-store-retention-and-gc-posture-by-profile.md`, `docs/496-store-retention-and-gc-posture-by-profile.md`, `docs/426-store-gc-plans-and-receipts.md`, `docs/404-zfs-boot-environments-as-system-generations.md`.

## 9) [DECIDED] Human identity + home data model (portable homes vs host accounts)

The product-shape default is now fixed:
- A uses host operator accounts when needed; portable homes are not the fleet-host default.
- B prefers portable, login-mounted home areas and rejects whole-home mounts into general interactive AppVMs by default.
- C keeps classic host accounts as the broad-compat default, with portable homes as an explicit option.
- D keeps maintenance identities separate and does not assume human home areas in production images.

What remains open is implementation detail, not the product-shape default.

Risk: if this drifts, always-mounted homes and whole-home AppVM sharing quietly become ambient authority again.

Also: if home/state unlock depends on TPM policies, we still need an operable story for policy evolution (avoid PCR brittleness). See `docs/272-sealed-secrets-attested-unsealing.md`.

See: `adrs/ADR-0053-human-identity-and-home-state-posture-by-profile.md`, `docs/463-human-identity-and-home-state-posture-by-profile.md`, `docs/269-portable-home-areas-and-user-records.md`, `docs/270-appvm-storage-private-volatile-and-home-areas.md`.

## 9h) Restore apply boundary (quarantine rehearsal vs live replacement) [DECIDED]

The archive now fixes the restore apply contract in `adrs/ADR-0210-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md`:

- `restore.plan` and `restore.receipt` are official artifacts now,
- ordinary restore remains quarantine-first (`quarantine-namespace`, `microvm-drill`, or `readonly-mount`),
- and `replacement-target` is a stronger promotion lane that must name either a prior verified restore receipt or explicit breakglass authority.

What remains open is implementation detail, not the contract boundary:

- exact restore frontend UX,
- exact quarantine dataset / microVM mechanics,
- detailed health-check taxonomies,
- and restore evidence export/retention defaults.

Risk: without a stable restore boundary, the archive drifts back toward direct-overwrite recovery folklore, clone/import ambiguity on workstations, and production replacement that cannot prove whether it was rehearsed or merely hoped.

See: `adrs/ADR-0210-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md`, `docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md`, `docs/316-backups-and-restores-as-derived-operations.md`, `docs/317-restore-drills-and-continuous-recovery-testing.md`.

See: `adrs/ADR-0053-human-identity-and-home-state-posture-by-profile.md`, `docs/463-human-identity-and-home-state-posture-by-profile.md`, `docs/269-portable-home-areas-and-user-records.md`, `docs/270-appvm-storage-private-volatile-and-home-areas.md`.

## 10) Continuous fuzzing + regression localization (signal vs noise) [DECIDED]

The archive now fixes the **default fuzz/promotion boundary** in `adrs/ADR-0089-fuzz-target-classes-and-flake-aware-promotion-boundary.md`:

- `fuzz.receipt` is evidence-only and records target class/id, harness/runner/sandbox identity, corpus inputs, and compact flake-aware outcome counts.
- `crash.case` is the canonical minimized replay artifact and now carries explicit reproducibility state (`stable`, `flaky`, `unreproduced`).
- Promotion gates key on required target classes plus open `crash.case` state, not raw coverage percentages.
- A/B/C/D keep different default fuzzing posture knobs in `spec/examples/product.profiles.json` instead of pretending all product shapes want identical release gates.

What remains open is implementation detail, not the boundary:

- exact numeric exec/time budgets per target class,
- exact corpus/crash retention windows per severity and product line,
- and the long-term detailed target-id namespace inside each required target class.

Risk: without this boundary, fuzzing still becomes a vanity dashboard and regressions still require heroics.

See: `adrs/ADR-0089-fuzz-target-classes-and-flake-aware-promotion-boundary.md`, `docs/499-fuzz-target-classes-and-flake-aware-promotion-gate-boundary.md`, `docs/274-continuous-fuzzing-farm.md`, `docs/275-root-cause-certificates-and-bisection.md`.

## 11) Kernel module policy + loader verification (don’t leave a pre-kernel hole) [DECIDED]

The archive now fixes the **boot code admission contract** in `adrs/ADR-0072-boot-code-admission-and-constrained-overrides.md`:

- `boot.manifest` is the authoritative boot-closure manifest and now carries `kmod.policy` + `boot.override.policy` digests,
- mutable boot overrides are restricted to a tiny typed surface (`next-entry`, `boot-mode`, `console-profile`) with `boot.override.receipt` evidence,
- `boot.attestation` now states which kernel/module/policy digests were verified,
- and `kmod.load.plan` / `kmod.load.receipt` bind back to `boot_manifest_digest` so post-kernel module posture does not drift away from the boot closure.

What remains open is implementation detail, not the contract boundary:

- the exact loader backend and trust-anchor transport,
- the final trusted-UI / console UX for choosing approved overrides,
- and the exact breakglass ceremony for out-of-policy boot mutation.

Recent decided narrow workstation transfer cuts worth preserving here as historical context: `ADR-0269` fixed the first explicit manifest-entry floor, `ADR-0270` fixed canonical manifest order by normalized review path, `ADR-0271` fixed authoritative compact collection identity on the canonical manifest digest, `ADR-0272` fixed normalized review paths themselves as collection-relative clean slash-separated Unicode NFC identity paths with fail-closed collisions after normalization, `ADR-0273` fixed top-level reviewed names as explicit reviewed state instead of silent broker repair, `ADR-0274` fixed authoritative manifest ancestry so parent directories become explicit reviewed structural state instead of retrieve-time implicit synthesis, including ancestor-only directory rows, `ADR-0275` fixed selected roots themselves as overlap-free reviewed state instead of silent ancestor/descendant subsumption or hidden broker memory, `ADR-0276` fixed retrieve/materialization itself as fresh-destination-root only instead of silent merge/overwrite/rename/reuse into pre-existing local trees, and `ADR-0277` now fixes profile scope itself as B/C/D-only instead of leaving fleet-host support open under vague operator-posture wording, while `ADR-0278` now fixes the first implementation collision answer itself as fail-closed instead of leaving trusted-UI top-level aliasing as a standing maybe, `ADR-0280` now fixes advisory MIME type as optional descriptive metadata instead of a mandatory reviewed field, `ADR-0281` now fixes result-root evidence itself so fresh-rooted retrieve no longer stops at parent-hint or pathless success prose, `ADR-0282` now fixes placement hints themselves as receiver-local advisory UI rather than reviewed authority, and `ADR-0283` now fixes result-root locator posture itself so the exact created fresh root is joined through a receiver-local stable result-root handle rather than mutable path text, `ADR-0284` now fixes advisory display-snapshot continuity so any human-facing retrieve note stays retrieve-frozen when present instead of rewriting itself into a moving current-location story, `ADR-0285` now fixes result-root handle posture itself so that authoritative stable handle stays opaque and non-path-shaped instead of quietly degrading into a path string or URI, and `ADR-0286` now fixes richer filesystem metadata posture itself so owner/group, mode-bit, mtime, xattr, ACL, and similar filesystem-metadata fidelity stay out of this lane entirely instead of remaining a standing maybe inside the same reviewed handoff contract, while `ADR-0287` now fixes one canonical current-stack map for the dense `docs/674-*` through `docs/696-*` tightening cluster so the lane can be read and maintained as one implementation-shaped contract instead of through stale local companion lists.

- [DECIDED] `ADR-0287` + `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` now fix one canonical current-stack map for the dense reviewed finite-collection tightening cluster spanning `docs/674-*` through `docs/696-*`, so the RFC and nearby docs stop acting like stale partial companion lists right when the lane becomes implementation-shaped.
- [DECIDED] `adrs/ADR-0288-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md` now fixes the next implementation noun cut too: the first richer lane now stands on the exact `ui.collection.handoff.grant` / `ui.collection.handoff.manifest` / `ui.collection.handoff.receipt` family instead of leaving the final richer-lane nouns provisional even after the boundary semantics were already narrow enough to implement.

Risk: without a stable contract, secure boot becomes a checkbox while attackers (or accidents) still control which kernel code runs through mutable boot folklore.

See: `adrs/ADR-0072-boot-code-admission-and-constrained-overrides.md`, `docs/482-boot-code-admission-and-constrained-overrides.md`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/277-loader-verification-and-boot-config-constraints.md`, `docs/313-boot-manifests-and-eventlog-replay.md`.

## 12) [DECIDED] Baseline removable media + device posture (USB is the universal footgun)

The baseline posture is now decided in `adrs/ADR-0048-removable-media-and-usb-posture-by-profile.md`:

- no automount into the most trusted plane by default
- removable media stays quarantine-first across profiles
- B requires device domains when hardware supports clean isolation
- D uses a device-domain or dedicated ingest-station posture
- C may use a bounded local authorization fallback instead of ambient attach

What remains open is implementation detail, not the product-shape default.

Risk: convenience drift turns a universal hardware footgun into ambient trusted-plane authority.

See: `adrs/ADR-0048-removable-media-and-usb-posture-by-profile.md`, `docs/458-removable-media-and-usb-posture-by-profile.md`, `docs/278-device-grants-and-devfs-rulesets.md`, `docs/279-usb-quarantine-and-removable-media-workflow.md`, `docs/204-device-isolation-domains.md`.

## 13) Origin labels + quarantine metadata (prevent laundering and stripping) [DECIDED]

The archive now fixes the provenance-authority boundary in `adrs/ADR-0074-origin-label-authority-and-anti-laundering-boundary.md`:

- `content.origin` is the authoritative provenance record,
- filesystem quarantine/origin labels are pointer/cache only,
- `content.import.receipt` must say whether metadata was preserved, rehydrated, cleared-by-policy, or `laundering-suspected`,
- and provenance preservation across lossy transports is only promised through portal / bundle lanes that can rehydrate labels from authoritative records.

What remains open is implementation detail, not the authority boundary:

- the exact filesystem attribute names and frontend UX,
- the exact rehydration path on non-preserving filesystems/transports,
- and the detailed query/privacy policy for metadata indexing.

Risk: without the accepted boundary, provenance either collapses into fragile xattrs or disappears into sidecar folklore.

See: `adrs/ADR-0074-origin-label-authority-and-anti-laundering-boundary.md`, `docs/484-origin-label-authority-and-anti-laundering-boundary.md`, `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/293-attribute-indexed-metadata-and-live-queries.md`, `docs/251-export-policies-and-support-bundle-portal.md`.

## 14) Outbound network policy + consent UX (avoid silent exfil or click-ops) [DECIDED]

This is now a decided product-shape boundary in v0:

- **A** keeps outbound networking brokered/policy-derived and non-interactive by default.
- **B** keeps outbound networking brokered for general apps; trusted-UI prompts are allowed, but approvals must land in short leases or durable policy objects.
- **C** keeps brokered egress as the default for derived workloads, with an explicit adapter fallback for legacy/dev viability.
- **D** keeps deny-by-default / offline-first posture, with only explicitly approved brokered service egress.
- Hostname-based policy implies brokered DNS mediation for the governed lane.

What remains open is implementation detail, not the product-shape default.

Risk: if this boundary is forgotten or softened, networking collapses back into ambient sockets or click-ops that A/D cannot share.

See: `adrs/ADR-0049-outbound-network-posture-by-profile.md`, `docs/459-outbound-network-posture-by-profile.md`, `docs/281-network-egress-broker-and-consent.md`, `docs/305-dns-mediation-and-hostname-binding.md`.

## 15) Witness networks as security parameters (availability, diversity, governance) [DECIDED]

The archive now fixes witness trust as a digest-bound policy boundary in `adrs/ADR-0080-witness-policy-and-roster-quorum-boundary.md`:

- `witness.policy` is the authoritative object for witness roster, operator-diversity grouping, quorum thresholds, and publish/consume shortfall behavior.
- `log.checkpoint.receipt` remains evidence-only but must bind `witness_policy_digest` + `quorum_verdict`.
- `transparency.monitor.policy` and `release.authority.policy` may reference a pinned witness-policy digest, but they no longer silently define witness trust with inline quorum integers.
- `release.publish.receipt.transparency_verification` summarizes the witness-policy result without replacing threshold publication authority.

What remains open is implementation detail, not the boundary itself:

- final per-profile default witness-policy values,
- witness-policy distribution/rotation transport,
- and the exact monitor-diversity expectations for specific channels.

Risk: if this boundary drifts, receipts and service config start smuggling in witness-trust changes that should have been explicit and reviewable.

See: `adrs/ADR-0080-witness-policy-and-roster-quorum-boundary.md`, `docs/490-witness-policy-and-roster-quorum-boundary.md`, `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`, `docs/259-transparency-monitors-and-witness-gossip.md`, `docs/488-release-transparency-evidence-and-monitor-gate-boundary.md`, `spec/witness.policy.schema.json`, `spec/log.checkpoint.receipt.schema.json`.

## 16) Trustworthy time in hostile environments (rollback-by-clock, offline bootstrap) [DECIDED]

The product-shape default is now fixed:
- **A** requires authenticated time with quorum/LKGT posture for expiry-sensitive gates and keeps degraded handling non-interactive.
- **B** prefers authenticated time, keeps degraded state visible in trusted UI, and gates sensitive operations rather than silently trusting weak time.
- **C** keeps authenticated time preferred while allowing explicit compatibility fallback.
- **D** requires bounded offline/bootstrap authority through signed time or authenticated quorum rather than “ignore time because airgap”.

What remains open is implementation detail, not the product-shape default.

Risk: if this drifts, expiry/freshness becomes ceremonial and offline/bootstrap operations normalize unauthenticated time folklore.

See: `adrs/ADR-0058-trustworthy-time-posture-by-profile.md`, `docs/468-trustworthy-time-posture-by-profile.md`, `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`, `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`, `docs/142-trustworthy-time-roughtime.md`.

## 17) Inbound exposure + firewall state (avoid ambient listeners and port-folklore) [DECIDED]

This is now a decided product-shape boundary in v0:

- **A** keeps inbound exposure brokered through service classes and non-interactive by default.
- **B** keeps loopback as the low-friction default for general interactive apps, while LAN/public exposure requires a trusted-UI-mediated lease or durable policy object.
- **C** keeps brokered listen classes as the default, with an explicit adapter fallback for legacy/dev viability.
- **D** keeps deny-by-default / offline-first posture, with only explicitly approved brokered services.
- Ambient “bind/listen and poke the firewall until it works” is not the baseline authority model for any profile.

What remains open is implementation detail, not the product-shape default.

Risk: if this boundary is forgotten or softened, services quietly become reachable and incidents cannot answer *what was exposed and why*.

See: `adrs/ADR-0050-inbound-listen-posture-by-profile.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `spec/net.listen.policy.schema.json`, `docs/238-portal-activated-services-and-socket-activation.md`.

## 18) Formal methods lane: models become stale or theatre

- If we add models, they must stay tied to real decisions and real CI receipts.
- The risk is that models drift from implementation/intent and become “diagramware”.

Risk: models drift from implementation/intent and become diagramware; the lane becomes theatre instead of a safety tool.

Mitigation:
- require an ADR/RFC link for each model
- require a passing `modelcheck.receipt` when a protocol changes
- keep models tiny and finite (favor invariants over completeness)

## 19) High-risk approvals: click-ops, bypass, and governance drift [DECIDED]

The product-shape default is now decided in `adrs/ADR-0064-high-risk-approval-posture-by-profile.md`:

- **A** keeps shared-trust mutations digest-bound, role-separated, and quorum-shaped by default; publish/trust-root/breakglass requester-self-approval is not the fleet baseline.
- **B** keeps trusted-UI user consent as the default for personal-risk actions; shared-trust or org-wide mutations, if enabled, stay in an explicit admin lane rather than hijacking ordinary prompts.
- **C** keeps single-principal local-admin viability by default and does not require a central approver service for ordinary local install/update/admin flows; quorum remains an explicit optional lane.
- **D** keeps production/manufacturing mutations offline/OOB-capable, digest-bound, role-separated, and quorum-shaped by default.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, approvals either degrade into requester-self-approval/social process for shared-trust mutations or expand into workstation/general-OS reviewer theater that operators route around.

See: `adrs/ADR-0064-high-risk-approval-posture-by-profile.md`, `docs/474-high-risk-approval-posture-by-profile.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`, `docs/256-consent-ux-contract.md`, `docs/107-two-person-integrity.md`, and `docs/260-release-authority-policy-and-key-management.md`.

## 20) Workload identity + credential issuance (avoid "static token" relapse) [DECIDED]

The product-shape default is now decided in `adrs/ADR-0060-workload-identity-and-credential-issuance-posture-by-profile.md`:

- **A** keeps workload/service authentication brokered, short-lived, digest-bound, and headless by default.
- **B** keeps workload identity preferred for AppVMs/dev services, while human login/account authority remains a separate lane.
- **C** keeps workload identity preferred, with static-token or file-credential compatibility only as explicit adapters.
- **D** keeps production/factory service identity short-lived and stronger-admission-shaped by default; shipped static shared production secrets are out of bounds.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, workload identity either turns into an overbuilt mandatory mesh or stays absent and static tokens become the ambient compatibility story everywhere.

See: `adrs/ADR-0060-workload-identity-and-credential-issuance-posture-by-profile.md`, `docs/470-workload-identity-and-credential-issuance-posture-by-profile.md`, `docs/181-workload-identity-and-secretless-deploys.md`, `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `spec/workload.identity.lease.schema.json`, `spec/workload.identity.issue.receipt.schema.json`.

## 21) Exec integrity enforcement: brittleness and bypass [DECIDED]

The authority boundary is now decided in `adrs/ADR-0076-exec-integrity-authority-and-verified-execution-boundary.md`:

- `exec.integrity.policy` is the authoritative policy object,
- `exec.integrity.plan` binds policy to backend and runtime composition (`runtime_manifest_digest`, `stratum_stack_digest`, `mount_view_digest`),
- `exec.integrity.receipt` is the authoritative activation result,
- `exec-verify-snapshot` / `exec-verify-event` remain backend observation artifacts,
- `exec.verify.policy.diff` stays the canonical drift surface name, but now compares authoritative `exec.integrity.policy` objects,
- change sets should use `apply-exec-integrity`,
- and the narrow v0 rule is: entrypoint bytes must come from allowed sources, interpreters resolve inside `mount.view`, loader resolution is ABI-anchor-only, and writable/quarantined bytes are denied in enforce mode unless explicitly excepted.

What remains open is backend implementation detail, not the authority boundary.

Risk: if this boundary is softened, operators fall back to backend-specific folklore or simply disable the feature, and the system returns to ambient execution from writable areas.

See: `adrs/ADR-0076-exec-integrity-authority-and-verified-execution-boundary.md`, `docs/486-exec-integrity-authority-and-verified-execution-boundary.md`, `docs/289-exec-integrity-policy-and-verified-execution.md`, `docs/233-verified-execution-as-evidence.md`, `docs/442-exec-verify-policy-diff-as-review-surface.md`, `spec/exec.integrity.policy.schema.json`, `spec/exec.integrity.plan.schema.json`, `spec/exec.integrity.receipt.schema.json`.

## 22) Keyless identity receipts: over-trust and identity confusion [DECIDED]

The archive now fixes the keyless-identity boundary in `adrs/ADR-0077-keyless-identity-evidence-and-offline-verification-boundary.md`:

- `publisher.identity.receipt` is explicitly **identity evidence only** (`authority_semantics = identity-evidence-only`), not publish authority,
- `release.authority.policy` may optionally say whether identity evidence is ignored / optional / required, but threshold publish authority still lives in the release-authority lane,
- `release.publish.receipt` can summarize whether identity evidence was accepted / rejected / unused,
- and `sigstore-keyless` receipts are bundle-first by requiring both `sigstore_bundle_digest` and `verification_roots_digest` for portable offline verification.

What remains open is implementation detail, not the authority boundary:

- the exact identity matcher language,
- the final issuer/template UX,
- and whether future private/public keyless instances get different default policy stances.

Risk: if this boundary is softened, supply-chain review collapses back into “it was signed by CI, ship it” folklore or online-only verification assumptions.

See: `adrs/ADR-0077-keyless-identity-evidence-and-offline-verification-boundary.md`, `docs/487-keyless-identity-evidence-and-offline-verification-boundary.md`, `docs/290-keyless-signing-and-publisher-identity-receipts.md`, `docs/333-sigstore-bundles-and-offline-verification.md`, `docs/260-release-authority-policy-and-key-management.md`, `spec/publisher.identity.receipt.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`.

## 22a) Supply-chain workflow verification: attestation confusion and silent CI authority [DECIDED]

The archive now fixes the workflow-verification boundary in `adrs/ADR-0079-supplychain-verification-evidence-and-publish-gate-boundary.md`:

- `supplychain-layout-policy` remains a workflow-constraint policy, not release authority,
- `supplychain-verify-receipt` is explicitly **workflow-verification evidence only** (`authority_semantics = workflow-verification-evidence-only`),
- `release.authority.policy` may require workflow verification via `supplychain_verification` rules without outsourcing threshold publication authority,
- `release.publish.receipt` can summarize whether workflow verification was accepted / rejected / unused,
- and provenance / SBOM / VEX / VSA-style objects remain evidence inputs to policy engines rather than ambient publish authority.

What remains open is implementation detail, not the authority boundary:

- whether these legacy hyphenated artifact kinds should be renamed in a future cleanup,
- exact freshness defaults for workflow-verification receipts by product shape,
- and how much verifier policy should be exportable as standardized VSA-like predicates.

Risk: if this boundary is softened, the archive slides back into “CI said green, ship it” folklore and release authority becomes a hidden property of whichever verifier backend happened to run last.

See: `adrs/ADR-0079-supplychain-verification-evidence-and-publish-gate-boundary.md`, `docs/489-supplychain-verification-evidence-and-publish-gate-boundary.md`, `docs/202-in-toto-layouts-and-step-policy.md`, `docs/71-attestations-dsse-in-toto-slsa.md`, `docs/260-release-authority-policy-and-key-management.md`, `spec/supplychain.layout.policy.schema.json`, `spec/supplychain.verify.receipt.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`.

## 23) Remote assistance + session recording: backdoors, stealth, and privacy drift [DECIDED]

The product-shape default is now decided in `adrs/ADR-0051-remote-assistance-posture-by-profile.md`:

- **A** treats remote assistance as brokered TTY/console support, not a general GUI remoting story.
- **B** allows visible, trusted-UI-mediated view/control sessions, with secure attention before control and lease/revoke semantics.
- **C** allows a brokered support path, but still forbids ambient always-on agents as the default.
- **D** keeps remote assistance absent by default in production images and only enables it in maintenance-shaped workflows with retained evidence.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, support convenience quietly becomes ambient remote authority or invisible surveillance.

See: `adrs/ADR-0051-remote-assistance-posture-by-profile.md`, `docs/461-remote-assistance-posture-by-profile.md`, `docs/291-remote-assistance-sessions-as-evidence.md`, `docs/292-terminal-session-recording-as-evidence.md`, `docs/256-consent-ux-contract.md`.

## 24) [DECIDED] Spec/policy authoring frontends: compiler trust and DSL sprawl

DeriveBSD now fixes the authority boundary in `adrs/ADR-0085-frontend-source-compile-receipt-and-canonical-ir-boundary.md`.

The accepted v0 posture is:

- the authoritative object remains the compiled canonical JSON Spec/policy artifact
- `frontend.compile.receipt` is evidence-only compiler/source provenance
- JSON + HuJSON are the blessed in-tree authoring surfaces
- richer frontends (CUE/Pkl/Nickel/Starlark/etc) remain adapter lanes rather than part of the core product contract

What remains open is implementation detail and future adapter-lane ergonomics, not the authority boundary.

Risk: frontend tooling becomes a large, fast-moving TCB that operators bypass or that silently changes semantics.

See: `adrs/ADR-0085-frontend-source-compile-receipt-and-canonical-ir-boundary.md`, `docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md`, `docs/79-derive-spec-frontends.md`, ADR-0023, `docs/83-evaluator-minimalism.md`, `docs/149-human-policy-hujson-and-canonicalization.md`.

## 25) Queryable metadata: privacy, laundering, and index integrity

Origin labels, quarantine state, capability bookmarks, and evidence pointers are only useful if they are discoverable under pressure. But metadata search can also become an ambient exfil surface.

Questions:

- Given the accepted dual-layer boundary (`content.origin` authoritative, xattrs pointer/cache), what is the safest minimum query/index substrate and privacy model?
- How do we prevent 'metadata laundering' (apps rewriting bytes without carrying labels)?
- How do we make indexes auditable (snapshots as evidence) and avoid stale/incorrect indexes?
- What is the minimum query/subscription interface that is useful without normalizing ambient search authority?

Risk: either metadata is too hard to use (people ignore it), or it becomes ambient surveillance/exfiltration.

See: `docs/293-attribute-indexed-metadata-and-live-queries.md`, `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/198-persistent-file-capabilities-bookmarks.md`, `docs/229-evidence-spine-overview.md`.

## 26) Multi-origin userlands: explicit strata vs ad-hoc chroots [DECIDED]

The archive now fixes the runtime-composition boundary in `adrs/ADR-0075-stratum-stack-and-runtime-composition-boundary.md`:

- `stratum.manifest` is the authoritative description of one digest-bound userland tree,
- `stratum.stack` is the only supported authored composition object,
- `mount.view` is the compiled runtime namespace / mount graph derived from the stack plus explicit writable mounts,
- every stack has exactly one ABI anchor and keeps host-library fallback forbidden,
- and `runtime.manifest` / runtime evidence must carry `stratum_stack_digest` + `mount_view_digest` so composition stays explainable.

What remains open is implementation detail, not the boundary:

- the final frontend UX for authoring component descriptors,
- the precise ABI taxonomy for future foreign ecosystems,
- and the final launch receipt kinds that record composition joins.

Risk: without this accepted boundary, compatibility would drift back into ad-hoc chroots and silent host-library leakage.

See: `adrs/ADR-0075-stratum-stack-and-runtime-composition-boundary.md`, `docs/485-stratum-stack-and-runtime-composition-boundary.md`, `docs/295-strata-and-multi-origin-userlands.md`, `docs/264-mount-namespaces-and-union-views.md`, `docs/297-component-descriptors-and-compiled-runtime-manifests.md`.

## 27) “How it runs” source vs runtime artifact sprawl (component descriptors) [DECIDED]

The archive now fixes the component-runtime source boundary in `adrs/ADR-0090-derive-unit-source-compile-receipt-and-runtime-boundary.md`:

- `derive.unit` is the authoritative human-authored source,
- a `derive.unit` must name runtime bytes via exactly one authored field (`rootfs` or `strata`),
- compiled runtime artifacts remain compiled outputs rather than hand-authored shadow sources,
- `runtime.manifest` stays the backend-facing launch authority object,
- and `derive.unit.compile.receipt` is the evidence-only source→compiled join.

What remains open is implementation detail, not the source/authority boundary:

- the exact breadth of v0 `contractset.json` / endpoint-contract typing,
- the exact `svcdb` vs launch-backend split for non-service units,
- and which future runtime backends deserve new compiled outputs instead of adapter wrappers.

Risk: if this boundary drifts, runtime policy becomes folklore again and compiled artifacts collapse back into hand-authored shadow config.

See: `adrs/ADR-0090-derive-unit-source-compile-receipt-and-runtime-boundary.md`, `docs/500-derive-unit-source-compile-receipt-and-runtime-boundary.md`, `docs/297-component-descriptors-and-compiled-runtime-manifests.md`, `docs/344-derive-unit-manifests-and-capability-routing.md`.

## 28) Permission creep despite explicit grants (need authority budgets) [DECIDED]

The archive now fixes the generic authority-budget boundary in `adrs/ADR-0084-authority-budgets-and-exception-boundary.md`:

- `authority.budget` is the authoritative least-authority policy object,
- `authority.budget.check` is evidence-only,
- `authority.exception` is an authoritative, timeboxed, field-scoped waiver,
- and the generic budget lane is intentionally limited to component-runtime dimensions: filesystem, network, devices, trust, and observability.

What remains open is implementation detail, not the authority boundary:

- default ratchet strength for new components,
- reviewer UX for budget deltas,
- and whether any future dimension deserves promotion into the generic budget lane.

Risk: if this boundary drifts, authority budgets either become toothless dashboards or an incoherent umbrella that duplicates accepted lane-specific authority contracts.

See: `adrs/ADR-0084-authority-budgets-and-exception-boundary.md`, `docs/494-authority-budget-policy-check-and-exception-boundary.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/106-blast-radius-diff.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`.

## 29) Lazy mounts and partial fetch: integrity, side-channels, and fallback drift [DECIDED]

The archive now fixes the lazy-mount boundary in `adrs/ADR-0117-verified-lazy-tree-mount-materialization-and-evidence-boundary.md`:

- reviewed deployment identity stays upstream in the object that requested the tree (`mount.view`, `closure.manifest`, `runtime.manifest`, `base.set`, etc.),
- `tree.mount.plan` is the typed projection/transport plan and must state `materialize` vs `prefetch` vs `lazy`, explicit fallback posture, and explicit fetch-evidence scope,
- `tree.mount.receipt` stays bounded and digest/summary-first by default,
- and path-level fetch traces are a stronger explicit debug/forensics lane instead of ambient default telemetry.

What remains open is implementation detail, not the authority/privacy/fallback boundary:

- exact planner heuristics for when `prefetch` beats `lazy`,
- exact cache-retention budgets and mirror posture per deployment line,
- and the final stronger artifact shape for optional path-level fetch tracing.

Risk: without this boundary, lazy pulling either becomes an unreviewed deployment path or an accidental surveillance surface.

See: `adrs/ADR-0117-verified-lazy-tree-mount-materialization-and-evidence-boundary.md`, `docs/299-verified-lazy-rootfs-and-on-demand-mounts.md`, `docs/527-verified-lazy-tree-mount-materialization-and-evidence-boundary.md`, `docs/119-casync-cvmfs-distribution.md`, `docs/192-observability-as-capability.md`.

## 30) Snapshot UX vs security: revocation, secret retention, and ambient exposure

We need "previous versions" UX, but naive snapshot exposure can leak old bytes after permissions change or secret rotation.

Open questions:
- Do we require portalized access only (no ambient snapshot dirs), even for power users?
- When a principal loses access, how do we ensure old snapshots aren't readable (filtered views vs per-principal encryption)?
- What is the retention policy interface that doesn't turn into "keep everything forever"?

Risk: snapshots become a silent data-exfil path and undermine least-authority promises.

See: `docs/300-time-travel-snapshots-as-leases.md`, `docs/195-deterministic-redaction-transforms.md`, `docs/251-export-policies-and-support-bundle-portal.md`.

## 31) P2P distribution: poisoning, identity confusion, and privacy leakage

P2P swarm distribution can accelerate rollouts, but it changes the threat model:

- peers are untrusted (poisoning attempts; downgrade attempts)
- peer-to-peer visibility can leak what a node is installing
- a swarm agent can become a privileged "side channel" if not compartmented and policy-bound

Open questions:
- How do we bind swarm participation to workload identity without conflating "can speak" with "can publish"?
- What evidence do we need to make P2P paths auditable without making fetch traces toxic?
- When should policy force HTTP-only or full materialization?

Risk: operators deploy P2P daemons outside the Derive trust/evidence model, or P2P becomes a stealthy exfil surface.

See: `docs/301-p2p-distribution-and-swarm-caches.md`, `docs/170-remote-cache-threat-model.md`, `docs/62-replay-rollback-freeze.md`.

## 32) Structured diagnostics vs privacy (Inspect trees can become ambient surveillance) [DECIDED]

The product-shape default is now fixed in `adrs/ADR-0067-evidence-collection-posture-by-profile.md`:

- **A** keeps bounded always-on local evidence as the fleet operability baseline.
- **B** keeps evidence locally useful and user-exportable, with richer capture or sharing staying trusted-UI-visible rather than ambient.
- **C** keeps local-retained evidence as the baseline and makes remote collectors/support agents explicit, optional choices.
- **D** keeps production evidence bundle-oriented and redacted by default rather than assuming live diagnostic streaming.

What remains open is implementation detail, not the product-default boundary:
- the exact diagnostics lease model,
- the exact redaction taxonomy,
- and the exact journal-vs-snapshot store split / retention mechanics.

Risk: without a stable default, operability either degrades into ambient surveillance or falls back to ad-hoc support tooling outside the evidence model.

See: `adrs/ADR-0067-evidence-collection-posture-by-profile.md`, `docs/478-evidence-collection-posture-by-profile.md`, `docs/302-structured-diagnostics-inspect-trees.md`, `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`, `docs/216-incident-snapshots-and-support-bundles.md`.

## 33) Flight recorders: overhead, covert channels, and “debug mode” bypasses

Always-on circular buffers are a huge operability win, but they must be bounded and policy-governed.

Open questions:
- Which backend substrate is best on FreeBSD (DTrace/ktrace/custom ring buffers), and what is the minimal TCB?
- How do we enforce budgets (rate, size, window) and make drops explicit rather than silent?
- How do we prevent "debug builds" or ad-hoc tooling from bypassing budgets and leases?

Risk: performance regressions, covert channels, or an ecosystem split where the real debugging happens outside the Derive evidence model.

Packet-capture / raw-socket / fast-packet-I/O posture is now fixed separately in `adrs/ADR-0096-packet-capture-raw-sockets-and-fast-packet-io-boundary.md` and `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`, so this item now focuses on bounded diagnostics rather than ambient packet visibility.

See: `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/216-incident-snapshots-and-support-bundles.md`.

## 34) Trust bundles: format choice, interop renderers, and drift control [DECIDED]

The product-shape default is now decided in `adrs/ADR-0070-trust-bundle-posture-by-profile.md`:

- **A** keeps trust roots purpose-scoped and diff-gated by default, and treats embedded shadow trust in official fleet lanes as blocking unless explicitly waived.
- **B** keeps a visible governed system trust baseline and allows extra roots through trusted-UI review rather than silent app-local bundle mutation.
- **C** keeps governed system trust preferred while preserving explicit local CA / app-specific trust overrides as real adapter territory.
- **D** keeps production/manufacturing trust roots fixed-purpose, digest-bound, and offline/strongly-approved rather than live-edited.

What remains open is implementation detail, not the product-shape default. Recent reduction in ambiguity: `ADR-0212` / `docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md` now also standardize `pki.trust.bundle.apply.receipt`, so the archive can prove which exact digest-bound trust view a host or unit served instead of delegating that answer to renderer/distributor folklore.

Risk: without a stable default, trust posture regresses to folklore — fleet services smuggle app-local roots, workstation users inherit invisible enterprise trust changes, general-purpose compatibility overrides quietly become the real baseline, and factory/regulatory systems lose provenance through ad-hoc live CA edits.

See: `adrs/ADR-0070-trust-bundle-posture-by-profile.md`, `adrs/ADR-0212-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md`, `docs/480-trust-bundle-posture-by-profile.md`, `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`, `docs/327-shadow-trust-and-system-ca-governance.md`, `docs/434-pki-trust-bundle-diff-as-review-surface.md`, `docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md`, `spec/pki.trust.bundle.schema.json`, `spec/pki.trust.bundle.diff.schema.json`, `spec/pki.trust.bundle.apply.receipt.schema.json`, `docs/228-pki-and-identity-lifecycle-as-evidence.md`.

## 35) DNS mediation receipts: TOCTOU control vs privacy toxicity [DECIDED]

The product-shape default is now decided in `adrs/ADR-0094-dns-receipt-detail-and-export-posture-by-profile.md`:

- Across all profiles, `net-flow-receipt` stays the normal explainability/export surface for governed egress, while `net-dns-query-receipt` stays scoped to broker-governed hostname resolution rather than an ambient whole-host DNS tap.
- **A** keeps bounded full-detail local DNS receipts normal for governed hostname lanes, but defaults external sharing to deterministic redaction and requires stronger incident/ticket scope for full qname disclosure.
- **B** keeps short-window local detail for governed app flows, with trusted-UI-visible redacted sharing by default and explicit trusted-UI expansion for full qname disclosure.
- **C** keeps bounded local detail for derived workloads and explicit redacted export, while compatibility adapters remain visible provenance gaps rather than silently inheriting brokered-DNS evidence promises.
- **D** keeps production DNS evidence aggregate-only or absent by default, with detailed per-query capture reserved for approved maintenance/incident lanes and external sharing minimal/redacted.

What remains open is implementation detail: exact retention windows, exact deterministic transform vocabulary, and exact learn/audit promotion rules.

Risk: without a stable default, hostname policy regresses to folklore on one side and privacy-toxic namespace logging on the other.

See: `adrs/ADR-0094-dns-receipt-detail-and-export-posture-by-profile.md`, `docs/504-dns-receipt-detail-and-export-posture-by-profile.md`, `docs/305-dns-mediation-and-hostname-binding.md`, `docs/459-outbound-network-posture-by-profile.md`, `docs/478-evidence-collection-posture-by-profile.md`, `docs/466-export-boundary-posture-by-profile.md`, `spec/net.dns.query.receipt.schema.json`.

## 36) Private-key and crypto-operation posture by profile [DECIDED]

The product-shape default is now decided in `adrs/ADR-0052-private-key-and-crypto-op-posture-by-profile.md`:

- **A** keeps private-key use brokered, non-exportable, and headless/policy-gated by default.
- **B** keeps human-facing key use brokered/non-exportable by default, with user presence and vault/keystore-style handles preferred over raw key bytes.
- **C** keeps brokered/non-exportable key use preferred, with file-backed keys and classic agents only as explicit adapter fallbacks.
- **D** keeps production/manufacturing/release keys offline or hardware-backed and quorum-shaped by default.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, static key files, ambient signing agents, and convenience copies quietly become the real product.

See: `adrs/ADR-0052-private-key-and-crypto-op-posture-by-profile.md`, `docs/462-private-key-and-crypto-op-posture-by-profile.md`, `docs/306-crypto-operations-portal-and-split-keys.md`, `docs/392-crypto-key-policies-and-nonexportable-handles.md`, `docs/437-split-secrets-brokers.md`.

## 37) Trustworthy time: quorum failures, expiry safety, and operational response [DECIDED]

The archive now fixes the degraded-time workflow boundary in `adrs/ADR-0292-time-requirement-degraded-time-response-stays-explicit-and-proof-bundle-bound.md`:

- `time.requirement` is now the authoritative place where a workflow states what happens under `degraded` and `unsynced` time
- degraded-time response is explicit typed policy through `degraded_response.on_degraded` / `degraded_response.on_unsynced` rather than daemon/UI folklore
- `allow-if-proof-fresh` is the only ordinary degraded-time continuation lane, and it must bind to an exact `time-proof-bundle` through `time.sync.snapshot.inputs.proof_bundle_digest`
- unsynced time cannot silently continue; the reviewed choices are denial, repair, or explicit breakglass

What remains open is implementation detail, not the authority boundary:

- exact quorum / skew defaults by class
- signed offline-time token envelope and replay/retention details
- workstation repair UX / alert cadence
- fleet monitor and escalation behavior when authenticated sources disagree for long periods

Risk: without this boundary, expiry-based security still degrades into per-workflow folklore and support surfaces still cannot show why a sensitive action proceeded under weak time.

See: `adrs/ADR-0292-time-requirement-degraded-time-response-stays-explicit-and-proof-bundle-bound.md`, `docs/702-time-requirement-degraded-response-stays-explicit-and-proof-bundle-bound.md`, `docs/468-trustworthy-time-posture-by-profile.md`, `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`, `docs/308-time-monitors-and-lie-detection.md`, `spec/time.requirement.schema.json`, `spec/time.sync.snapshot.schema.json`, `spec/time.proof.bundle.schema.json`.

## 38) Installation and recovery: disk layout idempotency, encryption ergonomics, and “don't wipe the wrong disk” [DECIDED]

The product-shape default is now decided in `adrs/ADR-0063-installation-and-recovery-posture-by-profile.md`:

- **A** keeps install/recovery target-device-bound and additive by default; destructive disk mutation requires breakglass/maintenance approval.
- **B** keeps install/recovery trusted-UI-guided, requires explicit disk identity confirmation for destructive edits, and makes encrypted-root posture the ordinary baseline.
- **C** keeps guided Derive installs and bounded compatibility/classic installer adapters viable, but destructive repartitioning remains explicit and reviewable.
- **D** keeps factory/regulatory install/recovery target-bound and offline-capable by default, with destructive reprovisioning governed by signed reset bundles/markers and retained approval/receipts.

The archive now also fixes the destructive reprovision contract in `adrs/ADR-0073-destructive-reprovisioning-and-reset-authority.md`: `reset.authorization` binds target + plan + install payload + authority signals, and `reset.receipt` records what destructive reset authority was actually observed.

ADR-0209 now fixes the next ambiguity too: the product-shaped evidence/detail/export default is now fixed, so destructive reset no longer gets to mean invisible remote reprovision, screenshot archaeology, or a universal reset recorder.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, install/recovery drifts into wrong-disk incidents, hidden destructive convenience flows, live-network rescue dependency, and unreceipted factory reset folklore.

See: `adrs/ADR-0063-installation-and-recovery-posture-by-profile.md`, `adrs/ADR-0073-destructive-reprovisioning-and-reset-authority.md`, `adrs/ADR-0209-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md`, `docs/473-installation-and-recovery-posture-by-profile.md`, `docs/483-destructive-reprovisioning-and-reset-authority.md`, `docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md`, `docs/309-installation-and-recovery-as-derived-operations.md`, `docs/310-disk-layout-plans-and-receipts.md`, `docs/360-derived-recovery-images-and-minimal-userspace.md`, `docs/155-trust-bootstrap.md`.

## 39) Operator access leases: JIT cert UX, audit value, and "no backdoor" posture [DECIDED]

The product-shape default is now decided in `adrs/ADR-0057-operator-access-posture-by-profile.md`:

- **A** keeps operator access brokered, JIT certificate-based, role-shell-first, and separate from escalation.
- **B** treats local secure-attention / user-presence admin as the default and keeps remote shell admin exceptional + leased rather than standing.
- **C** keeps classic local admin compatible, but JIT/leased remote admin is the preferred Derive-managed posture and static keys remain explicit adapter territory.
- **D** requires maintenance-window-shaped, JIT, strongly approved operator access and forbids standing vendor/admin keys in factory or shipped images by default.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, static keys, permanent bastions, and standing maintenance credentials quietly become the real operator-access story.

See: `adrs/ADR-0057-operator-access-posture-by-profile.md`, `docs/467-operator-access-posture-by-profile.md`, `docs/311-operator-access-leases-and-ssh-certs.md`, `spec/operator.session.schema.json`, `docs/292-terminal-session-recording-as-evidence.md`, `docs/236-breakglass-and-recovery-mode.md`.

## 40) Measured boot in practice: event-log replay ergonomics, attester lifecycle, and variance policy [DECIDED]

The archive now fixes the attestation-reference exception workflow boundary in `adrs/ADR-0231-attestation-reference-exceptions-stay-timeboxed-and-approval-shaped.md`:

- routine measured-boot references stay `scope.kind = cohort` and `boot.variance.mode = manifest-replay-first`,
- any `deployment` / `host` scope or `mixed` / `strict-pcr-only` variance posture must carry `attestation.reference.exception`,
- that exception record is timeboxed and approval-shaped (`reason`, `justification`, `expires_at`, `approvals`, `renewal_posture`, optional rollout/ticket joins),
- renewed exceptions mint a new artifact and use `supersedes_reference_digest` when they are the reviewed successor of a prior exception,
- `strict_pcr_values` may not hide under `manifest-replay-first`,
- and attestation results that name `attester_key_id` now also carry `identity_provenance.attester_provision_receipt_digest` so attester identity provenance is exportable evidence rather than registrar-only state.

What remains open is implementation detail, not the archive boundary:

- the exact minimum stable `boot.manifest` contents across hardware classes,
- the final canonical event-log representation and parser-upgrade policy,
- the day-0 attester-key lifecycle ceremony details (AK rotation, motherboard replacement, revocation),
- and durable-attestation retention budgets that stay useful without becoming privacy-toxic.

Risk: without a stable attestation-reference boundary, measured boot still decays into verifier-side databases, host-specific PCR folklore, overlapping exception rows, selector-precedence folklore, registrar-only identity truth, or policy that nobody can safely renew or explain.

See: `adrs/ADR-0231-attestation-reference-exceptions-stay-timeboxed-and-approval-shaped.md`, `adrs/ADR-0232-attestation-reference-renewals-stay-digest-linked-and-successor-shaped.md`, `adrs/ADR-0234-attestation-receipts-carry-attester-identity-provenance-by-digest.md`, `docs/176-measured-boot-attestation.md`, `docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/313-boot-manifests-and-eventlog-replay.md`, `docs/314-attester-provisioning-and-key-lifecycle-receipts.md`, `docs/640-attestation-reference-scope-and-variance-boundary.md`, `docs/641-attestation-reference-exceptions-stay-timeboxed-and-approval-shaped.md`, `docs/642-attestation-reference-renewals-stay-digest-linked-and-successor-shaped.md`, `docs/644-attestation-receipts-carry-attester-identity-provenance-by-digest.md`, `spec/boot.manifest.schema.json`, `spec/attester.provision.receipt.schema.json`, `spec/attestation.receipt.schema.json`.

## 41) Backups and restore drills: key availability, privacy, and false confidence [DECIDED]

The product-shape default is now decided in `adrs/ADR-0054-backup-and-restore-posture-by-profile.md`:

- **A** treats fleet hosts as replaceable and backs up state via receipted replication plus restore drills rather than normalizing full-host image nostalgia.
- **B** keeps user recovery explicit: exports and/or home-state replication rather than ambient whole-device clone assumptions.
- **C** keeps backup tooling as a compatibility choice, but Derive-managed backup lanes stay typed and receipted when used.
- **D** treats replication plus recurring restore drills as the default recoverability claim for factory/regulatory shapes.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, recovery posture drifts into full-machine folklore, mystery sync, or compliance claims unsupported by restore evidence.

See: `adrs/ADR-0054-backup-and-restore-posture-by-profile.md`, `docs/464-backup-and-restore-posture-by-profile.md`, `docs/316-backups-and-restores-as-derived-operations.md`, `docs/317-restore-drills-and-continuous-recovery-testing.md`, `spec/backup.plan.schema.json`, `spec/backup.receipt.schema.json`, `spec/restore.drill.receipt.schema.json`, `docs/255-policy-constrained-transports.md`, `docs/306-crypto-operations-portal-and-split-keys.md`.

## 42) Kernel mutation control: sysctls, boot tunables, and module loading drift [DECIDED]

The product-shape default is now decided in `adrs/ADR-0065-kernel-mutation-posture-by-profile.md`:

- **A** keeps kernel mutation activation-first and maintenance-leased: boot tunables stay generation-bound, risky runtime sysctl writes require maintenance leases, and modules are preload-first rather than ambient runtime tools.
- **B** keeps kernel mutation activation-first with trusted-UI maintenance: risky sysctl/debug changes or runtime module loads must be visible maintenance actions instead of silent background host mutation.
- **C** keeps derive-managed kernel mutation as the default while preserving explicit local-admin fallback for general-purpose viability; stronger lockdown/lease lanes remain optional, not hidden prerequisites.
- **D** keeps production kernel mutation preload-only plus lockdown by default; runtime sysctl/kmod mutation belongs to offline or tightly approved maintenance workflows.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, kernel posture drifts back into mutable folklore — fleets normalize ad-hoc sysctl edits, workstations inherit hidden host mutation from helpers, general-purpose viability gets confused with ambient service authority, and factory/regulatory lockdown claims stop meaning anything.

See: `adrs/ADR-0065-kernel-mutation-posture-by-profile.md`, `docs/475-kernel-mutation-posture-by-profile.md`, `docs/318-kernel-tunables-and-sysctls-as-evidence.md`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/230-lockdown-levels-and-securelevel.md`, `docs/429-sysctl-diff-as-drift-surface.md`.

## 43) Hardware inventory + compatibility gates: safety, privacy, and operability [DECIDED]

The product-shape default is now decided in `adrs/ADR-0069-hardware-compatibility-posture-by-profile.md`:

- **A** keeps hardware compatibility preflight blocking for boot-critical and remote-management-floor failures, with hardware-class cohorting normal and breakglass explicit.
- **B** keeps boot/display/input/storage floor failures blocking by default, while warnings stay trusted-UI-visible and require explicit consent plus a verified recovery path.
- **C** keeps compatibility preflight preferred and receipted while preserving explicit local override for broad-compatibility/general-purpose viability.
- **D** keeps production support admission-first: approved hardware classes and offline bundles carry the support story instead of best-effort live discovery.

The support-catalog implementation detail is now also fixed in `adrs/ADR-0118-hardware-support-matrix-and-bundled-admission-boundary.md`: `hw.support.matrix` is the typed approved-hardware catalog, and `hw.compat.report` now has an explicit `support_matrix` join state instead of burying support decisions in notes.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, upgrades keep drifting into either remote-brick roulette or privacy-toxic inventory sprawl — fleets switch blind, workstations surprise users with hardware regressions, and factory/regulatory support claims stop meaning anything.

See: `adrs/ADR-0069-hardware-compatibility-posture-by-profile.md`, `adrs/ADR-0118-hardware-support-matrix-and-bundled-admission-boundary.md`, `docs/479-hardware-compatibility-posture-by-profile.md`, `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`, `docs/319-hardware-inventory-and-driver-binding-as-evidence.md`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `spec/hw.inventory.receipt.schema.json`, `spec/hw.compat.report.schema.json`, `spec/hw.support.matrix.schema.json`, `docs/112-health-gated-updates.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`.

## 44) Firmware updates + UEFI variable drift: trust roots, remote bricks, and unreceipted platform mutation [DECIDED]

The product-shape default is now decided in `adrs/ADR-0061-firmware-update-posture-by-profile.md`:

- **A** keeps firmware mutation policy-gated and maintenance-shaped, with cohort-aware preflight and post-reboot evidence.
- **B** keeps firmware apply trusted-UI-visible and interactive-consent-first rather than silently mutating laptops under the user.
- **C** keeps firmware management user-choice, with managed lanes preferred and classic vendor tooling explicit adapter territory.
- **D** keeps production/factory firmware offline-staged by default instead of depending on live vendor reachability.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, firmware posture regresses to updater folklore — fleets accumulate ambient flashing authority, workstation users get surprised by platform changes, and regulated deployments quietly depend on online vendor paths they cannot actually govern.

See: `adrs/ADR-0061-firmware-update-posture-by-profile.md`, `docs/471-firmware-update-posture-by-profile.md`, `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `spec/fw.inventory.receipt.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`, `spec/uefi.var.set.plan.schema.json`, `spec/uefi.var.set.receipt.schema.json`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `docs/51-secure-boot-integration.md`.

## 44h) Firmware evidence/detail/export posture (digest-first truth vs raw platform dump folklore) [DECIDED]

The archive now also fixes the routine firmware-evidence boundary in `adrs/ADR-0211-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md`:

- `fw.inventory.receipt` is routine local evidence across A–D,
- `fw.inventory.diff` is the routine review surface when firmware/platform state is compared,
- `fw.update.receipt` and `uefi.var.set.receipt` remain the authoritative mutation proof,
- and raw vendor logs, raw efivar blobs, raw Secure Boot databases, and raw capsule bytes stay stronger side evidence instead of routine baseline export.

What remains open is implementation detail, not the product-shaped default.

Risk: without a stable default, firmware posture drifts into either invisible helper folklore or universal raw-platform export — fleets lose crisp trust-root/change proof, workstation support becomes efivar archaeology, general-purpose installs inherit helper-specific truth, and factory/regulatory lanes overshare blobs they cannot routinely govern.

See: `adrs/ADR-0211-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md`, `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md`, `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`, `docs/337-secure-boot-certificate-rotation-and-fleet-trust.md`, `spec/fw.inventory.receipt.schema.json`, `spec/fw.inventory.diff.schema.json`, `spec/fw.update.receipt.schema.json`, `spec/uefi.var.set.receipt.schema.json`.

## 44i) Official support handoff should carry typed firmware/platform drift proof [DECIDED]

The archive now also fixes the support-handoff drift boundary in `adrs/ADR-0222-incident-bundles-carry-fw-inventory-diff-proof-by-digest.md`:

- `incident.bundle` keeps `fw_inventory_digest` for the current inventory snapshot,
- `incident.bundle` may now also carry `fw_inventory_diff_digest` when a reviewed `fw.inventory.diff` materially shaped the incident/support story,
- and exact mutation proof still stays on `fw_update_receipt_digests` / `uefi_var_set_receipt_digests` rather than collapsing snapshot, diff, and mutation into one firmware blob.

What remains open is implementation detail, not the product or evidence boundary.

Risk: without a stable support-handoff join, firmware/platform drift falls back to screenshots, dashboard comparisons, or ticket prose — responders can see that “firmware changed” but not which exact bounded review artifact the archive meant them to trust.

See: `adrs/ADR-0222-incident-bundles-carry-fw-inventory-diff-proof-by-digest.md`, `docs/632-incident-bundles-carry-fw-inventory-diff-proof-by-digest.md`, `docs/428-fw-inventory-diff-as-drift-surface.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `spec/incident.bundle.schema.json`, `spec/fw.inventory.diff.schema.json`.

---

## 45) Network topology drift: routes, addresses, pf substrate, and remote-brick changes [DECIDED]

The product-shape default is now decided in `adrs/ADR-0068-network-topology-posture-by-profile.md`:

- **A** keeps host topology activation-first and commit-confirmed by default, with risky live mutation in maintenance-leased lanes rather than shell folklore.
- **B** keeps ordinary local networking humane in the trusted UI, but makes risky host-topology mutation visible, confirmable, and rollbackable rather than ambient.
- **C** keeps derived networking preferred and receipted while preserving explicit local-admin fallback for compatibility and lab workflows.
- **D** keeps production topology sealed/offline-windowed by default, with exposure-expanding changes confined to approved rollbackable maintenance workflows.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, networking regresses to folklore — remote incidents require SSH log spelunking, drift breaks reproducibility claims, workstations quietly broaden exposure, and factory/regulatory systems drift through ad-hoc live edits they cannot govern.

See: `adrs/ADR-0068-network-topology-posture-by-profile.md`, `docs/477-network-topology-posture-by-profile.md`, `docs/322-network-topology-and-firewall-as-derived-operations.md`, `spec/net.topology.plan.schema.json`, `spec/net.topology.receipt.schema.json`, `spec/net.topology.event.schema.json`, `docs/67-pf-anchors-per-instance.md`, `docs/64-networking-modes-mapping.md`, `docs/112-health-gated-updates.md`, `docs/311-operator-access-leases-and-ssh-certs.md`.

---

## 46) `/dev` drift: ambient device nodes, devfs ruleset folklore, and sandbox escapes [DECIDED]

The product-shape default is now decided in `adrs/ADR-0066-device-authority-posture-by-profile.md`:

- **A** keeps service compartments compiled-minimal by default and makes raw device-node expansion lease-shaped or maintenance-shaped rather than ambient.
- **B** keeps raw sensitive device ownership in the trusted host and makes general interactive app access portal-first with trusted-UI-visible exceptions instead of ambient host `/dev` exposure.
- **C** keeps compiled-minimal and mediated device lanes preferred, while preserving an explicit local compatibility fallback for software that truly needs raw device nodes.
- **D** keeps production/factory device authority compiled-minimal and sealed by default, with stronger raw-device expansion confined to offline or strongly approved maintenance workflows.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, `/dev` posture regresses to folklore — fleet services accumulate ambient raw authority, workstation apps inherit unsafe host device nodes, general-purpose compatibility gets confused with ambient authority, and factory/regulatory images silently depend on live devfs expansion.

See: `adrs/ADR-0066-device-authority-posture-by-profile.md`, `docs/476-device-authority-posture-by-profile.md`, `docs/323-devfs-views-plans-and-receipts.md`, `docs/278-device-grants-and-devfs-rulesets.md`, `docs/204-device-isolation-domains.md`, `docs/249-lease-registry-and-cross-lane-revocation.md`, `spec/devfs.view.plan.schema.json`, `spec/devfs.view.receipt.schema.json`, `spec/devfs.view.event.schema.json`.

## 63) Platform-provenance implementation details after the profile default

The product-shape default is now decided, but important implementation detail work remains:

- which actions are in the default “sensitive admission” set for A/D (identity issuance, secret release, rollout, remote admin, maintenance mode) and how those defaults are compiled into policy
- what the stable operator/user UX vocabulary should be beyond the new hard cut that degraded admission must already be requirement-shaped (`min_verdict = degraded`) rather than hidden-waiver-shaped
- how verifier/registrar/enrollment lifecycle should rotate cleanly without silently broadening trust or stranding recovered hosts now that decisive authority receipts pin the full requirement/receipt/policy tuple
- what workstation UX should show when measured posture is missing, stale, or degraded so B stays explainable without making attestation a surprise hard dependency
- how event-log replay, reference-value variance, and hardware class exceptions stay reviewable instead of turning into per-host allowlist sprawl

Risk: the product default is sound but the implementation lane still drifts into opaque verifier stacks, broad exceptions, or brittle PCR folklore that operators cannot explain.

See: `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md`, `docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/313-boot-manifests-and-eventlog-replay.md`, `docs/314-attester-provisioning-and-key-lifecycle-receipts.md`, `docs/315-durable-attestation-and-posture-timelines.md`, `docs/388-remote-attestation-admission-and-enrollment.md`, `docs/440-attestation-admission-policy-diff-as-review-surface.md`.

## 64) Workload-identity implementation details after the profile default

The product-shape default is now fixed. Remaining work is implementation detail:

- trust-domain naming, federation shape, and how much of it should be archive-level default vs deployment policy
- exact selector/binding vocabulary (closure digest, runtime digest, compartment id, attestation inputs, human-approved adapters)
- private-key backing choices for issued identities (in-guest, broker-held, TPM/platform handle, external token) without policy fragmentation
- default issuance/evidence/redaction budgets so renewals are explainable without turning support bundles into secret-adjacent telemetry
- classic adapter posture for static-token/file-credential software so compatibility stays explicit, killable, and reviewable

Risk: the product boundary stays correct on paper, but implementations drift into opaque mesh sprawl, selector folklore, or compatibility adapters that quietly recreate static-secret baselines.

See: `docs/470-workload-identity-and-credential-issuance-posture-by-profile.md`, `docs/181-workload-identity-and-secretless-deploys.md`, `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `docs/240-dynamic-service-identities.md`, `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`, `spec/workload.identity.lease.schema.json`, `spec/workload.identity.issue.receipt.schema.json`.

## 65) Vulnerability verification: noisy feeds and silent scanner authority [DECIDED]

The archive now fixes the vulnerability-verification boundary in `adrs/ADR-0081-vulnerability-verification-evidence-and-publish-gate-boundary.md`:

- `vuln.query.receipt` remains deterministic query evidence rather than publication authority,
- `vuln-gate-receipt` is explicitly **vulnerability-verification evidence only** (`authority_semantics = vulnerability-verification-evidence-only`),
- `release.authority.policy` may require vulnerability verification via `vulnerability_verification` rules without outsourcing threshold publication authority,
- `release.publish.receipt` can summarize whether vulnerability verification was accepted / warning / rejected / unused,
- and SBOM / VEX objects remain evidence inputs to vulnerability-verification policy rather than ambient publish authority.

What remains open is implementation detail, not the authority boundary:

- the exact shape of risk-acceptance / allowlist objects,
- default freshness posture by product shape,
- and whether warn-mode publication should have stronger workstation/general-purpose UX defaults.

Risk: if this boundary is softened, the archive slides back into “scanner said no” or “scanner said green” folklore and mutable vulnerability feeds quietly become release authority.

See: `adrs/ADR-0081-vulnerability-verification-evidence-and-publish-gate-boundary.md`, `docs/491-vulnerability-verification-evidence-and-publish-gate-boundary.md`, `docs/60-vulnerability-intel-and-gates.md`, `docs/338-vulnerability-snapshots-query-receipts-and-openvex.md`, `docs/168-sboms-and-vex-as-evidence.md`, `docs/260-release-authority-policy-and-key-management.md`, `spec/vuln.query.receipt.schema.json`, `spec/vuln.gate.policy.schema.json`, `spec/vuln.gate.receipt.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`.

## Rituals

- Every RFC should list which open questions it advances.
- Every milestone should burn down at least one risk item.

## 66) Attestation results vs issued authority (avoid “verifier said yes” folklore) [DECIDED]

The archive now fixes this boundary in `adrs/ADR-0082-attestation-results-evidence-and-admission-issue-boundary.md`:

- `attestation.receipt` is explicitly verifier evidence only (`authority_semantics = attestation-evidence-only`)
- `attestation.admission.policy` maps actions to `attestation.requirement` digests
- `attestation.requirement` stays the freshness/minimum-verdict acceptance rule
- authoritative consuming receipts such as `secret-receipt`, `breakglass-receipt`, and `workload-identity-issue-receipt` may summarize the accepted/rejected decision via `attestation_verification`, but decisive uses now also carry `attestation_receipt_verdict` so the exact pinned verifier outcome stays visible without backend archaeology
- degraded admission now stays requirement-shaped too: `attestation.requirement.min_verdict = degraded` is the sole portable way to allow degraded posture, and v0 has no hidden degraded-waiver lane
- post-breakglass ordinary resumption now also stays explicit: breakglass is not standing ordinary authority, and later ordinary attestation-gated lanes require a fresh `attestation.receipt` issued after the relevant breakglass receipt `created_at`

What remains open is implementation detail, not the authority boundary:

- which other action receipts should adopt `attestation_verification` in v0,
- exact verifier-topology/vendor integrations,
- and the final default sensitive-action set per profile.

Risk: without a stable boundary, remote attestation drifts back into ambient verifier folklore where raw receipts are mistaken for the actual authorization decision.

See: `adrs/ADR-0082-attestation-results-evidence-and-admission-issue-boundary.md`, `docs/492-attestation-results-evidence-and-admission-issue-boundary.md`, `docs/388-remote-attestation-admission-and-enrollment.md`, `docs/226-platform-posture-and-attestation-results-as-evidence.md`, `spec/attestation.receipt.schema.json`, `spec/attestation.admission.policy.schema.json`, `spec/attestation.requirement.schema.json`.

## 47) Product profiles (A–D) as first-class compilation targets [DECIDED]

The archive now fixes the default-vocabulary boundary in `adrs/ADR-0091-product-profile-default-vocabulary-boundary.md`:

- `product.profiles.defaults` stays a flat symbolic compilation-target map rather than a second policy language,
- the default-key vocabulary is explicitly allowlisted in `spec/product.profile.schema.json`,
- `docs/501-product-profile-default-vocabulary-boundary.md` is the canonical registry doc for those keys,
- overlapping observability posture is intentionally collapsed onto `evidence` + `evidence_exports` + `network_egress` rather than a separate `telemetry` key,
- structured policy continues to live in dedicated schemas/docs,
- and `required_invariants` remains the place for hard product-shape promises that do not deserve a new default key.

What remains open is implementation detail, not the vocabulary boundary:

- whether a given new idea belongs in an existing default key,
- which dedicated policy/spec lane should carry structured semantics when a symbolic posture is insufficient,
- and how individual lanes compile their profile defaults into concrete policy objects.

Risk: without a stable vocabulary boundary, A–D becomes an ad-hoc options tree and slowly stops being a reviewable shared product model.

See: `adrs/ADR-0091-product-profile-default-vocabulary-boundary.md`, `adrs/ADR-0093-no-separate-telemetry-product-profile-key.md`, `docs/411-product-profiles-as-compilation-target.md`, `docs/501-product-profile-default-vocabulary-boundary.md`, `docs/503-telemetry-is-not-a-product-profile-default-boundary.md`, `spec/product.profile.schema.json`, `spec/examples/product.profiles.json`, `tools/check_profile_default_vocabulary.py`.

## 48) Data-at-rest posture (ZFS encryption + keys + recovery) [DECIDED]

The product-shape default is now decided in `adrs/ADR-0055-data-at-rest-posture-by-profile.md`:

- **A** encrypts mutable state by default and only allows unattended bring-up through attested local or brokered recovery lanes rather than image-baked key files.
- **B** treats lost/stolen-device protection as real: ordinary user/home state should unlock with the human rather than ambient boot convenience.
- **C** keeps encryption preferred but allows an explicit compatibility fallback instead of pretending one posture fits every install.
- **D** encrypts production/factory state by default and keeps maintenance/recovery unlock explicit, receipted, and often quorum-shaped.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, deployments drift into raw file-key auto-unlock, always-unlocked workstation state, or hidden factory convenience secrets.

See: `adrs/ADR-0055-data-at-rest-posture-by-profile.md`, `docs/465-data-at-rest-posture-by-profile.md`, `docs/409-zfs-encryption-and-key-management.md`, `docs/250-breakglass-and-recovery-workflows.md`, `docs/272-sealed-secrets-attested-unsealing.md`, `docs/463-human-identity-and-home-state-posture-by-profile.md`.

## 49) Desktop viability implementation details (even if desktop is not v0)

The basic workstation boundary is now decided: host UI/brokers are trusted, general apps are AppVM-first, and the GUI crossing is now host-owned composition plus software-first remoted GUI rather than ambient host display-server or GPU authority.
What remains open is the implementation detail needed to make that boundary practical.

Open questions:
- what is the minimal trusted UI implementation we can defend across laptops/monitors/remote sessions?
- how do portals map onto capability brokers and leases in practice?
- which remoting transport / audio-video / IME details best fit the chosen host-owned composition boundary?
- is any future accelerated lane worth the complexity?
- is any future seamless per-window host-native integration worth standardizing after the session-surface-first baseline?
- are bounded drag&drop or clipboard-history exceptions worth standardizing after the no ambient shared cross-domain clipboard floor now that the ordinary `single-delivery` lane is explicitly one-shot and fresh-grant-required after success?
- what trusted-UI wording and review surface best communicates `fresh-grant` vs `supersedes-prior-grant` without encouraging “retry until it works” folklore now that reviewed re-offer lineage is explicit on the grant artifact itself?
- [DECIDED] `adrs/ADR-0260-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md` now closes the ordinary successor-vocabulary seam: `ui.datatransfer.grant.constraints` is closed-world and typed, so hidden extra successor execution posture is no longer baseline; future richer posture must come back through an ADR/spec change or a distinct richer lane.
- [DECIDED] `adrs/ADR-0261-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md` now freezes the frozen portable baseline as complete enough to implement; richer replay/batching, widened/substituting, collection-like, or otherwise broader transfer lanes are RFC-first instead of further quiet baseline growth.
- [DECIDED] `adrs/ADR-0262-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md` now fixes the next intake seam too: if a richer workstation transfer lane is accepted later, it must mint a distinct artifact family instead of widening or variant-switching ordinary `ui.datatransfer.grant` / `ui.datatransfer.receipt`.
- [DECIDED] `adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` now fixes the next priority cut too: if practice later forces one richer workstation transfer lane, the first RFC target is a reviewed finite collection handoff, and the draft design surface is `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md` rather than reopening the frozen ordinary baseline.
- [DECIDED] `adrs/ADR-0264-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` now fixes the first retrieve-width cut inside that RFC queue too: the first richer lane stays single-retrieve by default and auto-stops after the first successful retrieve instead of carrying repeated-retrieve replay semantics in the first cut.
- [DECIDED] `adrs/ADR-0265-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` now fixes the next directory-semantics cut inside that RFC queue too: selected directories in the first richer lane stay finite reviewed snapshot membership instead of quietly becoming live tree traversal or persistent directory authority.
- [DECIDED] `adrs/ADR-0266-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` now fixes the next snapshot-representation cut too: the first richer lane keeps manifest-first reviewed membership through an explicit per-member manifest, and any tree/collection digest stays supplementary summary evidence instead of replacing the primary review/export surface.
- [DECIDED] `adrs/ADR-0267-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` now fixes the next access-mode cut too: the first richer lane is read-only only in its first cut, and any write-enabled receive must come back as a separate follow-on RFC/ADR decision instead of lingering inside `RFC-0194`.
- [DECIDED] `adrs/ADR-0268-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` now fixes the next member-kind cut too: the first richer lane is regular-files-plus-explicit-directories only, and symlink/special-file semantics are not part of the first cut.
- [DECIDED] `adrs/ADR-0269-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` now fixes the next manifest-entry cut too: the first richer lane now has a smallest exact per-member field set with normalized review path + member kind for every entry and exact payload digest + byte length for regular files, while richer stat fidelity stays deferred.
- [DECIDED] `adrs/ADR-0270-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` now fixes the next serialization cut too: the authoritative per-member manifest is ordered only by normalized review path in strict ascending bytewise order, locale-independent, and duplicate normalized review paths fail closed instead of preserving traversal or click order as hidden reviewed state.
- [DECIDED] `adrs/ADR-0271-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` now fixes the next compact-identity cut too: the first richer lane carries one authoritative manifest digest computed from the canonical serialized explicit manifest, and tree/collection summary digests stay supplementary instead of becoming the real compact handle.
- [DECIDED] `adrs/ADR-0272-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md` now fixes the next path-grammar cut too: the first richer lane now uses collection-relative clean slash-separated Unicode NFC review paths and fails closed on normalization collisions instead of host/toolkit cleanup folklore.
- [DECIDED] `adrs/ADR-0273-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md` now fixes the next multi-root naming cut too: the first richer lane now keeps top-level reviewed names explicit, so silent auto-rename or wrapper-root repair is out of bounds and any disambiguation must become reviewed alias state or fail closed.
- [DECIDED] `adrs/ADR-0274-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md` now fixes the next namespace-shape cut too: the first richer lane now keeps the authoritative manifest ancestor-closed, so every proper parent path of each nested `review_path` must appear explicitly and receiver-side implicit parent synthesis is out of bounds.
- [DECIDED] `adrs/ADR-0275-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md` now fixes the next reviewed-root cut too: the first richer lane now keeps selected roots overlap-free after normalization and reviewed aliasing, so ancestor/descendant root overlap must fail closed instead of silently collapsing into one larger reviewed snapshot or hidden broker memory.
- [DECIDED] `adrs/ADR-0276-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md` now fixes the next retrieve/materialization cut too: the first richer lane now lands under a fresh destination root, so silent merge into an existing tree, overwrite, auto-rename, or same-bytes reuse are no longer left to receiver folklore.
- [DECIDED] `adrs/ADR-0277-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md` now fixes the next product-scope cut too: the first richer lane is now a B/C/D-only richer lane, while A stays on rollout/support/import-export/breakglass-shaped answers unless a later distinct operator file-ferry lane is justified.
- [DECIDED] `adrs/ADR-0278-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md` now fixes the next first-implementation collision cut too: the first richer lane now keeps trusted-UI top-level aliasing out, so multi-root basename collisions fail closed until a later explicit alias/disambiguation lane is justified.
- [DECIDED] `adrs/ADR-0279-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md` now fixes the next review-surface legibility cut too: the first richer lane now allows bounded path-compression of deterministic ancestor-only runs while keeping the authoritative manifest fully explicit and ancestor-closed.
- [DECIDED] `adrs/ADR-0280-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md` now fixes the next metadata cut too: advisory MIME stays optional and non-authoritative instead of becoming a mandatory reviewed field or hidden detector requirement.
- [DECIDED] `adrs/ADR-0281-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md` now fixes the next retrieve-result evidence cut too: successful retrieve receipts must pin the exact created fresh root instead of stopping at a parent chooser hint or pathless success prose.
- [DECIDED] `adrs/ADR-0282-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md` now fixes the next placement-authority cut too: placement hints stay advisory and receiver-local, so parent chooser, destination label, suggested folder, or save-into prompts stay receiver-local advisory UI state rather than authoritative reviewed state or sender-directed placement policy in the first richer lane.
- [DECIDED] `adrs/ADR-0283-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md` now fixes the next result-root locator posture cut too: successful retrieve now keeps a receiver-local stable result-root handle as the authoritative local result locator, and any path/display snapshot stays advisory instead of becoming mutable-path folklore.
- [DECIDED] `adrs/ADR-0284-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md` now fixes the next display-snapshot continuity cut too: if successful retrieve carries any human-facing path/display snapshot for the created fresh root, that advisory text is now retrieve-frozen instead of silently rewriting itself after later local rename/move/import/promote state.
- inside `RFC-0194`, is any owner/mode/mtime/xattr fidelity worth standardizing later?
- how should trusted-UI floor support matrices evolve across release trains without turning into hardware-vendor theater?
- inside the newly accepted view-first floor, which trusted/local or later sanitized derivatives should prefer persistent vs disposable `document_viewing` now that newly imported foreign originals are disposable-first and fail closed without a disposable viewer target, how should later approval/finalization lanes consume the now-accepted explicit candidate supersession chain, which approval/finalization adapters (if any) are worth standardizing on top of the now-accepted `content.reintegrate.*` lane, whether the now-accepted current-head exact supersession floor should later grow into first-class branch/merge semantics or remain intentionally linear now that stale denials must also carry `stale_target_evidence = observed-current-head-required` plus `stale_target_recovery = fresh-explicit-supersession-required`, whether the now-accepted stale-target recovery lane should remain only `recovery.mode = from-stale-supersession-denial` or later grow additional typed recovery modes, and which profile-`C` compatibility adapters (if any) are worth documenting beyond the official imported-document authoring chain?

Recent reduction in ambiguity: `adrs/ADR-0118-hardware-support-matrix-and-bundled-admission-boundary.md` fixes the typed support-catalog boundary, `adrs/ADR-0119-hardware-support-promotion-and-qualification-boundary.md` fixes how positive support labels carry `qualification` maturity/evidence floor, `adrs/ADR-0120-hardware-support-qualification-receipt-boundary.md` makes those claims receipt-bound through `qualification.receipt_digest` and lets `hw.compat.report.support_matrix` point back at exact proof via `matched_qualification_receipt_digests`, `adrs/ADR-0121-hardware-support-qualification-profile-boundary.md` binds those receipts to a typed `qualification.profile_digest` plus explicit `check_results[]`, `adrs/ADR-0122-hardware-support-qualification-freshness-boundary.md` adds a typed freshness answer (`fresh_until`, `reverify_on`) plus explicit `qualification-stale` preflight/reporting posture, `adrs/ADR-0123-hardware-support-qualification-status-boundary.md` now makes receipt lifecycle operational through `decision.status`, `status_effective_at`, `reason_code`, `replacement_receipt_digest`, and explicit `qualification-superseded` / `qualification-revoked` findings, `adrs/ADR-0124-hardware-support-conditions-and-known-limitations-boundary.md` now makes `conditional` / `canary-only` / `maintenance-only` publication carry typed `conditions[]`, `support_claim.condition_ids`, `matched_condition_ids`, and `support-condition-triggered` instead of caveat prose, `adrs/ADR-0125-hardware-support-qualification-target-scope-boundary.md` now adds target `release_train`, typed `target_binding`, and explicit `qualification-target-mismatch` / `target_scope_state` so older proof cannot silently float across release trains or boot-manifest lineages, `adrs/ADR-0126-workstation-display-composition-and-gpu-boundary.md` now decides that ordinary workstation GUI crossing stays on a host-owned composition boundary with software-first remoted GUI instead of ambient host display/GPU authority, `adrs/ADR-0127-workstation-remoted-session-surface-boundary.md` now decides that the baseline B crossing is **session-surface-first** instead of seamless per-window host-native integration, `adrs/ADR-0128-workstation-cross-domain-datatransfer-floor.md` now fixes B on a no ambient shared cross-domain clipboard floor with explicit brokered transfer and no cross-domain drag&drop as a baseline requirement, `adrs/ADR-0129-workstation-intent-routed-uri-opening-floor.md` now makes URI opening an intent-routed URI opening act where the trusted host is not the default renderer for untrusted external content, and `adrs/ADR-0130-workstation-role-bound-intent-targets-and-chooser-floor.md` now fixes chooser/default-app behavior onto trusted host-managed role slots instead of arbitrary app discovery or first-open default rewrites, while `adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md` now fixes remembered defaults onto a typed `intent.role.binding` object instead of ambient desktop registries, and `adrs/ADR-0132-role-binding-diff-as-review-surface.md` now fixes `intent.role.binding.diff` as the compact review surface for remembered-role changes instead of raw settings deltas, while `adrs/ADR-0133-role-binding-event-as-durable-mutation-evidence.md` now adds `intent.role.binding.event` as the durable mutation trail for event journals and support bundles, and `adrs/ADR-0134-role-binding-consent-lane-for-interactive-workstation-mutations.md` now reuses the generic consent substrate for trusted-settings UI approval evidence instead of inventing a workstation-only settings prompt family, while `adrs/ADR-0135-role-binding-policy-decision-join-for-noninteractive-mutations.md` now binds `policy-reconcile` role-binding events back to `policy.decision` instead of leaving fleet/factory/admin reconcile as daemon folklore. That still leaves trusted-UI implementation details, trusted/local or sanitized derivative heuristics for persistent versus disposable viewing after the now-accepted foreign-document disposable-first floor, broader remembered-role baseline distribution language beyond the exact mutation tuple, replica/distributed consumption mechanics beyond a minimal issuance identity, and a fuller actor/approval receipt family open. `adrs/ADR-0243-workstation-imported-foreign-document-viewing-stays-disposable-first.md` and `docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md` remove one more practical cliff by fixing ordinary foreign-document inspection onto a disposable `document_viewing` lane, keeping the allow-path route `policy-pinned` rather than remembered-persistent-default-shaped, and making missing disposable support fail closed instead of quietly reopening the persistent-viewer fallback. `adrs/ADR-0195-workstation-file-open-import-join-and-bounded-document-roles.md` and `docs/605-workstation-file-open-import-and-bounded-document-roles.md` remove one more practical cliff by fixing cross-compartment document open/view/edit as import-shaped first and route-shaped second, standardizing only the small `document_viewing` / `document_editing` role pair, and requiring route evidence to stay joinable back to the exact `content.import.receipt` through `intent.route.receipt.import_receipt_digest` instead of host-open or “open with…” folklore. `adrs/ADR-0196-workstation-imported-foreign-documents-stay-view-first-and-working-copy-shaped.md` and `docs/606-workstation-imported-foreign-documents-stay-view-first.md` remove the next mutation cliff by making imported foreign documents **view-first** and requiring an explicit working-copy transition before the ordinary `document_editing` lane applies, so baseline workstation behavior becomes **work on a copy** rather than **edit the imported original in place**. `adrs/ADR-0197-workstation-working-copy-receipts-and-edit-route-joins.md` and `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md` then remove the next implementation cliff by making that authoring transition typed as `content.working-copy.plan` / `content.working-copy.receipt`, extending `intent.request.context` and `intent.route.receipt` with `working_copy_receipt_digest`, and keeping allow-path edit routes joinable back to the explicit writable-copy act instead of path folklore. `adrs/ADR-0198-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md` and `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md` remove the next local-authoring cliff by requiring `content.working-copy.*.boundary.default_save_target = working-copy-output` plus `source_writeback = separate-act-required`, so ordinary save no longer smuggles source replacement back in through disposable/editor convenience behavior, and source write-back stays an explicit later boundary instead of a hidden editor side effect. `adrs/ADR-0199-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md` and `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md` then remove the next source-lineage cliff by introducing `content.reintegrate.plan` / `content.reintegrate.receipt` with `candidate_posture = local-successor-candidate`, `replace_in_place = forbidden`, and `upstream_finalize = separate-adapter-required`, so edited working-copy bytes can become an explicit successor candidate of the same authoritative origin without letting app/cloud folklore decide when the source was “really” updated. `adrs/ADR-0200-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md` and `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md` then remove the next evidence cliff by requiring `candidate_snapshot = immutable` plus `later_edits = new-candidate-required`, so a registered candidate stays frozen to one exact digest instead of drifting into a mutable working-path alias. `adrs/ADR-0201-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md` and `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md` then remove the next multi-candidate ordering cliff by requiring `candidate_ordering = explicit-supersession-only` plus `recency_precedence = forbidden`, so later candidates supersede earlier ones only by naming the exact earlier `content.reintegrate.receipt` digest instead of silently becoming current by recency or label folklore. `ADR-0202` / `adrs/ADR-0202-workstation-candidate-supersession-stays-same-origin-and-self-describing.md` and `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md` then remove the next scope/evidence cliff by requiring `supersession_scope = same-authoritative-origin-only` plus `superseded_candidate_digest` / `superseded_authoritative_origin_digest`, so explicit supersession cannot jump across authoritative origins or leave detached bundles guessing which exact prior snapshot was displaced. `ADR-0203` / `adrs/ADR-0203-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md` and `docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md` then remove the next freshness/race cliff by requiring `supersession_target_posture = current-unsuperseded-candidate-only` plus `stale_target_handling = fail-closed`, so a stale supersession request cannot silently retarget to some newer candidate or retroactively rethread the lineage. `adrs/ADR-0139-role-binding-policy-decisions-bind-exact-mutation.md` removes one more implementation cliff by requiring the joined `policy.decision` to bind the exact mutation tuple through `inputs.intent_role_binding_request` plus `effective_constraints.intent_role_binding_apply` instead of a vague class-level allow record. `adrs/ADR-0140-role-binding-policy-decisions-are-short-lived-and-single-apply.md` removes one more replay cliff by requiring that same apply block to carry `must_apply_before` plus `max_successful_events = 1` so successful remembered-role mutations consume a bounded allow record instead of inheriting a reusable standing permission. `adrs/ADR-0141-role-binding-policy-decisions-need-unique-instance-identity.md` removes the next digest-aliasing cliff by requiring `decision_instance_id` on the remembered-role policy profile so a fresh issuance for the same exact tuple stays distinguishable from an earlier consumed authorization. `adrs/ADR-0142-role-binding-policy-window-denials-need-typed-reasons.md` removes the next operability cliff by requiring `intent.role.binding.event.reason_code` to distinguish `policy-expired` and `policy-consumed` from broad `policy-denied`, so expired or already-spent exact-mutation authorizations remain queryable in support bundles and retry logic. `adrs/ADR-0143-role-binding-denial-precedence-between-policy-and-precondition.md` removes the next branch-order cliff by requiring non-interactive remembered-role apply to emit `policy-denied`, then `policy-consumed`, then `policy-expired`, and only then `precondition-failed`, so replay/expiry/ stale-state evidence stays deterministic across implementations. `adrs/ADR-0144-role-binding-policy-consumed-denials-point-to-consuming-event.md` removes the next support cliff by requiring `policy-consumed` denials to carry `consumed_by_event_id`, so spent-authority failures can point at the earlier successful consuming event instead of leaving winner identification to log archaeology. `adrs/ADR-0145-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md` removes the next recovery cliff by requiring retries to collapse to **already-applied** only when that consuming success matches the same exact mutation tuple, so crash-retry paths do not silently turn every spent authorization into either a hard failure or an ambient success story. `adrs/ADR-0146-role-binding-retries-need-a-stable-recovery-interpretation-field.md` removes the next support/export drift cliff by requiring `recovery_interpretation` on `policy-consumed` denials, so bundles and host-local admin/reconcile tooling can query the derived recovery answer without changing the durable denial reason. `adrs/ADR-0147-role-binding-policy-consumed-denials-carry-consuming-event-digest.md` removes the next detached-bundle verification cliff by requiring `consumed_by_event_digest` next to `consumed_by_event_id`, so the exact winner event that justified `already-applied` remains verifiable away from the live journal. `adrs/ADR-0148-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md` removes the next result-summary cliff by requiring `consumed_binding_digest`, so support bundles and retry/export tooling can also read the earlier winner's resulting binding digest without reopening that winner event body first. `adrs/ADR-0149-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md` removes the next review-summary cliff by requiring `consumed_diff_digest`, so those same support/retry/export surfaces can also read the earlier winner's applied review-surface digest without reopening that winner event body first. `adrs/ADR-0150-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md` removes the next old-edge-summary cliff by requiring `consumed_previous_binding_digest` for updated winners, so those same support/retry/export surfaces can also read the earlier winner's replaced `previous_binding.digest` without reopening that winner event body first. `adrs/ADR-0151-role-binding-policy-consumed-denials-carry-consuming-event-action.md` removes the next winner-shape cliff by requiring `consuming_event_action`, so those same support/retry/export surfaces can also tell whether the earlier winner was an `initialized` first-write or an `updated` compare-and-swap and can interpret the presence or absence of `consumed_previous_binding_digest` without reopening that winner event body first. `adrs/ADR-0136-role-binding-diff-precondition-and-conflict-denial.md` now removes one more implementation cliff by making `intent.role.binding.diff.from_binding.digest` the mutation precondition and requiring stale writes to leave typed `precondition-failed` evidence through `intent.role.binding.event.observed_binding` instead of silently rebasing, while `adrs/ADR-0137-role-binding-support-import-join-via-content-import-receipt.md` now makes imported remembered-role mutations point back to the exact typed `content.import.receipt` through `import_receipt_digest` instead of restore-log folklore. `adrs/ADR-0138-role-binding-authority-lanes-not-invocation-surfaces.md` removes one more ambiguity by treating local CLI or remote admin identity as `source.*` metadata while keeping `trigger` reserved for typed consent/policy/import authority lanes.

`ADR-0244` and `docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md` reduce one more ambiguity here: sanitized inspection derivatives now stay inspection-shaped and disposable-first by default, so sanitizer success is no longer allowed to masquerade as ambient persistent-viewer trust promotion.

`ADR-0245`, `ADR-0246`, and `ADR-0247` remove the next searchable-inspection convenience cliffs too: OCR/searchable reconstruction stays explicit and secondary, searchable inspection stays out of ambient host/global indexes by default, and copied OCR-derived text still leaves that lane only through explicit plain-text single-delivery transfer with a provenance-carrying `content_source` join instead of ambient clipboard/export folklore. `ADR-0248` and `ADR-0249` then tighten the same lane into portable evidence: transfer artifacts now name both the exact offer-side subject and the exact consumed grant artifact (`grant_digest`) instead of leaving actor or policy reconstruction to broker memory. `ADR-0250` then fixes the next recovery interpretation too: the ordinary `single-delivery` lane is one-shot, so the first successful read-side transfer exhausts the grant and recovery is fresh grant / re-offer required rather than replay/history resurrection. `ADR-0251` then fixes the exact unused-authority deadline through `effective_until`, `ADR-0252` fixes the next reviewed continuity seam by requiring successor grants to say so explicitly with `renewal_posture` plus `supersedes_grant_digest` instead of mutating older grants in place, and `ADR-0253` fixes the next widening seam by requiring those successor grants to stay same-actor-pair and no-wider-offer through `successor_scope_posture` instead of quietly broadening MIME/byte/source/destination scope under old-story wording. `ADR-0254` fixes the next payload-lineage seam by requiring successor continuity to keep exact `offer.content_source` and exact `offer.redaction_profile_digest`, so reviewed retry cannot quietly retarget payload lineage or redaction posture while pretending to be the same transfer story. `ADR-0255` fixes the next substitution seam by requiring successor continuity to keep exact `offer.payload_digest`, so newly rendered or semantically equivalent bytes are a fresh reviewed grant instead of semantic-equivalence folklore. `ADR-0256` then keeps foreground posture exact under successor continuity, `ADR-0257` keeps `delivery_mode` exact too, `ADR-0258` keeps `constraints.rate_limit` exact, `ADR-0259` now keeps `constraints.expires_at` exact as well, and `ADR-0260` closes the open-ended vocabulary seam by making `ui.datatransfer.grant.constraints` closed-world and typed, so reviewed successor retry cannot quietly widen through hidden extra `constraints.*` posture under the old story, and `ADR-0261` now freezes the ordinary portable transfer lane as the frozen portable baseline, complete enough to implement, with richer widened/substituting/broader lanes RFC-first instead of further quiet baseline drift. `ADR-0262` then fixes the intake split so any richer lane must mint a distinct artifact family, `ADR-0263` now fixes the next queueing question too by prioritizing a reviewed finite collection handoff as the first richer-lane RFC target instead of persistent tree or replay-first convenience, and `ADR-0264` now fixes the first retrieve-width question inside that RFC queue too by keeping the first cut single-retrieve by default and auto-stop after the first successful retrieve instead of letting replay semantics sneak into the richer lane by convenience.

See: `docs/410-desktop-viability-checklist.md`, `docs/179-portals-and-powerbox.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`, `docs/536-workstation-display-composition-and-gpu-boundary.md`, `docs/537-workstation-remoted-session-surface-boundary.md`, `docs/538-workstation-cross-domain-datatransfer-floor.md`, `docs/539-workstation-intent-routed-uri-opening-floor.md`, `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`, `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`, `docs/542-role-binding-diff-as-review-surface.md`, `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`, `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md`, `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`, `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`, `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`, `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`, `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`, `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md`, `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md`, `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`, `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`, `docs/529-hardware-support-promotion-and-qualification-boundary.md`, `docs/530-hardware-support-qualification-receipt-boundary.md`, `docs/531-hardware-support-qualification-profile-boundary.md`, `docs/532-hardware-support-qualification-freshness-boundary.md`, `docs/533-hardware-support-qualification-status-boundary.md`, `docs/534-hardware-support-conditions-and-known-limitations-boundary.md`, `spec/hw.support.qualification.profile.schema.json`, `spec/hw.support.qualification.receipt.schema.json`.

Risk: B becomes infeasible in practice, forcing forks or abandoning the workstation story despite the high-level boundary being correct.

## 50) Removable-media implementation details on imperfect hardware

The baseline posture is decided, but execution details still matter:

- how do we detect and qualify “device-domain supported” hardware robustly?
- what does the BSD-native local authorization fallback look like (policy daemon, prompt UX, remembered approvals, revocation)?
- [DECIDED] `adrs/ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` now fixes the first removable-storage fallback itself: on imperfect B/C hardware the only accepted local fallback is storage-only, session-scoped, quarantine-first, read-only-first, and composed from existing `device.attach.*`, `devfs.view.plan`, and `content.import.receipt` nouns instead of generic USB passthrough or trusted-plane automount.
- [DECIDED] `adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md` now fixes the next execution cut too: the first buildable B/C fallback keeps attach and read-only mount authority host-controlled, feeds a disposable no-network jail through `mount.view`, and keeps that jail block-empty rather than handing it raw storage device nodes.
- [DECIDED] `adrs/ADR-0315-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md` now fixes the next admission cut too: the host must probe with `fstyp`, admit only `msdosfs`, `exfat`, `ufs`, and `cd9660`, and fail closed on `ext2fs`, `ntfs`, `zfs`, `geli`, and unknown probe results until a later explicit lane earns them.
- [DECIDED] `adrs/ADR-0316-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md` now fixes the next mount-semantics cut too: even after a family is admitted, the host-side mount must keep `ro,nodev,nosuid,noexec,nosymfollow`, the mounted tree stays inert input only, and side-effect launch metadata stays bytes rather than ambient instructions.
- [DECIDED] `adrs/ADR-0317-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md` now fixes the next ingest-walk cut too: traversal stays physical and root-pinned beneath `/ingest`, the first admitted member kinds are regular files plus explicit directories only, symlink/device/FIFO/socket semantics fail closed, and hardlink topology stays out of scope in the first cut.
- [DECIDED] `adrs/ADR-0318-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md` now fixes the next naming cut too: admitted member paths normalize to relative-clean Unicode NFC text, normalization collisions fail closed, and the first cut performs no silent auto-rename, wrapper-root insertion, or source-prefix repair.
- [DECIDED] `adrs/ADR-0319-removable-media-local-fallback-keeps-owner-mode-mtime-xattr-fidelity-out-of-the-first-lane.md` now fixes the next metadata cut too: reviewed/import identity stays path/kind/payload-first, owner/group, mode-bit, mtime, xattr, ACL, and similar metadata fidelity stay out of scope in the first cut, and any receiver-local metadata outcomes stay realization detail rather than portable reviewed state.
- [DECIDED] `adrs/ADR-0320-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md` now fixes the next selection-width cut too: the first host-local removable-media ingest lane stays single-selected-subject only, direct multi-member review/import stays out of scope in the first cut, and multiple outputs only arise as a deterministic consequence of processing that one selected subject.
- [DECIDED] `adrs/ADR-0321-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md` now fixes the next selected-subject-kind cut too: the first host-local removable-media ingest lane stays regular-file-only in the first cut, directories may still appear during candidate browsing, but directories are not selectable import subjects in this lane.
- [DECIDED] `adrs/ADR-0322-removable-media-local-fallback-approval-stays-present-device-instance-only-and-reattach-requires-fresh-grant.md` now fixes the next approval-continuity cut too: approval stays present-device-instance-only in the first cut, physical detach or lease end revokes it, and reattach requires a fresh grant even when serial or disk-ident hints look the same.
- [DECIDED] `adrs/ADR-0323-removable-media-local-fallback-attach-receipts-carry-observed-hints-and-keep-them-evidence-only.md` now fixes the next attach-evidence cut too: the canonical `device.attach.receipt` for this lane carries a finite current-presence hint bundle (`ugen`/provider plus disk-ident or physical-path hints when available), explicitly marks those hints evidence-only, and keeps same-hints-on-reattach non-authoritative.
- [DECIDED] `adrs/ADR-0324-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md` now fixes the next capture-first cut too: once one selected regular file is chosen, the first non-browsing step captures that exact subject into `/work`, later operations consume the captured file rather than the live mounted path, digest verification is required before later operations proceed, and capture failure or mismatch fails closed.
- [DECIDED] `adrs/ADR-0325-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md` now fixes the next authority-lifetime cut too: once that capture verifies, the host ends the removable-medium session and emits `device.detach.receipt` before later classify/scan/sanitize work continues, so later work no longer depends on continued device presence.
- [DECIDED] `adrs/ADR-0326-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md` now fixes the next post-detach execution cut too: after verified capture and detach, later classify/scan/sanitize work restarts in a fresh disposable worker with `/ingest` absent and with no inherited live medium references from the pre-detach worker.
- [DECIDED] `adrs/ADR-0327-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md` now fixes the next evidence-lifetime cut too: after capture verification, detach, and the post-detach worker restart, the exact captured subject remains preserved evidence and later sanitize/convert work must emit separate derivatives instead of rewriting the preserved capture in place.
- [DECIDED] `adrs/ADR-0328-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md` now fixes the next preserved-evidence authority seam too: the verified capture may not remain authoritative only under disposable `/work`; before detach it must commit into authoritative quarantine store, and later work must read the stored preserved capture or a read-only projection of it.
- [DECIDED] `adrs/ADR-0329-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md` now fixes the next post-detach delivery seam too: later work may receive only one preserved selected subject through a synthetic single-object projection or equivalent brokered handle, and it may not browse the authoritative quarantine-store namespace.
- [DECIDED] `adrs/ADR-0330-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md` now fixes the next post-detach continuity seam too: the later worker may still receive only one synthetic single-object delivery, but that delivery must match the preserved selected subject digest before later ops begin and the canonical receipt must record that digest-bound continuity explicitly.
- [DECIDED] `adrs/ADR-0331-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md` now fixes the next post-detach execution seam too: once that one delivery is prepared, later execution must stay on one launcher-preopened read-only object (or equivalent), any worker-visible path remains compatibility-only plumbing, and the later worker may not reacquire the subject through broader path or authoritative-store lookup.
- [DECIDED] `adrs/ADR-0332-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md` now fixes the next post-detach derivative-egress seam too: later-worker output must leave through launcher-prepared disposable sink objects, worker outbox paths stay non-authoritative execution plumbing, and the launcher/broker must collect + remeasure those bytes before `content.import.receipt` names an authoritative derivative locator.
- [DECIDED] `adrs/ADR-0333-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md` now fixes the next output-surface seam too: the later worker gets only one declared writable derivative slot, any receipt-visible derivative must come from that slot, and extra worker result surface stays out in the first lane.
- [DECIDED] `adrs/ADR-0334-removable-media-local-fallback-post-detach-derivative-slot-stays-empty-writeonly-and-no-readback-or-truncate.md` now fixes the next output-slot I/O seam too: that one declared derivative slot starts as a launcher-precreated empty regular file, later-worker authority omits readback/seek/truncate, and derivative egress stays forward-only with no worker readback or truncate before broker collection.
- [DECIDED] `adrs/ADR-0335-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md` now fixes the next FreeBSD-shaped output-slot seam too: if the first lane keeps a seekable regular-file sink, the launcher hands it over append-open, keeps it append-only-protected while the worker runs, omits `CAP_READ`/`CAP_FTRUNCATE`/`CAP_FCNTL`, and treats any `CAP_SEEK` there as implementation ballast rather than rewrite authority.
- [DECIDED] `adrs/ADR-0336-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md` now fixes the next post-detach startup seam too: the launcher or its approved shim must enter capability mode before handing control to later classify/scan/sanitize tool code, descendants inherit that mode and may not clear it, ambient absolute-path opens stay out after `cap_enter()`, and tools that cannot run on the preopened capability set stay out of this first lane unless a later explicit wrapper/broker contract earns them.
- [DECIDED] `adrs/ADR-0337-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md` now fixes the next hidden-inheritance seam too: after that post-detach capability boundary, the later worker inherits only the reviewed descriptor set, the launcher closes or spawn-closefroms every non-reviewed descriptor before handoff, `stdin` stays inert null/empty input only, and `stdout`/`stderr` stay launcher-owned observation channels or reviewed append-only log sinks instead of inherited parent-session surfaces.
- how do integrated devices (Bluetooth, webcams, FIDO/smart-card readers) fit the same posture without becoming exception folklore?

Risk: the baseline stays correct on paper, but fallback mechanics turn into ad-hoc convenience paths that recreate ambient device authority.

See: `docs/458-removable-media-and-usb-posture-by-profile.md`, `docs/279-usb-quarantine-and-removable-media-workflow.md`, `docs/207-input-authority-secure-attention-and-hid-risk.md`, `docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`, `docs/725-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md`, `docs/726-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md`, `docs/727-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md`, `docs/728-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md`, `docs/729-removable-media-local-fallback-keeps-owner-mode-mtime-xattr-fidelity-out-of-the-first-lane.md`, `docs/730-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md`, `docs/731-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md`, `docs/733-removable-media-local-fallback-attach-receipts-carry-observed-hints-and-keep-them-evidence-only.md`, `docs/734-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md`, `docs/735-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md`, `docs/736-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md`, `docs/737-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md`.

## 51) Export boundary drift: policy changes, redaction defaults, and exfil risk [DECIDED]

The product-shape default is now decided in `adrs/ADR-0056-export-boundary-posture-by-profile.md`:

- **A** keeps fleet evidence export brokered, ticket-shaped, encrypted for external recipients, and review-heavy when the boundary expands.
- **B** keeps evidence sharing user-mediated, recipient-visible, and redaction-aware in the trusted UI rather than ambient background helpers.
- **C** prefers Derive-managed export lanes while keeping classic support/upload tooling as an explicit adapter fallback.
- **D** keeps factory/regulatory export minimal, redacted, encrypted, strongly approved, and transparency-aware by default.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, exports revert to folklore (“someone emailed a tarball”), making incidents less explainable and turning support tooling into an exfiltration footgun.

See: `adrs/ADR-0056-export-boundary-posture-by-profile.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/433-export-policy-diff-as-review-surface.md`, `spec/export.policy.schema.json`, `spec/export.receipt.schema.json`, `spec/export.policy.diff.schema.json`.

## 52) Attestation admission policy drift: keep “what is gated?” stable and reviewable [DECIDED]

The product-shape default is now decided in `adrs/ADR-0059-platform-provenance-and-attestation-admission-posture-by-profile.md`:

- **A** keeps measured platform posture receipted and available to gate sensitive admissions by default.
- **B** keeps measured posture visible and exportable to the human/support path, while limiting default attestation gating to sensitive operations rather than ordinary local use.
- **C** keeps measured posture optional/exportable, with explicit gates available where a deployment chooses them.
- **D** keeps measured posture retained and available for production enrollment, maintenance access, and sensitive release gates by default.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, attestation becomes theater — either a dashboard nobody depends on, or a hidden hard requirement that quietly breaks workstation/general-OS viability.

See: `adrs/ADR-0059-platform-provenance-and-attestation-admission-posture-by-profile.md`, `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md`, `docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/388-remote-attestation-admission-and-enrollment.md`, `docs/440-attestation-admission-policy-diff-as-review-surface.md`, `spec/attestation.admission.policy.schema.json`, `spec/attestation.admission.policy.diff.schema.json`.

## 53) Egress evidence budgets + learning ergonomics [DECIDED]

The archive now fixes the core learn/audit convergence contract in `adrs/ADR-0095-network-learn-audit-convergence-contract.md`:

- learn/audit runs are explicit **bounded sessions** with both time and event limits,
- `net-flow-summary` is the compact **evidence-only** review surface derived from `net-flow-receipt` plus optional `net-dns-query-receipt` evidence,
- `policy-suggestion` remains the reviewable proposed patch, and `net-egress-policy` remains the authoritative enforced object,
- and class broadening / hostname wildcarding / CIDR broadening / DNS-mediation relaxations require stronger review by default in the stricter product shapes.

What remains open is implementation detail: exact aggregation heuristics, exact CLI/UI, and exact approval thresholds.

Risk: without this decision, the network evidence lane would either become packet-capture folklore or a permanent permissive “audit mode.”
The contract now blocks both failure modes while keeping convergence practical.

See: `adrs/ADR-0095-network-learn-audit-convergence-contract.md`, `docs/505-network-learn-audit-convergence-contract.md`, `docs/328-learned-network-policies-from-flow-receipts.md`, `docs/305-dns-mediation-and-hostname-binding.md`, `docs/504-dns-receipt-detail-and-export-posture-by-profile.md`, `docs/369-consent-ledgers-and-permission-review-ui.md`, `spec/net.flow.receipt.schema.json`, `spec/net.dns.query.receipt.schema.json`, `spec/net.flow.summary.schema.json`.

## 54) Listen-broker evidence budget + developer/share ergonomics [DECIDED]

The archive now fixes the temporary-sharing boundary in `adrs/ADR-0152-relay-backed-publish-sessions-for-temporary-service-sharing.md`:

- durable non-loopback host exposure stays on the existing `net.listen.policy` / `net.listen.grant` / `net.listen.receipt` lane,
- B/C temporary sharing now has a separate typed `net.publish.session` envelope instead of shadow tunnels or ad-hoc firewall edits,
- publish sessions must stay local-first, leased, and joined to authority + transport evidence,
- ADR-0153 then makes audience/publicness explicit too, so `organization-users`, `named-recipients`, `support-session-peer`, `public-webhook`, and `public-link` are typed postures instead of guesses hidden behind `internet`,
- ADR-0154 then makes temporary publish sessions explicitly reboot-cleared and `new-session-with-fresh-authority`, so relay-backed sharing cannot silently auto-resume from remembered daemon/config state,
- ADR-0155 then makes public/org/support locator posture explicitly `session-scoped`, so reserved relay domains, custom DNS, or remembered public hostnames cannot quietly become the real durable-ingress surface,
- ADR-0156 then keeps secret-gated publish sessions redacted by requiring a separate `secret.receipt` handoff digest instead of letting query-token URLs, fragments, or pasted bearer links become the evidence surface,
- ADR-0157 then keeps that separate handoff secret `session-authority-bounded`, so a revoked or expired publish session cannot leave behind a still-valid secret as the real access channel,
- ADR-0158 then makes secret consumption explicit too, so `single-use-secret` means `single-successful-admission` while `shared-secret` remains `reusable-until-expiry`,
- ADR-0159 then makes support-peer publication subordinate to the exact support-session lane by requiring `authority.trigger = support-session` plus `authority.support_session_digest`,
- ADR-0160 then fixes access-model posture so `public-link` / `public-webhook` stay `relay-url` shaped while `support-peer` stays `peer-relay` shaped,
- ADR-0161 then fixes the private tailnet lane too, so `tailnet` / `tailnet-users` / `tailnet-identity` / `tailnet-device-name` stay `reverse-forward` shaped instead of borrowing public-share URL vocabulary,
- ADR-0162 then fixes the remaining audience-bound human-share lane too, so `organization-users` and `named-recipients` stay `relay-url` shaped instead of borrowing support-peer or tailnet vocabulary,
- ADR-0163 then requires audience-binding hints, so `provider-identity` / `organization-users` shares name `identity_provider_hint` and `named-recipients` shares name `recipient_hint` instead of leaving those audience labels hand-wavy,
- ADR-0182 then keeps those binding hints as inverse evidence too, so non-IdP and non-recipient lanes cannot borrow binding hints as spare metadata,
- ADR-0183 then keeps the already-typed organization-user lane exposure-coherent too, so `organization-users` can no longer say "coworkers only" while still claiming generic internet exposure,
- ADR-0184 then keeps the outward published-endpoint surface lease-frozen too, so the same bounded share can no longer quietly repoint hostname/path/audience/access posture underneath one `authority.lease_id`,
- ADR-0185 then keeps the compact publish-session envelope baseline-safe too, so backstage relay/admin diagnostics no longer ride directly on `evidence.diagnostic_artifact_digests` inside the bounded share receipt,
- ADR-0186 then removes free-text `evidence.notes` from that same compact envelope too, so commentary and backstage interpretation cannot reopen a prose side channel on the bounded receipt,
- ADR-0187 then replaces the old boolean visibility bit with required `evidence.visible_indicator_posture = durable-until-ended`, so a one-shot toast or transient banner cannot masquerade as the lifetime-visible active-share cue,
- ADR-0164 then requires `public-webhook` validation hints, so callback publication names `validation_hint` instead of leaving the receiver-side verification posture hidden in adapter folklore,
- ADR-0181 then keeps that same `validation_hint` lane webhook-only, so public-link, audience-bound human shares, and support-peer receipts cannot borrow callback-verification prose as a generic spare note field,
- ADR-0165 then fixes endpoint-hint grammar by requiring `hostname + port` for `relay-url` and `reverse-forward` while keeping `peer-relay` free of URL/host endpoint hints, so support-peer and tailnet lanes stop reusing public-share locator language,
- ADR-0167 then fixes relay-side locator value grammar too, so `uri-hint` values stay URI-shaped while `portal-object` / `object-path` / `opaque` values stay non-URI-shaped,
- ADR-0168 then keeps optional relay-side destination hints subordinate to that same relay locator, so URL-shaped shares keep `relay.destination_hint = relay.remote_locator.value` while `portal-object` / `object-path` / `opaque` destination hints stay non-URI-shaped,
- ADR-0169 then keeps the `relay-url` published-endpoint URL-hint family subordinate to the canonical endpoint tuple, so `url_hint` / `path_prefix` travel together and serialize the same `hostname + port + path_prefix` instead of becoming a second contradictory URL story,
- ADR-0170 then keeps the local-source `service_uri_hint` subordinate to the same local-first boundary, so optional local URI hints stay loopback-shaped, absolute, and free of userinfo/query/fragment instead of becoming a LAN/public target hint or a localhost credential string,
- ADR-0171 then keeps the canonical published host token subordinate to that same endpoint boundary, so optional `published_endpoint.hostname` stays lowercase + host-shaped instead of becoming a pasted URL, `host:port`, or localhost-style endpoint string,
- ADR-0173 then keeps the outward `relay-url` `published_endpoint.url_hint` securely web-shaped, so the most copyable public-facing hint stays lowercase `https` + authority-bearing and free of userinfo/query/fragment instead of reopening weaker or authority-obscuring URI folklore,
- ADR-0174 then keeps relay-side `uri-hint` locators non-web-shaped, so the relay locator cannot silently collapse into a second public endpoint URL beside that already-separated outward hint,
- ADR-0175 then keeps the canonical published path token decode-stable too, so `published_endpoint.path_prefix` stays URI-path-safe with no percent-encoding, raw spaces, or backslashes instead of reopening a second percent-decoding / cleanup ladder beside the typed endpoint tuple.
- ADR-0176 then keeps the authority lane singular and trigger-shaped too, so `trusted-ui`, `policy`, `operator-session`, and `support-session` publication each name one exact joined digest (`consent_receipt_digest`, `policy_decision_digest`, `operator_session_digest`, or `support_session_digest`) instead of mixing several authority-digest families in the same receipt.
- ADR-0178, ADR-0177 then keeps the same bounded authority instance directly addressable too, so every publish session now carries `authority.lease_id` instead of leaving revoke/query/support flows to rediscover the share through timestamps, relay hints, or adjacent authority evidence.
- ADR-0179 then keeps the authn story singular too, so `secret_handoff` cannot sit beside `none`, `provider-identity`, `support-session`, or `tailnet-identity` as a second hidden secret lane.
- `net-listen-receipt` stays summary-shaped rather than turning into a per-connection or tunnel-transcript database,
- and A/D do not inherit workstation/developer relay habits as a production ingress model.

What remains open is implementation detail, not the authority boundary:

- exact trusted-UI and CLI ergonomics for B/C share flows,
- exact relay adapters/providers worth shipping first,
- exact TLS termination defaults inside specific adapters,
- the final `identity_provider_hint` / `recipient_hint` / `validation_hint` vocabulary and roster-picker UX, once binding hints inverse evidence is fixed by ADR-0182,
- whether `named-recipients` should ultimately stay multi-scope or collapse to a narrower internal/external exposure rule, even after ADR-0183 fixed only `organization-users`,
- and which optional diagnostics/service-log joins are worth standardizing beyond the session envelope.

Risk: without this boundary, B/C users keep bypassing the broker with shadow tunnels while A/D quietly inherit those same habits as production folklore; even worse, “temporary” shares can quietly survive reboot or logout as remembered background endpoints, keep reappearing under reserved relay domains / remembered public hostnames that have become the real ingress surface, leak their usable secret through logs, screenshots, and support bundles because the publish-session receipt itself became the bearer channel, or leave behind a still-valid secret after the session authority has supposedly ended, or blur one-time handoffs into reusable secrets because `single-use-secret` never actually said what one use meant, or leave `support-peer` shares looking support-flavored without any exact `support_session_digest` proving which support session justified them, or flatten support handoffs and public callback/demo publication into the same generic tunnel-URL story because `access_model` never said whether the share was peer/session-shaped or URL-shaped, or leave private tailnet/device-name sharing speaking in public-share URL vocabulary even after the archive had already decided the internet lane separately, or leave ordinary audience-bound human shares looking like support-peer or private-device publication because `organization-users` / `named-recipients` never said what share shape they were supposed to keep, or keep audience-bound shares formally non-public while still being unable to explain which IdP or recipient binding actually held the gate because `identity_provider_hint` / `recipient_hint` never became part of the contract, or let `organization-users` say "coworkers only" while still claiming generic internet exposure even after the archive had already separated public-link, support-peer, and tailnet posture, or leave `public-webhook` shares looking callback-shaped without any durable clue about what the receiver was supposed to validate because `validation_hint` never became part of the contract, or let that same `validation_hint` field drift onto public-link, human-share, or support-peer receipts so callback-verification prose becomes a generic note slot again, or keep the now-distinct `relay-url`, `reverse-forward`, and `peer-relay` lanes reusing the same mixed URL/host locator hints because `hostname + port` and URL-only hints never got tied back to access model, or let `relay.remote_locator.kind` quietly smuggle URI/session/device grammar back into the wrong lane even after `published_endpoint` was made coherent, or let non-URI relay kinds hide copyable URL-looking value text in `relay.remote_locator.value` even after the kind itself was typed, or let an adjacent `relay.destination_hint` field reopen the same drift by carrying a second conflicting copy surface for URL-shaped shares or hidden URL-looking display text for support/tailnet lanes, or keep `relay-url` shares carrying a typed `hostname + port + path_prefix` tuple while `url_hint` quietly serializes some other host, port, or path, or keep that outward published-endpoint surface drifting under the same bounded lease so copied URLs and support trails disagree about which share instance the lease actually meant, or blur a compact publish-session envelope with backstage relay/admin diagnostics because `diagnostic_artifact_digests` let privileged investigation artifacts ride on an otherwise ship-safe share receipt, or keep the supposedly visible active share honest only as a boolean so a short-lived toast or banner can disappear while the share remains live, or let a supposedly local-first source hint quietly point at a LAN/public target or hide localhost credentials because `local_service.service_uri_hint` never had to stay loopback-shaped and secret-clean, or let the canonical `published_endpoint.hostname` field itself smuggle scheme-bearing URL text, `host:port`, or localhost text back into the supposedly typed published endpoint tuple, or let the canonical `published_endpoint.path_prefix` field still carry repeated separators or `.` / `..` segments that make later readers guess whether the typed path was supposed to be normalized before use, or let that same typed path field still carry `%2F` / `%2E`, raw spaces, or backslashes that force a second percent-decoding / cleanup ladder beside the receipt, or keep `relay.remote_locator.value` formally URI-shaped while still letting it reuse `http` / `https` public-endpoint grammar so the relay-side locator silently becomes a second web URL surface beside the already-separate outward endpoint hint, or leave a supposedly leased publish session with no required `authority.lease_id` so revoke/query/support flows have to infer the live bounded share instance from timestamps, hostnames, relay locators, or operator-session folklore, or let support-session proof justify a non-support share shape so callback/demo or audience-bound URL publication starts wearing support authority language without actually being a support-peer handoff, or leave `authn_mode` saying `none`, `provider-identity`, `support-session`, or `tailnet-identity` while `secret_handoff` still carries a second hidden secret lane that support/export/policy have to rediscover by folklore. ADR-0180 now also keeps the reserved maintenance trigger digest-empty, so `authority.trigger = maintenance` cannot quietly borrow trusted-UI/policy/operator/support proof as placeholder maintenance-window evidence.

See: `adrs/ADR-0152-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `adrs/ADR-0153-publish-session-audience-binding-and-publicness-posture.md`, `adrs/ADR-0154-publish-session-end-conditions-and-no-auto-resume-posture.md`, `adrs/ADR-0155-publish-session-session-scoped-locator-posture.md`, `adrs/ADR-0156-publish-session-redacted-locators-and-separate-secret-handoff.md`, `adrs/ADR-0157-publish-session-secret-lifetime-coupled-to-session-authority.md`, `adrs/ADR-0158-publish-session-secret-consumption-semantics.md`, `adrs/ADR-0159-publish-session-support-peer-shares-require-support-session-authority.md`, `adrs/ADR-0160-publish-session-access-model-posture-boundary.md`, `adrs/ADR-0161-publish-session-tailnet-shares-stay-reverse-forward-shaped.md`, `adrs/ADR-0162-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`, `adrs/ADR-0163-publish-session-audience-bound-shares-require-binding-hints.md`, `adrs/ADR-0164-publish-session-public-webhook-shares-require-validation-hints.md`, `adrs/ADR-0165-publish-session-endpoint-hints-follow-access-model.md`, `adrs/ADR-0166-publish-session-relay-remote-locator-kind-follows-access-model.md`, `adrs/ADR-0167-publish-session-relay-remote-locator-values-follow-locator-kind.md`, `adrs/ADR-0168-publish-session-destination-hint-follows-remote-locator.md`, `adrs/ADR-0169-publish-session-url-hints-follow-endpoint-tuple.md`, `adrs/ADR-0170-publish-session-local-service-uri-hints-stay-loopback-shaped.md`, `adrs/ADR-0171-publish-session-published-endpoint-hostnames-stay-host-shaped.md`, `adrs/ADR-0172-publish-session-path-prefixes-stay-normalized.md`, `adrs/ADR-0173-publish-session-relay-url-hints-stay-https-shaped.md`, `adrs/ADR-0174-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md`, `adrs/ADR-0175-publish-session-path-prefixes-stay-uri-path-safe.md`, `adrs/ADR-0176-publish-session-authority-joins-follow-trigger.md`, `adrs/ADR-0177-publish-session-authority-stays-lease-addressable.md`, `adrs/ADR-0179-publish-session-secret-handoffs-follow-authn-mode.md`, `adrs/ADR-0181-publish-session-validation-hints-stay-webhook-only.md`, `adrs/ADR-0184-publish-session-published-endpoint-surface-stays-lease-frozen.md`, `adrs/ADR-0185-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md`, `adrs/ADR-0187-publish-session-visible-indicators-stay-durable-until-ended.md`, `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`, `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`, `docs/565-publish-session-session-scoped-locator-posture-boundary.md`, `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`, `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md`, `docs/568-publish-session-secret-consumption-semantics-boundary.md`, `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md`, `docs/570-publish-session-access-model-posture-boundary.md`, `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`, `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`, `docs/573-publish-session-audience-bound-shares-require-binding-hints.md`, `docs/574-publish-session-public-webhook-shares-require-validation-hints.md`, `docs/575-publish-session-endpoint-hints-follow-access-model.md`, `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`, `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md`, `docs/578-publish-session-destination-hint-follows-remote-locator.md`, `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`, `docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md`, `docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md`, `docs/597-publish-session-visible-indicators-stay-durable-until-ended.md`, `adrs/ADR-0188-publish-session-post-end-access-stays-fail-closed.md`, `adrs/ADR-0189-publish-session-revocation-affordances-stay-same-surface-durable.md`, `adrs/ADR-0190-publish-session-return-paths-stay-trusted-ui-persistent.md`, `adrs/ADR-0191-publish-session-management-return-paths-stay-lease-exact.md`, `adrs/ADR-0192-publish-session-post-end-management-return-stays-lease-exact-ended.md`, `adrs/ADR-0193-publish-session-ended-states-stay-terminal-cause-exact.md`, `docs/598-publish-session-post-end-access-stays-fail-closed.md`, `docs/599-publish-session-revocation-affordances-stay-same-surface-durable.md`, `docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md`, `docs/601-publish-session-management-return-paths-stay-lease-exact.md`, `docs/602-publish-session-post-end-management-return-stays-lease-exact-ended.md`, `docs/603-publish-session-ended-states-stay-terminal-cause-exact.md`, `docs/580-publish-session-local-service-uri-hints-stay-loopback-shaped.md`, `docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md`, `docs/582-publish-session-path-prefixes-stay-normalized.md`, `docs/583-publish-session-relay-url-hints-stay-https-shaped.md`, `docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md`, `docs/585-publish-session-path-prefixes-stay-uri-path-safe.md`, `docs/586-publish-session-authority-joins-follow-trigger.md`, `docs/587-publish-session-authority-stays-lease-addressable.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/255-policy-constrained-transports.md`, `spec/net.publish.session.schema.json`. Current exactness posture also now includes `lifecycle.post_end_access_posture = explicit-ended-or-fresh-share` so stale temporary-share handles cannot silently bind to a successor session or generic launcher after the lease ends, plus `evidence.revocation_affordance_posture = same-surface-durable-until-ended` so a live-share cue cannot coexist with a buried or vanishing stop path, plus `evidence.management_return_path_posture = trusted-ui-persistent-until-ended` so leaving the active-share surface cannot strand a still-live share behind browser back/history luck, a one-shot toast, or route rediscovery, plus `evidence.management_return_binding = lease-exact` so that stable return affordance lands on the exact live `authority.lease_id` instead of a generic share home, nearest-current-share view, or successor lease, plus `lifecycle.post_end_management_return_posture = exact-ended-state-if-followed` so any surviving trusted-UI return path or management deep link that is followed after end still resolves to the exact ended-share state for that same lease instead of losing bounded-share identity in a generic share hub, successor lease, or blank miss, and plus `lifecycle.terminal_end_condition` so that explicit ended bounded-share state keeps the exact terminal cause instead of flattening lease expiry, manual revoke, local-service loss, session end, or host reboot into a vague terminal label.

## 55) Remote assistance implementation details after the profile default

The product-shape default and the recording/detail/export posture are now decided, but the implementation lane still needs sharper answers:

- which scopes require quorum by default (remote control, TTY input recording, file export, maintenance-window enablement)?
- how do persistent portal/backend restore tokens map onto Derive lease/policy objects without silently reintroducing ambient authority?
- what is the preferred relay/transport posture so support remains outbound-first where possible and does not punch surprise holes in ingress policy?
- what are the exact retention windows and richer capture artifact shapes once a stronger maintenance/incident lane wants more than `support.session` plus output-only TTY evidence?

Risk: the product boundary stays correct on paper, but implementation details could still drift into stealthy persistence, ambient richer capture, or folklore tunnels.

ADR-0206 now fixes the first expensive ambiguity: remote assistance recording/detail/export posture stays profile-shaped, `support.session` remains the mandatory baseline evidence object, output-only TTY recording is the normal stronger lane, and TTY input capture stays a higher-risk explicit scope instead of a universal default. A new cross-lane invariant also helps here: the authoritative temporary-authority object stays lane-specific, while `lease.envelope`, `lease.issue.receipt`, and `lease.use.receipt` remain metadata / evidence-only surfaces. That keeps remembered tokens, restore handles, and later operation receipts from silently becoming the authority object.

See: `adrs/ADR-0206-remote-assistance-recording-detail-and-export-posture-by-profile.md`, `docs/461-remote-assistance-posture-by-profile.md`, `docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md`, `docs/291-remote-assistance-sessions-as-evidence.md`, `docs/292-terminal-session-recording-as-evidence.md`, `docs/256-consent-ux-contract.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/281-network-egress-broker-and-consent.md`.

## 56) Crypto compatibility agents and remembered approvals boundary [DECIDED]

The product-shape default remains the same: brokered, non-exportable crypto use is the reviewed center.
The first expensive compatibility ambiguity is now closed:

- classic `ssh-agent` / `gpg-agent` paths may exist only as typed projections over the brokered lane
- the baseline projection scope is `local-session-only`
- remembered approvals stay `same-lease-only`
- remote agent forwarding remains out of the reviewed baseline and needs a future explicit lane if ever standardized

Remaining implementation detail work is narrower now:

- default receipt detail/redaction posture by profile
- which key classes require quorum beyond the product baseline
- how heterogeneous backends share one broker identity surface without policy fragmentation

Risk: reduced, because the archive no longer leaves ambient compatibility-agent authority open as an accidental default.

See: `adrs/ADR-0293-crypto-compatibility-agents-stay-local-session-projections-and-not-ambient-remote-authority.md`, `docs/703-crypto-compatibility-agents-stay-local-session-projections-and-not-ambient-remote-authority.md`, `docs/462-private-key-and-crypto-op-posture-by-profile.md`, `docs/306-crypto-operations-portal-and-split-keys.md`, `docs/392-crypto-key-policies-and-nonexportable-handles.md`, `docs/437-split-secrets-brokers.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`.

## 57) Human identity / home-state implementation details after the profile default

The product-shape default is now decided, but the implementation lane still needs sharper answers:

- what is the minimal canonical `user.record` surface versus adapter layer for existing host-account ecosystems?
- how do group membership, per-machine exceptions, and admin roles compose with portable identity without turning the record into non-portable host config?
- what are the default unlock sources and evolution rules (password only, brokered credential, TPM/policy-authorize, recovery path) without creating brittle PCR traps?
- how should whole-home exceptional leases, project mounts, and backup/export/import semantics work so users do not fall back to ambient whole-home sharing?

Risk: the product boundary stays correct on paper, but implementations drift into always-mounted homes, folklore compatibility hacks, or opaque unlock failures.

See: `docs/463-human-identity-and-home-state-posture-by-profile.md`, `docs/269-portable-home-areas-and-user-records.md`, `docs/270-appvm-storage-private-volatile-and-home-areas.md`, `docs/272-sealed-secrets-attested-unsealing.md`, `docs/386-userenv-activation-plans-and-receipts.md`.

## 58) Backup / restore implementation details after the profile default

The product-shape default is now fixed. Remaining work is implementation detail:

- exact restore-drill cadence by data class / product shape
- default backup-encryption posture and key-availability rules under incident conditions
- restore-target quarantine semantics (mount-only vs cold-start vs full rehearsal)
- digest-first vs detail-rich receipt budgets and support-export redaction
- when, if ever, a break-glass full-host image lane is worth standardizing for otherwise replaceable systems

Risk: the archive agrees on posture but still ships a recovery lane that is too awkward, too privacy-toxic, or too expensive to run often enough.

See: `docs/464-backup-and-restore-posture-by-profile.md`, `docs/316-backups-and-restores-as-derived-operations.md`, `docs/317-restore-drills-and-continuous-recovery-testing.md`, `docs/413-zfs-replication-resume-bookmarks-and-receipted-backups.md`.

## 59) Data-at-rest implementation details after the profile default

The product-shape default is now fixed. Remaining work is implementation detail:

- exact dataset split between boot-critical / device-available / login-bounded / production state
- default unlock-source evolution rules (passphrase, TPM/policy-authorize, brokered recovery, quorum maintenance) without brittle PCR traps
- how strict to be about `keylocation=file://...` or `http(s)://...` adapter lanes and what evidence/redaction they require
- break-glass vs ordinary unattended unlock controls, rate limits, and receipt vocabulary
- re-key / migration / escrow workflows that remain operable under incident pressure

Risk: the archive agrees on posture but still ships unlock/recovery workflows that are too brittle, too opaque, or too convenience-biased to survive real incidents.

See: `docs/465-data-at-rest-posture-by-profile.md`, `docs/409-zfs-encryption-and-key-management.md`, `docs/250-breakglass-and-recovery-workflows.md`, `docs/272-sealed-secrets-attested-unsealing.md`, `docs/463-human-identity-and-home-state-posture-by-profile.md`.

## 60) Export-boundary implementation details after the profile default

The product-shape default is now fixed. Remaining work is implementation detail:

- exact `risk_flags` vocabulary for `export.policy.diff` so review catches real boundary expansion without alert fatigue
- which export-policy changes require two-person integrity by default by profile/class (recipient broadening, consent relaxation, raw-blob enablement, transparency downgrade)
- transport-independent ticket/case semantics across adapters without baking in one helpdesk
- privacy-safe transparency metadata defaults (hashed ticket ids/recipients, inclusion requirements, retention)
- default redaction catalogs and raw-blob exception lanes that stay useful without becoming exfil folklore

Risk: the archive agrees on posture but still ships an export lane that is too permissive, too noisy, or too adapter-fragmented to keep evidence sharing safe and explainable.

See: `docs/466-export-boundary-posture-by-profile.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/433-export-policy-diff-as-review-surface.md`, `docs/195-deterministic-redaction-transforms.md`, `docs/254-export-transparency-logs.md`.

## 61) Operator-access implementation details after the profile and recording defaults

The product-shape admission default is now fixed, and the product-shaped recording/detail/export default is now fixed in `adrs/ADR-0207-operator-access-recording-detail-and-export-posture-by-profile.md`. Remaining work is implementation detail:

- exact role-shell / forced-command vocabulary and how much shell surface restricted roles really need
- finer role/class retention and stronger-capture rules beyond the accepted metadata-vs-output-only product default
- offline or partitioned operation when the broker/CA is unreachable without reintroducing standing credentials
- workstation local-elevation UX details: secure-attention hooks, consent caching limits, and how far doas/polkit-style adapters may go
- renewal / revoke / expiry semantics for long-running sessions and what survives network partitions

Risk: the archive agrees on posture but still ships an operator-access lane that is too brittle, too privacy-toxic, or too awkward to replace static-key folklore in practice.

See: `docs/467-operator-access-posture-by-profile.md`, `docs/617-operator-access-recording-detail-and-export-posture-by-profile.md`, `docs/311-operator-access-leases-and-ssh-certs.md`, `docs/292-terminal-session-recording-as-evidence.md`, `docs/236-breakglass-and-recovery-mode.md`, `docs/147-doas-minimal-privilege-escalation.md`.

## 62) Trustworthy-time implementation details after the profile default

The product-shape default and degraded-time workflow boundary are now fixed. Remaining work is implementation detail:

- signed offline-time token envelope, approval semantics, and replay/retention behavior
- RTC-bounds and LKGT persistence choices that resist rollback without turning failures into lockout traps
- workstation trusted-UI wording / alert cadence / temporary degraded allowances for sensitive operations
- monitor/escalation behavior when authenticated sources disagree or disappear for long periods

Risk: the archive agrees on posture but still ships a trustworthy-time lane that is either too brittle for real operations or too weak/noisy to keep expiry and freshness meaningful.

See: `docs/468-trustworthy-time-posture-by-profile.md`, `docs/702-time-requirement-degraded-response-stays-explicit-and-proof-bundle-bound.md`, `docs/722-time-source-policy-profile-floors-stay-finite-and-profile-mapped.md`, `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`, `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`, `docs/308-time-monitors-and-lie-detection.md`, `docs/438-time-source-policy-diff-as-review-surface.md`.

## 62a) Breakglass implementation details after the profile and recording defaults

The product-shape default is now fixed, the product-shaped recording/detail/export default is now fixed in `adrs/ADR-0208-breakglass-recording-detail-and-export-posture-by-profile.md`, the concrete session-method boundary is now fixed in `ADR-0296`, and the closeout truth boundary is now fixed in `adrs/ADR-0295-breakglass-closeout-stays-explicit-repair-outcome-and-receipt-joined.md`. Remaining work is implementation detail now that the `console|serial|ssh` method split is settled:

- exact recovery-console / rescue-shell UX beyond the accepted `session-open-before-first-prompt` recording start boundary
- offline approval and attestation-gate ceremony details when time, broker reachability, or normal trust roots are degraded
- whether a dedicated adapter-side-evidence artifact family is worth standardizing now that `ADR-0300` fixed that the baseline breakglass receipt now stays adapter-thin, keep adapter/runtime detail as redacted side evidence, and keep `notes` from becoming a loophole for console URLs, session ids/tokens, image locators, or copied console-entry hints
- whether the future richer adapter-side-evidence family should ever become first-class support-bundle contract material now that `ADR-0301` keeps official breakglass support handoff authority-first on `breakglass_receipt_digests` and leaves richer adapter/runtime material supplementary until that family actually exists
- bootstrap receipt joins are now decided through `ADR-0297`, `ADR-0298`, and `ADR-0299`: breakglass proof keeps exact `boot.override.receipt` / `reset.receipt` digests, plural joins stay earliest-to-latest-pre-session-enabling-only, and the paired one-time-boot case records `boot.override.receipt` then `reset.receipt` rather than UI-order folklore.
- retention windows and richer review UX for emergency-session artifacts beyond the accepted metadata-vs-output-only product default, now that `ADR-0302` keeps supplementary adapter/runtime exports receipt-first on typed export/redaction/transport proof instead of raw attachment folklore, `ADR-0303` keeps those supplementary receipt chains authority-anchored to exact `breakglass_receipt_digests` instead of letting them float as self-authenticating breakglass proof, `ADR-0304` keeps portable supplementary evidence artifactized instead of letting live control locators become the archive-facing story, and `ADR-0305` keeps that same portable story payload-anchored to at least one passive artifact digest or accepted case-object proof instead of stopping at receipt-only handling proof
- accepted case-object proof is now narrowed by `ADR-0306`, `ADR-0307`, `ADR-0308`, `ADR-0309`, and `ADR-0310`: the accepted-case-object payload anchor stays object-exact, validator-pinned when visible, and preserves remote-protection / remote-locator continuity; remote-locator continuity must stay tied to the same accepted object revision/version rather than parent case/container browse URLs.
- `ADR-0311` now settles the next follow-up floor too: when the adapter can later metadata-check the same accepted object revision/version without re-downloading the body, the canonical follow-up object is typed `transport.reverification.receipt` with `reverification.body_downloaded = false` rather than screenshots or body-download folklore
- the next narrower question is now whether some profiles should eventually require periodic accepted-case-object metadata-only reverification or a stronger remote digest echo when the adapter can obtain one metadata-first
- auto-revoke, UI ceremony, and recovery-ready rollback ergonomics under network partitions or untrusted time now that `breakglass.receipt.repair_outcome` fixes the closeout truth boundary

Risk: the archive agrees on posture but still ships a breakglass lane that is too invisible, too privacy-toxic, or too awkward to replace rescue-shell folklore in practice.

See: `docs/236-breakglass-and-recovery-mode.md`, `docs/250-breakglass-and-recovery-workflows.md`, `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`, `docs/704-breakglass-interactive-sessions-carry-tty-recording-proof-and-start-at-session-open.md`, `docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md`, `docs/708-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md`, `docs/709-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md`, `docs/473-installation-and-recovery-posture-by-profile.md`, `docs/292-terminal-session-recording-as-evidence.md`, `docs/474-high-risk-approval-posture-by-profile.md`.

## 67) Packet capture sessions + export posture after the raw-packet boundary [DECIDED]

The authority boundary is now decided in `adrs/ADR-0096-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`, and the canonical session/export contract is now pinned in `adrs/ADR-0097-packet-capture-session-and-summary-first-export-boundary.md`:

- packet capture remains a stronger explicit authority lane rather than ordinary networking,
- bounded capture now uses authoritative `packet.capture.session` objects rather than shell-command folklore,
- session metadata / `packet.capture.summary` objects are the normal review and support surfaces,
- the authoritative session now carries a typed `packet.capture.selector` rather than a backend-specific free-form filter string,
- and raw packet payload export stays an explicit stronger exception rather than the default incident/support handoff.
- stronger sideband/decryption-bearing packet-capture artifacts now stay on a typed safe-open `content.import.*` lane and normalize before ordinary promotion/export,
- and incident/support bundles now join packet-capture participation through typed session/summary/import/redaction receipt digests instead of default raw-packet members.
- and stronger normalized raw-byte exports now stay proof-bound on the generic export lane via typed packet-capture policy/receipt profiles rather than “upload the `.pcapng`” folklore.
- and stronger `packet.capture.normalized` exports now also require explicit non-auto approval evidence on the generic consent lane rather than hiding behind an ambient export path.
- and completed stronger `packet.capture.normalized` exports now also require typed transport evidence and may not terminate as `destination.type = file`, so a local save no longer counts as the completed stronger handoff.
- and final stronger `packet.capture.normalized` export now also requires recipient acceptance evidence, so the chain ends at `delivery_state = recipient-accepted` plus `transport_acceptance_receipt_digest` rather than assuming transport success means the recipient-side lane actually accepted the artifact.
- and the stronger approval/transport/export chain must now stay digest-stable, so `consent.request.action.artifact_digest`, `transport.receipt.artifact.digest`, and `export.receipt.artifact.digest` all keep the same normalized digest instead of drifting into related-but-different derivatives.
- and stronger packet export approval is now destination-bound too, so `consent.request.action.destination`, `transport.receipt.destination`, `transport.acceptance.receipt.recipient`, and `export.receipt.destination` keep the same approved recipient identity instead of allowing retargeted delivery after approval.
- and stronger packet recipient acceptance is now digest-confirming too, so `transport.acceptance.receipt.acceptance.remote_artifact_digest` must echo the same normalized artifact digest instead of treating “accepted something in CASE-8841” as good enough final evidence.
- and stronger packet export closure is now remote-object-continuous too, so `transport.receipt.result.remote_id`, `transport.acceptance.receipt.acceptance.remote_reference`, and `export.receipt.adapter.remote_id` must stay on the same remote object identifier instead of letting the proof chain drift across multiple attachments in the same case.
- and stronger packet export closure is now remote-validator-continuous too, so `transport.receipt.result.remote_validator`, `transport.acceptance.receipt.acceptance.remote_validator`, and `export.receipt.adapter.remote_validator` must stay on the same remote validator instead of collapsing the stronger proof chain back to object id alone.
- and stronger packet export closure is now remote-protection-shaped too, so `transport.acceptance.receipt.acceptance.remote_protection` and `export.receipt.adapter.remote_protection` must stay on the same remote protection posture instead of treating recipient acceptance alone as durable remote evidence.
- and stronger packet export closure is now remote-locator-continuous too, so `transport.receipt.result.remote_locator`, `transport.acceptance.receipt.acceptance.remote_locator`, and `export.receipt.adapter.remote_locator` must stay on the same remote locator instead of leaving later evidence retrieval to portal folklore. See `adrs/ADR-0114-packet-capture-strong-export-remote-locator-continuity-boundary.md`, `docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`.

What remains open is implementation detail, not the default workflow.

Risk: without this boundary, teams quietly standardize on mystery `.pcap` blobs, packet-capture authority drifts away from leases and receipts, and A/B/C/D lose their claimed evidence/export posture under incident pressure.

See: `adrs/ADR-0096-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`, `adrs/ADR-0097-packet-capture-session-and-summary-first-export-boundary.md`, `adrs/ADR-0098-packet-capture-summary-review-surface-boundary.md`, `adrs/ADR-0099-packet-capture-selector-compiler-boundary.md`, `adrs/ADR-0100-packet-capture-local-artifact-metadata-and-retention-boundary.md`, `adrs/ADR-0101-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, `adrs/ADR-0105-packet-capture-strong-export-approval-evidence-boundary.md`, `adrs/ADR-0106-packet-capture-strong-export-transport-boundary.md`, `adrs/ADR-0107-packet-capture-strong-export-digest-stability-boundary.md`, `adrs/ADR-0108-packet-capture-strong-export-recipient-acceptance-boundary.md`, `adrs/ADR-0109-packet-capture-strong-export-destination-bound-approval-boundary.md`, `adrs/ADR-0110-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`, `adrs/ADR-0111-packet-capture-strong-export-remote-object-continuity-boundary.md`, `adrs/ADR-0112-packet-capture-strong-export-remote-validator-continuity-boundary.md`, `adrs/ADR-0113-packet-capture-strong-export-remote-protection-posture-boundary.md`, `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`, `docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/508-packet-capture-summary-review-surface-boundary.md`, `docs/509-packet-capture-selector-compiler-boundary.md`, `docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md`, `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`, `docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`, `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`, `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/516-packet-capture-strong-export-transport-boundary.md`, `docs/517-packet-capture-strong-export-digest-stability-boundary.md`, `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`, `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`, `docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`, `docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`, `docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`, `docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/216-incident-snapshots-and-support-bundles.md`.

## 67a) Typed remote reverification for stronger packet export [DECIDED]

The archive now fixes the **remote reverification boundary** in `adrs/ADR-0115-packet-capture-strong-export-remote-reverification-boundary.md`:

- later follow-up on stronger `packet.capture.normalized` export now uses typed `transport.reverification.receipt` evidence rather than screenshots or ad-hoc portal clicking,
- canonical packet-specific reverification is metadata-only (`reverification.body_downloaded = false`),
- and the reverification receipt must stay aligned with the same accepted remote validator / protection posture / locator.

What remains open is implementation detail, not the boundary:

- exact adapter support for metadata-only re-check APIs,
- whether remote digest echo should ever become mandatory for reverification,
- and whether non-packet export classes should reuse the same typed reverification receipt.

Risk: without this boundary, later support or regulatory review slides back to screenshots, UI clicking, or another raw-byte download just to re-check the same accepted remote evidence.

See: `adrs/ADR-0115-packet-capture-strong-export-remote-reverification-boundary.md`, `docs/525-packet-capture-strong-export-remote-reverification-boundary.md`, `spec/transport.reverification.receipt.schema.json`, `spec/packet.capture.export.transport.reverification.receipt.profile.schema.json`.

## 68) Guided incident reproduction + safe-open workflows [DECIDED]

The archive now fixes the **safe-open support-bundle intake and incident-reproduction boundary** in `ADR-0088` / `adrs/ADR-0088-safe-open-support-bundle-intake-and-repro-boundary.md`:

- foreign support bundles and similar risky investigation artifacts enter through typed `content.import.plan` / `content.import.receipt` lanes rather than ad-hoc host opening,
- the canonical support path is `execution.isolation = microvm`, `execution.network = none`, and `execution.lifetime = disposable`,
- and deeper reproduction remains a derived operation inside a disposable workspace rather than promoting imported bundle bytes into host authority.

What remains open is implementation detail, not the default boundary:

- exact UI/UX for previewing `incident.timeline` and `bundle.payload.manifest` before opening payload members,
- how much replay polish belongs in generic disposable workspaces versus dedicated support tooling,
- and which compatibility adapters, if any, deserve a documented `jail` or `host-adapter` fallback.

Risk: without this boundary, operators drift back to opening foreign tarballs on the host, support bundles silently become quasi-authoritative, and incident reproduction collapses into shell folklore instead of receipts and disposable replay lanes.

See: `adrs/ADR-0088-safe-open-support-bundle-intake-and-repro-boundary.md`, `docs/498-safe-open-support-bundle-intake-and-repro-boundary.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/267-sanitization-portal-and-disposable-sandboxes.md`, `docs/421-disposable-workspaces-and-template-microvms.md`, `docs/220-operational-time-travel-debugging.md`, `spec/content.import.plan.schema.json`, `spec/content.import.receipt.schema.json`, `spec/content.import.support-bundle.plan.schema.json`, `spec/content.import.support-bundle.receipt.schema.json`.

Recent attestation/breakglass work removed one more hidden resolver too: post-breakglass ordinary resumption now carries `relevant_breakglass_receipt_digest` when breakglass materially formed the barrier, that exact breakglass join stays same-host bound to the pinned `attestation.receipt`, and the portable story is now time-ordered too: the pinned `attestation.receipt.created_at` must be strictly later than the breakglass receipt `created_at`, while the later ordinary receipt must not predate the pinned attestation receipt. The next narrow cut is no longer join discovery or subject binding; it is whether stale post-breakglass ordinary attempts deserve a dedicated typed denial surface instead of generic failure prose.
- [DECIDED] `ADR-0194` + `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` fix one canonical current-stack map for the recent `docs/593-*` through `docs/603-*` publish-session tightening cluster so the archive does not rely on stale local companion lists.

- `ADR-0208` now requires breakglass recording/detail/export posture to stay profile-shaped so emergency shell/recovery evidence no longer drifts between invisible rescue folklore and one universal panic recorder.
- `ADR-0204` now requires stale supersession denials to carry observed current-head evidence plus `fresh-explicit-supersession-required` recovery posture.
- `ADR-0205` now requires fresh stale-target recovery acts to stay denial-joined and head-pinned through `recovery.mode = from-stale-supersession-denial`, `stale_denial_receipt_digest`, `expected_current_receipt_digest`, `expected_current_candidate_digest`, and `expected_current_authoritative_origin_digest` instead of drifting into generic retry folklore.


## Reviewed post-detach process launch context

The next first-lane removable-media cut is now accepted in `adrs/ADR-0338-removable-media-local-fallback-post-detach-process-launch-context-stays-reviewed-and-ambient-free.md` and `docs/749-removable-media-local-fallback-post-detach-process-launch-context-stays-reviewed-and-ambient-free.md`.
After the descriptor set is closed-world, the later worker must also start with `reviewed-minimal-env-no-inherited-parent-env`, `launcher-reviewed-argv-no-media-derived-args`, and `launcher-owned-empty-workdir-no-ingest-store-cwd`.
That means parent environment is not inherited wholesale, media-derived names do not become worker arguments, and cwd is launcher-owned empty scratch rather than `/ingest`, the authoritative store, or the parent cwd.

## Pinned post-detach executable identity

The next first-lane removable-media cut is now accepted in `adrs/ADR-0339-removable-media-local-fallback-post-detach-executable-identity-stays-launcher-pinned-and-path-search-free.md` and `docs/750-removable-media-local-fallback-post-detach-executable-identity-stays-launcher-pinned-and-path-search-free.md`.
After reviewed descriptors plus reviewed env/argv/cwd, the later worker must also use `launcher-resolved-executable-digest-no-path-search` and `receipt-records-executable-and-wrapper-digests`.
That means `PATH`, cwd, mutable package state, media-derived executable names, and implicit helper/plugin discovery do not choose the code that processes the preserved subject; helper/plugin discovery stays `no-implicit-helper-or-plugin-discovery` unless a later explicit wrapper/broker contract admits it.

## Pinned post-detach runtime dependency closure

The next first-lane removable-media cut is now accepted in `adrs/ADR-0340-removable-media-local-fallback-post-detach-runtime-dependency-closure-stays-launcher-pinned-and-loader-path-free.md` and `docs/751-removable-media-local-fallback-post-detach-runtime-dependency-closure-stays-launcher-pinned-and-loader-path-free.md`.
After executable identity is pinned, the later worker must also use `launcher-pinned-runtime-dependency-closure-no-ambient-loader-search` and `receipt-records-runtime-dependency-closure-digest`.
That means `LD_LIBRARY_PATH`, cwd-relative library lookup, `/ingest` or media-derived library paths, host-global loader hints, and mutable package state do not choose runtime code; dynamic-loader posture stays `no-ld-library-path-cwd-or-media-derived-loader-inputs` unless a later explicit wrapper/broker contract admits richer dependency discovery.

## Launcher-fixed post-detach credential envelope

The next first-lane removable-media cut is now accepted in `adrs/ADR-0341-removable-media-local-fallback-post-detach-credential-envelope-stays-launcher-fixed-and-non-elevating.md` and `docs/752-removable-media-local-fallback-post-detach-credential-envelope-stays-launcher-fixed-and-non-elevating.md`.
After executable and runtime dependency identity are pinned, the later worker must also use `launcher-fixed-unprivileged-credential-envelope-no-supplementary-groups` and `receipt-records-worker-credential-envelope`.
That means the worker runs as the reviewed `derive-rm-worker:derive-rm-worker` envelope, supplementary groups stay `no-supplementary-groups`, and setuid/setgid/saved-ID or ambient privilege regain stays `no-setuid-setgid-saved-id-or-ambient-privilege-regain` unless a later explicit broker/helper lane admits and receipts privileged behavior.

## Launcher-supervised post-detach worker lifecycle

The next first-lane removable-media cut is now accepted in `adrs/ADR-0342-removable-media-local-fallback-post-detach-worker-lifecycle-stays-launcher-supervised-and-daemon-free.md` and `docs/753-removable-media-local-fallback-post-detach-worker-lifecycle-stays-launcher-supervised-and-daemon-free.md`.
After credentials are launcher-fixed and non-elevating, the later worker must also use `launcher-supervised-no-daemon-or-orphan-descendants` and `receipt-records-worker-exit-and-descendant-reap`.
That means background descendants and unreviewed subprocesses stay `no-background-descendants-or-unreviewed-subprocesses`, and the launcher must `launcher-reaps-entire-worker-tree-before-receipt` so derivative receipt authority does not race a still-running helper or orphaned process tree.

## Launcher-enforced post-detach resource envelope

The next first-lane removable-media cut is now accepted in `adrs/ADR-0343-removable-media-local-fallback-post-detach-resource-envelope-stays-launcher-enforced-and-receipt-visible.md` and `docs/754-removable-media-local-fallback-post-detach-resource-envelope-stays-launcher-enforced-and-receipt-visible.md`.
After worker lifecycle is launcher-supervised and daemon-free, the later worker must also use `launcher-enforced-resource-envelope-no-unbounded-worker-consumption` and `receipt-records-resource-envelope-and-observed-usage`.
That means CPU time, wall clock, memory, open-file count, process count, scratch bytes, and declared derivative-output bytes are launcher-fixed before tool mainline starts; `declared-derivative-output-size-bound-before-receipt` keeps the single declared sink bounded, and `resource-limit-hit-fails-closed-no-derivative-authority` keeps partial output from becoming authoritative after a limit hit.

The next first-lane removable-media cut is now accepted in `adrs/ADR-0344-removable-media-local-fallback-post-detach-peer-interaction-stays-launcher-isolated-and-ambient-ipc-free.md` and `docs/755-removable-media-local-fallback-post-detach-peer-interaction-stays-launcher-isolated-and-ambient-ipc-free.md`.
After the resource envelope is launcher-enforced and receipt-visible, peer interaction must also be explicit: `launcher-isolated-peer-envelope-no-ambient-ptrace-signal-or-ipc` and `receipt-records-peer-isolation-and-signal-policy` keep same-UID peer control, parent-session signals, procfs/ptrace/ktrace visibility, and unreviewed IPC out of the ordinary post-detach derivative path.
Signal authority stays `launcher-only-signal-control-no-peer-or-session-control`, IPC stays `no-unreviewed-ipc-sockets-shm-pipes-or-procfs`, and process-observation surfaces stay `procfs-ptrace-and-ktrace-unavailable-to-worker-and-peers`.


The next first-lane removable-media cut is now accepted in `adrs/ADR-0345-removable-media-local-fallback-post-detach-ambient-inputs-stay-launcher-sealed-and-receipt-visible.md` and `docs/756-removable-media-local-fallback-post-detach-ambient-inputs-stay-launcher-sealed-and-receipt-visible.md`.
After peer interaction is launcher-isolated and ambient-IPC-free, ambient host observations must also be explicit: `launcher-sealed-ambient-input-envelope-no-worker-clock-random-or-host-identity` and `receipt-records-ambient-input-envelope-and-launcher-owned-timestamps` keep wall-clock time, timezone state, host entropy, randomness, hostname, kernel/sysctl facts, locale, and machine identity out of ordinary derivative input authority.
Time stays `worker-wall-clock-and-timezone-not-derivative-authority`, randomness stays `no-worker-randomness-or-host-entropy-as-derivative-input`, and host identity stays `hostname-kernel-sysctl-locale-and-machine-identity-not-derivative-authority` unless a later explicit compatibility lane declares and receipts those inputs.

The next first-lane removable-media cut is now accepted in `adrs/ADR-0346-removable-media-local-fallback-post-detach-network-egress-stays-absent-and-receipt-visible.md` and `docs/757-removable-media-local-fallback-post-detach-network-egress-stays-absent-and-receipt-visible.md`.
After ambient host inputs are launcher-sealed, remote authority must also stay explicit: `network-egress-absent-no-socket-dns-or-remote-callbacks` and `receipt-records-network-absent-envelope` keep socket egress, DNS/NSS/name-service lookup, proxy configuration, remote fetches, telemetry, license checks, update checks, safe-browsing lookups, and callbacks out of ordinary derivative authority.
Name resolution stays `no-dns-mdns-nss-or-resolver-host-input`, proxy state stays `no-proxy-or-remote-service-configuration`, and remote dependencies stay `no-remote-fetch-or-callback-derivative-authority` unless a later explicit compatibility lane brokers and receipts network authority.

The next persistent-state cut is fixed too: `persistent-state-absent-no-home-cache-or-host-state-writes` and `receipt-records-persistent-state-absence-and-scratch-cleanup` keep user-home/cache/config/history, crash dumps, lock files, durable tool profiles, and reusable scratch out of the first lane. Scratch is `launcher-created-empty-scratch-nonauthoritative`, cleanup is `scratch-destroyed-before-derivative-receipt`, and `no-user-home-cache-config-or-history-state` means local tool caches or profile stores cannot become ordinary derivative authority unless a later compatibility lane declares and receipts them.

## Removable-media post-detach contract closure decision

The next first-lane removable-media cut is now accepted in `adrs/ADR-0348-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md` and `docs/759-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md`.

The remaining posture strings are no longer enough by themselves: the ordinary lane now records `schema-backed-positive-and-negative-fixture-guarded`, `receipt-must-bind-freebsd-launch-evidence-to-contract`, and `known-bad-authority-shapes-must-fail-validation`. This closes the immediate risk that home preopens, reusable scratch, path reopen, Casper network service authority, best-effort cleanup, or undeclared output surfaces drift in without a negative fixture.

## r505 risk update: backend evidence grammar

The removable-media backend-evidence risk is narrowed by `typed-freebsd-launch-evidence-positive-and-negative-fixture-guarded` and `known-bad-freebsd-launch-evidence-shapes-must-fail-validation`. The remaining implementation risk is no longer “what should the receipt prove?” but “can the first FreeBSD launcher reliably collect fd rights, Capsicum state, jail/devfs/pf posture, Casper absence, environment sealing, scratch teardown, and output-slot identity without creating a new ambient authority path?”


## r506 risk update: recovery evidence semantics

The removable-media persistent-state risk is narrowed by `typed-post-detach-recovery-evidence-positive-and-negative-fixture-guarded` and `known-bad-recovery-evidence-shapes-must-fail-validation`. The remaining implementation risk is now concrete: can the first FreeBSD launcher collect crash/kill recovery facts, scratch teardown or key-discard evidence, worker-tree reap evidence, and output-slot sealing evidence without reopening media paths or introducing a persistent recovery cache?


### r507 removable-media query-projection cut

The broad queryable-metadata risk is not closed, but the first ordinary removable-media post-detach lane now has a concrete typed projection: `typed-post-detach-query-projection-positive-and-negative-fixture-guarded` with `known-bad-query-projection-shapes-must-fail-validation`. The cut keeps raw paths, observed media hints, host identity, filenames, body text, live subscriptions, unbounded retention, and ambient cross-lane joins out of the first receipt-query surface.

## r508 removable-media export-bundle carve-out

The broad evidence-export problem remains open, but the first ordinary removable-media post-detach lane now has a concrete typed export bundle: `typed-post-detach-export-bundle-positive-and-negative-fixture-guarded` with `known-bad-post-detach-export-bundle-shapes-must-fail-validation`. This cut blocks the easiest regression after query projection: support/debug workflows that include raw paths, raw receipts, host identity, filenames, body text, live locators, unbounded retention, or secret material.



## r509 removable-media revocation tombstone risk note

`typed-post-detach-revocation-tombstone-positive-and-negative-fixture-guarded` and `known-bad-post-detach-revocation-tombstone-shapes-must-fail-validation` close the support/export lifetime gap for the first removable-media local fallback lane. Remaining risk: the system must communicate honestly that a tombstone denies future DeriveBSD-mediated query/export/rehydration authority and can delete/revoke managed objects, but does not prove erasure of unmanaged offline copies.


## r510 denial-receipt risk closure

The removable-media metadata risk now has a stronger executable floor: `typed-post-detach-denial-receipt-positive-and-negative-fixture-guarded` plus `known-bad-post-detach-denial-receipt-shapes-must-fail-validation` makes stale query/export/rehydration denial evidence typed and red-tested. Remaining risk: future generic denial receipts must preserve the exact-digest/no-raw-handle model instead of weakening it for convenience.

## r511 decided removable-media fresh-authority reissue

[DECIDED] `adrs/ADR-0355-removable-media-local-fallback-post-detach-fresh-authority-reissue-is-typed-and-negative-tested.md` fixes the post-tombstone successor path for the removable-media local fallback. `typed-post-detach-fresh-authority-receipt-positive-and-negative-fixture-guarded` and `known-bad-post-detach-fresh-authority-receipt-shapes-must-fail-validation` mean renewed query/export/rehydration authority must be a fresh lease plus a new policy decision, not stale-handle replay, tombstone mutation, broad successor scope, raw locator leakage, secret material, or an offline-erasure overclaim.

Last updated: 2026-05-25r520
## r512 decided removable-media fresh-authority consumption

[DECIDED] `adrs/ADR-0356-removable-media-local-fallback-post-detach-fresh-authority-consumption-is-typed-and-negative-tested.md` fixes the one-shot apply step after fresh-authority reissue. `typed-post-detach-fresh-authority-consumption-positive-and-negative-fixture-guarded` and `known-bad-post-detach-fresh-authority-consumption-shapes-must-fail-validation` mean renewed query/export/rehydration authority must be consumed once into exact successor artifacts, not reused, double-spent, broadened through pattern subjects, leaked through raw locators, or overclaimed as offline-copy erasure.

## r513 decided removable-media successor-index cutover

[DECIDED] `adrs/ADR-0357-removable-media-local-fallback-post-detach-successor-index-cutover-is-typed-and-negative-tested.md` fixes the untyped successor-index transition after fresh-authority consumption. `typed-post-detach-successor-index-cutover-positive-and-negative-fixture-guarded` and `known-bad-post-detach-successor-index-cutover-shapes-must-fail-validation` mean renewed query/export/rehydration authority must cut over from old terminal handles to exact successor digests with an append-only marker, not by leaving old and new rows dual-live, forking successors, indexing raw locators/filenames, rolling back to the old index, or overclaiming offline erasure.


## r514 decided removable-media successor-index checkpoint

[DECIDED] `adrs/ADR-0358-removable-media-local-fallback-post-detach-successor-index-checkpoint-is-typed-and-negative-tested.md` fixes the post-cutover reader-fence gap after successor-index cutover. `typed-post-detach-successor-index-checkpoint-positive-and-negative-fixture-guarded` and `known-bad-post-detach-successor-index-checkpoint-shapes-must-fail-validation` mean renewed query/export/rehydration authority must be read from a monotonic checkpointed index root, not from a stale backup, restored old-handle root, dual-active snapshot, unanchored/mutable checkpoint, raw locator/filename projection, full-text index, secret-bearing bundle, or offline-erasure overclaim.

## r517 removable-media reader-use ledger risk note

Risk: a budgeted reader-use receipt can still be double-spent or rolled back if the budget ledger is not itself typed. `typed-post-detach-reader-use-ledger-positive-and-negative-fixture-guarded` and `known-bad-post-detach-reader-use-ledger-shapes-must-fail-validation` now make the ledger root a first-class receipt so stale roots, forked roots, non-monotonic sequences, replayed idempotency keys, uncommitted debits, live subscriptions, raw locators, filenames, body/full-text values, host identity, and secret material remain fail-closed.

Last updated: 2026-05-25r520
## r515 decided removable-media reader admission

[DECIDED] `adrs/ADR-0359-removable-media-local-fallback-post-detach-reader-admission-is-typed-and-negative-tested.md` fixes the post-checkpoint broker-use gap. `typed-post-detach-reader-admission-positive-and-negative-fixture-guarded` and `known-bad-post-detach-reader-admission-shapes-must-fail-validation` mean renewed query/export/rehydration authority must be admitted only after a reader proves it observed the r514 checkpointed root for one exact successor subject, not after a stale backup root, restored old-handle root, dual-active snapshot, broad prefix, live subscription, raw locator, filename, host identity, secret-bearing payload, or offline-erasure overclaim.

## r516 decided removable-media reader use

[DECIDED] `adrs/ADR-0360-removable-media-local-fallback-post-detach-reader-use-is-typed-and-negative-tested.md` fixes the post-admission observation gap. `typed-post-detach-reader-use-positive-and-negative-fixture-guarded` and `known-bad-post-detach-reader-use-shapes-must-fail-validation` mean an admitted reader must still emit a budgeted, sequenced, redacted reader-use receipt before any result is visible, not reuse admission as a live subscription, replay token, over-budget query, broad scope, export/rehydration grant, raw locator/filename/body/full-text return, host identity leak, secret-bearing payload, or offline-erasure overclaim.

## r518 removable-media reader-use ledger retention risk note

`typed-post-detach-reader-use-ledger-retention-positive-and-negative-fixture-guarded` reduces two coupled risks: raw evidence hoarding and unauditable compaction. The remaining implementation risk is proving that compacted ledger summaries preserve enough causality for denial, budget exhaustion, and future reader admission without reintroducing raw locator, filename, body-text, host-identity, or secret-bearing indexes.
## r519 removable-media reader-use ledger retention expiry risk note

Reader-use ledger retention expiry is now guarded by `typed-post-detach-reader-use-ledger-retention-expiry-positive-and-negative-fixture-guarded`. Remaining prototype risk: ensure implementation clocks, CAS roots, and support projections cannot extend retention outside the expiry receipt or delete proof-carry-forward needed to explain denial decisions.

## r520 removable-media reader-use ledger retention expiry enforcement risk note

Reader-use ledger retention expiry enforcement is now guarded by `typed-post-detach-reader-use-ledger-retention-expiry-enforcement-positive-and-negative-fixture-guarded`. Remaining prototype risk: ensure implementation brokers emit the enforcement receipt on every expired-root attempt, rate-limit repeated stale attempts, and never downgrade the denial to a raw support/debug payload.

Last updated: 2026-05-25r520
