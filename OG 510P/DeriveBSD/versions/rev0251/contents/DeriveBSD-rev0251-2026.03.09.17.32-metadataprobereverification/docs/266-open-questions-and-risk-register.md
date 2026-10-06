# Open questions and risk register (v0)

This archive is intentionally ambitious. To avoid “design tourism”, we keep a short list of the highest-leverage unknowns.

When an item moves from “open” → “decided”, capture it in an ADR.

## Conventions

- Each numeric heading is an item.
- If an item is decided, append the tag **[DECIDED]** to the heading and include an ADR link in the section.
- Generated surfaces (context pack + risk register index) treat **[DECIDED]** items as historical context and exclude them from the "top open questions" list.


## 1) Package recipe surface: how much language is allowed?

- How do we express build recipes while keeping the Derive core small?
- What is the smallest “escape hatch” that still keeps evaluation deterministic?

Risk: a rich language becomes the real product; the typed Spec becomes a veneer.

## 2) Cross compilation and multi-arch closures

- Do we encode target triples in the store path (like Nix) or keep them external?
- How do we prevent accidental host/target mixing in closures?

Risk: subtle non-reproducible builds and broken caches.

## 3) Kernel/userland split: pkgbase vs “derive base”

FreeBSD is moving toward packaged base systems (`pkgbase`).
Do we:
- treat base as derivations (kernel/userland/toolchain split)?
- import pkgbase metadata via an adapter?

See: adapter lane discipline (`docs/402-adapter-lanes-and-strangler-discipline.md`).

Risk: base becomes a special snowflake lane.

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

## 64) Supply-chain workflow verification: attestation confusion and silent CI authority [DECIDED]

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


## 29) Lazy mounts and partial fetch: integrity, side-channels, and fallback drift

On-demand mounting and lazy pulling can dramatically improve cold-start, but they introduce new risks:

- partial fetch patterns leak "what was read" (access-pattern side channels)
- complex backends can become a de-facto new TCB if not strictly adapterized
- fallback to full materialization can silently change operational posture (privacy vs performance)

Open questions:
- What is the minimal evidence we need for lazy mounts (digests only, no path-level traces by default)?
- How do we make privacy-preserving modes first-class (prefetch/materialize) without killing the feature?
- Which kernel/backend constraints do we accept (and how do we model them in plan-time checks)?

Risk: the optimization becomes an unreviewed distribution path, or it becomes an ambient surveillance surface.

See: `docs/299-verified-lazy-rootfs-and-on-demand-mounts.md`, `docs/119-casync-cvmfs-distribution.md`, `docs/192-observability-as-capability.md`.


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

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, trust posture regresses to folklore — fleet services smuggle app-local roots, workstation users inherit invisible enterprise trust changes, general-purpose compatibility overrides quietly become the real baseline, and factory/regulatory systems lose provenance through ad-hoc live CA edits.

See: `adrs/ADR-0070-trust-bundle-posture-by-profile.md`, `docs/480-trust-bundle-posture-by-profile.md`, `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`, `docs/327-shadow-trust-and-system-ca-governance.md`, `docs/434-pki-trust-bundle-diff-as-review-surface.md`, `spec/pki.trust.bundle.schema.json`, `spec/pki.trust.bundle.diff.schema.json`, `docs/228-pki-and-identity-lifecycle-as-evidence.md`.


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


## 37) Trustworthy time: quorum failures, expiry safety, and operational response

DeriveBSD leans on time for expiry windows (channel metadata, certificates, freshness checks). Secure time helps, but we still need clear behavior when time is *not* trustworthy:

- quorum disagreement across sources
- large steps (forward/backward)
- time “freezes” due to network isolation

Open questions:
- What is the default policy response when time is degraded: stop updates only, or also stop credential issuance and secret release?
- Do we require `time-proof-bundle` evidence for expiry-sensitive decisions in high-assurance channels?
- What is the minimal fleet monitoring loop that detects a drifting/lying source quickly without making time transcripts privacy-toxic?

Risk: expiry-based security becomes a bypass (“clock was wrong”), or operators add ad-hoc time tooling outside the Derive evidence model.

See: `docs/200-secure-time-bootstrapping.md`, `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`, `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`, `docs/308-time-monitors-and-lie-detection.md`, `docs/61-channel-metadata-tuf-inspired.md`.


## 38) Installation and recovery: disk layout idempotency, encryption ergonomics, and “don't wipe the wrong disk” [DECIDED]

The product-shape default is now decided in `adrs/ADR-0063-installation-and-recovery-posture-by-profile.md`:

