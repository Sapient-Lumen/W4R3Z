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

## 5) Update distribution strategy

We already have:
- TUF-inspired channel metadata
- staged rollouts and cohorts
- offline signed bundles

But:
- what is the strategy for long-term source availability if a deployment must rebuild (SWHID fallback, distfiles, source bundles in mirror kits)? See `docs/403-swhid-fallback-and-long-term-source-availability.md`.
- what is the “happy path” for air-gapped ops? (mirror kits + quarantine→promote; see `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`)
- what is the minimum operator burden for keys and rotation?

Risk: the secure path is too hard; people bypass it.

## 6) Human-scale debugging

We have strong plans for receipts and explainability, but we need concrete answers:
- what is the default “support bundle” format and redaction policy?
- do we standardize a **typed incident timeline** (`incident.timeline`) as the default “one page” orientation surface (and include it in bundles)?
  See: `docs/419-incident-timelines-as-derived-artifacts.md`.
- what is the workflow for a user to reproduce a failed build or boot?
- how do we make “open/export untrusted files safely” a default workflow (sanitization portal)?

Risk: beautiful theory, miserable incidents (if we never ship the human-scale views).

## 7) Desktop/interactive workload stance (if any)

Portals and intent routing are in the archive, but:
- do we officially support desktop workloads on the host?
- if not, what is the blessed AppVM/portal model for desktop apps? (see `docs/268-desktop-appvms-and-portalized-apps.md`)
- or are those strictly inside workload VMs?

Risk: unclear target leads to conflicting security postures.

## 8) Store growth + GC + long-lived fleets

- What are the default GC policies?
- How do we reconcile fleet-wide rollback windows with local disk constraints?

Risk: fleets silently fall out of rollback coverage.

## 9) Human identity + home data model (portable homes vs host accounts)

If we embrace AppVMs for desktop, we need a crisp answer for:
- what is the canonical “user identity” object?
- what persists by default (per-AppVM private vs user-wide home)?
- do we support a portable home container that embeds the user record?

Risk: users reinvent unsafe sharing (mount whole home everywhere) or admins keep homes always mounted (data exposure at rest).

Also: if home/state unlock depends on TPM policies, we need an operable story for policy evolution (avoid PCR brittleness). See `docs/272-sealed-secrets-attested-unsealing.md`.

See: `docs/269-portable-home-areas-and-user-records.md`, `docs/270-appvm-storage-private-volatile-and-home-areas.md`.


## 10) Continuous fuzzing + regression localization (signal vs noise)

- What are the minimum target sets we require fuzz coverage for (kernel syscalls, key parsers, drivers)?
- How do we budget fuzzing so it is continuous but not runaway (CPU, storage for corpora/crash cases)?
- How do we prevent flaky crashes or non-deterministic failures from producing false blame?
- What is the retention policy for corpora and crash cases (per severity / per component class)?

Risk: fuzzing becomes a vanity dashboard, while regressions still require heroics.

See: `docs/274-continuous-fuzzing-farm.md`, `docs/275-root-cause-certificates-and-bisection.md`.


## 11) Kernel module policy + loader verification (don’t leave a pre-kernel hole)

- What is the minimal, enforceable policy surface for kernel modules (allowlist by digest, autoload behavior, recovery windows)?
- What is the boot-time verification story for kernel + modules when some boot config must remain mutable?
- How do we bind “what was verified” into attestation and evidence bundles?

Risk: secure boot becomes a checkbox while attackers (or accidents) still control which kernel code runs.

See: `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/277-loader-verification-and-boot-config-constraints.md`.



## 12) Removable media + device posture (USB is the universal footgun)

- What is the default “no automount” UX for removable media?
- Do we require a USB quarantine/device domain on systems that can support it?
- How do we bind device attach/detach into receipts and incident bundles so “who had the device?” is always answerable?
- What is the safe default for untrusted files (sanitize portal) and block devices (read-only by default)?

Risk: a single untrusted USB device collapses the security posture, or users invent ad-hoc bypass workflows.

See: `docs/278-device-grants-and-devfs-rulesets.md`, `docs/279-usb-quarantine-and-removable-media-workflow.md`, `docs/204-device-isolation-domains.md`.


## 13) Origin labels + quarantine metadata (prevent laundering and stripping)

- How do we store quarantine/origin labels (xattrs, sidecars, store-backed metadata) in a way that survives common workflows?
- What is the blessed path for copy/zip/unzip/export so labels are preserved by default?
- How do we detect and explain “origin laundering” (apps that rewrite content without carrying provenance)?

