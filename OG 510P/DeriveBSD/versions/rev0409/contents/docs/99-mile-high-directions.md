# Mile-high directions (idea inventory)

This file integrates a “mile-high brainstorm” into the archive **without turning it into a manifesto**.

Each idea is:
- compatible with the Derive pipeline (Spec → Lock → Plan → Artifact)
- compatible with “hostile builders” and “policy-governed artifacts”
- short here, with deeper discussion in RFCs

## 1) Deployments are commits (ZFS-native)

Treat host generations and workload images as *commit-like* objects:
- content-addressed tree/root digest
- signed metadata + attestations
- atomic switch + instant rollback

See: `docs/100-deployments-are-commits.md`, RFC-0069.

## 2) CAS everywhere (not just “binary cache”)

Make every stage output addressable:
- Spec/Lock/Plan objects
- closure manifests/proofs
- build action outputs

This enables uniform verification and distributed caching.

See: `docs/101-cas-everywhere.md`, RFC-0070.

## 3) Emergency patch mode (“grafts”, but auditable)

Allow fast security patch deployment **without pretending it is a pure rebuild**:
- time-bounded, explicit override records
- new Plan + new closure proof
- explainable “why this is allowed”

See: `docs/102-emergency-grafts.md`, RFC-0071.

## 4) Runtime enforcement (don’t just sign; enforce)

Optional integration with a verified execution mechanism so the runtime can enforce:
- only closure-approved binaries execute
- only closure-approved libraries load

See: `docs/103-runtime-verified-execution.md`, RFC-0072.

## 5) Builder strategy tiers

Two sandboxes (fast → strong):
- Tier 1: jail builds (deny network; no secrets)
- Tier 2: microVM builders (stronger isolation)

See: `docs/104-builder-tiers.md`, RFC-0073.

## 6) Compatibility view for “normally linked” binaries

Provide a policy-governed way to run foreign binaries *without making the host mutable*:
- generate a minimal FHS-ish view from a closure
- use libmap/hints to map libraries
- record mapping evidence for `derive explain`

See: `docs/105-compat-view-foreign-binaries.md`, RFC-0074.

## 7) Blast-radius diffs

Not just “what changed”, but “what authority changed”:
- syscalls/devfs exposure
- pf egress/ingress rules
- writable paths
- capability boundaries

See: `docs/106-blast-radius-diff.md`, RFC-0075.

## 8) Two-person integrity

Support separate approvals for:
- plan/policy approval
- artifact publication
- optional witness rebuild attestations

See: `docs/107-two-person-integrity.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`, RFC-0076.

## 9) Ports/pkg adapter lane

Bootstrap breadth by translating ports/pkg patterns into Derive Plans while enforcing sandbox and recording impurities.

See: `docs/108-ports-pkg-adapter-lane.md`, RFC-0077.

## 10) Repo signing UX lessons (pkg-style ergonomics)

Use the *operational* lessons from pkg repo signing:
- simple repository config
- explicit signature modes
- smooth key distribution

See: `docs/109-repo-signing-ux.md`, RFC-0078.

## 11) Packaged base sets (pkgbase lessons)

Treat the “base system” as explicit, derivable sets (kernel/userland/toolchain) that can be pinned, signed, switched atomically, and rolled back.

See: `docs/111-packaged-base-pkgbase.md`, RFC-0079.

## 12) Health-gated updates (boot success gate)

Switching generations becomes “tentative until healthy”: boot into the new ZFS BE, run minimal health probes, then commit or auto-rollback.

See: `docs/112-health-gated-updates.md`, RFC-0080.

## 13) Signed revertible patchsets (syspatch-style)

For urgent fixes, provide a patchset artifact lane: small signed deltas with automatic rollback payloads, bound to a specific set/generation and policy-bounded.

See: `docs/113-syspatch-style-patchsets.md`, RFC-0081.

## 14) Compartmentalized control planes (Qubes lessons)

Split privileged subsystems into isolated domains (fetch, publish, networking, firewall) so compromise in a network-exposed component cannot silently disable policy.

See: `docs/115-compartmentalized-control-planes.md`, RFC-0083.

## 15) Witness rebuilders (independent verification)

Optionally require independent rebuild attestations for promotion; use deep diffs (diffoscope) to explain divergence.

See: `docs/116-witness-rebuilders-diffoscope.md`, RFC-0084.

## 16) Service dependency graphs (SMF lessons)

Keep rc.d as a backend if desired, but derive and diff a service graph manifest so service intent becomes explainable and reviewable.

See: `docs/114-service-manifests-smf-lessons.md`, RFC-0082; `docs/214-service-supervision-health-as-evidence.md`, RFC-0149.