- **A** keeps install/recovery target-device-bound and additive by default; destructive disk mutation requires breakglass/maintenance approval.
- **B** keeps install/recovery trusted-UI-guided, requires explicit disk identity confirmation for destructive edits, and makes encrypted-root posture the ordinary baseline.
- **C** keeps guided Derive installs and bounded compatibility/classic installer adapters viable, but destructive repartitioning remains explicit and reviewable.
- **D** keeps factory/regulatory install/recovery target-bound and offline-capable by default, with destructive reprovisioning governed by signed reset bundles/markers and retained approval/receipts.

The archive now also fixes the destructive reprovision contract in `adrs/ADR-0073-destructive-reprovisioning-and-reset-authority.md`: `reset.authorization` binds target + plan + install payload + authority signals, and `reset.receipt` records what destructive reset authority was actually observed.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, install/recovery drifts into wrong-disk incidents, hidden destructive convenience flows, live-network rescue dependency, and unreceipted factory reset folklore.

See: `adrs/ADR-0063-installation-and-recovery-posture-by-profile.md`, `adrs/ADR-0073-destructive-reprovisioning-and-reset-authority.md`, `docs/473-installation-and-recovery-posture-by-profile.md`, `docs/483-destructive-reprovisioning-and-reset-authority.md`, `docs/309-installation-and-recovery-as-derived-operations.md`, `docs/310-disk-layout-plans-and-receipts.md`, `docs/360-derived-recovery-images-and-minimal-userspace.md`, `docs/155-trust-bootstrap.md`.



## 39) Operator access leases: JIT cert UX, audit value, and "no backdoor" posture [DECIDED]

The product-shape default is now decided in `adrs/ADR-0057-operator-access-posture-by-profile.md`:

- **A** keeps operator access brokered, JIT certificate-based, role-shell-first, and separate from escalation.
- **B** treats local secure-attention / user-presence admin as the default and keeps remote shell admin exceptional + leased rather than standing.
- **C** keeps classic local admin compatible, but JIT/leased remote admin is the preferred Derive-managed posture and static keys remain explicit adapter territory.
- **D** requires maintenance-window-shaped, JIT, strongly approved operator access and forbids standing vendor/admin keys in factory or shipped images by default.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, static keys, permanent bastions, and standing maintenance credentials quietly become the real operator-access story.

See: `adrs/ADR-0057-operator-access-posture-by-profile.md`, `docs/467-operator-access-posture-by-profile.md`, `docs/311-operator-access-leases-and-ssh-certs.md`, `spec/operator.session.schema.json`, `docs/292-terminal-session-recording-as-evidence.md`, `docs/236-breakglass-and-recovery-mode.md`.


## 40) Measured boot in practice: event-log replay ergonomics, attester lifecycle, and variance policy

DeriveBSD’s measured-boot lane is intentionally optional, but high-assurance users will expect it to be **operable**.
Most attestation deployments collapse into either brittle golden PCR allowlists or “turn it off when it breaks”.

Open questions:
- What is the minimum stable `boot.manifest` set that stays useful without being brittle across firmware and loader variance?
- What canonical event-log representation do we standardize first, and how do we keep parsers upgradable without losing determinism?
- How do we express “allowed variance” in `attestation.reference` without turning it into a per-host allowlist database?
- What is the day-0 lifecycle model for attester keys (AK rotation, revocation, motherboard replacement), and how do we keep enrollment receipts non–privacy toxic?
- Do we adopt “durable attestation” (receipt chaining + posture timelines) by default, and what retention budgets keep it useful without becoming privacy-toxic?

Risk: the lane exists “on paper” but is too painful to adopt, so secrets/update gates drift into bespoke vendor tooling outside the Derive evidence model.

See: `docs/176-measured-boot-attestation.md`, `docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/313-boot-manifests-and-eventlog-replay.md`, `docs/314-attester-provisioning-and-key-lifecycle-receipts.md`, `spec/boot.manifest.schema.json`, `spec/attester.provision.receipt.schema.json`.


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

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, upgrades keep drifting into either remote-brick roulette or privacy-toxic inventory sprawl — fleets switch blind, workstations surprise users with hardware regressions, and factory/regulatory support claims stop meaning anything.

See: `adrs/ADR-0069-hardware-compatibility-posture-by-profile.md`, `docs/479-hardware-compatibility-posture-by-profile.md`, `docs/319-hardware-inventory-and-driver-binding-as-evidence.md`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `spec/hw.inventory.receipt.schema.json`, `spec/hw.compat.report.schema.json`, `docs/112-health-gated-updates.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`.


## 44) Firmware updates + UEFI variable drift: trust roots, remote bricks, and unreceipted platform mutation [DECIDED]

The product-shape default is now decided in `adrs/ADR-0061-firmware-update-posture-by-profile.md`:

- **A** keeps firmware mutation policy-gated and maintenance-shaped, with cohort-aware preflight and post-reboot evidence.
- **B** keeps firmware apply trusted-UI-visible and interactive-consent-first rather than silently mutating laptops under the user.
- **C** keeps firmware management user-choice, with managed lanes preferred and classic vendor tooling explicit adapter territory.
- **D** keeps production/factory firmware offline-staged by default instead of depending on live vendor reachability.

What remains open is implementation detail, not the product-shape default.

Risk: without a stable default, firmware posture regresses to updater folklore — fleets accumulate ambient flashing authority, workstation users get surprised by platform changes, and regulated deployments quietly depend on online vendor paths they cannot actually govern.

See: `adrs/ADR-0061-firmware-update-posture-by-profile.md`, `docs/471-firmware-update-posture-by-profile.md`, `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `spec/fw.inventory.receipt.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`, `spec/uefi.var.set.plan.schema.json`, `spec/uefi.var.set.receipt.schema.json`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `docs/51-secure-boot-integration.md`.

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
- what the stable degraded/waived verdict vocabulary should be so operators can distinguish “collect-only”, “visible warning”, and “hard gate” without vendor folklore
- how verifier/registrar/enrollment lifecycle should rotate cleanly without silently broadening trust or stranding recovered hosts
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
- authoritative consuming receipts such as `secret-receipt`, `breakglass-receipt`, and `workload-identity-issue-receipt` may summarize the accepted/rejected decision via `attestation_verification`

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

The basic workstation boundary is now decided: host UI/brokers are trusted, and general apps are AppVM-first.
What remains open is the implementation detail needed to make that boundary practical.

Open questions:
- what is the minimal trusted UI implementation we can defend across laptops/monitors/remote sessions?
- how do portals map onto capability brokers and leases in practice?
- what is the device mediation strategy for USB/HID/GPU without encouraging dangerous bypasses?

See: `docs/410-desktop-viability-checklist.md`, `docs/179-portals-and-powerbox.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`.

Risk: B becomes infeasible in practice, forcing forks or abandoning the workstation story despite the high-level boundary being correct.

## 50) Removable-media implementation details on imperfect hardware

The baseline posture is decided, but execution details still matter:

- how do we detect and qualify “device-domain supported” hardware robustly?
- what does the BSD-native local authorization fallback look like (policy daemon, prompt UX, remembered approvals, revocation)?
- how do integrated devices (Bluetooth, webcams, FIDO/smart-card readers) fit the same posture without becoming exception folklore?

Risk: the baseline stays correct on paper, but fallback mechanics turn into ad-hoc convenience paths that recreate ambient device authority.

See: `docs/458-removable-media-and-usb-posture-by-profile.md`, `docs/279-usb-quarantine-and-removable-media-workflow.md`, `docs/207-input-authority-secure-attention-and-hid-risk.md`.

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


## 54) Listen-broker evidence budget + developer/share ergonomics

The product-shape default is now decided, but practical questions remain:

- how much detail belongs in `net-listen-receipt` vs per-connection logs or support bundles?
- what is the blessed path for temporary sharing, remote assistance, reverse tunnels, or one-off demos so B/C users do not bypass the broker?
- where do TLS termination and key-placement choices live when the broker is in the path?
- how do we keep loopback-first local development ergonomic without training users to promote services via folklore firewall edits?

Risk: the authority model exists on paper, but real users bypass it for debug/support/dev workflows and the archive quietly regresses to ambient listeners.

See: `docs/460-inbound-listen-posture-by-profile.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `spec/net.listen.receipt.schema.json`, `docs/291-remote-assistance-sessions-as-evidence.md`, `docs/208-screencast-and-remote-desktop-portals.md`.

## 55) Remote assistance implementation details after the profile default

The product-shape default is now decided, but the implementation lane still needs sharper answers:

- what is the default recording posture by profile (view-only metadata, output-only TTY, input capture, retention, redaction/export)?
- which scopes require quorum by default (remote control, input recording, file export, maintenance-window enablement)?
- how do persistent portal/backend restore tokens map onto Derive lease/policy objects without silently reintroducing ambient authority?
- what is the preferred relay/transport posture so support remains outbound-first where possible and does not punch surprise holes in ingress policy?

Risk: the product boundary stays correct on paper, but implementation details drift into stealthy persistence, privacy-toxic recording, or folklore tunnels.

A new cross-lane invariant now helps here too: the authoritative temporary-authority object stays lane-specific, while `lease.envelope`, `lease.issue.receipt`, and `lease.use.receipt` remain metadata / evidence-only surfaces. That keeps remembered tokens, restore handles, and later operation receipts from silently becoming the authority object.

See: `docs/461-remote-assistance-posture-by-profile.md`, `docs/291-remote-assistance-sessions-as-evidence.md`, `docs/292-terminal-session-recording-as-evidence.md`, `docs/256-consent-ux-contract.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/281-network-egress-broker-and-consent.md`.