Risk: the system reverts to mystery bytes, and the safe open path becomes optional folklore.

See: `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/267-sanitization-portal-and-disposable-sandboxes.md`, `docs/251-export-policies-and-support-bundle-portal.md`.




## 14) Outbound network policy + consent UX (avoid silent exfil or click-ops)

We want outbound networking to be explicit and brokered, but:

- what is the default “deny + explain” UX for services/apps that try to connect?
- how do we keep interactive prompts from becoming “click Allow until it works”?
- what is the stable landing spot for approvals (short-lived grants vs policy edits)?
- what is the default retention/redaction policy for `net-flow-receipt` evidence?

Risk: either networking becomes ambient again, or users/admins train themselves to bypass the safe path.

See: `docs/281-network-egress-broker-and-consent.md`, `spec/net.egress.grant.schema.json`, `spec/net.flow.receipt.schema.json`.


## 15) Witness networks as security parameters (availability, diversity, governance)

Witness cosigning is a strong split-view defense, but it introduces governance questions:

- who chooses the witness set (channel operator vs fleet policy)?
- what quorum is required for publish vs consume?
- how do we rotate witness keys/membership without breaking verification?
- what is the degrade/halt behavior when witnesses are unavailable?

Risk: hard-coded witness lists (centralization) or brittle availability requirements.

See: `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`, `docs/259-transparency-monitors-and-witness-gossip.md`, `spec/log.checkpoint.receipt.schema.json`.


## 16) Trustworthy time in hostile environments (rollback-by-clock, offline bootstrap)

We have a rich time discipline lane, but we still need crisp defaults:

- when do we require authenticated time (NTS/Roughtime) vs allow degraded time?
- how do we persist LKGT across reboots and failures without creating lockout risks?
- what is the offline/air-gapped bootstrap story (RTC bounds, operator time tokens)?
- how do we bind time proofs to security-sensitive receipts (publish, promote, unseal)?

Risk: security checks degrade into “ignore expiry” during incidents, which becomes normal.

See: `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`, `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`, `docs/142-trustworthy-time-roughtime.md`.


## 17) Inbound exposure + firewall state (avoid ambient listeners and port-folklore)

We have a strong outbound networking lane, but inbound exposure is just as dangerous:

- who is allowed to bind/listen on which addresses/ports?
- how do we prevent 'temporary' firewall edits from becoming permanent folklore?
- how do we keep interactive approvals from becoming click-ops?
- what is the default stance for low-traffic services (socket activation) vs long-running daemons?

Risk: services quietly become internet-facing, and incidents cannot answer *what was exposed and why*.

See: `docs/286-inbound-listen-broker-and-firewall-leases.md`, `spec/net.listen.policy.schema.json`, `docs/238-portal-activated-services-and-socket-activation.md`, `docs/67-pf-anchors-per-instance.md`.



## 18) Formal methods lane: models become stale or theatre

- If we add models, they must stay tied to real decisions and real CI receipts.
- The risk is that models drift from implementation/intent and become “diagramware”.

Risk: models drift from implementation/intent and become diagramware; the lane becomes theatre instead of a safety tool.

Mitigation:
- require an ADR/RFC link for each model
- require a passing `modelcheck.receipt` when a protocol changes
- keep models tiny and finite (favor invariants over completeness)


## 19) Quorum approvals: click-ops, bypass, and governance drift

We increasingly rely on approvals/leases (networking, exports, breakglass, publishing). We need crisp defaults:

- what actions require two-person/quorum approvals vs single-party consent?
- how do we keep approvals digest-bound (approve the plan/policy/artifact, not an idea)?
- how do we enforce separation of duties (decide vs ship) and distinct principals?
- what is the offline/OOB story for high-value keys (root/publish)?

Risk: approvals become “click until it works” or a purely social process that attackers bypass.

See: `docs/288-multiparty-approvals-and-separation-of-duties.md`, `docs/256-consent-ux-contract.md`, `docs/107-two-person-integrity.md`, and `docs/260-release-authority-policy-and-key-management.md`.


## 20) Workload identity + credential issuance (avoid "static token" relapse)

We can broker inbound/outbound networking, but services still need a boring default for auth.
If we don't bake it in, ecosystems fall back to long-lived API tokens and shared secrets.

Questions:

- What is the minimal issuance model we can support without building a full service-mesh control plane?
- How do we bind issuance to what is actually running (artifact digest / attestation) and keep it digest-bound?
- What is the key handling posture (TPM keys vs broker-held keys vs OS keystore handles)?
- How do we rotate trust bundles (roots/intermediates) safely and visibly?

Risk: either the identity lane becomes an overbuilt “mesh”, or it stays absent and people reintroduce static secrets.

See: `docs/181-workload-identity-and-secretless-deploys.md`, `spec/workload.identity.lease.schema.json`, `spec/workload.identity.issue.receipt.schema.json`.



## 21) Exec integrity enforcement: brittleness and bypass

If we add verified execution, it must be *operable*:

- How do we update/attach new binaries without falling back to mutable paths?
- What is the story for interpreters (scripts) and dynamic loaders?
- How do we avoid "turn it off during incident" becoming permanent folklore?
- How do we represent temporary exceptions (lease-based) without normalizing them?

Risk: enforcement is perceived as brittle, so it's disabled or bypassed, and the system returns to ambient execution from writable areas.

See: `docs/289-exec-integrity-policy-and-verified-execution.md`, `spec/exec.integrity.policy.schema.json`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`.


## 22) Keyless identity receipts: over-trust and identity confusion

Keyless signing makes identity evidence cheap, but:

- OIDC claims vary by issuer; "email" is not a stable principal for automation.
- Many keyless systems assume public internet availability (Fulcio/Rekor).
- Operators may conflate "identity evidence" with "promotion authority".

Risk: supply chain checks devolve into "it's signed, ship it" with weak identity semantics.

See: `docs/290-keyless-signing-and-publisher-identity-receipts.md`, `spec/publisher.identity.receipt.schema.json`, `docs/260-release-authority-policy-and-key-management.md`.


## 23) Remote assistance + session recording: backdoors, stealth, and privacy drift

We want a blessed remote support path, but it is high risk:

- How do we ensure remote view/control cannot be stealthy (always visible indicators + secure attention transitions)?
- What scopes require quorum approvals (e.g., enabling remote control, input recording, exports)?
- How do we keep “temporary” support agents from persisting beyond a lease?
- What is the default posture for session recording (output-only vs input+output), retention, and redaction/export?

Risk: remote support becomes a permanent backdoor, or recording becomes surveillance; either outcome trains users to bypass the safe path.

See: `docs/291-remote-assistance-sessions-as-evidence.md`, `docs/292-terminal-session-recording-as-evidence.md`, `docs/208-screencast-and-remote-desktop-portals.md`, `docs/256-consent-ux-contract.md`, and `docs/195-deterministic-redaction-transforms.md`.




## 24) Spec/policy authoring frontends: compiler trust and DSL sprawl

We want optional frontends (CUE/Pkl/Nickel/etc) without repeating Nix's failure mode where the language becomes the product.

Questions:

- Which frontend(s) are blessed first, if any?
- How do we keep the core IR stable while frontends evolve (and don't create fragmentation)?
- How do we pin and verify frontend compiler artifacts (supply-chain + bootstrap story)?
- How do we produce usable 'why is this value here?' traces without embedding an evaluator in the core?

Risk: frontend tooling becomes a large, fast-moving TCB that operators bypass or that silently changes semantics.

See: `docs/79-derive-spec-frontends.md`, ADR-0023, `docs/83-evaluator-minimalism.md`, `docs/149-human-policy-hujson-and-canonicalization.md`.


## 25) Queryable metadata: privacy, laundering, and index integrity

Origin labels, quarantine state, capability bookmarks, and evidence pointers are only useful if they are discoverable under pressure. But metadata search can also become an ambient exfil surface.

Questions:

- Where does the authoritative metadata live (xattrs vs CAS sidecars vs both), and how do we preserve it across copies/exports?
- How do we prevent 'metadata laundering' (apps rewriting bytes without carrying labels)?
- How do we make indexes auditable (snapshots as evidence) and avoid stale/incorrect indexes?
- What is the minimum query/subscription interface that is useful without normalizing ambient search authority?

Risk: either metadata is too hard to use (people ignore it), or it becomes ambient surveillance/exfiltration.

See: `docs/293-attribute-indexed-metadata-and-live-queries.md`, `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/198-persistent-file-capabilities-bookmarks.md`, `docs/229-evidence-spine-overview.md`.


## 26) Multi-origin userlands: explicit strata vs ad-hoc chroots

Adoption pressure will push us toward mixing ecosystems (base sets + pkg adapters + vendor runtimes + “foreign userlands”).
If we don’t define a first-class composition model, we’ll end up with invisible precedence rules, silent host-library leakage, and “works on my machine” folklore.

Questions:

- Do we standardize a **stratum** concept (digest-bound trees + ABI assumptions) as a first-class input to `mount.view`?
- How do we prevent accidental mixing across strata while still enabling useful stacks (devshells, compat views)?
- What’s the minimum evidence we need so “where did this binary/library come from?” is always answerable?

Risk: the ecosystem invents unofficial composition patterns that bypass provenance, policy, and explainability.

See: `docs/295-strata-and-multi-origin-userlands.md`, `docs/105-compat-view-foreign-binaries.md`, `docs/264-mount-namespaces-and-union-views.md`, `docs/108-ports-pkg-adapter-lane.md`.


## 27) “How it runs” source vs runtime artifact sprawl (component descriptors)

We are accumulating many compiled runtime artifacts (service graphs, caproute, preopen maps, mount views, stratum stacks, state footprints, health checks).
Without a unifying *source* format, teams will invent inconsistent mini-manifests and silently expand authority.

Open questions:
- What is the minimal component descriptor source that still compiles to all required runtime IR?
- Where does the canonical IR live (schema/format), and how do we version it?
- How do we keep descriptor scope tight (runtime contract) without turning it into “all config”?

Risk: runtime policy becomes folklore; review/diff tooling loses leverage.

See: `docs/297-component-descriptors-and-compiled-runtime-manifests.md`, `docs/114-service-manifests-smf-lessons.md`, `docs/140-capability-routing-manifests.md`, `docs/294-oblivious-sandboxing-launchers.md`.

## 28) Permission creep despite explicit grants (need authority budgets)

Even with explicit routing and preopen maps, systems tend to accumulate “temporary” privileges over time.
We need a first-class way to set and enforce budgets, and to surface drift as incidents.

Open questions:
- Which budget dimensions have the best signal (counts vs kinds vs “ambient roots”)?
- How do we ratchet budgets over time without blocking iteration?
- How do timeboxed exceptions integrate with multiparty approvals and evidence?

Risk: components become overprivileged; sandbox primitives exist but are not used in practice.

See: `docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/106-blast-radius-diff.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`.


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


## 32) Structured diagnostics vs privacy (Inspect trees can become ambient surveillance)

We want queryable structured diagnostics (inspect trees), but they can leak sensitive state if access is ambient.

Open questions:
- What is the minimal diagnostics lease model (who can query what, and how is it attributed)?
- What is the default redaction taxonomy, and how do we prevent accidental secret exposure?
- Where do snapshots live (event journal vs separate store), and what is the retention model?

Risk: operability features become a new exfiltration surface or a compliance nightmare.

See: `docs/302-structured-diagnostics-inspect-trees.md`, `docs/192-observability-as-capability.md`, `docs/251-export-policies-and-support-bundle-portal.md`.


## 33) Flight recorders: overhead, covert channels, and “debug mode” bypasses

Always-on circular buffers are a huge operability win, but they must be bounded and policy-governed.

Open questions:
- Which backend substrate is best on FreeBSD (DTrace/ktrace/custom ring buffers), and what is the minimal TCB?
- How do we enforce budgets (rate, size, window) and make drops explicit rather than silent?
- How do we prevent "debug builds" or ad-hoc tooling from bypassing budgets and leases?

Risk: performance regressions, covert channels, or an ecosystem split where the real debugging happens outside the Derive evidence model.

See: `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/216-incident-snapshots-and-support-bundles.md`.


## 34) Trust bundles: format choice, interop renderers, and drift control

We want the trust store to be a versioned object, not ambient files, but we still need crisp defaults:

Open questions:
- Do we adopt a single canonical trust-bundle encoding (PEM-only) or support multiple encodings (e.g., JWK bundles for SPIFFE-shaped mTLS)?
- Which interop renderers are mandatory on day-0 (OpenSSL CAfile) vs optional (NSS DB, p11-kit trust module)?
- Should promotions require a typed trust drift surface (`pki.trust.bundle.diff`) in drift bundles, and what are the default gates/risk flags (new anchor, removed anchor, broadened constraints/distribution)?
- How do we prevent "shadow trust" paths (apps shipping their own CA bundles) from undermining fleet policy?

Risk: trust roots drift silently, TLS validation becomes inconsistent across libraries, and incidents can't answer "what roots were trusted".

See: `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`, `docs/327-shadow-trust-and-system-ca-governance.md`.


## 35) DNS mediation receipts: TOCTOU control vs privacy toxicity

Brokered DNS makes hostname-based policy real, but DNS evidence can quickly become privacy-toxic.

Open questions:
- Do we emit per-query receipts by default, or only aggregate counts unless an incident trigger promotes detail?
- What is the default redaction stance (hash qnames, keep only domains, or keep full names inside support bundles only)?
- How do we handle split-horizon/internal names without leaking them into shared receipts?

Risk: either hostname policy devolves into folklore again, or DNS evidence becomes too sensitive to keep/ship.

See: `docs/305-dns-mediation-and-hostname-binding.md`, `spec/net.dns.query.receipt.schema.json`, `docs/195-deterministic-redaction-transforms.md`.



## 36) Crypto operations portal: key abuse, user presence, and audit toxicity

We want non-exportable private keys (sign/decrypt by lease), but adding a crypto broker introduces new risks:

- a "sign anything" API becomes a high-value abuse surface
- background signing can silently reintroduce ambient authority
- per-op receipts can become privacy-toxic if they capture too much context
- backend diversity (KeyVM vs TPM vs external KMS) can fragment policy if not unified

Open questions:
- How do we support “split secrets” user workflows (Split SSH/GPG style) without turning agent sockets into ambient authority (interop via Adapter→Shadow→Replace)?
- What is the minimal broker identity + portal routing surface to prevent confused-deputy (client cannot silently target a different vault)?
- What is the minimal key-policy model that blocks the worst footguns (purpose/algorithm allowlists, destination tags, rate limits)?
- When is user presence required by default (interactive desktop) vs prohibited (headless fleet) and how is that expressed in policy?
- What is the default per-op receipt: which digests/fields are mandatory, and what is redacted/aggregated by default?
- How do we make two-person signing the easy path for release/publishing workflows?

Risk: operators fall back to file-based keys and ad-hoc agents, or the broker becomes an unreviewable, omnipotent signing daemon.

See: `docs/306-crypto-operations-portal-and-split-keys.md`, `docs/437-split-secrets-brokers.md`, `docs/223-secrets-and-key-management-as-evidence.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`.


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


## 38) Installation and recovery: disk layout idempotency, encryption ergonomics, and “don't wipe the wrong disk”

DeriveBSD's security and operability claims collapse if install/recovery is an ad-hoc script pile. Making disk mutation first-class helps, but the defaults must be crisp.

Open questions:
- How strict is `target_device` matching by default (WWN/serial required vs optional), and how do we make "I picked the wrong disk" hard to do?
- What's the exact additive model: create/grow only (systemd-repart style) vs allowing destructive edits under explicit breakglass?
- What is the day-0 posture for encrypted ZFS roots: required vs optional, and how do we keep recovery workable without leaking keys into live images?
- How do we ensure recovery images are *always available* (on-disk fallback, mirror kits) and still verifiable/policy-bound?

Risk: installation is too brittle or scary, operators bypass the Derive model, and recovery devolves into unreceipted folklore tooling.

See: `docs/309-installation-and-recovery-as-derived-operations.md`, `docs/310-disk-layout-plans-and-receipts.md`, `docs/155-trust-bootstrap.md`, `docs/284-bootenv-switching-as-evidence.md`, `docs/272-sealed-secrets-attested-unsealing.md`.



## 39) Operator access leases: JIT cert UX, audit value, and "no backdoor" posture

DeriveBSD can’t pretend operators don’t need shells, but static SSH keys and permanent bastion accounts are a security and incident-response disaster.
The alternative (short-lived certs + leased admission + optional recording) has its own sharp edges.

Open questions:
- What is the day-0 default: metadata-only `operator.session`, output-only recording for privileged roles, or always record?
- How do we prevent recording and counterfactual traces from becoming surveillance or privacy-toxic artifacts (retention, redaction, export gates)?
- What is the minimal "role shell"/forced-command model that meaningfully reduces blast radius without making oncall unusable?
- How does offline/partitioned operation work (access when the broker is unreachable) without reintroducing permanent keys?
- How do we unify operator access with breakglass and separation-of-duties so emergencies don’t normalize permanent escalations?

Risk: either operators keep static keys and bypass the Derive model, or we build an access broker that is too complex, too central, or too privacy-toxic to adopt.

See: `docs/311-operator-access-leases-and-ssh-certs.md`, `spec/operator.session.schema.json`, `docs/292-terminal-session-recording-as-evidence.md`, `docs/236-breakglass-and-recovery-mode.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`.


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


## 41) Backups and restore drills: key availability, privacy, and false confidence

DeriveBSD can make backups auditable, but operational failure modes remain:

- encryption keys exist only in one place (or can't be accessed under incident posture)
- restore procedures bitrot (nobody runs them)
- receipts become privacy-toxic (too much metadata)
- retention/pruning is folklore (no receipts, no deletion evidence)

Open questions:
- What is the day-0 default for backup encryption: always-on with portalized keys, or allow plaintext under explicit breakglass?
- How do we express restore target safety (quarantine namespaces, read-only drills) so drills are safe by default?
- What minimal restore-drill cadence is recommended for different data classes, and how is that expressed in budgets?
- How do we ensure backup receipts stay digest-first while still being useful for incident triage?

Risk: fleets accumulate “feel-good backups” that cannot be restored, or build shadow backup tooling outside the Derive evidence model.

See: `docs/316-backups-and-restores-as-derived-operations.md`, `docs/317-restore-drills-and-continuous-recovery-testing.md`, `spec/backup.plan.schema.json`, `spec/backup.receipt.schema.json`, `spec/restore.drill.receipt.schema.json`, `docs/255-policy-constrained-transports.md`, `docs/306-crypto-operations-portal-and-split-keys.md`.


## 42) Kernel mutation control: sysctls, boot tunables, and module loading drift

DeriveBSD’s “planned system” posture collapses if kernel state can be mutated by ambient scripts or ad-hoc admin tooling.
Two common footguns:

- sysctl/tunable drift (nobody knows what changed, or why)
- runtime module injection (new privileged code after activation)

Open questions:
- What is the day-0 default for **sysctl writes** outside activation: always deny, allow only under maintenance leases, or allow some classes (e.g., network tuning) with budgets?
- Do we require commit-confirmed transactions for a shortlist of risky knobs (routing, jail hardening, debug toggles)?
- How often do we run drift checks, and what is the retention/export budget for drift events so they are useful but not privacy-toxic?
- For upgrades, do we require `sysctl.diff` (planned keyset) as a drift-bundle attachment, and what key classification/risk flags are stable enough for gates?
- For upgrades, do we require `kmod.policy.diff` (policy drift) as a drift-bundle attachment, and what module classifications/risk flags are stable enough for gates?
- For kernel modules, what is the minimal operable posture: preload-only + lockdown by default, with explicit breakglass maintenance windows?
- How do we make “why was this module loaded?” explainable (policy rule id + correlation to change-set/device grant) without building a second service manager?

Risk: kernel state becomes mutable folklore, undermining verification claims and making incident response depend on guesswork.

See: `docs/318-kernel-tunables-and-sysctls-as-evidence.md`, `spec/sysctl.plan.schema.json`, `spec/sysctl.receipt.schema.json`, `spec/sysctl.event.schema.json`, `docs/429-sysctl-diff-as-drift-surface.md`, `spec/sysctl.diff.schema.json`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/439-kmod-policy-diff-as-review-surface.md`, `spec/kmod.policy.schema.json`, `spec/kmod.policy.diff.schema.json`, `spec/kmod.load.plan.schema.json`, `spec/kmod.load.receipt.schema.json`, `spec/kmod.event.schema.json`, `docs/230-lockdown-levels-and-securelevel.md`.