## 17) Distribution beyond caches (casync/CernVM-FS lessons)

Optional adapters to distribute store snapshots and images efficiently via content-addressed chunking and HTTP/CDN-friendly transport.

See: `docs/119-casync-cvmfs-distribution.md`, RFC-0087.

## 18) Store view minimization, but scalable (sandboxfs optimization)

Hermetic visibility is security-correct but can be expensive if implemented as “mount N inputs.”
Offer an optional sandboxfs-style virtual view mechanism to keep the contract while reducing mount storms.

See: `docs/152-store-view-minimization.md`, `docs/167-sandboxfs-accelerated-storeviews.md`, RFC-0102.

## 19) SBOM + VEX as first-class evidence

Bake “inventory + exploitability context” into the evidence system: signed SBOM statements plus a companion VEX statement bound to policy snapshot.

See: `docs/168-sboms-and-vex-as-evidence.md`, RFC-0103.

## 20) Jobsets as the operational unit of continuous derivation

Define jobsets (target matrices + policies + promotion rules) so continuous build/test/promotion becomes explicit and reviewable.

See: `docs/169-jobsets-and-build-farms.md`, RFC-0104.

## 21) Remote caches are not authorities

Adopt remote caching for performance, but define poisoning/replay boundaries and require verification before import.

See: `docs/170-remote-cache-threat-model.md`, RFC-0105.


## 22) Evidence spine: operations produce receipts (not log folklore)

Make “operational truth” as derivable and inspectable as builds:
- every privileged action emits a typed receipt
- evidence is content-addressed and cross-linked by digest
- incident bundles become *bounded evidence graphs*, not ad-hoc tarballs

See: `docs/229-evidence-spine-overview.md`.


## 23) Lockdown levels as policy outputs (securelevel lessons)

Encode a monotonic “steady-state lockdown” in the posture profile:
- activation runs in `bootstrap`
- once healthy, raise lockdown and emit a receipt
- escape hatches are specialisations / maintenance windows (explicit + receipted)

See: `docs/230-lockdown-levels-and-securelevel.md`, RFC-0164.


## 24) Explicit A/B lifecycle semantics (update_engine mindset)

Health-gated updates need a crisp lifecycle contract:
- stage to an inactive slot (BE)
- explicit boot success recording
- bounded retries and automatic rollback
- incident evidence capture on failure

See: `docs/231-ab-updates-and-recovery-semantics.md`, RFC-0165.


## 25) Typed feature flags (USE lesson)

Treat optional features as typed inputs flowing through Spec→Lock→Plan, so they are reviewable and cache-keyed.

See: `docs/262-feature-flags-and-constraints.md`.

## 26) Standardize project input graphs + registries (flakes lesson)

Bake in a boring “input graph + lock + registry mapping” standard to keep composition deterministic and policy-governed.

See: `docs/263-flake-style-input-graphs-and-registries.md`.

## 27) Filesystem views as derived objects (Plan 9 namespace/union lesson)

Make view composition (bind/union/overlay) a hashable artifact that shows up in diffs and receipts.

See: `docs/264-mount-namespaces-and-union-views.md`.

## 28) Ops tooling as attach/detach bundles (portable services lesson)

Provide a sanctioned, timeboxed “ops bundle” lane instead of letting the base grow forever or normalizing SSH-snowflakes.

See: `docs/265-portable-service-bundles.md`.

## 29) Document sanitization as a first-class portal (Dangerzone lesson)

Make “open untrusted document safely” a standard workflow: disposable sandbox render + evidence-bound output artifact.

See: `docs/267-sanitization-portal-and-disposable-sandboxes.md`.

## 30) Desktop apps as AppVM artifacts (Qubes/Flatpak stance)

Keep the host small by running interactive apps in derived compartments with portal-only host integration.

See: `docs/268-desktop-appvms-and-portalized-apps.md`.

## 31) Portable home areas + embedded user records (systemd-homed lesson)

Make human accounts portable and self-describing by binding identity metadata to an encrypted home container.
Keep unlock/attach operations policy-bound and receipted.

See: `docs/269-portable-home-areas-and-user-records.md`.

## 32) Standardize AppVM persistence (template/private/volatile)

Disposables only work at scale if persistence is predictable.
Bake in a standard storage contract for AppVMs so “what persists?” is answerable and reviewable.

See: `docs/270-appvm-storage-private-volatile-and-home-areas.md`.


## 33) Sealed secrets with evolvable boot policies (TPM lane)

Make TPM-backed sealing operable by designing around PCR brittleness: allow signed policy updates (policy-authorize style) and emit unseal receipts.

See: `docs/272-sealed-secrets-attested-unsealing.md`.