## 56) Crypto-operation implementation details after the profile default

The product-shape default is now decided, but the implementation lane still needs sharper answers:

- what is the default per-op receipt/redaction posture by profile (digests only, destination tags, aggregate counters, support-bundle detail)?
- which key classes require quorum by default beyond the product-shape baseline (release signing, recovery escrow, maintenance signing, user-auth keys)?
- how do platform keystores, TPMs, PKCS#11 tokens, and KeyVM backends map into one broker identity + receipt surface without policy fragmentation?
- how do remembered approvals and agent/socket adapters map onto leases or durable policy objects without silently reintroducing ambient signing authority?

Risk: the product boundary stays correct on paper, but implementations drift into opaque prompt spam, privacy-toxic receipts, or classic file-key/agent folklore.

See: `docs/462-private-key-and-crypto-op-posture-by-profile.md`, `docs/306-crypto-operations-portal-and-split-keys.md`, `docs/392-crypto-key-policies-and-nonexportable-handles.md`, `docs/437-split-secrets-brokers.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`.


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

## 61) Operator-access implementation details after the profile default

The product-shape default is now fixed. Remaining work is implementation detail:

- exact role-shell / forced-command vocabulary and how much shell surface restricted roles really need
- metadata-only vs output-only vs richer session-recording defaults by role/profile/class
- offline or partitioned operation when the broker/CA is unreachable without reintroducing standing credentials
- workstation local-elevation UX details: secure-attention hooks, consent caching limits, and how far doas/polkit-style adapters may go
- renewal / revoke / expiry semantics for long-running sessions and what survives network partitions

Risk: the archive agrees on posture but still ships an operator-access lane that is too brittle, too privacy-toxic, or too awkward to replace static-key folklore in practice.

See: `docs/467-operator-access-posture-by-profile.md`, `docs/311-operator-access-leases-and-ssh-certs.md`, `docs/292-terminal-session-recording-as-evidence.md`, `docs/236-breakglass-and-recovery-mode.md`, `docs/147-doas-minimal-privilege-escalation.md`.

## 62) Trustworthy-time implementation details after the profile default

The product-shape default is now fixed. Remaining work is implementation detail:

- exact quorum / `min_sources` / skew defaults by class and when Roughtime is mandatory vs optional
- signed offline-time token envelope, approval semantics, and replay/retention behavior
- RTC-bounds and LKGT persistence choices that resist rollback without turning failures into lockout traps
- workstation trusted-UI wording / alert cadence / temporary degraded allowances for sensitive operations
- monitor/escalation behavior when authenticated sources disagree or disappear for long periods

Risk: the archive agrees on posture but still ships a trustworthy-time lane that is either too brittle for real operations or too weak/noisy to keep expiry and freshness meaningful.

See: `docs/468-trustworthy-time-posture-by-profile.md`, `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`, `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`, `docs/308-time-monitors-and-lie-detection.md`, `docs/438-time-source-policy-diff-as-review-surface.md`.

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


## 48) Typed remote reverification for stronger packet export [DECIDED]

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

Last updated: 2026-03-09r254
## 53) Guided incident reproduction + safe-open workflows [DECIDED]

The default workflow is now decided in `adrs/ADR-0088-safe-open-support-bundle-intake-and-repro-boundary.md`, and the typed intake-shape boundary is now pinned in `adrs/ADR-0092-support-bundle-intake-typed-plan-and-receipt-profiles.md`:

- foreign support bundles and other risky investigation artifacts enter via `content.import.plan` / `content.import.receipt`, not direct host open,
- the official support-bundle intake path is `microvm` + `network = none` + `lifetime = disposable`,
- responders preview `incident.timeline` / `incident.bundle` / `bundle.payload.manifest` metadata first,
- the canonical typed intake shapes are `spec/content.import.support-bundle.plan.schema.json` and `spec/content.import.support-bundle.receipt.schema.json`,
- and deeper reproduction stages imported digests/receipts/capsules inside a disposable workspace rather than treating the received archive as host authority.

What remains open is implementation detail, not the default workflow.

Risk: without this boundary, support tooling quietly regresses to untar-on-host folklore, unsafe foreign-byte inspection, and ad-hoc reproduction shell sessions that widen authority at the worst possible moment.

See: `adrs/ADR-0088-safe-open-support-bundle-intake-and-repro-boundary.md`, `adrs/ADR-0092-support-bundle-intake-typed-plan-and-receipt-profiles.md`, `docs/498-safe-open-support-bundle-intake-and-repro-boundary.md`, `docs/502-support-bundle-intake-typed-plan-and-receipt-shapes.md`, `docs/267-sanitization-portal-and-disposable-sandboxes.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/220-operational-time-travel-debugging.md`.