## 43) Hardware inventory + compatibility gates: safety, privacy, and operability

DeriveBSD wants to prevent the classic remote-brick failure mode (driver regressions), but hardware facts are also a fingerprint.
The design has to thread the needle: useful preflight checks and cohorting without turning support bundles into asset-tag leaks.

Open questions:
- What is the day-0 cadence for emitting `hw.inventory.receipt` (every boot, every activation, periodic)?
- What identifiers are allowed in inventories by default (IDs yes, serials no; hashed serials only under explicit policy)?
- What is the minimal  (network/storage requirements) for different deployment classes?
- How do we express 0 (CVE’d firmware, broken module versions) as a policy decision that influences compatibility reports?
- How do we keep `hw.compat.report` reason codes stable and actionable without baking in vendor-specific knowledge?

Risk: we either under-specify the lane and upgrades keep bricking hosts, or we over-collect identifiers and the evidence model becomes privacy-toxic.

See: `docs/319-hardware-inventory-and-driver-binding-as-evidence.md`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `spec/hw.inventory.receipt.schema.json`, `spec/hw.compat.report.schema.json`, `docs/112-health-gated-updates.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`.


## 44) Firmware updates + UEFI variable drift: trust roots, remote bricks, and unreceipted platform mutation

Firmware and UEFI variables are some of the longest-lived drift sources in real fleets:

- system firmware updates performed with ad-hoc vendor tools
- silent changes to Secure Boot databases (`PK/KEK/db/dbx`) and boot order
- device firmware regressions that strand the host (NIC/storage)
- uncertainty about what actually applied across reboot stages (capsules)

Open questions:
- What is the day-0 supported update mechanism mix (UEFI capsules vs live flashing vs BMC lanes), and how do we keep it adapterized?
- What is the minimal operable policy posture: maintenance-lease required, approvals required for which classes, and what is the offline story?
- How do we represent Secure Boot variable updates as digest-bound plans/receipts without storing privacy-toxic blobs by default?
- How do we bind `fw.inventory.receipt` and update receipts into `hw.compat.report` and high-assurance promotion gates?
- What is the canonical failure taxonomy so incidents can answer: staged vs applied vs postcheck failed?

Risk: firmware and boot policy drift happen outside the Derive evidence model, undermining attestation, trust-bootstrap claims, and upgrade safety.

See: `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `spec/fw.inventory.receipt.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`, `spec/uefi.var.set.plan.schema.json`, `spec/uefi.var.set.receipt.schema.json`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `docs/51-secure-boot-integration.md`.

---

## 45) Network topology drift: routes, addresses, pf substrate, and remote-brick changes

DeriveBSD already treats **egress** and **listening** as brokered capabilities.
But the host networking substrate (links/bridges, addressing, routes, pf root ruleset + attachment points) can still drift via:

- ad-hoc `ifconfig`/route tweaks under incident pressure
- pf hotfixes applied by hand and later overwritten
- DHCP/RA/WiFi side effects that are not captured as a planned state
- “commit failed” changes that strand the host (remote bricks)

Open questions:
- What is the day-0 default for ambient network mutation outside activation: deny by default (require maintenance leases), or allow a constrained allowlist?
- How do we compute an observed, privacy-safe state digest that is stable across harmless reordering (addresses/routes) but sensitive to real drift?
- What is the minimal operable commit-confirmed posture for risky topology changes (TTL defaults, rollback triggers, health checks)?
- How do we ensure pf anchor lifecycle is always captured in topology receipts without forcing per-instance launch to depend on a heavyweight host planner?

Risk: networking becomes folklore again — remote incidents require SSH log spelunking, drift breaks reproducibility claims, and topology changes become a top-3 remote brick vector.

See: `docs/322-network-topology-and-firewall-as-derived-operations.md`, `spec/net.topology.plan.schema.json`, `spec/net.topology.receipt.schema.json`, `spec/net.topology.event.schema.json`, `docs/67-pf-anchors-per-instance.md`, `docs/64-networking-modes-mapping.md`, `docs/112-health-gated-updates.md`, `docs/311-operator-access-leases-and-ssh-certs.md`.


---

## 46) `/dev` drift: ambient device nodes, devfs ruleset folklore, and sandbox escapes

DeriveBSD treats device nodes as authority, but `/dev` can still drift unless devfs is pulled into the same plan/receipt model as networking and sysctls. Common drift sources:

- hand-edited `/etc/devfs.rules` under incident pressure
- devfs rulesets not applied (or applied to the wrong jail)
- new device nodes appearing after a kernel/driver update
- device attach/detach actions that are not reflected in the effective `/dev` view
- “helpful” base system defaults that accidentally expand `/dev` across domains

Open questions:
- What is the stable, privacy-safe canonicalization for computing an observed node digest (ordering, naming churn, hashed identifiers)?
- What is the day-0 `service-minimal` pseudo-dev set, and do we version it as policy?
- How do we unify the authority model across jails vs microVMs (guest `/dev` vs host portals)?
- When should drift events page humans vs auto-quarantine the compartment?

Risk: `/dev` becomes folklore again, sandboxing claims are undermined, and permission creep happens via invisible device exposure.

See: `docs/323-devfs-views-plans-and-receipts.md`, `docs/278-device-grants-and-devfs-rulesets.md`, `docs/204-device-isolation-domains.md`, `docs/249-lease-registry-and-cross-lane-revocation.md`, `spec/devfs.view.plan.schema.json`, `spec/devfs.view.receipt.schema.json`, `spec/devfs.view.event.schema.json`.


## Rituals

- Every RFC should list which open questions it advances.
- Every milestone should burn down at least one risk item.

## 47) Product profiles (A–D) as first-class compilation targets

We want DeriveBSD to serve (A) fleet host, (B) workstation, (C) general OS, (D) appliance/regulatory without forks.

Open questions:
- what is the minimal stable vocabulary of “defaults” we encode in `product.profiles` without turning it into a second policy language?
- how do we ensure new features declare tier + profile applicability (linting and review surfaces)?
- what are the “hard constraints” per profile (must never regress)?

See: `docs/411-product-profiles-as-compilation-target.md`, `spec/product.profiles.schema.json`.

Risk: A–D becomes an untestable promise and the archive drifts toward a single implicit product shape.


## 48) Data-at-rest posture (ZFS encryption + keys + recovery)

We already have notes on ZFS encryption, but we need a coherent cross-profile story:
- unattended boot vs “lost device” UX,
- TPM sealing vs passphrases,
- break-glass remote unlock receipts,
- rollback and re-key semantics.

See: `docs/409-zfs-encryption-and-key-management.md`, `docs/250-breakglass-and-recovery-workflows.md`.

Risk: deployments invent ad-hoc key handling that leaks secrets or makes recovery folklore.


## 49) Desktop viability constraints (even if desktop is not v0)

If profile B must remain viable, we need to avoid accidental decisions that make secure desktop mediation impossible.

Open questions:
- what is the minimal trusted UI boundary we can defend?
- how do portals map onto capability brokers and leases in practice?
- what is the device mediation strategy for USB/HID/GPU without encouraging dangerous bypasses?

See: `docs/410-desktop-viability-checklist.md`, `docs/179-portals-and-powerbox.md`.

Risk: B becomes infeasible, forcing forks or abandoning the workstation story.

## 50) Export boundary drift: policy changes, redaction defaults, and exfil risk

DeriveBSD’s support bundles and diagnostics are only safe if “export” is treated as a first-class, least-authority boundary.
But policy objects also drift under pressure:

- new recipients or recipient classes are added as “temporary exceptions”
- approval constraints relax to “unblock support”
- raw blobs (coredumps, traces, memory images) get enabled without durable review

Open questions:
- What is the stable, low-noise `risk_flags` vocabulary for `export.policy.diff` so gates catch real boundary expansion without alert fatigue?
- Which changes require two-person integrity by default in profiles A/D (recipient class broadening, consent relaxation, raw blob enablement)?
- How do we keep “ticket required” semantics meaningful across different transport adapters (Jira, ServiceNow, email handoff) without baking in one ticketing system?
- What is the default posture for transparency logging of exports (required vs advisory), and how do we keep it privacy-safe (hashed ticket ids/recipients)?

Risk: exports revert to folklore (“someone emailed a tarball”), making incidents less explainable and turning support tooling into an exfiltration footgun.

See: `docs/251-export-policies-and-support-bundle-portal.md`, `docs/433-export-policy-diff-as-review-surface.md`, `spec/export.policy.schema.json`, `spec/export.receipt.schema.json`, `spec/export.policy.diff.schema.json`.



## 51) Attestation admission policy drift: keep “what is gated?” stable and reviewable

Remote attestation only matters when other subsystems **gate admission** on verifier-issued receipts.
That creates a high-leverage policy surface (`attestation.admission.policy`) whose drift must be reviewable:

- a rule is removed under pressure (“temporary exception”),
- a selector is broadened to cover more hosts than intended,
- a `requirement_ref` changes from strong → weak.

Open questions:
- What is the default semantics when no admission rule matches (deny by default vs allow by default), and how do we make it impossible to drift silently?
- What is the stable, low-noise `risk_flags` vocabulary for `attestation.admission.policy.diff` so gates catch real admission weakening without alert fatigue?
- How do we keep rule identity stable (keyed by `(action, selector)`), especially when selector structure evolves (labels, classes, fleets)?
- Which admission policy changes should require two-person integrity by default in profiles A/D (rule removal, requirement weakening, selector broadening)?

Risk: admission control becomes folklore (“we totally check attestation”), turning attestation into theater and enabling accidental (or malicious) permission expansion.

See: `docs/388-remote-attestation-admission-and-enrollment.md`, `docs/440-attestation-admission-policy-diff-as-review-surface.md`, `spec/attestation.admission.policy.schema.json`, `spec/attestation.admission.policy.diff.schema.json`.
Last updated: 2026-03-04r177