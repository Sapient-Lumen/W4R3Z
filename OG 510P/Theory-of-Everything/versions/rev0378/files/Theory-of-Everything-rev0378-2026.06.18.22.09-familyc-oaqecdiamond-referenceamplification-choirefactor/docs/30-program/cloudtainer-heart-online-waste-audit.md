# Cloudtainer heart / online-pressure / waste audit

Revision: `rev0366`

## Scope

This audit reopens `docs/30-program/mission-heart-missing-waste-audit.md` after rev0365. It asks what the archive is really doing, what rev0365 repaired, what is still missing, which work is wasteful, and which online frontier pressure should steer later source-custody or scientific-discriminator moves. It is a control and triage surface only: it does not promote any route, evidence unit, forecast, decision outcome, public-record credit, or observed-sector recovery state.

## Heart of the mission

The archive is a **salient unification control system**, not a theory announcement. Its live job is to keep every candidate route honest while the field waits for evidence or mathematics sharp enough to discriminate between deep organizing principles.

The heart can be stated compactly:

> Find the minimal generative spine by forcing every proposed bridge to pay its recovery, public-record, witness, negative-control, and rollback debts before it can become authority.

That means the archive should reward only changes that reduce one of these burdens:

- recover known low-energy QFT / Standard Model structure rather than merely fit a surrogate;
- recover classical, semiclassical, and strong-field gravity in the correct domain;
- explain entropy, horizon, information, and observer-record structure without metaphor inflation;
- connect cosmological parameters, boundary conditions, and global state to candidate-native mechanisms;
- name public records, acquisition protocols, and failure modes rather than treating papers, benchmarks, or packages as evidence by themselves.

The deepest design insight remains correct: **anti-laundering is part of discovery**. Without the archive's caps, a public data release, a beautiful duality, a benchmark, a generated provenance sidecar, or a lab-forecast headline can all be retold as “evidence for a theory of everything” even when they only improve custody, denominator pressure, or a local bridge.

## What rev0365 actually fixed

rev0365 fixed real cloudtainer problems rather than moving scientific authority:

- It added RO-Crate / PROV-facing sidecars without making them a second source of truth.
- It made lint and package smoke progress observable with elapsed-time steps.
- It turned candidate-native docket boilerplate into a measurable duplication surface.
- It refactored neutral source-role helper mechanics without collapsing route-specific scientific checks.
- It kept compact public-source custody and route non-promotion intact.

Those fixes matter because the archive was beginning to suffer from a paradox: the controls were strong, but a human could not easily tell whether the cloudtainer was slow, stale, duplicated, or scientifically meaningful. rev0365 improved observability.

## What is still missing

### 1. A positive two-page kernel testcard

The archive has hundreds of ledgers explaining what cannot be overclaimed, but it still lacks a compact **positive kernel testcard**: a tiny surface that asks each candidate or bridge family for its primitive objects, dynamical rule, gauge/redundancy quotient, coarse-graining map, observer/public-record map, and first three discriminator-bearing observables.

This should not become another router. It should be a one-table compression target tied to existing route rows.

### 2. Release-identity decoupling from durable ledgers

The archive policy already says durable ledgers and vocabularies should be revisionless unless the revision tag itself changes continuation state. In practice, `registered-ledger-revision-alignment` still forces broad top-level revision churn. This is the largest remaining waste pattern because release-control changes make many durable files look semantically touched.

### 3. A current-source watch schedule that is stricter than “freshness”

The archive now has frontier freshness assertions and source snapshots, but the next useful layer is a **source-intake triage schedule**:

- exact-version custody when an official record, checksum, inventory, or DOI version changes;
- zero-placement watchlist when a public release is not yet cosmology / route-bearing;
- no custody when the only available material is bulky payload, press prose, or a mutable landing page;
- route-denominator pressure only when the source changes a blocker, negative control, acquisition state, or observed-sector burden.

### 4. A stricter BMV/GIE comparator-model gate

The BMV/GIE lane is attractive because it offers low-energy laboratory contact, but it is also high-risk because “entanglement happened” can be laundered into “gravity is quantized” or even “a ToE candidate is favored.” The route already caps this; future work should strengthen comparator-model and shielding/noise gates before accepting any public result as more than conditional discriminator pressure.

### 5. Generated-surface hierarchy and expansion-on-demand

`AUTHORITY-DEPENDENCY-GRAPH.json`, large generated audits, and long ledgers are useful for replay but not for human mission reentry. The archive should designate which generated outputs are:

- restart-facing summaries,
- machine-only expansion products,
- failure-diagnostic products,
- or deprecated once their generator is trusted.

## Online-pressure readout

Current public context supports the archive's conservative posture:

- GWTC-5 is now a real large public gravitational-wave catalog / candidate-data surface, but it is still mostly a strong-field-GR and population-astrophysics source, not a quantum-gravity discriminator by itself.
- DESI DR2 and ACT DR6 are strong cosmology records, but their ToE relevance is still parameterization-, likelihood-, and cross-probe-systematics-capped.
- Euclid Q1 is a public astrophysics quick release, not a cosmology-likelihood release; near-future Euclid releases deserve exact watchlist/custody handling only when their official record status changes.
- NANOGrav 15-year data strengthens nanohertz gravitational-wave background pressure, but source attribution and cosmological/exotic alternatives remain route-local, not ToE closure.
- RO-Crate, PROV, SLSA, DataCite, and SWHID-style identifiers are good interoperability targets only if they point to existing archive truth rather than duplicating scientific authority.

## What went severely wrong or wasteful

### Severe: stale currentness was allowed to survive

Earlier bundles allowed human-facing currentness wording to drift from manifest truth. This was severe because it could make a restart cite or continue the wrong head. Later lint and mirror rules correctly made currentness drift a package-level failure.

### Severe: locator-only custody looked safer than it was

A landing page, record locator, or public prose inventory is not stable payload custody. rev0357-rev0363 fixed much of this by adding compact source snapshots, exact-version pins, retained checksums, and local inventory-control files. The correction should continue only when a compact retained control file makes future replay fail closed.

### Wasteful: release-control churn still touches durable ledgers

A top-level `revision` field in every durable ledger causes archive-control releases to mutate semantic surfaces that did not change. This makes diffs noisy and makes real science deltas harder to see. The correction should be a schema-level distinction between row semantic version, ledger schema version, and bundle release identity.

### Wasteful: the no-overclaim machinery can become the mission

The archive has successfully blocked many bad promotions. The next risk is that each blocked phrase creates a new ledger family, docket, or mirror. Controls should now be judged by compression return: does this surface prevent a distinct live inflation step, or is it only repeating “do not overclaim” in another namespace?

### Wasteful: monolithic lint is too big to understand locally

The lint path passes, but `tools/lint_archive.py` is too large for ordinary review and contains most of its logic as long top-level execution. It should be split into semantic validators by family while preserving the aggregate `make lint` entrypoint and negative replay coverage.

## What should change next

1. Add the positive kernel testcard as a compact table, not a new family of ledgers.
2. Start durable-ledger revision-stamp decoupling with a small pilot: choose one low-risk ledger family, separate `semantic_revision` / `schema_version` / `bundle_checked_at`, and make the generated alignment audit accept the distinction.
3. Keep the compact source-custody rule: retain only official checksums, manifests, inventories, exact-version identity pins, or tiny public payloads that add replay value.
4. Split lint by validator family while preserving one aggregate package contract.
5. Make every online frontier intake produce one of four outcomes: no-placement, watchlist, custody-only, or route-denominator delta. Anything else is literature accumulation.

## Speculative readout

The archive's strongest scientific bet is not “Family C wins.” It is that the winning theory, if one becomes visible, will be the one whose primitive spine makes multiple bridge debts collapse at once: local QFT, semiclassical gravity, entropy/observer/public-record structure, and cosmological boundary conditions become different projections of one small mechanism.

Family C / holographic-QEC remains the most structured partial route because it already relates geometry, entanglement, reconstruction, and operator access. But it still borrows too much from boundary conditions, large-`N` / AdS-like regimes, selected dictionaries, and witness assumptions to count as broad ToE authority. Late-time cosmology and gravitational-wave catalogs are empirically rich but many-to-one. BMV/GIE is potentially revolutionary but inference-fragile. String/M, asymptotic safety, causal set, amplitudes/bootstrap, thermodynamic gravity, and QRF/relational routes each pay some debts while leaving others dominant.

The positive opportunity is therefore to turn the archive into a **discriminator factory**: each revision should sharpen one public-record burden, one negative control, one comparator family, or one kernel testcard cell. Archive-control work is justified only when it makes that factory harder to fool and easier to restart.

## Non-promotion boundary

This audit changes cloudtainer guidance and followthrough priority only. It does not promote any route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, citation head, or scientific current-head ordering.