## 34) Air-gap mirror kits + sneakernet updates (offline happy path)

Make offline updates boring and verifiable: mirror kits, quarantine→promote, receipts, and optional delta packs.

See: `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`.


## 35) Continuous fuzzing + automatic bisection (make regressions cheap)

Bake in the ops+security loop:
- continuous fuzzing emits receipts and produces minimized crash cases as replayable bundles
- regressions automatically bisect over Plan digests and emit signed root-cause certificates

See: `docs/274-continuous-fuzzing-farm.md`, `docs/275-root-cause-certificates-and-bisection.md`.


## 36) Origin labels + quarantine attributes (stop mystery bytes)

Make inbound content (downloads, attachments, USB files, shares) carry a stable origin label and quarantine metadata, and route opening through sanitize-first portals.

See: `docs/280-origin-labels-and-quarantine-attributes.md`.


## 37) Outbound network is leased authority (per-app firewall lesson)

Bake in a network egress broker that issues timeboxed grants and emits flow receipts, and compile enforcement to PF anchors.

See: `docs/281-network-egress-broker-and-consent.md`.


## 38) Split-view defense must be operable (witness network lesson)

For high-assurance channels, require witness-cosigned checkpoints as a policy-tunable quorum, and make checkpoint receipts a first-class offline verification unit.

See: `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`, `docs/259-transparency-monitors-and-witness-gossip.md`.


## 39) Time is a security input (NTS + Roughtime + LKGT)

Treat time like other operational facts: policy allowlists, proof bundles, snapshots, receipts, and LKGT monotonicity to prevent rollback-by-clock.

See: `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`, `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`.


## 40) Model-check the scary state machines (formal lane)

Some DeriveBSD ideas are *protocols* (state machines) more than “code”:
- bootenv switching with try-counters
- update freshness/expiry and witness cosigning
- network lease brokers (listen/egress)
- breakglass and revocation

Bake in a minimal contract: tiny finite models + CI runs that emit a receipt.

See: `docs/287-formal-model-checking-and-invariants.md`.

## 41) Workload identity + attested mTLS (SPIFFE-style)

Avoid static API tokens and ad-hoc shared secrets by issuing short-lived workload credentials (lease-based) and normalizing mTLS as a compiled constraint.
Bind issuance to artifact digests/attestation, and emit receipts for issuance/renewal.

See: `docs/181-workload-identity-and-secretless-deploys.md`.


## 42) No unverified execution (exec integrity policy)

Treat "what can execute" as a first-class policy and compile it from the closure. Prefer BSD-native backends (MAC/veriexec) when available, and always emit activation receipts so incidents can answer what enforcement was active.

See: `docs/289-exec-integrity-policy-and-verified-execution.md`, `spec/exec.integrity.policy.schema.json`.


## 43) Keyless signing as identity evidence (not promotion authority)

Support a Sigstore-shaped keyless signing lane that yields digest-bound identity receipts, suitable for dev channels and third-party caches, without weakening the threshold publish lane.

See: `docs/290-keyless-signing-and-publisher-identity-receipts.md`, `spec/publisher.identity.receipt.schema.json`.


## 44) Remote assistance sessions as evidence (no backdoors)

Bake in a blessed remote support path: timeboxed leases for screen share/control, explicit consent/quorum approvals, and an envelope object that ties the session to receipts, recordings, and exports so incidents can answer what happened.

See: `docs/291-remote-assistance-sessions-as-evidence.md`, `spec/support.session.schema.json`.


## 45) Terminal session recording as leased authority (output-only by default)

Support opt-in terminal session recording for incident response and accountability, but make it explicit, bounded, revocable, and exportable only through deterministic redaction + export policies.

See: `docs/292-terminal-session-recording-as-evidence.md`, `spec/tty.session.recording.schema.json`.



## 46) Treat authoring as “frontend → canonical IR” (config languages as compiler lanes)

A greenfield advantage is refusing to let the authoring language become the real product.
Ship a canonical JSON IR and allow optional frontends (CUE/Pkl/Nickel/etc) only as pinned compiler lanes that emit canonical JSON plus traces.

See: `docs/79-derive-spec-frontends.md`, ADR-0023, `docs/83-evaluator-minimalism.md`.


## 47) Attribute-indexed metadata + live queries (BFS lesson)

If we standardize origin/quarantine labels and capability bookmarks, we should also standardize *how you query them*.
Make metadata search a portal/lease (not ambient), and treat index snapshots as evidence so incidents can answer “what was where, and why”.

See: `docs/293-attribute-indexed-metadata-and-live-queries.md`, `docs/280-origin-labels-and-quarantine-attributes.md`.


Last updated: 2026-02-26
