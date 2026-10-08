# Changelog

## rev0378 — Family-C OAQEC diamond / reference amplification / Choi refactor

Slug: `familyc-oaqecdiamond-referenceamplification-choirefactor`. Bundle: `Theory-of-Everything-rev0378-2026.06.18.22.09-familyc-oaqecdiamond-referenceamplification-choirefactor.zip`.

- Completes the finite-dimensional Family-C OAQEC theorem denominator with the complementary-channel diamond defect `delta_A=||Nhat-Nhat o P_{A'}||_diamond` and Bény's two-sided recovery bounds `delta_A^2/4<=E_A<=2 sqrt(delta_A)`.
- Inverts the sufficient theorem branch: target recovery error `tau` requires `delta_A<=tau^2/4`; a generic dimension-aware state-to-diamond lift further requires `epsilon_state<=tau^2/(4 d_code)`.
- Adds an exact transpose-dephasing CPTP family in dimension `d`: the unassisted state envelope is `2/(d+1)` while the exact complementary diamond defect is `(d-1)/(d+1)`. At `d=4096`, the former is `4.88162e-4` and the latter is `0.999512`, forcing recovery error at least `0.249756` through the theorem.
- Adds an exact erasure-channel common-decoder positive control with `delta_A=E_A=2p(1-1/d^2)`, separating a true operational reconstruction benchmark from the reference-amplification failure.
- Makes the nonperturbative dimension wedge executable: for `d_code~exp(s/G)` and state error `~exp(-c/G)`, the generic lift converges only when `c>s`; the critical `c=s` case plateaus.
- Factors maximally entangled vectors, swap operators, diagonal-correlation projectors, and Choi/Jordan audits into shared route-local operator helpers while retaining theorem policy in the owning Family-C benchmark.
- Strengthens the existing forecast, decision, decoder, algebraic-locality, QEC, and source-role audits to require diamond/cb norm, arbitrary external reference, explicit code/reference dimension, and worst-sector quantification; no new registry family or route promotion is introduced.

## rev0377 — Family-C Condition-2 routing / coherent split / policy refactor

Slug: `familyc-condition2-routing-coherentsplit-policyrefactor`. Bundle: `Theory-of-Everything-rev0377-2026.06.18.19.56-familyc-condition2-routing-coherentsplit-policyrefactor.zip`.

- Converts REF-0735 Definition 7 Condition 2 into a sharp sector-diagonal/direct-sum common-decoder bound `epsilon_common<=epsilon_block+2 epsilon_sub-tr/(1-epsilon_iso,small)` and verifies exact saturation with fitted power one.
- Inverts the bound into concrete source budgets: at `epsilon_iso,small=0.001`, target errors `0.1`, `0.05`, and `0.01` require `epsilon_sub-tr<=0.04995`, `0.024975`, and `0.004995` for dominant-block decoder certificates; full-sector-only certificates pay a factor-two tighter budget.
- Adds two exact-isometry coherent-sector controls: one has coherent error exactly paid by `epsilon_OD` while `epsilon_sub-tr=r`; the other has `epsilon_OD=0` while the full Condition-2 trace-norm term pays. No unjustified universal sum rule is asserted.
- Adds a rare-sector negative control where average leakage and average decoder error vanish as `1/K` while worst-sector error remains `0.2`, preserving Condition 2's uniform quantifier.
- Factors the source-conditioned theorem translation into `tools/familyc_source_routing.py` and hardens the existing finite-N policy to match semantic concept groups after notation normalization instead of brittle underscore/hyphen spellings.
- Re-execs the lint and package-smoke orchestrators under Python `-S` while leaving child validators on the normal interpreter, and stages lint output in file-backed logs; the measured idle orchestration parent fell from about 290 MiB RSS to about 19 MiB, removing avoidable overlap with schema/archive validators.
- Integrates the sharper denominator into the kernel testcard, Family-C forecast, decision, empirical-delta, decoder, relative-entropy, bridge, workstream, and source-role surfaces without adding a registry or promoting route authority.

## rev0376 — Family-C commutant gluing / algebra quotient / source correction

Slug: `familyc-commutantgluing-algebraquotient-sourcecorrection`. Bundle: `Theory-of-Everything-rev0376-2026.06.18.17.24-familyc-commutantgluing-algebraquotient-sourcecorrection.zip`.

- Corrects a source-scope error: REF-0735 fixes one boundary-region pair across sectors and reconstructs a block-diagonal direct-sum wedge algebra, so the source is no longer charged with sector-dependent region switching or automatic off-diagonal coherence preservation.
- Adds an exact fixed-region decoder-gluing cell with OAQEC commutant residual `1.8883e-18`, coherent-decoder error `1.9029e-16`, and direct-sum algebra expectation residual `1.1102e-16`.
- Separates direct-sum algebra recovery from full-Hilbert coherence recovery: a valid algebra decoder may dephase excluded coherences, while a coherent controlled decoder succeeds when the sector tag is retained.
- Adds a worst-sector sector-instrument control that saturates the sharp `2 p_max` state/center-observable cost and a hidden-frame cell with a linear common-decoder obstruction.
- Quarantines the rev0375 wedge-switching code as a generic state-dependent-region comparator rather than a debt of REF-0735.
- Refactors decoder-gluing/OAQEC mechanics into `tools/familyc_decoder_gluing.py`, leaving generic matrix and operator-algebra utilities in `tools/familyc_operator_algebra.py`.
- Promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

## rev0375 — Family-C factor blocks / wedge switching / decoder refactor

Slug: `familyc-factorblocks-wedgeswitch-decoderrefactor`. Bundle: `Theory-of-Everything-rev0375-2026.06.18.15.07-familyc-factorblocks-wedgeswitch-decoderrefactor.zip`.

- Extends the direct-sum audit from its commutative sector center to `A=direct_sum_alpha M_2`; verifies `D(full)=D(center)+sum_alpha q_alpha D(factor_alpha)` with residual `2.22e-16` and nonzero factor commutators.
- Proves exact additive center/factor contributions to the declared product-domain `D_max` and `L_K^osc`; center-only accounting captures only `0.4610` and `0.4904` of the totals.
- Adds a noncommuting modular-frame negative control: for `lambda=exp(-1/G)` and `theta=G`, state trace error vanishes as `G` while operator-log error tends to one nat; `theta=G^2` restores convergence.
- Adds a state-dependent wedge/common-decoder code: AC and BC reconstruct their own sectors exactly, but each fixed region erases the other sector and forces minimax trace recovery error at least `1`.
- Separates direct-sum algebra recovery from full-Hilbert recovery: adaptive sector routing recovers the block algebra but dephases cross-sector coherence by trace error `1`; the fixed union region is an exact positive control.
- Refactors shared quantum-matrix mechanics into `tools/familyc_operator_algebra.py` and corrects an audit bug that had applied a Hermitian-only norm to an anti-Hermitian commutator.
- Integrates the stricter fixed-region, factor-block, and coherence obligations into the kernel testcard, forecast, empirical delta, decision experiment, route-control ledgers, workstream, bridge, and restart surfaces without route promotion.

## rev0374 — Family-C FLM isometry / weighted transport / smoothness refactor

Slug: `familyc-flmisometry-weightedtransport-smoothnessrefactor`. Bundle: `Theory-of-Everything-rev0374-2026.06.18.13.18-familyc-flmisometry-weightedtransport-smoothnessrefactor.zip`.

- Propagates the source Appendix-C full-system approximate-FLM implication `eps_iso,small <= 2 sqrt(eps_FLM)` and Lemma-4 large-code bound `delta_iso <= eps_iso,small + eps_OD`; explicitly bars inference of this branch from subregion FLM alone.
- Derives the source-closed exponential-sector wedge `a>max(t,2 gamma)` for `eps_FLM~G^a`, `eps_tail~G^t`, and `K~exp(c/G^gamma)`, with success-trace power `min((a-t)/4,a/4-gamma/2)` up to logs.
- Adds exact commuting-sector log-smoothness transport algebra: `eps_l_smooth=max_alpha |log((T p)_alpha/p_alpha)|` and the sufficient relative-inflow bound `eps_l_smooth<=-log(1-zeta)`.
- Adds a severe Gaussian-tail control where `1e-8` nearest-neighbor leakage and `9.32050e-10` total variation coexist with `83.08617` nats of operator-log error at 513 sectors.
- Adds a constructive `p`-stationary detailed-balance control with log-smoothness residual below `4.1e-13`.
- Refactors representation-neutral linear fitting, state-domain sector transport, and source-isometry exponent algebra into existing narrow helpers; extends the existing Family-C source-role audit rather than adding a registry.
- Integrates the sharper denominator into the kernel testcard, decision experiment, forecast, empirical delta, bridge/workstream, and restart surfaces without promoting any route or public-record authority.

## rev0373 — Family-C sector weights / domain wedge / geometry refactor

Slug: `familyc-sectorweights-domainwedge-geometryrefactor`. Bundle: `Theory-of-Everything-rev0373-2026.06.18.10.45-familyc-sectorweights-domainwedge-geometryrefactor.zip`.

- Derives exact finite-dimensional reduced-algebra geometry for the spectral-floor domain: `D_max=(1-d lambda) log[(1-(d-1)lambda)/lambda]` and `L_K^osc=log[(1-(d-1)lambda)/lambda]`, with explicit extremizer replay to floating-point precision.
- Restricts the large direct sum to its classical sector center and proves that fixed total floor mass gives `D_max,L_K^osc=Theta(log K)`; sector-local log stability does not control the sector-weight simplex.
- Adds an executable exponential-sector false-convergence cell: `eps_FLM~G^3`, `eps_tail~G`, `eps_iso_small=delta_iso~G`, and source `eta` all vanish, while `K~exp(1/G)` leaves the flagged defect and success-conditioned theorem bound order one.
- Adds comparison cells showing polynomial sector growth converges under the same local powers and exponential growth converges when `delta_iso~G^2`, isolating the necessary threshold `delta_iso log K -> 0` for this bridge.
- Corrects the domain notation so `D_max` and `L_K^osc` belong to the reduced bulk-wedge/reconstructed algebra appearing in the JLMS comparison, not an unspecified full-code state space.
- Refactors exact spectral-floor and sector-simplex geometry into `tools/familyc_state_domain.py`; scenario policy, acceptance thresholds, and interpretation remain in the owning Family-C benchmark.
- Integrates the result into the kernel testcard, Family-C decision experiment, bridge/workstream, and restart surfaces without promoting any route or public-record authority.

## rev0372 — Family-C flagged channel / tail wedge / theorem split

Slug: `familyc-flagchannel-tailwedge-theoremsplit`. Bundle: `Theory-of-Everything-rev0372-2026.06.18.08.42-familyc-flagchannel-tailwedge-theoremsplit.zip`.

- Constructs a genuine contraction-scaled flagged CPTP theorem completion of the approximate encoding; conditioning on the orthogonal success branch exactly recovers the source's nonlinear normalized state, while the flag is explicitly a proof device rather than an asserted physical CFT output.
- Derives explicit flagged-channel and success-conditioned decoder budgets in terms of projected residual `eta`, isometry defect `delta_iso`, modular oscillation `L_K^osc`, and same-domain relative-entropy diameter `D_max` instead of leaving free polar transport terms.
- Executes a 36-state full-rank probe: affinity, success-branch identity, and block relative-entropy decomposition close to machine precision; target inversion shows that with spectral floor `0.01` and `eta=0`, a `0.1` recovery target permits only about `3.72e-5` isometry defect.
- Propagates the source Eq. (3.17) tail-ratio structure into a conditional exponent wedge: `a>t` is necessary, code-domain growth can cancel convergence, and the theorem route produces an additional square-root loss in success-conditioned trace/observable control.
- Adds executable failure cases for a nonclosing tail ratio and for domain growth that erases apparent source improvement; retains the rare-sector, non-affinity, and spectral-floor controls from prior revisions.
- Adds a noncommuting full-rank qubit audit with explicit Kraus operators, Choi positivity, trace preservation, success-state identity, and quantum block-relative-entropy replay; the actual flagged loss remains below the generic domain-diameter bound.
- Refactors route-local theorem algebra, stable inversions, diagonal and noncommuting flagged-channel probes, and source-schedule calculations into `tools/familyc_channel_completion.py`; the artifact generator now orchestrates rather than owning all mathematics.
- Integrates the result into the kernel testcard, Family-C decision/forecast/bridge/workstream/restart surfaces without promoting any route or public-record authority.

## rev0371 — Family-C channel premise / polar join / numeric refactor

Slug: `familyc-channelpremise-polarjoin-numericrefactor`. Bundle: `Theory-of-Everything-rev0371-2026.06.18.07.03-familyc-channelpremise-polarjoin-numericrefactor.zip`.

- Corrects a load-bearing premise error in the Family-C JLMS bridge: the source-normalized map `V rho V^dagger / Tr(V rho V^dagger)` is non-affine whenever `V^dagger V` is not scalar, so it is not the quantum channel required by universal recovery.
- Derives and executes the exact identity joining a uniform projected-JLMS residual to all-pairs relative entropy; exact/scalar encoding gives the direct `2 eta` bound after logarithm-unit conversion.
- Adds explicit polar channelization `U=V(V^dagger V)^(-1/2)` and the conditional genuine-channel budget `eta/(1-delta_iso)+chi_out+chi_bulk`; a `0.1` trace/observable target permits only `3.43280349090821e-4` nats of total channel residual.
- Adds a non-affinity midpoint probe and a spectral-floor stress where the residual-only approximate-map bound first fails at `lambda_min=10^-6`; retains the rare-sector average-to-supremum negative control.
- Refactors the qutrit, approximate-recovery, and JLMS calculations onto `tools/benchmark_numeric.py` for shared stable-number and log-log-slope mechanics while leaving scientific models and acceptance policy local.
- Integrates the corrected denominator into the kernel testcard, Family-C decision/forecast, bridge, workstream, and restart surfaces without promoting any route or public-record authority.

## rev0370 — Family-C JLMS budget / rare-sector / generator refactor

Slug: `familyc-jlmsbudget-raresector-generatorrefactor`. Bundle: `Theory-of-Everything-rev0370-2026.06.18.05.03-familyc-jlmsbudget-raresector-generatorrefactor.zip`.

- Adds `tools/familyc_jlms_recovery_budget_benchmark.py` and deterministic JSON/Markdown outputs.
- Translates a uniform pairwise base-2 relative-entropy defect into universal-recovery fidelity, local trace-norm, arbitrary-code-state trace/normalized-observable, and target-remainder budgets.
- Makes the theorem exponent loss executable: an `O(R^-p)` defect gives only `O(R^-p/2)` trace/observable control through the stated theorem, while squared-fidelity infidelity remains `O(R^-p)`.
- Adds a rare-sector negative control where a uniform reference-mixture defect and its mixture error fall as `1/K` but the declared bad-sector defect and minimax recovery error stay order one; laundering the average into a whole-domain bound becomes self-contradictory at `K=16`.
- Pins relative-entropy units to bits, records the nats conversion, and keeps toy `D`, abstract `R`, and physical `N`/`G` resources explicitly unmapped.
- Integrates the result into the kernel testcard, Family-C decision/forecast/relative-entropy/decoder surfaces, bridge experiment, workstream, source-role audit, and restart path without route promotion.
- Refactors the qutrit, approximate-scaling, and JLMS generators onto `tools/generated_benchmark_artifact.py`, sharing only deterministic write/check/CLI mechanics while keeping scientific logic local; updates `FT-0355-003`.

## rev0369 — Family-C operational norm / scaling / dilution refactor

Slug: `familyc-operationalnorm-scaling-dilutionrefactor`. Bundle: `Theory-of-Everything-rev0369-2026.06.18.02.54-familyc-operationalnorm-scaling-dilutionrefactor.zip`.

- Adds `tools/familyc_approximate_recovery_scaling_benchmark.py` and generated JSON/Markdown outputs.
- Replaces a free leakage sweep with a prime-dimension family carrying exact complementary-channel diamond distance and exact declared-decoder worst-case entanglement fidelity.
- Checks fitted `D^-1/2` leakage and `D^-1` decoder-infidelity laws against analytic prefactors, including the asymptotic `pi^2/32` information-disturbance ratio.
- Adds a fixed-leakage negative control that exposes max-entry Knill-Laflamme residuals as a dimension-diluted false convergence metric.
- Integrates the result into the kernel testcard, Family-C decision experiment, workstream, bridge experiment, and decoder-fidelity audit without route promotion.
- Refactors `tools/run_lint_steps.py` so children suppress bytecode transients, capture output deterministically, and fail with a bounded per-step timeout instead of inheriting descriptors indefinitely.

## rev0368 — Family-C qutrit cell / same-record / helper refactor

Slug: `familyc-qutritcell-samerecord-helperrefactor`. Bundle: `Theory-of-Everything-rev0368-2026.06.18.00.38-familyc-qutritcell-samerecord-helperrefactor.zip`.

- Adds a standard-library executable three-qutrit reconstruction benchmark with exact single-erasure checks, any-two-share decoder probes, and deterministic generated JSON/Markdown.
- Adds a same-restricted-record discriminator: two declared logical dictionaries coincide on every one-share record but separate after the richer any-two-share decoded record.
- Adds a controlled leakage sweep and an isometric repetition-code negative control so success cannot be inferred from isometry or metric choice alone.
- Integrates the owned result into the existing Family-C kernel testcard, decision experiment, bridge surface, workstream, and restart path without adding a router or promoting the route.
- Refactors both Family-C source-role policies onto shared neutral row/source-ref helpers and updates `FT-0355-003` while keeping route-specific science local.
- Adds `REF-0735` as the large-code approximate-QEC/JLMS denominator for the next substantive step.

## rev0367 — Executable kernel testcard / smoke-share refactor

Slug: `kerneltestcard-executable-smokeshare-refactor`. Bundle: `Theory-of-Everything-rev0367-2026.06.17.18.01-kerneltestcard-executable-smokeshare-refactor.zip`.

- Adds `KERNEL-TESTCARD.json` and generated `docs/40-model/positive-kernel-testcard.md` so all 13 current OQ-0057 routes now have positive primitive/dynamics/quotient/coarse-graining/public-record/negative-control/discriminator/debt/next-work cells.
- Adds `tools/kernel_testcard_audit.py` and `docs/30-program/kernel-testcard-audit.generated.md`, with `make index`, `make lint`, and package smoke checking coverage, caps, and generated-surface drift.
- Refactors lint-step ownership into `tools/lint_steps_config.py` so `tools/run_lint_steps.py` and `tools/smoke_package_release.py` share one semantic step inventory.
- Closes `FT-0366-001`; the active followthrough queue now has 8 items.
- Preserves compact public-source custody and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

## rev0366 — Heartscan / online-waste / kernel-testcard triage

Slug: `heartscan-onlinewaste-kerneltestcard`. Bundle: `Theory-of-Everything-rev0366-2026.06.17.16.25-heartscan-onlinewaste-kerneltestcard.zip`.

- Adds `docs/30-program/cloudtainer-heart-online-waste-audit.md` as the fresh mission-heart / missing-controls / waste-correction audit for this session.
- Wires the new audit into WS-0062 and adds `FT-0366-001` for a positive candidate-kernel testcard without minting another router family.
- Keeps ACT/DESI/GWTC/SPT/NANOGrav compact public-source custody intact and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

## rev0365 — Release provenance / smoke-progress refactor

Slug: `provenance-smokerefactor`. Bundle: `Theory-of-Everything-rev0365-2026.06.14.17.58-provenance-smokerefactor.zip`.

- Adds generated standards-facing release sidecars: `ro-crate-metadata.json` and `RELEASE-BUILD-PROVENANCE.json`, produced and checked by `tools/release_provenance_sidecar.py`.
- Replaces the opaque aggregate `make lint` path with `tools/run_lint_steps.py`, emitting named elapsed-time phases; package smoke now checks sidecar/audit drift and prints per-subprocess elapsed time.
- Reworks source-role negative replay to use a temporary mutation-tree symlink mirror with private-copy-on-write before mutations, cutting replay wall time while avoiding unsafe hard links.
- Adds `docs/10-method/candidate-native-docket-common-block.md` plus `docs/30-program/candidate-native-docket-duplication-audit.generated.md` to quantify and bound candidate-native docket boilerplate before future compression.
- Refactors neutral source-role row lookup/source-ref helpers into `tools/source_role_event_utils.py` and updates cosmology/B-mode source-role policies to use them without moving route-specific checks.
- Preserves compact ACT/DESI/GWTC/SPT/NANOGrav custody state and promotes no route, evidence unit, forecast, decision outcome, public-record credit, or observed-sector recovery state.


## rev0364 — Mission triage / heartscan audit

Slug: `missiontriage-heartscan`. Bundle: `Theory-of-Everything-rev0364-2026.06.14.17.21-missiontriage-heartscan.zip`.

- Adds `docs/30-program/mission-heart-missing-waste-audit.md` as a cloudtainer deep-read audit of the archive's mission heart, missing controls, and waste-correction path.
- Identifies RO-Crate/PROV-style research-object metadata, SLSA-like release attestation, SWHID-style software-source identifiers, lint progress/timeout instrumentation, generated/docket compression, and durable-ledger revision-stamp decoupling as future correction lanes.
- Wires the audit to `WS-0062` without changing the active followthrough queue.
- Promotes no route, evidence unit, forecast, decision outcome, public-record credit, or observed-sector recovery state.

## rev0363 — ACT DR6 inventory-control replay refactor

Slug: `actdr6-inventorycontrol-replayrefactor`. Bundle: `Theory-of-Everything-rev0363-2026.06.13.17.42-actdr6-inventorycontrol-replayrefactor.zip`.

- Upgrades `REF-0729` ACT DR6.02 public-data custody and `REF-0731` ACT DR6 lensing-likelihood custody from locator-only to retained compact inventory-control JSON.
- Adds semantic validation for `inventory_control_json` local payload records, including source-ref binding, entry counts, category counts, source-page locators, payload-retention vocabulary, component-name coverage, and S0 cap consistency.
- Expands source-role negative replay from 18 to 19 cases by mutating retained inventory-control semantics while keeping generic file hash/size/line-count metadata coherent.
- Adds `docs/30-program/act-dr6-inventory-control-replay-audit.md`.
- Promotes no route, evidence unit, forecast, decision outcome, public-record credit, or observed-sector recovery state.

## rev0362 — NANOGrav md5 inventory / replay refactor

Slug: `nanograv-md5inventory-replayrefactor`. Bundle: `Theory-of-Everything-rev0362-2026.06.13.14.48-nanograv-md5inventory-replayrefactor.zip`.

- Upgrades `REF-0734` NANOGrav public-data custody from locator-only to exact Zenodo v2.1.0 timing-data identity plus md5 inventory for related public analysis products.
- Strengthens `tools/source_snapshot_manifest.py` with Zenodo DOI/record checks and payload-inventory checksum validation.
- Adds a source-snapshot negative replay that corrupts an inventory checksum and must fail lint.
- Adds `docs/30-program/nanograv-md5-inventory-versionpin-audit.md`.
- Promotes no route, evidence unit, forecast, decision outcome, public-record credit, or observed-sector recovery state.


## rev0361 — GWTC md5 anomaly replay refactor

Slug: `gwtcmd5-anomaly-replay-refactor`. Bundle: `Theory-of-Everything-rev0361-2026.06.13.08.17-gwtcmd5-anomaly-replay-refactor.zip`.

- Retains the official GWTC-5 Zenodo v2 `md5sums.txt` checksum manifest under `payload-snapshots/REF-0629-GWTC5-O4B-CANDIDATE-DATA/` with local SHA-256, byte-size, line-count, and upstream component-md5 replay.
- Upgrades `SOURCE-SNAPSHOT-MANIFEST.json` to schema `0.5` and changes the GWTC custody row from component-md5 inventory only to retained md5-manifest custody without vendoring the bulky candidate-data archives.
- Refactors `tools/source_snapshot_manifest.py` to validate retained files against upstream component checksums when available, allow only declared upstream malformed checksum-manifest lines, and report known malformed-line counts in the generated audit.
- Expands source-role negative replay from 16 to 17 cases by mutating the declared malformed GWTC manifest line while keeping generic file and component-checksum metadata coherent.
- Adds `docs/30-program/gwtc-md5-manifest-anomaly-custody-audit.md`; no route, evidence unit, public-record credit, forecast, or decision outcome is promoted.

## rev0360 — DESI SHA-256 manifest replay refactor

Slug: `desisha256-manifest-replay-refactor`. Bundle: `Theory-of-Everything-rev0360-2026.06.13.05.58-desisha256-manifest-replay-refactor.zip`.

- Retains the official DESI DR2 BAO cosmology SHA-256 checksum manifest under `payload-snapshots/REF-0626-DESI-DR2-BAO-COSMO-PARAMS/` and records local SHA-256, byte-size, line-count, entry-count, and path-root replay.
- Changes `SOURCE-SNAPSHOT-MANIFEST.json` to schema `0.4` and upgrades `SSM-REF-0626-DESI-DR2-CHAIN-RELEASE-CUSTODY` from locator/inventory custody to retained compact integrity-map custody without vendoring bulky chain/posterior payloads.
- Refactors `tools/source_snapshot_manifest.py` to parse retained checksum manifests, validate per-entry checksum syntax, reject unsafe component paths, and enforce checksum-manifest path-root counts.
- Expands source-role negative replay from 15 to 16 cases by coherently mutating a retained checksum manifest so generic local file hash metadata still matches while checksum-manifest syntax fails.
- Adds `docs/30-program/desi-sha256-manifest-custody-audit.md`; no route, evidence unit, public-record credit, forecast, or decision outcome is promoted.

## rev0359 — Local payload hash / version-pin audit refactor

Slug: `localhash-versionpin-auditrefactor`. Bundle: `Theory-of-Everything-rev0359-2026.06.13.05.06-localhash-versionpin-auditrefactor.zip`.

- Retains the two small NASA LAMBDA SPT-3G text bandpower payloads under `payload-snapshots/REF-0642-SPT3G-LAMBDA-BANDPOWERS/` and records SHA-256, byte-size, and line-count replay in `SOURCE-SNAPSHOT-MANIFEST.json`.
- Updates GWTC-5 payload custody to exact Zenodo v2 identity, DOI, latest-pointer resolution, and v2 md5 component checksums instead of silently relying on the older v1 record.
- Refactors `tools/source_snapshot_manifest.py` to validate local retained payload files, small-text size caps, local hash drift, and versioned public-record identity.
- Expands source-role negative replay from 13 to 15 cases by mutating a retained local payload and deleting version identity, proving both failures are caught.
- Adds `docs/30-program/local-payload-hash-versionpin-audit.md`; no route, evidence unit, public-record credit, forecast, or decision outcome is promoted.

## rev0358 — Payload custody source-gap audit/refactor

Slug: `payloadcustody-sourcegap-auditrefactor`. Bundle: `Theory-of-Everything-rev0358-2026.06.13.03.20-payloadcustody-sourcegap-auditrefactor.zip`.

- Extends `SOURCE-SNAPSHOT-MANIFEST.json` from 6 ACT/PTA rows to 12 public-source custody rows covering ACT, PTA/NANOGrav, GWTC-5, DESI DR2, SPT-3G, and Euclid Q1.
- Adds payload-custody fields and lint for upstream checksum state, local payload retention state, payload inventory, optional payload component checksums, and zero-route-placement receipts.
- Records upstream GWTC-5 md5 component checksums while keeping bulky public data external and non-vendored.
- Records DESI DR2 chain/posterior and SPT-3G B-mode product inventories as explicit no-upstream-checksum custody rather than pretending locators prove payload integrity.
- Adds Euclid Q1 as a zero-route-placement source-snapshot watchlist row backed by a frontier freshness receipt; no route is promoted.

## rev0357 — ACT/PTA source snapshot pressure refactor

Slug: `actpta-snapshot-pressure-refactor`. Bundle: `Theory-of-Everything-rev0357-2026.06.12.19.44-actpta-snapshot-pressure-refactor.zip`.

- Adds `SOURCE-SNAPSHOT-MANIFEST.json`, `tools/source_snapshot_manifest.py`, and a generated audit so locator-only public-source custody must be backed by typed source-role events and S0 caps.
- Adds ACT DR6 refs `REF-0729` through `REF-0731` and PTA/NANOGrav refs `REF-0732` through `REF-0734` to the bibliography and frontier-source freshness assertions.
- Adds S0 public-record carriers, acquisition protocols, empirical deltas, and route-head handoff events for ACT DR6 and PTA/NANOGrav pressure without adding route-head source_refs.
- Updates source-custody isolation policy so the new refs can appear only on their bounded ACT/CMB/cosmology or PTA/GW routes.
- Replaces the fulfilled ACT/PTA followthrough gap with broader payload-hash and durable-revision-stamp followthrough; no route is promoted.

## rev0356 — Deep-read router debt / source-gap audit

Slug: `deepread-routerdebt-sourcegap-audit`. Bundle: `Theory-of-Everything-rev0356-2026.06.12.17.22-deepread-routerdebt-sourcegap-audit.zip`.

- Records a cloudtainer deep-read audit in `docs/30-program/deepread-routerdebt-sourcegap-audit.md`, separating immediate defects from longer-running waste and source-custody followthrough.
- Neutralizes the stale `Current release identity (rev0330)` wording that survived in stable navigation and could mislead a restart despite manifest/head correctness.
- Adds lint so fixed-revision `Current release identity (rev####)` headings and stale `Current linked release:` lines fail in stable current-head surfaces.
- Expands followthrough for durable-ledger revision-stamp churn, public source snapshot/hash custody, ACT DR6/PTA frontier-source intake, and cloudtainer replay cost.
- Preserves all route states and caps; no route is promoted.

## rev0355 — Credit-cap warning / replay-mode / compression refactor

Slug: `creditcap-warning-replaymode-compression-refactor`. Bundle: `Theory-of-Everything-rev0355-2026.06.10.15.09-creditcap-warning-replaymode-compression-refactor.zip`.

- Adds `tools/source_role_credit_cap_policy.py` and a compact generated audit so `no-new-credit` is reserved for retained acquired public-record freshness custody, while forecast/status/denominator/handoff/wrapper source-custody events remain S0/no-route-credit.
- Normalizes 14 ambiguous historical source-role events to S0 event custody without changing route state, row authority, or evidence credit.
- Adds replay-mode counts to the frontier-source freshness audit and lints human warning metrics against the generated 31-assertion / 547-event-row replay state.
- Expands source-role negative replay to 13 mutation cases, including credit-cap drift and acquired-support, forecast-runway, and operational-status source-ref removal.
- Compresses route-condition ceiling generated output while retaining all 3455 authority checks; no route is promoted.

## rev0354 — Mixed-role freshness replay / Euclid watchlist refactor

Slug: `mixed-role-freshness-replay-euclid-watchlist-refactor`. Bundle: `Theory-of-Everything-rev0354-2026.06.10.10.24-mixed-role-freshness-replay-euclid-watchlist-refactor.zip`.

- Converts `FSF-0022-COSMO-DESI-LYA-EUCLID-SOURCE-STAGING` from a non-replayed mixed assertion into row-scoped typed replay policies for acquired DESI public custody, Lyman-alpha/String-M denominator pressure, and Euclid forecast runway.
- Adds five FSF-0022 source snapshot receipts, including `REF-0675`, and adds six `forecast_runway` / `retained_as_forecast_runway` source-role events for Euclid release-timeline custody on rows that already carry `REF-0637`.
- Makes the zero-row Euclid/CERN watchlist boundary executable with `watchlist_zero_route_placement_policy`; `REF-0627` and `REF-0628` must remain at zero route-bearing placements.
- Hardens `tools/frontier_source_freshness.py`, `tools/source_role_negative_replay_tests.py`, and `tools/lint_archive.py`; negative replay now includes mixed-role event removal and watchlist route-placement injection.
- Adds `docs/30-program/mixed-role-freshness-replay-euclid-watchlist-refactor-audit.md`; no route is promoted.

## rev0353 — Core freshness replay / public-custody refactor

Slug: `core-freshness-replay-public-custody-refactor`. Bundle: `Theory-of-Everything-rev0353-2026.06.10.08.08-core-freshness-replay-public-custody-refactor.zip`.

- Extends typed frontier freshness replay from 15 to 29 assertions and from 394 to 536 event-row checks; 29 of 31 freshness assertions now replay typed source-role event custody.
- Adds `retained_as_acquired_support`, `retained_as_forecast_runway`, and `retained_as_operational_status` dispositions so public-record freshness can distinguish row custody from incremental route authority.
- Repairs 139 `source_role_events` across core public-record and theory-pressure rows, covering GWTC/DESI/SPT/CMB-S4/LISA, BMV/GIE, graviton-counting, amplitudes, asymptotic-safety, learned-inverse, causal-set, GW-test, and CMB B-mode assertion groups.
- Expands source-role negative replay tests to include retained acquired-support ref removal, so an acquired-support row cannot keep passing after its event-covered source ref is removed.
- Adds `docs/30-program/core-freshness-replay-public-custody-refactor-audit.md`; no route is promoted.

## rev0352 — Replay helper / generated-audit compression refactor

Slug: `replay-helper-generated-audit-compression-refactor`. Bundle: `Theory-of-Everything-rev0352-2026.06.10.05.02-replay-helper-generated-audit-compression-refactor.zip`.

- Extends typed frontier freshness replay from 8 to 15 assertions and from 320 to 394 event-row checks by enabling bridge-local replay for Family-C subregion, Family-B thermodynamic, String/M atlas, QRF frame-transport, Family-B nonequilibrium, Family-C finite-N/island, and Lab-GIE protocol seams.
- Adds 21 missing `source_role_events` so selected bridge rows no longer pass freshness on bare `source_refs`; the new events are S0 denominator, route-local handoff, or acquired-evidence exclusion custody only.
- Adds `tools/source_role_event_utils.py` and factors shared source-role constants/event helpers into freshness replay, negative replay tests, and lint.
- Compresses `docs/30-program/cosmology-source-role-audit.generated.md` from an all-pass check table into a check-family summary and adds lint preventing table/line-count regrowth.
- Adds `docs/30-program/replay-helper-generated-audit-compression-refactor-audit.md`; no route is promoted.

## rev0351 — Freshness event replay / credit-cap / compression refactor

Slug: `freshness-event-replay-creditcap-compression-refactor`. Bundle: `Theory-of-Everything-rev0351-2026.06.10.04.35-freshness-event-replay-creditcap-compression-refactor.zip`.

- Extends `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json` to schema version `1.5` with typed event replay policies for the high-risk source-role freshness assertions.
- Hardens `tools/frontier_source_freshness.py` so required public refs must have covering `source_role_events` with expected dispositions and S0 source-custody caps, not just row-level `source_refs`.
- Adds missing event coverage exposed by the replay and normalizes 31 ambiguous source-custody event caps to `S0` while preserving old row-context cap values explicitly.
- Compresses the route-state and graviton-counting generated restart surfaces while preserving full executable scans.
- Expands source-role negative replay tests to 7 compact failure modes and adds `docs/30-program/freshness-event-replay-creditcap-compression-refactor-audit.md`; no route is promoted.

## rev0350 — Protocol/measurement boundary event extinction refactor

Slug: `protocol-measurement-boundary-event-extinction-refactor`. Bundle: `Theory-of-Everything-rev0350-2026.06.10.02.50-protocol-measurement-boundary-event-extinction-refactor.zip`.

- Retires the remaining 79 old `revXXXX_*note` JSON fields; zero old note keys remain in JSON sources.
- Converts 74 source-bearing notes into typed `source_role_events` across acquisition/protocol, public-carrier, measurement, systematic, calibration, severity, topology, entropy, QRF, causal-set, String/M, Family-B, Family-C, B-mode, cosmology, and GW-runway rows.
- Converts 5 claim-language/credit current-vs-conditional notes into typed `authority_boundary_events`, keeping spend authority separate from source custody.
- Hardens `tools/lint_archive.py` with global note-key extinction lint, dynamic source-role-event validation across all ledgers, authority-boundary drift checks, and stricter `credit_cap` validation.
- Adds `tools/source_role_negative_replay_tests.py` to `make lint` so representative source-role and authority-boundary mutations fail closed.
- Adds `docs/30-program/protocol-measurement-boundary-event-extinction-refactor-audit.md`; no route is promoted.

## rev0349 — Cosmology/symmetry bridge event refactor

Slug: `cosmo-symmetry-bridge-event-refactor`. Bundle: `Theory-of-Everything-rev0349-2026.06.09.23.59-cosmo-symmetry-bridge-event-refactor.zip`.

- Refactors `VACUUM-ENERGY-LEDGER.json`, `THERMAL-HISTORY-LEDGER.json`, `CPT-DISCRETE-SYMMETRY-LEDGER.json`, `HORIZON-STRUCTURE-LEDGER.json`, `GAUGE-SYMMETRY-LEDGER.json`, `UNITARITY-CHECK-LEDGER.json`, `SCATTERING-OBSERVABLE-LEDGER.json`, and `QUANTIZATION-MAP-LEDGER.json` away from source-bearing revXXXX note fields into typed denominator or metadata-wrapper events.
- Refactors `EMPIRICAL-DELTA-LEDGER.json`, `DISCRIMINATOR-FORECAST-LEDGER.json`, and `DECISION-EXPERIMENT-LEDGER.json` bridge note fields into route-local handoff events.
- Converts decision `rev0327_nested_ceiling_note` fields into 4 `authority_ceiling_events`, keeping spendable outcome ceilings separate from source-role custody.
- Adds dark-sector and Lorentz/CPT source snapshot receipts in `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json`.
- Expands `tools/lint_archive.py` so the migrated refs require typed denominator, wrapper, handoff, or ceiling coverage and cannot be read as acquired support.
- Adds `docs/30-program/cosmo-symmetry-bridge-event-refactor-audit.md`; no route is promoted.

## rev0348 — Route/matter source events leakage refactor

Slug: `route-matter-source-events-leakage-refactor`. Bundle: `Theory-of-Everything-rev0348-2026.06.09.17.21-route-matter-source-events-leakage-refactor.zip`.

- Refactors `CANDIDATE-ROUTE-STATE-LEDGER.json` away from 59 ad hoc route source-role notes into 85 typed route-local handoff / denominator-pressure events.
- Refactors `PARTICLE-SPECTRUM-LEDGER.json`, `MASS-HIERARCHY-LEDGER.json`, and `INTERACTION-COUPLING-LEDGER.json` away from 85 row-level plus 3 top-level matter-sector note fields into 127 row-level plus 3 top-level events.
- Refactors `COSMOLOGICAL-BACKGROUND-LEDGER.json`, `LORENTZ-COVARIANCE-LEDGER.json`, and `MICROCAUSALITY-LOCALITY-LEDGER.json` away from 58 additional note fields into typed retained-denominator events.
- Adds per-source snapshot receipts for matter, QCD, and electroweak/flavor/neutrino public records in `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json`.
- Expands lint and repairs route/matter policy scanners so route-local handoff events are allowed only as typed custody and cannot be read as acquired support.
- Adds `docs/30-program/route-matter-source-events-leakage-refactor-audit.md`; no route is promoted.

## rev0347 — Evidence-exclusion events / observed-sector refactor

Slug: `evidence-exclusion-events-observed-sector-refactor`. Bundle: `Theory-of-Everything-rev0347-2026.06.09.14.52-evidence-exclusion-events-observed-sector-refactor.zip`.

- Refactors `EVIDENCE-UNIT-LEDGER.json` away from 64 ad hoc per-revision source-role notes into durable `source_role_events` that preserve excluded-ref and metadata-wrapper semantics.
- Refactors selected `OBSERVED-SECTOR-RECOVERY-LEDGER.json`, `CLASSICAL-LIMIT-LEDGER.json`, `WEAK-FIELD-PPN-LEDGER.json`, and `LOCAL-QFT-RECOVERY-LEDGER.json` rows away from 22 additional rev-note fields into typed denominator-retained events.
- Adds source snapshot receipts for classical-GR observed-sector and QM/QFT/gauge public records in `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json`.
- Expands `tools/lint_archive.py` so normalized ledgers cannot regrow `revXXXX_*note` keys or leak denominator refs into acquired evidence-unit credit or metadata wrappers.
- No route is promoted.

## rev0346 — Typed source-role receipts / equivalence-principle refactor

Slug: `typed-source-role-receipts-ep-refactor`. Bundle: `Theory-of-Everything-rev0346-2026.06.09.12.10-typed-source-role-receipts-ep-refactor.zip`.

- Hardens `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json` with typed `source_role`, `checked_at`, `public_status`, `no_promotion_disposition`, and source snapshot receipts.
- Refactors `EQUIVALENCE-PRINCIPLE-LEDGER.json` away from rev0344 ad hoc note keys into durable `source_role_events` capped at S0 for denominator-pressure refs.
- Adds executable lint for equivalence-principle source-role leakage and stale current-linked navigation lines.
- Prunes stale current-head history from high-salience navigation surfaces and preserves the no-promotion boundary.


## rev0345 — 2026.06.09.03.48 — cloudtainer-deepread-drift-waste-audit
- Repaired stale current-head/front-matter drift in `START_HERE.md`, `README.md`, `ARCHIVE_INDEX.md`, `docs/00-meta/trajectory-map.md`, `docs/40-model/current-head-control-router.md`, `context-pack.json`, and `SURFACE-STATUS.json`.
- Added `docs/30-program/cloudtainer-deep-read-drift-waste-audit.md` and `WS-0062` to track semantic drift, source-role, freshness, schema, and compression repairs.
- Reactivated `FOLLOWTHROUGH-QUEUE.json` with five active archive-control repair items; no route was promoted.
- Hardened `tools/lint_archive.py` so first headings, `START_HERE.md` top line, and `context-pack.json` current posture name the manifest revision.
- Corrected three stale `rev0343_equivalence_principle_source_role_note` keys to rev0344-equivalence naming.
- Packaged release: `Theory-of-Everything-rev0345-2026.06.09.03.48-cloudtainer-deepread-drift-waste-audit.zip`.

## rev0344 — 2026.06.06.00.25 — equivalence-fifthforce-weakfield-denominator-audit

- Added equivalence-principle / fifth-force / weak-field denominator pressure as S0 route-local burden, using MICROSCOPE, short-range inverse-square/fifth-force, in-orbit atom-interferometer WEP, ACES/PHARAO clock/redshift, and torsion-balance custody.
- Extended the existing classical-GR observed-sector policy rather than adding a new policy file.
- Added `DF-0029-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-OBSERVED-SECTOR-REPLAY`, `ED-0035-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-OBSERVED-SECTOR-PRESSURE`, `DX-0022-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-OBSERVED-SECTOR-REPLAY`, and `FSF-0032-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-SOURCE-ROLE` while keeping `REF-0437` and `REF-0725`–`REF-0728` out of acquired evidence-unit source credit and metadata-wrapper freshness.
- No route was promoted. Bundle: `Theory-of-Everything-rev0344-2026.06.06.00.25-equivalence-fifthforce-weakfield-denominator-audit.zip`.

# Changelog

## rev0343 — 2026.06.05.23.40 — electroweak-flavor-neutrino-nav-freshness-audit

- Landed electroweak/flavor/neutrino denominator pressure on the canonical line by extending the existing observed-sector matter policy instead of adding another policy file.
- Added `DF-0028-ELECTROWEAK-FLAVOR-NEUTRINO-OBSERVED-SECTOR-REPLAY`, `ED-0034-ELECTROWEAK-FLAVOR-NEUTRINO-OBSERVED-SECTOR-PRESSURE`, and `DX-0021-ELECTROWEAK-FLAVOR-NEUTRINO-OBSERVED-SECTOR-REPLAY`, all capped at `S0` across every route.
- Added `REF-0719` through `REF-0724` for CMS W-mass, CKMfitter CKM status, HFLAV averages, NuFIT 6.0, LHCb Z-mass, and JUNO first oscillation results.
- Repaired stable `ARCHIVE_INDEX.md` current-head drift and added lint coverage for the first current-linked-revision line in stable navigation surfaces.
- No route was promoted. Bundle: `Theory-of-Everything-rev0343-2026.06.05.23.40-electroweak-flavor-neutrino-nav-freshness-audit.zip`.

## rev0342 — 2026.06.05.22.00 — lorentz-cpt-sme-denominator-qft-refactor-audit

- Extended the existing QM/QFT observed-sector policy to cover Lorentz/CPT/SME denominator pressure rather than adding a new policy file.
- Added `DF-0027-LORENTZ-CPT-SME-OBSERVED-SECTOR-REPLAY`, `ED-0033-LORENTZ-CPT-SME-OBSERVED-SECTOR-PRESSURE`, and `DX-0020-LORENTZ-CPT-SME-OBSERVED-SECTOR-REPLAY`, all capped at `S0`.
- Reused existing `REF-0509` for SME Data Tables/current coefficient custody and added `REF-0715` through `REF-0718` for hydrogen/antihydrogen spectroscopy, molecular-ion Lorentz/CPT theory, GRB photon-propagation limits, and charm-meson CPT bounds.
- Attached the refs to route-local Lorentz, CPT/discrete-symmetry, and microcausality/locality rows while keeping them out of acquired evidence-unit `source_refs` and metadata-wrapper source credit.
- Added human audit `docs/30-program/lorentz-cpt-sme-denominator-qft-refactor-audit.md`; no route was promoted. Bundle: `Theory-of-Everything-rev0342-2026.06.05.22.00-lorentz-cpt-sme-denominator-qft-refactor-audit.zip`.

## rev0341 — 2026.06.05.20.05 — qcd-hadronic-observed-sector-denominator-audit

- Integrated QCD/hadronic observed-sector pressure into the existing observed-sector matter policy instead of adding a new policy file.
- Added `DF-0026-QCD-HADRONIC-OBSERVED-SECTOR-REPLAY`, `ED-0032-QCD-HADRONIC-OBSERVED-SECTOR-PRESSURE`, and `DX-0019-QCD-HADRONIC-OBSERVED-SECTOR-REPLAY`, all capped at `S0`.
- Added `REF-0712` through `REF-0714` for FLAG/lattice-QCD, precision `alpha_s`, and CMS jet/PDF running denominator pressure.
- Extended frontier-source freshness/isolation and observed-sector matter auditing so QCD refs cannot enter acquired evidence-unit source credit, metadata-wrapper freshness, or route promotion.
- Added human audit `docs/30-program/qcd-hadronic-observed-sector-denominator-audit.md`; no route was promoted. Bundle: `Theory-of-Everything-rev0341-2026.06.05.20.05-qcd-hadronic-observed-sector-denominator-audit.zip`.

## rev0340 — 2026.06.05.18.30 — qm-qft-observed-sector-source-role-audit

- Added QM/QFT/gauge observed-sector denominator pressure: `DF-0025-QM-QFT-GAUGE-OBSERVED-SECTOR-REPLAY`, `ED-0031-QM-QFT-GAUGE-OBSERVED-SECTOR-PRESSURE`, and `DX-0018-QM-QFT-GAUGE-OBSERVED-SECTOR-REPLAY`.
- Added `tools/qm_qft_observed_sector_policy.py` and generated audit coverage.
- `REF-0710` and `REF-0711` are NIST/CODATA and lepton magnetic-moment denominator refs only; they are excluded from acquired evidence-unit source credit.
- No route was promoted. Bundle: `Theory-of-Everything-rev0340-2026.06.05.18.30-qm-qft-observed-sector-source-role-audit.zip`.

## rev0340 — 2026.06.05.18.30 — qm-qft-observed-sector-source-role-audit

- Packaged release: `Theory-of-Everything-rev0340-2026.06.05.18.30-qm-qft-observed-sector-source-role-audit.zip`
- Previous release: `Theory-of-Everything-rev0339-2026.06.05.16.40-negative-control-dark-sector-denominator-audit.zip`
- Added QM/QFT/gauge observed-sector denominator pressure for CODATA/NIST constants and precision electron magnetic-moment custody.
- Added `tools/qm_qft_observed_sector_policy.py` and generated audit `docs/30-program/qm-qft-observed-sector-source-role-audit.generated.md`.
- Added `DF-0025`, `ED-0031`, and `DX-0018`; route mirrors and evidence-unit reciprocal handles are updated without importing the new refs into acquired evidence-unit `source_refs`.
- Extended frontier-source freshness and source-custody isolation to `REF-0710` and `REF-0711`; no route was promoted.

## rev0339 — 2026.06.05.16.40 — negative-control-dark-sector-denominator-audit

- Packaged release: `Theory-of-Everything-rev0339-2026.06.05.16.40-negative-control-dark-sector-denominator-audit.zip`
- Previous release: `Theory-of-Everything-rev0338-2026.06.05.15.05-classical-gr-observed-sector-source-role-audit.zip`
- Dark-sector rows from `REF-0706` through `REF-0709` are executable S0 denominator pressure across vacuum-energy, cosmological-background, and thermal-history ledgers, not acquired evidence-unit support.
- Added `tools/dark_sector_constraint_policy.py` and generated audit `docs/30-program/dark-sector-constraint-source-role-audit.generated.md`.
- Added `tools/negative_control_route_overlap_policy.py` and generated audit `docs/30-program/negative-control-route-overlap-audit.generated.md`.
- Added `NC-FAMILYC-ISLAND-DECODER-DECOY` and `NC-LEARNED-INVERSE-CODE-SPACE-OVERFIT`; route-state rows now mirror route-local `negative_control_ids`.
- Repaired cross-route falsifier placements in learned-inverse, finite-N/island, and classical-GR decision rows.
- No route was promoted.

## rev0338 — 2026.06.05.15.05 — classical-gr-observed-sector-source-role-audit

- Packaged release: `Theory-of-Everything-rev0338-2026.06.05.15.05-classical-gr-observed-sector-source-role-audit.zip`
- Previous release: `Theory-of-Everything-rev0337-2026.06.05.13.20-observed-sector-matter-frontier-source-role-audit.zip`
- Added classical-GR observed-sector source-role pressure for EHT M87/Sgr A*, GRAVITY S2 precession, and DESI full-shape/growth gravity constraints.
- Added `DF-0024`, `ED-0030`, and `DX-0017` as route-facing pressure for routes that claim `OSR-CLASSICAL-GR`.
- Added `tools/classical_gr_observed_sector_policy.py` and generated audit `docs/30-program/classical-gr-observed-sector-source-role-audit.generated.md`.
- Repaired `OSR-CLASSICAL-GR.route_ids_touching` so it matches route-ledger declarations, including FamilyB.
- No route was promoted; the new refs are excluded from acquired evidence-unit source credit.

## rev0337 — 2026.06.05.13.20 — observed-sector-matter-frontier-source-role-audit

- Package target: `Theory-of-Everything-rev0337-2026.06.05.13.20-observed-sector-matter-frontier-source-role-audit.zip`.
- Added `tools/observed_sector_matter_policy.py` and generated/human audits for current observed-sector matter source-role custody.
- Attached current PDG 2026, final Fermilab Muon g-2, KATRIN direct neutrino-mass, and CMS Higgs 2025 refs to route-specific particle-spectrum, interaction-coupling, mass/hierarchy, and observed-sector-recovery denominator rows.
- Capped non-Standard-Model-recovery routes at `S0` for observed-sector matter credit and kept metadata-wrapper rows plus acquired evidence-unit `source_refs` fenced from the broad matter-frontier refs.
- No route was promoted.

## rev0336 — 2026.06.05.11.45 — claim-language-current-boundary-realization-refactor-audit

- Package target: `Theory-of-Everything-rev0336-2026.06.05.11.45-claim-language-current-boundary-realization-refactor-audit.zip`.
- Added executable claim-language current-boundary enforcement so conditional-ceiling routes must distinguish current authority from future trigger wording.
- Tightened causal-set, lab GIE/BMV, and lab graviton-counting claim-language permission rows. No route was promoted.

## rev0335 — 2026.06.05.10.30 — lab-gie-protocol-noise-classical-split-audit

- Package target: `Theory-of-Everything-rev0335-2026.06.05.10.30-lab-gie-protocol-noise-classical-split-audit.zip`.
- Added lab GIE/BMV protocol/noise/classical-split source-role pressure rows: `DF-0023`, `ED-0029`, and `DX-0016`.
- Added `tools/lab_gie_bmv_source_role_policy.py` and wired it into generated-surface sync and archive lint.
- Kept `REF-0695` through `REF-0698` route-local and excluded from `EU-0008-LAB-GIE-MEDIATOR.source_refs`; no route was promoted.


## rev0334 — FamilyC finite-N QEC / island decoder source-role audit

- Package target: `Theory-of-Everything-rev0334-2026.06.05.08.55-familyc-finite-n-qec-decoder-source-role-audit.zip`.
- Added `DF-0022-FAMILYC-FINITE-N-QEC-ISLAND-DECODER-REPLAY`, `ED-0028-FAMILYC-FINITE-N-QEC-ISLAND-PRESSURE`, and `DX-0015-FAMILYC-FINITE-N-QEC-ISLAND-DECODER-REPLAY` to make finite-N/interior-QEC/island decoder pressure route-facing for `R-OQ0057-FAMILYC-EW-CODE`.
- Added `REF-0691` through `REF-0694` as route-local pressure refs only; excluded them from `EU-0001-FAMILYC-EW-RECONSTRUCTION.source_refs`.
- Added `tools/familyc_finite_n_reconstruction_policy.py` and generated audit coverage.
- Compacted frontier-source isolation audit output to reduce retained PASS-row exhaust while preserving evaluator coverage.
- No route was promoted.


## rev0333 — ceiling-field coverage / lab graviton realization audit

- Package target: `Theory-of-Everything-rev0333-2026.06.05.06.05-ceiling-field-coverage-lab-graviton-realization-audit.zip`.
- Expanded route-ceiling enforcement to cover previously unchecked S-level fields: `maximum_authority_credit`, `maximum_route_effect`, `maximum_credit_if_passed`, `realist_status_ceiling`, and `current_update_ceiling`.
- Added explicit `route_authority_ceilings` to thirteen multi-route carrier, protocol, contrast, and severity rows exposed by the wider ceiling-field scan.
- Extended realization-status auditing from the lab GIE/BMV lane to the lab graviton-counting lane, keeping current support at `S2` and the `S3` pocket conditional on a future detector-local public record.
- Compacted `route-condition-ceiling-audit.generated.md` from a retained PASS table into route/field/file summaries plus failures, cutting audit exhaust while preserving executable coverage.
- Refactored `tools/smoke_package_release.py` to use bounded captured subprocess output instead of long-lived inherited-output polling after the cloudtainer reproduced a parent/child polling hang during extracted lint.
- No route was promoted.

## rev0332 — cosmology DESI source-staging / Lyman-alpha / Euclid audit

- Package target: `Theory-of-Everything-rev0332-2026.06.05.04.18-cosmology-source-staging-desi-lya-euclid-audit.zip`.
- Added `tools/cosmology_source_role_policy.py` and generated cosmology source-role audit.
- Added `DF-0021` and `ED-0027` to make DESI source staging, Lyman-alpha/gBAO/SNe/CMB combination pressure, and Euclid release runway route-facing.
- Moved DESI extended dark-energy interpretation out of `EU-0012` acquired evidence-unit `source_refs`; official chain/likelihood product custody remains.
- Kept `R-OQ0057-COSMO-DARK-ENERGY-BAO` at `S2`; no route is promoted.


## rev0331 — CMB B-mode successor runway / FamilyB policy-wire audit

- Package target: `Theory-of-Everything-rev0331-2026.06.05.02.20-cmb-bmode-successor-familyb-policy-wire-audit.zip`.
- Wired the rev0330 FamilyB thermodynamic source-role policy into generated-surface sync and archive lint enforcement.
- Added `DF-0020` and `ED-0026` so primordial tensor B-mode successor mission forecasts and causal-source ambiguity pressure are route-facing.
- Repaired `DX-0005` so it hooks SPT-3G acquired pressure plus successor/ambiguity pressure while keeping fresh successor refs out of `EU-0013` acquired evidence-unit source credit.
- No route was promoted.

## rev0330 — FamilyB nonequilibrium entropy / source-role dedupe audit

- Package target: `Theory-of-Everything-rev0330-2026.06.04.20.25-familyb-nonequilibrium-entropy-source-dedupe-audit.zip`.
- Added `DF-0019` and `ED-0025` for FamilyB nonequilibrium entropy-production and non-extensive/topological horizon-entropy calibration pressure.
- Added executable FamilyB source-role audit and source-ref dedupe enforcement.
- Kept `R-OQ0057-FAMILYB-THERMO-ENTROPIC` at S1; no route promoted.

## rev0329 — causal-set correlator / horizon-entropy / source-role audit

- Package target: `Theory-of-Everything-rev0329-2026.06.04.18.45-causal-set-correlator-horizon-entropy-source-role-audit.zip`.
- Added `DF-0018-CAUSAL-SET-CORRELATOR-HORIZON-ENTROPY-REPLAY` and `ED-0024-CAUSAL-SET-MATTER-CORRELATOR-HORIZON-ENTROPY-PRESSURE` as route-local S1 pressure.
- Updated `DX-0010-CAUSAL-SET-MATTER-CONTINUUM-RECOVERY`, `EU-0006-CAUSAL-SET-DYNAMICS`, and causal-set AP/SV/CFN/BHT controls so matter-correlator/scattering and horizon-molecule/entropy progress cannot be spent as acquired source credit or route promotion.
- Added `tools/causal_set_matter_horizon_policy.py` and generated audit `docs/30-program/causal-set-matter-horizon-source-role-audit.generated.md`.
- No route is promoted.

## rev0328 — QRF frame-transport / cross-route handoff / route-pressure mirror audit

- Slug: `qrf-frame-transport-crossroute-handoff-audit`.
- Package target: `Theory-of-Everything-rev0328-2026.06.04.17.21-qrf-frame-transport-crossroute-handoff-audit.zip`.
- Repaired a cross-route empirical-delta/evidence-unit leak: FamilyC-only subregion-state pressure no longer hangs off `EU-0010-QRF-FRAME-TRANSPORT`, and evidence-delta handoff lint now requires route overlap.
- Added `ED-0023-QRF-FRAME-TRANSPORT-LARGE-GAUGE-PRESSURE` plus route-local QRF source-role pressure from QRF large-gauge and crossed-product observer-dependence work.
- Added exact route-state mirrors for route-facing forecast, empirical-delta, and decision-experiment hooks, with executable generated audit coverage.
- Kept `R-OQ0057-FRAME-QRF-RELATIONAL` at `S2`; new QRF refs are not acquired evidence-unit credit and do not promote a route.

## rev0327 — nested decision ceiling / GW source-role audit

- Slug: `nested-decision-ceiling-gw-source-role-audit`.
- Package target: `Theory-of-Everything-rev0327-2026.06.04.15.58-nested-decision-ceiling-gw-source-role-audit.zip`.
- Closed the nested-outcome authority loophole: route-ceiling lint now recursively checks nested `outcome_effects[*].promotion_ceiling` and any future nested S-level authority fields.
- Capped generic GW, DESI, and primordial-B-mode decision outcomes back to their route ceilings unless a future candidate-specific split route and independent evidence unit are opened.
- Added per-route spendable ceilings to the multi-route FamilyC public-reconstruction decision row.
- Split GW strong-field source roles: current public GR-test/spectroscopy refs `REF-0677` and `REF-0678` are S2 constraint pressure, while LISA/next-generation runway refs are forbidden on current acquired evidence and credit rows.
- Added executable GW public-test source-role auditing and regenerated route-condition ceiling coverage.
- No route is promoted.

## rev0326 — multi-route ceiling / String-M observed-sector source-role audit

- Slug: `multiroute-ceiling-stringm-observed-sector-audit`.
- Package target: `Theory-of-Everything-rev0326-2026.06.04.14.05-multiroute-ceiling-stringm-observed-sector-audit.zip`.
- Closed the multi-route authority-ceiling loophole: S-level multi-route rows now carry route-specific spendable ceilings and lint treats them as covered, not excluded.
- Added String/M observed-sector atlas pressure (`DF-0017`, `ED-0022`) requiring flux-vacuum enumeration, moduli stabilization, duality quotient, measure prior, spectrum/EFT, cosmology/de Sitter convention, failed-vacuum accounting, and replay scripts before inverse language can be spent.
- Kept fresh refs `REF-0673` through `REF-0676` out of `EU-0004` acquired evidence-unit source credit.
- Added executable String/M observed-sector auditing plus frontier-source freshness/isolation coverage for the new refs.
- No route is promoted.

## rev0325 — learned-inverse OOD / route-ceiling / source-ID repair audit

- Slug: `learned-inverse-ood-route-ceiling-source-id-repair-audit`.
- Package target: `Theory-of-Everything-rev0325-2026.06.04.12.35-learned-inverse-ood-route-ceiling-source-id-repair-audit.zip`.
- Made the learned-inverse / ML reconstruction lane pay current finite-frequency/cutoff, OOD/abstention, simulator-inheritance, training-regime, PINN/SciML failure-mode, and uncertainty/coverage pressure explicitly.
- Added `DX-0014-FAMILYC-LEARNED-INVERSE-OOD-ABSTENTION`, `tools/learned_inverse_ood_policy.py`, and generated learned-inverse OOD audit coverage.
- Kept fresh refs `REF-0131`/`REF-0143` plus `REF-0670` through `REF-0672` out of `EU-0002-FAMILYC-LEARNED-INVERSE-BENCHMARK` acquired evidence-unit source credit.
- Extended frontier-source freshness/isolation to the learned-inverse current source set.
- No route is promoted.

## rev0324 — asymptotic-safety Lorentzian-observable hotpath audit

- Slug: `asymptotic-safety-lorentzian-observable-hotpath-audit`.
- Package target: `Theory-of-Everything-rev0324-2026.06.04.11.45-asymptotic-safety-lorentzian-observable-hotpath-audit.zip`.
- Made the asymptotic-safety route pay Lorentzian scattering, momentum-dependent form-factor, massless-IR, derivative-expansion/RG-improvement, GLOB/black-hole, topology, and swampland pressure explicitly.
- Kept `R-OQ0057-ASYMPTOTIC-SAFETY` at current `S2`; no route is promoted.
- Kept current AS refs `REF-0166`, `REF-0481`, `REF-0658`, and `REF-0659` out of `EU-0005-AS-RG-TRUNCATION` acquired evidence-unit source credit.
- Added executable asymptotic-safety source-role auditing and frontier-source freshness/isolation coverage for the new refs.

## rev0323 — amplitudes evidence-delta handoff / release hotpath audit

- Slug: `amplitudes-evidence-delta-handoff-release-hotpath-audit`.
- Package target: `Theory-of-Everything-rev0323-2026.06.04.10.46-amplitudes-evidence-delta-handoff-release-hotpath-audit.zip`.
- Completed the rev0323 amplitudes/bootstrap source-pressure repair as route-local S2 pressure only.
- Repaired empirical-delta/evidence-unit reciprocal handoff and removed empirical-delta pressure from the S0 metadata wrapper.
- Added executable evidence-delta handoff auditing while keeping fresh current refs out of acquired evidence credit.
- Preserved bounded, phase-visible extracted-package smoke validation.
- No route is promoted.


## rev0323 — 2026.06.04.10.33 — gravity-ir-positivity-ed-namespace-audit

- Repaired the empirical-delta ordinal namespace collision: `ED-0018-GRAVITON-REALIZATION-AND-QUANTIZATION-SPLIT-PRESSURE` remains ED-0018, the FamilyC subregion-state pressure row is now `ED-0020-FAMILYC-SUBREGION-STATE-PORTABILITY-PRESSURE`, and amplitudes gravity/IR pressure is `ED-0021-AMPLITUDES-GRAVITY-IR-POSITIVITY-PRESSURE`.
- Renamed and broadened `DF-0016` so amplitudes/bootstrap support must name massless-graviton pole handling, loop corrections, light-spectrum/IR assumptions, subtraction count, high-spin support, numerical stability, and kinematic-domain tags.
- Updated `DX-0011`, STB/SCAT/IRD/ASYM route controls, frontier-source freshness assertions, and `tools/amplitudes_gravity_bootstrap_policy.py` so current gravity/IR positivity papers remain route-local pressure and stay out of `EU-0007` acquired evidence support.
- Added the human audit `docs/30-program/amplitudes-gravity-ir-positivity-and-ed-namespace-audit.md` and lint enforcement for the generated amplitudes/bootstrap source-role audit.
- Package target: `Theory-of-Everything-rev0323-2026.06.04.10.33-gravity-ir-positivity-ed-namespace-audit.zip`. No route is promoted.

## rev0322 — 2026.06.04.09.45 — familyc-subregion-desi-forecast-credit-source-order-audit

- Closes forecast/future-record current-credit overrun: discriminator forecasts and forecast-public evidence cannot exceed current route authority.
- Keeps graviton-counting current credit at S2, causal-set dynamics forecast credit at S1, and DESI DR2 dynamic-dark-energy combination pressure at route-local S2.
- Adds route-local FamilyC subregion/gravitating-region state portability pressure (`DF-0015`, `ED-0018`) while keeping fresh theory refs out of acquired evidence-unit support.
- Fixes stale `SURFACE-STATUS` release identity, ledger-family order drift, and duplicate bibliography-reference custody; lint now blocks these regressions.
- Package: `Theory-of-Everything-rev0322-2026.06.04.09.45-familyc-subregion-desi-forecast-credit-source-order-audit.zip`. No route is promoted.


## rev0321 — 2026.06.04.08.10 — lab-gie-bmv-realization-graviton-source-role-audit

- Demoted current Lab GIE/BMV route authority from S3 to S2 because the direct entanglement experiment remains unrealized; retained only a conditional S3 ceiling after a clean acquired public record.
- Reclassified `EU-0008-LAB-GIE-MEDIATOR` from acquired `public-record`/S3 support to `forecast-public-record`/S2 support.
- Added `ED-0017-GIE-BMV-INFERENCE-SPLIT-PRESSURE` plus route-realization audit/lint enforcement for the BMV/GIE model-class inference split.
- Completed the lab graviton-counting source-role partition so classical GW/LISA trigger/runway refs cannot stand in for detector-local single-graviton/click evidence.
- Extended frontier-source freshness/isolation coverage through `REF-0648` and regenerated generated surfaces.
- Package: `Theory-of-Everything-rev0321-2026.06.04.08.10-lab-gie-bmv-realization-graviton-source-role-audit.zip`. No route is promoted.

## rev0320 — 2026.06.04.07.20 — source-isolation-spt3g-bmode-pressure-audit

- Closed remaining S2 route-facing discriminator-forecast gaps for learned inverse/OOD, DESI DR2 late-time-expansion tension splitting, and post-CMB-S4 primordial-tensor forecast-realization custody.
- Removed volatile frontier-source refs from generic all-route metadata/provenance and multi-route defeater surfaces, replacing source bleed with executable route-local custody checks.
- Added route-local SPT-3G two-year B-mode public bandpower/likelihood pressure for the primordial-tensor lane while preserving the S2 ceiling and no-detection boundary.
- Added source-custody isolation audit/lint enforcement and retained the authority-graph hot-path no-deep-copy refactor.
- Package: `Theory-of-Everything-rev0320-2026.06.04.07.20-source-isolation-spt3g-bmode-pressure-audit.zip`. No route is promoted.

## rev0319 — 2026.06.04.05.58 — empirical-delta-route-cmbs4-source-smoke-audit

- Added empirical-delta→route authority edges and lint/generation checks so empirical/source-pressure rows directly condition route authority.
- Added four empirical-delta rows covering learned inverse/OOD, asymptotic-safety regulator portability, causal-set QSG dynamics, and thermo-entropic local-law scope pressure; every route now has empirical/source-pressure coverage.
- Kept the decision-handoff repair: every live route has explicit route-facing decision-experiment pressure rather than forecast-only narrative survival.
- Repaired CMB-S4 primordial-tensor custody: CMB-S4 project-status rows now cap the lane as historical design / successor-record pressure, and `DX-0005` includes a project-realization failure outcome.
- Extended frontier-source freshness to check required and forbidden refs; CMB-S4-specific rows require `REF-0633` and reject the LIGO/GWOSC `REF-0629` ref where it would be semantically wrong.
- Preserved GWTC-5/GWOSC O4b and DESI DR2 freshness assertions plus deterministic package smoke/rebuild verification.
- No route is promoted.

## rev0318 — 2026.06.04.05.03 — frontier-route-pressure-transient-cleanup-audit

- Advanced the live gravitational-wave empirical-delta handle from GWTC-4 to GWTC-5 source custody and updated related GW carrier/acquisition/severity/evidence/measurement rows.
- Added DESI DR2 cosmology chains/data-products source custody to the DESI late-time expansion corridor while preserving its S2 ceiling.
- Added Euclid Q1 and CERN accelerator-schedule references as watchlist/caution pressure only, not evidence for route promotion.
- Added three route-facing discriminator forecasts so the previously unpressured FamilyB thermo-entropic, amplitudes/bootstrap, and QRF-relational corridors no longer survive as pure narrative lanes.
- Added forecast→route and decision-experiment→route authority-graph edges plus generated lint/audit coverage proving all 13 route rows have at least one route-facing forecast or decision row.
- Added `tools/clean_transients.py`, `make clean`, and clean-first lint/package behavior so transient bytecode cannot self-poison archive reuse.
- Added `docs/30-program/frontier-data-freshness-and-transient-cleanup-audit.md` and `docs/30-program/decision-forecast-route-pressure-integrity-audit.md`.
- No route was promoted.

## rev0317 — 2026.06.04.03.51 — authority-graph-source-replay-claim-support-refactor

- Changed `make index` so `AUTHORITY-DEPENDENCY-GRAPH.json` is rebuilt from source ledgers in memory rather than merely carrying forward the previous compact graph.
- Added lint enforcement that compares the stored compact authority graph against deterministic source-ledger replay.
- Refreshed the graph to `51,673` logical edges, preserving all prior logical edges and adding `74` missing route/carrier/protocol claim-support edges for `OQ-0111` and `OQ-0112`.
- Added `docs/30-program/authority-graph-source-replay-audit.md` to record the stale-generated-surface failure mode, the superseded augmentation rule, and the non-promotion boundary.
- No route was promoted to `S4` or `S5`.

## rev0316 — 2026.06.04.03.02 — authority-graph-codec-compact-release-refactor

- Replaced the default expanded `AUTHORITY-DEPENDENCY-GRAPH.json` payload with deterministic `columnar-dictionary-v1` JSON while preserving the logical 51,599-edge graph.
- Added `tools/authority_graph_codec.py` and routed graph reads/writes in generated-surface sync and lint through the codec.
- Extended `schemas/authority-dependency-graph.schema.json` and `tools/lint_archive.py` so compact storage, roundtrip digest, row-count parity, deterministic output, and size-regression checks are enforced.
- Added `docs/30-program/authority-graph-compaction-codec-audit.md` and closed `FT-0315-001` by execution.
- No route was promoted to `S4` or `S5`.

## rev0315 — 2026.06.04.02.30 — schema-validation-authority-graph-waste-audit

- Added `tools/validate_registered_json_schemas.py` and wired registered JSON Schema instance validation into `make lint`.
- Repaired schema/data type drift exposed by direct instance validation across registered ledger/schema pairs.
- Normalized claim-route binding claim-language fields to arrays and repaired the one multi-rollback field representation.
- Added `docs/30-program/deep-cube-schema-validation-and-weight-audit.md` to record schema-validation, authority-graph, and cloudtainer waste findings.
- Corrected stale public status wording and opened `FT-0315-001` for authority-graph compaction.
- No route was promoted to `S4` or `S5`.

## rev0314 — uncertainty-interval-significance-coverage-bibliography-audit

- Added executable `UNCERTAINTY-INTERVAL-LEDGER.json`, `SIGNIFICANCE-THRESHOLD-LEDGER.json`, and `COVERAGE-CALIBRATION-LEDGER.json`.
- Added `OQ-0112` and `CL-0488` through `CL-0493` to block interval, p-value, sigma-threshold, discovery/exclusion, coverage, and calibration overclaim.
- Added bibliography reference-sequence auditing so REF id duplication, max-id continuity, and retirement-ledger coverage are lint-visible.
- No route was promoted to `S4` or `S5`.

## rev0313 — units-constants-scale-setting-chronology-audit

- Added executable `UNIT-CONVENTION-LEDGER.json`, `FUNDAMENTAL-CONSTANT-LEDGER.json`, and `SCALE-SETTING-LEDGER.json`.
- Added `OQ-0111` and `CL-0482` through `CL-0487` to block unit/constant/scale-setting overclaim.
- Added release-chronology consistency auditing and refactored `make index` toward a fast registry-driven path that repairs missing registered route/binding edges without replaying every historical graph augmentation.
- No route was promoted to `S4` or `S5`.

## rev0312 — prospective-preregistration-blinding-navigation-freshness-audit

- Added executable prospective-prediction, preregistration-protocol, and blinding/deviation controls under `OQ-0110`.
- Added release-navigation freshness auditing so human and machine entry surfaces cannot lag the manifest and receipt.
- No route promoted to `S4` or `S5`; prediction/preregistration/blinding credit remains route-local and noncompensatory.


## rev0311 — 2026.05.29.12.30 — benchmark-suite-metric-evaluation-review-index-audit

- Added executable benchmark-suite, benchmark-metric, and evaluation-protocol controls.
- Added `OQ-0109` and `CL-0470`–`CL-0475` to block benchmark, leaderboard, metric, SOTA, hidden-test, and evaluation-protocol overclaim.
- Added context-pack release freshness auditing and normalized stale context-pack fields.
- Added program routing entries `WS-0059`, `BR-0059`, and `RF-59`.
- No route was promoted to S4/S5.


## rev0310 — 2026.05.29.09.30 — simulator-fidelity-surrogate-emulator-sim-to-real-summary-freshness-audit

- Added executable simulator-fidelity, surrogate-emulator, and sim-to-real transfer controls (`SIMULATOR-FIDELITY-LEDGER.json`, `SURROGATE-EMULATOR-LEDGER.json`, `SIM-TO-REAL-TRANSFER-LEDGER.json`).
- Added `OQ-0108` and `CL-0464`–`CL-0469` to block simulator, synthetic-data, emulator, digital-twin, calibration, and domain-gap overclaim.
- Added registered generated-summary revision freshness auditing so registered summaries cannot silently lag the current release token after a rebuild.
- No route was promoted; simulator and emulator support remains denominator-bound and cannot spend S4/S5 authority.


## rev0309 — 2026.05.29.06.30 — data-reduction-feature-sufficiency-artifact-reference-audit

- Added executable data-reduction, feature-extraction, and summary-statistic sufficiency controls (`DATA-REDUCTION-LEDGER.json`, `FEATURE-EXTRACTION-LEDGER.json`, `SUMMARY-STATISTIC-SUFFICIENCY-LEDGER.json`).
- Added `OQ-0107` and `CL-0458`–`CL-0463` to block compressed-record, feature, embedding, information-bottleneck, MOPED/score-compression, ABC/SBI, and summary-statistic overclaim.
- Added registered artifact-reference integrity auditing to catch stale ledger, schema, generated-summary, owner-surface, and controlling-ledger paths.
- No route was promoted; compressed or learned summaries remain denominator-bound and cannot spend S4/S5 authority.

## rev0308 — 2026.05.29.03.30 — stochastic-sampling-estimator-convergence-id-reference-audit

- Added executable stochastic-sampler, estimator-variance, and convergence-diagnostic controls under `OQ-0106`.
- Added registered ID-reference integrity auditing and repaired stale perturbative resummation loop-link aliases from `LOP-*` to `LCT-*`.
- No candidate route is promoted; route-state distribution remains `S1: 2`, `S2: 9`, `S3: 2`, `S4/S5: 0`.


## rev0307 — 2026.05.28.22.30 — perturbative-expansion-loop-resummation-family-namespace-audit

- Added executable `PERTURBATIVE-EXPANSION-LEDGER.json`, `LOOP-ORDER-COUNTERTERM-LEDGER.json`, and `RESUMMATION-BOREL-LEDGER.json`.
- Added `OQ-0105` and `CL-0446`–`CL-0451` to block perturbative, loop-order, counterterm, Borel, resurgence, transseries, renormalon, resummation, all-order, and UV-completion overclaiming.
- Added ledger-family namespace auditing so family ids, ledger files, schema files, and generated summary paths cannot collide silently.
- No route promoted to `S4` or `S5`.


## rev0306 — 2026.05.28.19.30 — equation-of-state-transport-fluctuation-dissipation-revision-audit

- Added executable equation-of-state, transport-coefficient, and fluctuation-dissipation ledgers plus schemas and generated summary.
- Added `OQ-0104` and `CL-0440`–`CL-0445`; no route is promoted to S4/S5.
- Added registered-ledger revision-alignment auditing so registered executable ledgers cannot silently lag the current manifest revision.

## rev0305 — 2026.05.28.16.30 — circuit-holographic-complexity-controlling-ledger-audit

- Added executable circuit-complexity, holographic-complexity, and computational-hardness ledgers plus schemas and generated summary.
- Added `OQ-0103` and `CL-0434`–`CL-0439`; no route is promoted to S4/S5.
- Added claim-route controlling-ledger order/deduplication auditing so binding rows cannot hide duplicate or unknown controlling ledgers.

## rev0304 — 2026.05.28.13.30 — qec-logical-decoder-source-kind-audit

- Added executable QEC code-subspace, logical-operator reconstruction, and decoder-certification ledgers plus schemas and generated summary.
- Added `OQ-0102` and `CL-0428`–`CL-0433`; no route is promoted to S4/S5.
- Added registered source-kind coverage audit so route-local ledger families cannot lose dependency-graph source-kind coverage silently.


## rev0303 — 2026.05.28.10.30 — entanglement-modular-relative-entropy-dependency-edge-audit

- Added executable `ENTANGLEMENT-STRUCTURE-LEDGER.json`, `MODULAR-FLOW-LEDGER.json`, and `RELATIVE-ENTROPY-RECOVERY-LEDGER.json`.
- Added `OQ-0101` and `CL-0422`–`CL-0427` to block entanglement-wedge, modular-flow, relative-entropy, JLMS, QES/island, and recovery-map language from becoming candidate-native closure.
- Added generated `docs/30-program/entanglement-modular-relative-entropy-summary.generated.md`.
- Added generated `docs/30-program/registered-dependency-edge-coverage-audit.generated.md` so route-local support handles cannot silently lose authority-dependency graph edges.
- No route was promoted to `S4` or `S5`.

## rev0302 — 2026.05.28.07.30 — locality microcausality cluster decomposition audits

- Added executable microcausality/locality, cluster-decomposition, and local-QFT-recovery ledgers under `OQ-0100`.
- Added `CL-0416` through `CL-0421` to block locality, no-signalling, cluster, isolability, local-algebra, and local-QFT-recovery language unless the new route-local rows are current.
- Added route-field prefix collision auditing so route-support handle namespaces cannot duplicate, shadow, or ambiguously prefix one another.
- No route was promoted; all locality and local-QFT language remains route-local and rollback-bound.

## rev0301 — 2026.05.28.03.30 — lorentz-cpt-spin-statistics-summary-writer-audit

- Added executable Lorentz-covariance, spin-statistics, and CPT/discrete-symmetry ledgers.
- Added `OQ-0099` and `CL-0410`–`CL-0415` to block Lorentz/CPT/spin-statistics laundering.
- Added generated-summary writer coverage audit and refactored compactification graph augmentation so it is not nested under the defect-layer branch.
- No candidate route is promoted; S4/S5 remain empty.


## rev0300 — 2026.05.27.21.30 — compactification-moduli-swampland-registry-schema-audit

- Added executable compactification-geometry, moduli-stabilization, and swampland/landscape compatibility ledgers plus schemas and generated summaries.
- Added `OQ-0098` and claims `CL-0404`–`CL-0409` to block compactification, moduli, de Sitter, landscape, swampland, tower, WGC, tadpole, and vacuum-selection language from becoming candidate-native closure.
- Added ledger-family registry schema audit so registered support-family metadata, summary paths, cardinality policies, and audit notes remain schema-visible.
- No route was promoted; S4/S5 remain empty.

## rev0299 — 2026.05.27.18.30 — defects-instantons-vacuum-decay-array-type-audit

- Added executable topological-defect, instanton/saddle, and vacuum-decay/tunneling ledgers.
- Added `OQ-0097` and `CL-0398`–`CL-0403` to block nonperturbative-sector, defect, instanton, bounce, false-vacuum, metastability, and tunneling-rate overclaims.
- Added a route/binding schema array-type audit so registered route-layer handles remain arrays of string IDs in both route rows and claim-route binding rows.
- No route was promoted to `S4` or `S5`.


## rev0297 — 2026.05.27.12.30 — phase-structure-order-parameter-universality-schema-property-audit

- Added executable phase-structure, order-parameter, and universality-class controls under `OQ-0095`.
- Added `PHASE-STRUCTURE-LEDGER.json`, `ORDER-PARAMETER-LEDGER.json`, and `UNIVERSALITY-CLASS-LEDGER.json`, plus generated summary and dependency edges.
- Added route/binding schema property audit so required route-support fields must also have schema property declarations.
- No route is promoted; phase, criticality, order-parameter, scaling-collapse, and universality-class wording remains bounded by route state and public-record gates.

## rev0296 — 2026.05.27.09.30 — correlator-operator-bootstrap-binding-schema-audit

- Added executable correlation-function, operator-insertion, and bootstrap/CFT-data ledgers under `OQ-0094`.
- Added claim-route binding schema-field audit to keep registered route fields required by the binding schema.
- Updated route rows, claim-route bindings, registry, vocabulary, bibliography, generated summaries, source audits, and lint hooks.
- No route promoted to `S4` or `S5`.

## rev0295 — 2026.05.27.06.30 — discretization-finite-volume-continuum-row-id-audit

- Added executable discretization-regime, finite-volume/scaling, and continuum-extrapolation controls under `OQ-0093`.
- Added `DISCRETIZATION-REGIME-LEDGER.json`, `FINITE-VOLUME-SCALING-LEDGER.json`, and `CONTINUUM-EXTRAPOLATION-LEDGER.json`, plus generated summary and dependency edges.
- Added `docs/30-program/ledger-row-id-uniqueness-audit.generated.md` so registered ledger row identifiers cannot silently collide.
- No route is promoted; lattice, simulation, finite-volume, and continuum-limit wording remains bounded by route state and public-record gates.

## rev0294 — 2026.05.27.03.30 — asymptotic-ir-dressing-inclusive-observables-route-schema-audit

- Added executable asymptotic-state, infrared-dressing, and scattering/inclusive-observable controls under `OQ-0092`.
- Added `ASYMPTOTIC-STATE-LEDGER.json`, `INFRARED-DRESSING-LEDGER.json`, `SCATTERING-OBSERVABLE-LEDGER.json`, their schemas, route handles, generated summary, claim binding, claims `CL-0368`–`CL-0373`, and references `REF-0450`–`REF-0457`.
- Added candidate-route schema field coverage audit so registered route-layer fields cannot silently drift out of `schemas/candidate-route-state-ledger.schema.json`.
- No candidate route is promoted; S-matrix, IR-finite, soft-sector, memory, inclusive-rate, finite-time scattering, and asymptotic-completeness language is narrowed.


## rev0293 — 2026.05.26.21.30 — state-preparation-detector-decoherence-schema-audit

- Added executable state-preparation, detector-response, and decoherence/pointer-record controls under `OQ-0091`.
- Added `STATE-PREPARATION-LEDGER.json`, `DETECTOR-RESPONSE-LEDGER.json`, `DECOHERENCE-POINTER-LEDGER.json`, schemas, generated summary, and route/binding handles.
- Added schema-envelope coverage auditing for registered ledger families.
- No candidate route was promoted; all state/preparation/detector/decoherence rows are cap/rollback denominators only.



## rev0292 — 2026.05.26.18.30 — classical-gr-equivalence-ppn-radiation-audits

- Added executable classical-GR recovery controls: `EQUIVALENCE-PRINCIPLE-LEDGER.json`, `WEAK-FIELD-PPN-LEDGER.json`, and `GRAVITATIONAL-RADIATION-LEDGER.json`.
- Added `OQ-0090` and `CL-0356`–`CL-0361` to block equivalence-principle, weak-field/PPN, metric-theory, gravitational-radiation, binary-pulsar, and classical-GR-recovered wording unless the new ledgers are current.
- Added `docs/30-program/classical-gr-recovery-summary.generated.md` and route-layer dependency edges for equivalence-principle, weak-field/PPN, and gravitational-radiation controls.
- Added `docs/30-program/ledger-row-count-parity-audit.generated.md` so route-local-plus-wrapper families expose row-count drift, missing wrappers, and ledger mismatch before the route stack silently under-reports itself.
- No candidate route was promoted; all S4/S5 counts remain zero.


## rev0291 — 2026.05.26.15.30 — stress-energy-backreaction-ledger-coverage-audit

- Added executable stress-energy/source, semiclassical-backreaction, and energy-condition controls under `OQ-0089`.
- Added `STRESS-ENERGY-SOURCE-LEDGER.json`, `SEMICLASSICAL-BACKREACTION-LEDGER.json`, `ENERGY-CONDITION-LEDGER.json`, and generated `docs/30-program/stress-energy-backreaction-summary.generated.md`.
- Normalized generated-summary paths in `LEDGER-FAMILY-REGISTRY.json` and added `docs/30-program/ledger-summary-coverage-audit.generated.md` so route-layer summaries cannot silently disappear from the registry surface audit.
- Updated route rows, claim-route bindings, source references, program routing, and audits. No route is promoted to `S4` or `S5`.


## rev0290 — 2026.05.26.12.30 — singularity-resolution-censorship-hyperbolicity-audits

- Added executable curvature-regime, singularity-resolution, and censorship/global-hyperbolicity controls under `OQ-0088`.
- Added `CURVATURE-REGIME-LEDGER.json`, `SINGULARITY-RESOLUTION-LEDGER.json`, `CENSORSHIP-HYPERBOLICITY-LEDGER.json`, and generated `docs/30-program/singularity-censorship-summary.generated.md`.
- Added a generated constitutional CL/OQ namespace audit at `docs/30-program/constitutional-id-namespace-audit.generated.md`.
- Updated route rows, claim-route bindings, registry coverage, source references, and program routing. No route is promoted to `S4` or `S5`.


## rev0289 — 2026.05.26.09.30 — black-hole-horizon-thermodynamics-source-audit

- Added executable black-hole horizon-structure, thermodynamics/microstate, and evaporation/radiation controls.
- Added `OQ-0087` and `CL-0338`–`CL-0343` to block black-hole-sector, entropy-microstate, Hawking-radiation, Page-curve, endpoint, and information-recovery laundering.
- Added a source-reference usage audit and retired duplicate `REF-0396` in favor of canonical `REF-0034`.
- No route promoted; Family C remains bounded `S3`, lab discriminator pockets remain bounded `S3`, and all completion/black-hole corridors remain below closure.



## rev0288 — 2026.05.26.06.30 — cosmology-vacuum-thermal-history-oq-gate-audit

- Added executable cosmological-background, vacuum-energy/matter-sector, and thermal-history/structure controls.
- Added `OQ-0086` and `CL-0332`–`CL-0337` to block cosmology-recovery, Lambda/matter-sector, inflation/reheating/BBN, and structure-formation laundering.
- Added an open-question gate-coverage generated audit so each registered route-layer family has a visible OQ binding and controlling-ledger coverage.
- No route promoted; Family C remains bounded `S3`, lab discriminator pockets remain bounded `S3`, and all completion/cosmology corridors remain below closure.


## rev0287 — 2026.05.26.03.30 — matter-spectrum-coupling-mass-program-id-audit

- Added executable matter-sector controls: `PARTICLE-SPECTRUM-LEDGER.json`, `INTERACTION-COUPLING-LEDGER.json`, and `MASS-HIERARCHY-LEDGER.json`.
- Added `OQ-0085` and `CL-0326`–`CL-0331` to block Standard Model, particle-spectrum, coupling, Higgs/EWSB, flavor, neutrino, matter-sector, and matter-coupled-gravity laundering.
- Added a program-ID namespace audit and repaired duplicate `WS-0033` / `BR-0033` program entries plus a stale `RF-33` gate pointer.
- No route was promoted to `S4` or `S5`.

## rev0286 — 2026.05.25.23.55 — measure-typicality-subsystem-algebra-audits

- Added `MEASURE-DEFINITION-LEDGER.json`, `ENSEMBLE-SAMPLING-LEDGER.json`, and `TYPICALITY-WEIGHTING-LEDGER.json`.
- Added `OQ-0083` and `CL-0314`–`CL-0319` for measure, ensemble, typicality, naturalness, anthropic, observer-weighting, and prediction-language controls.
- Added `docs/30-program/binding-control-ledger-coverage-audit.generated.md` so binding rows that spend registered fields must list their controlling ledgers.
- No route promoted to `S4` or `S5`.


## rev0285 — 2026.05.25.23.30 — topology-dimension-signature-binding-normalization

- Added executable spacetime-topology, dimension-realization, and signature-structure ledgers plus schemas, method surfaces, program mirrors, model audits, claim rows `CL-0308`–`CL-0313`, open question `OQ-0082`, and bibliography refs `REF-0364`–`REF-0372`.
- Normalized `CLAIM-ROUTE-BINDING-LEDGER.json` against `LEDGER-FAMILY-REGISTRY.json`; added a generated binding-field audit so late-added route-layer fields cannot be invisible on binding rows.
- Preserved the conservative route posture: no route was promoted to `S4` or `S5`; topology, dimension, and signature rows cap wording rather than add closure credit.

## rev0284

- Added executable symmetry-realization, anomaly-matching, and conservation-law ledgers plus schemas, method surfaces, program mirrors, model audits, claim rows `CL-0302`–`CL-0307`, open question `OQ-0081`, and bibliography refs `REF-0356`–`REF-0363`.
- Refactored `docs/30-program/route-state-summary.generated.md` to render route-support families from `LEDGER-FAMILY-REGISTRY.json`, preventing stale hard-coded summaries when new route layers are added.
- No route was promoted; S4/S5 remain empty.


## rev0283 — 2026.05.25.18.30 — information-flow-entropy-no-go-binding-cardinality-audit

- Added `INFORMATION-FLOW-LEDGER.json`, `ENTROPY-ACCOUNTING-LEDGER.json`, and `NO-GO-COMPLIANCE-LEDGER.json` with generated `docs/30-program/information-entropy-summary.generated.md`.
- Added `OQ-0080` and `CL-0296`–`CL-0301` to block information-recovery, entropy-balance, Page-curve, no-cloning/no-signalling, data-processing, and no-go-compliance language from promoting route authority.
- Audited `LEDGER-FAMILY-REGISTRY.json` and tightened existing route-local families to explicit `route-local-plus-wrapper` cardinality with maximum route-field cardinality where applicable.
- Added information/entropy/no-go bibliography anchors `REF-0348`–`REF-0355`.

## rev0282 — 2026.05.25.15.30 — quantization-correspondence-layer-registry-audit

- Added `QUANTIZATION-MAP-LEDGER.json`, `CLASSICAL-LIMIT-LEDGER.json`, and `SEMICLASSICAL-CORRESPONDENCE-LEDGER.json` plus schemas and generated summary.
- Added `OQ-0079` and `CL-0290`–`CL-0295` to block quantum-completion, classical-limit, WKB, decoherence, clock-recovery, and semiclassical-bridge language unless route-local rows are declared.
- Added `LEDGER-FAMILY-REGISTRY.json`, `schemas/ledger-family-registry.schema.json`, and generated route-layer coverage audit.
- Refactored rev0280 composition/interface/global-consistency route handles from overbroad all-row binding to route-local-plus-wrapper binding; this reduces dependency-graph sprawl and makes composition support more faithful to row ownership.
- No candidate route was promoted; `S4`/`S5` remain empty.

## rev0281 — 2026-05-25 — unitarity causality stability viability controls

- Added `UNITARITY-CHECK-LEDGER.json`, `CAUSALITY-CONE-LEDGER.json`, and `STABILITY-POSITIVITY-LEDGER.json`.
- Added `OQ-0078` and `CL-0284`–`CL-0289` so unitarity, causality, analyticity, stability, positivity, healthy-degree-of-freedom, and physical-viability language cannot be borrowed from global consistency, formal proofs, public likelihoods, matched EFTs, or composed modules.
- Added method/program/model surfaces for viability denominators, generated summaries, dependency-graph edges, and linter checks.
- No lane was promoted or demoted; route-state distribution remains S1/S2/S3 with zero S4/S5 rows.

## rev0280 — 2026.05.25.09.30 — composition-interface-global-consistency-controls

- Added executable composition-law, interface-compatibility, and global-consistency ledgers: `COMPOSITION-LAW-LEDGER.json`, `INTERFACE-COMPATIBILITY-LEDGER.json`, and `GLOBAL-CONSISTENCY-LEDGER.json`.
- Added schemas and generated summary `docs/30-program/composition-consistency-summary.generated.md`.
- Added `OQ-0077` plus `CL-0278`–`CL-0283` to block modularity, gluing, local-to-global, all-sector, factorization, interface-compatibility, and unification laundering.
- Updated route rows, claim-route bindings, dependency graph generation, witness vocabulary, bibliography, routing surfaces, and linter checks.
- No route was promoted to `S4` or `S5`; Family C remains bounded `S3`.

## rev0279 — 2026.05.25.06.30 — regularization-renormalization-scale-matching-controls

- Added executable regularization-scheme, renormalization-flow, and matching-condition ledgers plus schemas, generated summary, route handles, claim-route bindings, and linter checks.
- Added `OQ-0076` plus `CL-0272`–`CL-0277` to block regulator-specific, scheme-dependent, RG-trajectory-local, running-coupling, threshold-matching, EFT-matching, counterterm, naturalness, and scale-setting laundering.
- Added dependency-graph edges for regularization, renormalization-flow, and matching conditions.
- No route was promoted to `S4` or `S5`; all scheme/scale/matching support remains bounded by the route ceiling.

## rev0278 — 2026.05.25.03.30 — gauge-constraints-observable-quotient-controls

- Added executable gauge-symmetry, constraint-closure, and observable-quotient ledgers after boundary/initial/sector controls.
- Added `OQ-0075` plus `CL-0266`–`CL-0271` to block gauge-fixed representative, unclosed-constraint, anomaly, unreduced-coordinate, and noninvariant-observable laundering.
- Added generated gauge/constraint summary, dependency-graph augmentation, linter checks, and claim-route bindings.
- No route promoted; `S4`/`S5` remain empty.


## rev0277 — 2026.05.24.18.30 — boundary-conditions-initial-data-sector-selection-controls

- Added executable boundary-condition, initial-data, and sector-selection ledgers plus schemas, generated summary, route handles, claim-route bindings, and linter checks.
- Added `OQ-0074` and `CL-0260`–`CL-0265` to block fixed-background, selected-boundary, chosen-initial-state, selected-vacuum, gauge-sector, regulator-sector, apparatus-window, survey-window, and map-pipeline laundering.
- Added dependency-graph edges for boundary, initial-data, and sector-selection conditions.
- No route was promoted to `S4` or `S5`; all selected-boundary and selected-sector support remains bounded by the route ceiling.

## rev0276 — 2026.05.24.15.30 — idealization-approximation-limit-interchange-controls

- Added executable idealization, approximation-error, and limit-interchange ledgers plus schemas, generated summary, route handles, claim-route bindings, and linter checks.
- Added `OQ-0073` and `CL-0254`–`CL-0259` to block exact-in-the-model, exact-in-the-limit, asymptotic, continuum, deidealized, no-error, and finite-target support laundering.
- Added dependency-graph edges for idealization, approximation-error, and limit-interchange conditions.
- No route was promoted to `S4` or `S5`; all exact-limit and ideal-model support remains bounded by the route ceiling.

## rev0275 — 2026.05.24.12.30 — formal-proof-obligations-assumption-discharge-formalization-coverage

- Added executable proof-obligation, assumption-discharge, and formalization-coverage ledgers plus schemas, generated summary, route handles, claim-route bindings, and linter checks.
- Added `OQ-0072` and `CL-0248`–`CL-0253` to block theorem, derivation, no-go, uniqueness, mechanized-proof, proof-certificate, axiom-boundary, and assumption-discharge laundering.
- Added a missing `OQ-0070` social-authority claim-route binding while wiring the new formal-proof controls into current bindings.
- No route was promoted to `S4` or `S5`; Family C and low-energy discriminator pockets remain bounded.

## rev0274 — 2026.05.24.09.30 — computational-reproducibility-numerical-stability-software-provenance

- Added executable computational-reproducibility, numerical-stability, and software-supply-chain/provenance ledgers.
- Added `OQ-0071` and `CL-0242`–`CL-0247` to block runnable-code, container, solver-output, generated-summary, artifact-badge, and software-provenance laundering.
- Added computational handles to route rows and related support ledgers; claim-route bindings now include computational / numerical / software controls.
- Added generated computational-reproducibility summary and dependency-graph edges for computational replay, numerical stability, and software supply-chain conditions.
- No route was promoted; `S4`/`S5` remain empty.

## rev0273 — 2026.05.24.06.30 — social-authority-review-consensus-boundaries

- Added executable social-authority, review/replication, and consensus/elicitation ledgers.
- Added `OQ-0070` and `CL-0236`–`CL-0241` to block peer-review, expert-testimony, institutional-prestige, citation-count, registered-report, replication, and consensus laundering.
- Added social-authority handles to route rows and related support ledgers; claim-route bindings now include social / review / consensus controls.
- Added generated social-authority summary and dependency-graph edges for social authority, review/replication, and consensus/elicitation conditions.
- No route was promoted; `S4`/`S5` remain empty.

## rev0272 — 2026.05.24.03.00 — semantic-bindings-ontology-commitments-language-permissions

- Added executable semantic-term, ontology-commitment, and claim-language-permission ledgers.
- Added `OQ-0069` and `CL-0230`–`CL-0235` to block semantic drift, ontology relabeling, equivalence-to-identity conversion, public-term-to-native-term conversion, and closure by familiar vocabulary.
- Added semantic handles to route rows and related support ledgers; claim-route bindings now include semantic / ontology / permission controls.
- Added generated semantic-binding summary and dependency-graph edges for semantic, ontology, and language-permission conditions.
- No route was promoted; `S4`/`S5` remain empty.



## rev0271 — 2026.05.23.05.30 — model-capacity-complexity-penalty-generalization-controls

- Added executable model-capacity, complexity-penalty, and predictive-generalization ledgers.
- Added `OQ-0068` and `CL-0224`–`CL-0229` to block flexible-fit, simplicity, parsimony, compression, Occam, and generalization laundering.
- Added route/evidence/update/measurement/domain/causal/selection bindings for capacity, complexity, and generalization handles.
- Added generated `docs/30-program/model-capacity-summary.generated.md` and linter checks for the new capacity layer.
- No route is promoted to `S4` or `S5`.

## rev0270 — 2026.05.22.16.30 — selection-multiplicity-reporting-bias-controls

- Added executable selection-function, multiplicity-control, and reporting-bias ledgers, schemas, generated summary, linter checks, and dependency-graph edges.
- Added `OQ-0067` and `CL-0218`–`CL-0223` to block selected-positive, look-elsewhere, surprise, anomaly, discovery, benchmark-win, and file-drawer-insensitive rhetoric.
- Bound route rows, evidence units, credit/update/prior rows, measurement/systematics, validity/transport, causal/intervention/counterfactual, severity, decision, forecast, and claim-route rows to the new selection layer.
- No candidate route was promoted; no `S4` or `S5` route exists.

## rev0269 — 2026.05.22.13.45 — causal-mechanisms-interventions-counterfactual-robustness

- Added executable causal-mechanism, intervention-protocol, and counterfactual-robustness ledgers, schemas, generated summary, linter checks, and dependency-graph edges.
- Added `OQ-0066` and `CL-0212`–`CL-0217` to block mechanism, cause, mediator, intervention, natural-experiment, ablation, and counterfactual laundering.
- Bound route rows, evidence units, credit/update/prior rows, measurement/systematics, validity/transport rows, and claim-route bindings to the new causal layer.
- No candidate route was promoted; no `S4` or `S5` route exists.

## rev0268 — 2026.05.22.10.15 — validity-domains-transportability-extrapolation-fences

- Added executable validity-domain, transportability, and extrapolation-fence ledgers, schemas, linter checks, generated summary, and dependency-graph edges.
- Added `OQ-0065` and `CL-0206`–`CL-0211` to block local-to-global / source-to-target support laundering.
- Bound route rows, evidence units, credit rows, likelihood/update rows, prior-sensitivity rows, and measurement-model rows to validity/transport/fence handles.
- No candidate route was promoted; no `S4` or `S5` route exists.


## rev0267 — 2026-05-22 — measurement models, systematic uncertainty, and calibration traceability

- Added executable measurement-model, systematic-uncertainty, and calibration/traceability ledgers with schemas and a generated summary.
- Bound every route row, evidence unit, credit-allocation row, likelihood/update row, and prior-sensitivity row to measurement/systematics/traceability handles so likelihood and support language cannot hide raw-to-observable, nuisance, correction, or calibration debt.
- Added `OQ-0064` and claims `CL-0200` through `CL-0205` to block raw-record, catalog, benchmark, proof-artifact, public-likelihood, and metadata-wrapper laundering.
- Hardened the linter and authority-dependency graph for measurement-model, systematic-uncertainty, and calibration-traceability edges.
- No route was promoted; the new layer is a cap/rollback layer for update language.

## rev0266 — 2026-05-22 — contrast classes, prior sensitivity, likelihood updates

- Added executable contrast-class, likelihood/update, and prior-sensitivity ledgers with schemas and a generated summary.
- Bound every candidate route to contrast classes, update rules, and prior-sensitivity handles so support cannot be stated without alternatives, likelihood/update discipline, and update ceilings.
- Added OQ-0063 and claims CL-0194 through CL-0199 to block noncontrastive support, prior-insensitive model-selection rhetoric, and metadata-as-physical-evidence laundering.
- Hardened the linter and authority-dependency graph for contrast-class, likelihood-update, and prior-sensitivity edges.
- Fixed duplicate empirical-delta identifiers inherited from the rev0262/rev0263 layering.


## rev0265 — 2026-05-21 — evidence units, independence assumptions, and no-double-counting credit allocation

- Added `EVIDENCE-UNIT-LEDGER.json`, `INDEPENDENCE-ASSUMPTION-LEDGER.json`, and `CREDIT-ALLOCATION-LEDGER.json`, plus schemas and a generated evidence-credit summary.
- Added `evidence_unit_ids`, `independence_assumption_ids`, and `credit_allocation_ids` to every route row so route evidence can be counted, capped, merged, or rolled back without double-counting shared support chains.
- Added `CL-0189`–`CL-0193` and `OQ-0062`; imported robustness, independent-evidence, evidence-amalgamation, Bayesian variety-of-evidence, and reproducibility anchors.
- Hardened lint so empirical deltas, forecasts, decision experiments, severity tests, authority-dependency edges, claim-route bindings, and generated summaries reference evidence units and credit rows coherently.
- No route was promoted; the new layer mostly makes apparent convergence easier to collapse into correlated support when independence is not established.

## rev0264 — 2026-05-21 — defeaters, rollback propagation, dependency graph, and severity tests

- Added `EPISTEMIC-DEFEATER-LEDGER.json`, `ROLLBACK-PROPAGATION-LEDGER.json`, `EVIDENCE-SEVERITY-LEDGER.json`, and generated `AUTHORITY-DEPENDENCY-GRAPH.json`, plus schemas and a generated defeat/rollback summary.
- Added `defeater_ids`, `rollback_rule_ids`, and `severity_test_ids` to route rows so authority-loss handles are executable rather than hidden in prose.
- Added `CL-0183`–`CL-0188` and `OQ-0061`; imported belief-revision, defeater, formal-argumentation, truth-maintenance, severe-testing, and underdetermination anchors.
- Hardened lint so new ledgers, dependency edges, route loss handles, rollback floors, severity tests, and generated summaries remain internally coherent.
- No route was promoted; the new layer mostly makes authority easier to lose and harder to regain by summary.

## rev0263 — 2026-05-21 — public-record carriers, acquisition protocols, and claim-route bindings

- Added `PUBLIC-RECORD-CARRIER-LEDGER.json`, `ACQUISITION-PROTOCOL-LEDGER.json`, and `CLAIM-ROUTE-BINDING-LEDGER.json`, plus schemas and a generated carrier/acquisition/binding summary.
- Added carrier/protocol ids to route rows, discriminator forecasts, and decision experiments so public-record language must name custody, provenance, replay, challenge, and maximum-credit constraints.
- Added `CL-0177`–`CL-0182` and `OQ-0060`; added FAIR, PROV, DataCite, GWOSC, DESI, LAMBDA, and HEPData carrier anchors.
- Hardened lint so carrier/protocol/binding references, restart-tier paths, generated summaries, and package VCS cleanliness are checked.
- No route was promoted; carrier publicness and acquisition replay remain evidence-custody discipline, not candidate-native identifiability closure.

## rev0262 — 2026-05-21 — promotion gates, observed-sector recovery, and forecast ledgers

- Added `PROMOTION-GATE-LEDGER.json`, `OBSERVED-SECTOR-RECOVERY-LEDGER.json`, and `DISCRIMINATOR-FORECAST-LEDGER.json`, plus schemas and a generated promotion/recovery/forecast summary.
- Added method and model owners for no-compensation promotion gates, observed-sector recovery burdens, discriminator forecasts, observed-sector crosswalks, and the single-graviton / graviton-counting empirical route.
- Added `R-OQ0057-LAB-GRAVITON-COUNTING`, two negative controls, and two empirical deltas for single-graviton stimulated absorption and graviton-counting/state-characterization work.
- Added `CL-0173`–`CL-0176` and `OQ-0059`; hardened lint against malformed claim boundaries, route-state over-ceiling, missing promotion/OSR references, S3 rows without enough controls/deltas, and generated-summary drift.
- No live lane was promoted; all `S4`/`S5` wording remains blocked.

## rev0261 — 2026-05-21 — executable route ledgers and empirical delta

- Added machine-readable route-state, negative-control, record-denominator-template, and empirical-delta ledgers: `CANDIDATE-ROUTE-STATE-LEDGER.json`, `NEGATIVE-CONTROL-LEDGER.json`, `RECORD-DENOMINATOR-TEMPLATES.json`, and `EMPIRICAL-DELTA-LEDGER.json`.
- Added executable schema surfaces under `schemas/` and lint checks for denominator fields, legal state labels, route/control cross-references, score-code vocabulary, and empirical-delta references.
- Added method/program/model surfaces for route-ledger schema, residual-deficiency scoring, duality / underdetermination adjudication, executable route readout, empirical deltas, gravity witness taxonomy, lab quantum-gravity discriminator routing, cross-family scorecards, and duality-versus-candidate-identity auditing.
- Added `REF-0198`–`REF-0207`, `CL-0166`–`CL-0172`, and `OQ-0058` without promoting any live lane; Family C and low-energy lab routes remain bounded `S3` pockets, not `S4` / `S5` closures.

## rev0260 — 2026-05-21 — identifiability state machine and record bridges

- Added `docs/10-method/candidate-identifiability-state-machine.md` as the semantic owner for `OQ-0057` route states, authority transitions, rollback, quarantine, terminal states, and the shared record denominator.
- Added public-record / physics pressure surfaces for gravitational locality and subsystem obstruction, locally covariant public-record bridging, QES / island identifiability pressure, frame-transport equivalence, operational record language, identifiability-theory imports, negative controls, worked examples, head semantics, session scratch policy, and REF-gap accounting.
- Added `CL-0159`–`CL-0165`, `REF-0189`–`REF-0197`, expanded `WITNESS-VOCABULARY.json`, and clarified bundle / scientific / release-control / operational / citation head semantics.
- Extended lint to check changelog placement and previous-revision continuity, claim-status vocabulary membership, REF-gap ledger coverage, unknown `OQ-####` references, and explicit head-semantics fields.
- No live lane was promoted or demoted; the followthrough queue remains empty.

## rev0259 — 2026-05-20 — identifiability authority-rollback docket

- Added `docs/40-model/candidate-native-identifiability-authority-rollback-docket.md`.
- Added `CL-0158` and updated `OQ-0057` so rollback / quarantine handles named by authority-transition rows must be executed through an explicit rollback state before failed or withdrawn transitions restore predecessors, preserve successors, split scopes, vacate authority, or repair mirrors.
- Wired the rollback docket into the current-head custody stack, current-head router, canonical homes, trajectory map, workstreams, bridge experiments, README / START_HERE / context / status / receipt / manifest, and generated index.
- No lane was promoted or demoted; the followthrough queue remains empty.

## rev0258 — 2026-05-20 — identifiability authority-transition docket

- Added `docs/40-model/candidate-native-identifiability-authority-transition-docket.md`.
- Added `CL-0157` and updated `OQ-0057` so scoped current-authority rows must pass an explicit transition docket before authority changes, narrows, splits, vacates, or gets replaced.
- Wired the transition docket into the current-head custody stack, current-head router, canonical homes, trajectory map, workstreams, bridge experiments, README / START_HERE / context / status / receipt / manifest, and generated index.
- No lane was promoted or demoted; the followthrough queue remained empty.

## rev0257 — 2026-05-20 — identifiability current-authority ledger

- Added `docs/40-model/candidate-native-identifiability-current-authority-ledger.md`.
- Added `CL-0156` and updated `OQ-0057` so adopted, succeeded, arbitrated, retired, vacant, quarantined, or reinstated authority states must be consolidated into one scoped current-authority row before they can be reused as standing posture.
- Wired the ledger into the current-head custody stack, live-lane routers, canonical homes, trajectory map, workstreams, bridge experiments, README / START_HERE / context / status / receipt / manifest, and generated index.
- No lane was promoted or demoted; the followthrough queue remains empty.

## rev0256 — 2026-05-20 — identifiability head-reinstatement / thaw docket

- Added `docs/40-model/candidate-native-identifiability-head-reinstatement-thaw-docket.md`.
- Added `CL-0155` and updated `OQ-0057` so retired, vacant, quarantined, carrier-repaired, challenge-repaired, or historical-only heads must pass a head-reinstatement / thaw check before withdrawn authority re-enters current bounded use.
- Wired the docket into the current-head custody stack, live-lane routers, canonical homes, trajectory map, workstreams, bridge experiments, README / START_HERE / context / status / receipt / manifest, and generated index.
- No lane was promoted or demoted; the followthrough queue remains empty.

## rev0255 — 2026-05-20 — identifiability head-retirement / vacancy docket

- Added `docs/40-model/candidate-native-identifiability-head-retirement-vacancy-docket.md`.
- Added `CL-0154` and updated `OQ-0057` so failed, challenged, carrier-broken, successorless, or branch-unresolved heads must pass a head-retirement / vacancy check before authority is withdrawn, scoped, vacated, quarantined, preserved as historical, or replaced by fallback posture.
- Wired the docket into the current-head custody stack, live-lane routers, canonical homes, trajectory map, workstreams, bridge experiments, README / START_HERE / context / status / receipt / manifest, and generated index.
- No lane was promoted or demoted; the followthrough queue remains empty.


## rev0254 — 2026-05-20 — identifiability head-branch arbitration docket

- Added `docs/40-model/candidate-native-identifiability-head-branch-arbitration-docket.md`.
- Added `CL-0153` and updated `OQ-0057` so competing successor releases, forks, extracted roots, local edits, generated mirrors, or cherry-picked continuations must pass a head-branch arbitration check before one bounded head or scoped merge can carry current authority.
- Wired the new arbitration surface into the head-succession, head-adoption, seal-verification, release-seal, lineage, reimport, export, residual-cap, calibration, adversarial-control, promotion, readiness, route-ledger, current-head router, live-lane router, canonical-home, trajectory, workstream, bridge-experiment, README, START_HERE, context, status, receipt, and generated-index surfaces.
- No live lane is promoted or demoted; the followthrough queue remains empty.

## rev0253 — 2026-05-20 — identifiability head-succession docket

- Added `docs/40-model/candidate-native-identifiability-head-succession-docket.md`.
- Added `CL-0152` and updated `OQ-0057` so later releases, extracted roots, copied continuations, local edits, generated mirrors, forks, branches, or returned bundles must pass a head-succession check before replacing an adopted bounded `OQ-0057` head.
- Wired the new succession surface into the head-adoption, seal-verification, release-seal, lineage, reimport, export, residual-cap, calibration, adversarial-control, promotion, readiness, route-ledger, current-head router, live-lane router, canonical-home, trajectory, workstream, bridge-experiment, README, START_HERE, context, status, receipt, and generated-index surfaces.
- No live lane is promoted or demoted; the followthrough queue remains empty.

## rev0252 — 2026-05-20 — identifiability head-adoption docket

- Added `docs/40-model/candidate-native-identifiability-head-adoption-docket.md`.
- Added `CL-0151` and updated `OQ-0057` so seal-verified carriers still need lineage, owner-chain, cap, challenge / freeze, mirror-authority, and rollback checks before they can set current bounded `OQ-0057` head posture.
- Wired the new adoption surface into the seal-verification, release-seal, lineage, reimport, export, residual-cap, calibration, adversarial-control, promotion, readiness, route-ledger, current-head router, live-lane router, canonical-home, trajectory, workstream, bridge-experiment, README, START_HERE, context, status, receipt, and generated-index surfaces.
- No live lane is promoted or demoted; the followthrough queue remains empty.


## rev0251 — 2026-05-18 — identifiability seal-verification docket

- Added `docs/40-model/candidate-native-identifiability-seal-verification-docket.md`.
- Added `CL-0150` and updated `OQ-0057` so release-sealed zips, extracted trees, copied roots, manifests, receipts, status warnings, context posture, generated mirrors, changelog bullets, and release slugs must verify identity, owner-chain replay, residual caps, no-closure wording, mirror parity, package boundary, and rebuild / package evidence before carrying bounded posture forward.
- Wired the new verification surface into the release-seal, lineage, reimport, export, residual-cap, calibration, adversarial-control, promotion, readiness, route-ledger, live-lane router, canonical-home, trajectory, workstream, bridge-experiment, README, START_HERE, context, status, receipt, and generated-index surfaces.
- No live lane is promoted or demoted; the followthrough queue remains empty.

## rev0250 — 2026-05-18 — identifiability release-seal docket

- Added `docs/40-model/candidate-native-identifiability-release-seal-docket.md`.
- Added `CL-0149` and updated `OQ-0057` so current-head packages, manifests, receipts, generated mirrors, README / START_HERE summaries, changelog bullets, context posture, and zipped release carriers preserve owner rows, caps, no-closure wording, package-boundary integrity, and future reimport / lineage treatment rather than becoming surrogate identifiability evidence.
- Wired release sealing into the lineage-merge / reimport / export stack, route ledger, promotion gate, readiness matrix, lifecycle dockets, adversarial / calibration / residual-cap controls, live-lane routers, canonical homes, trajectory map, workstreams, bridge experiments, README, context, status, receipt, and generated index.
- No lane was promoted or demoted; the followthrough queue remains empty.

## rev0249 — 2026-05-18 — identifiability lineage-merge docket

- Added `docs/40-model/candidate-native-identifiability-lineage-merge-docket.md`.
- Added `CL-0148` and updated `OQ-0057` so older releases, forks, copied archive fragments, cherry-picked surfaces, generated archive artifacts, and externally edited bundles must be lineage-rebased before their branch-local identifiability posture can support the current head.
- Wired lineage merge into the reimport firewall, route ledger, promotion gate, readiness matrix, lifecycle dockets, adversarial / calibration / residual-cap / export stack, live-lane routers, canonical homes, trajectory map, workstreams, bridge experiments, README, context, status, receipt, and generated index.
- No lane was promoted or demoted; the followthrough queue remains empty.

## rev0248 and earlier — compressed identifiability custody phase

- Earlier `OQ-0057` custody passes installed reimport, export, residual-cap, calibration, adversarial-control, challenge, replay, trace, conflict, propagation, decay, and evidence-intake controls. Details remain in revision receipts and canonical surfaces.
- No live lane was promoted or demoted in that compressed phase.

## rev0247 — 2026-05-18 — identifiability export-claim docket

- Added `docs/40-model/candidate-native-identifiability-export-claim-docket.md`.
- Added `CL-0146` and updated `OQ-0057` so outward-facing or top-level compressed identifiability wording must carry source rows, minimum caps, owner boundaries, comparison denominators, public / witness conditions, no-closure ballast, and rollback handles before release summaries, restart cards, abstracts, handoff notes, or user-facing answers can export it.
- Wired the export-claim docket into the identifiability stack, residual-cap ledger, live-lane routers, canonical homes, trajectory map, workstreams, bridge experiments, context, status, receipt, changelog, and generated index.
- No live lane was promoted or demoted; the followthrough queue remains empty.

## rev0246 — 2026-05-18 — identifiability residual-cap ledger

- Added `docs/40-model/candidate-native-identifiability-residual-cap-ledger.md`.
- Added `CL-0145` and updated `OQ-0057` so calibrated candidate-native-identifiability labels cannot be reused in broad mirrors unless their bounded label, owner boundary, and earliest remaining blocker travel with the score.
- Wired the residual-cap ledger into the identifiability stack, live-lane routers, canonical homes, trajectory map, workstreams, bridge experiments, context, status, receipt, changelog, and generated index.

## rev0245 — 2026-05-18 — identifiability calibration-anchor docket

- Added `docs/40-model/candidate-native-identifiability-calibration-anchor-docket.md`.
- Added `CL-0144` and updated `OQ-0057` so future route-score reuse, readiness comparisons, adversarial-control passes, or high-state posture claims must calibrate target grain, record denominator, route width, control difficulty, publicness, and witness-owner boundaries before `S` labels are compared or spent.
- Wired the calibration-anchor docket into the identifiability stack, live-lane routers, canonical homes, trajectory map, workstreams, bridge experiments, context, status, receipt, changelog, and generated index.
- No live lane was promoted or demoted; the followthrough queue remains empty.

## rev0244 — 2026-05-18 — identifiability adversarial-control battery

- Added `docs/40-model/candidate-native-identifiability-adversarial-control-battery.md`.
- Added `CL-0143` and updated `OQ-0057` so future `S4`/`S5` promotion attempts, high-state reuses, or route-bearing challenges must declare hostile decoys, spoofing checks, prior-leakage checks, margin perturbations, abstention hard negatives, public-bridge fragility checks, and witness-borrowing substitution controls.
- Wired the battery into the identifiability route stack, lifecycle dockets, live-lane routers, restart mirrors, and program surfaces without promoting or demoting any live lane.


## rev0243 — 2026-05-16 — identifiability challenge-closure docket

- Added `docs/40-model/candidate-native-identifiability-challenge-closure-docket.md`.
- Added `CL-0142` and updated `OQ-0057` so answered or sustained identifiability challenges now require a closure state before challenged credit is reused.
- Wired challenge closure into the identifiability lifecycle, live-lane routers, restart mirrors, and program surfaces without promoting or demoting any live lane.

## rev0242 — 2026-05-16 — identifiability challenge-response docket

- Added `docs/40-model/candidate-native-identifiability-challenge-response-docket.md`.
- Added `CL-0141` and updated `OQ-0057` so replayed identifiability credit now has a route-bearing challenge-response step.
- Wired challenge response into the identifiability template, route ledger, promotion gate, promotion-readiness matrix, evidence-intake docket, supersession docket, dependency-propagation docket, conflict-adjudication docket, decision-trace docket, replay / rollback docket, family-C stack/router, completion-bid stack, witness and empirical-contact routers, cross-family audit, canonical homes, trajectory map, bridge experiments, README, context, status, and receipt.
- No lane was promoted or demoted; the followthrough queue remains empty.

## rev0241 — 2026-05-15 — identifiability replay / rollback docket

- Added `docs/40-model/candidate-native-identifiability-replay-rollback-docket.md`.
- Added `CL-0140` and updated `OQ-0057` so traced decisions must now be replayable from canonical owner surfaces before they continue to support candidate-native identifiability posture.
- Wired replay / rollback control into the identifiability template, route ledger, promotion gate, promotion-readiness matrix, evidence-intake docket, supersession docket, dependency-propagation docket, conflict-adjudication docket, decision-trace docket, family-C stack/router, completion-bid stack, witness and empirical-contact routers, cross-family audit, canonical homes, trajectory map, bridge experiments, README, context, status, and receipt.
- No lane was promoted or demoted; the followthrough queue remains empty.

## rev0240 — 2026-05-15 — identifiability decision-trace docket

- Added `docs/40-model/candidate-native-identifiability-decision-trace-docket.md`.
- Added `CL-0139` and updated `OQ-0057` so post-adjudication outcomes must now leave a durable decision trace before `OQ-0057` posture, route ledgers, readiness matrices, registries, routers, release status, or broad mirrors change.
- Wired decision-trace control into the identifiability template, route ledger, promotion gate, promotion-readiness matrix, evidence-intake docket, supersession docket, dependency-propagation docket, conflict-adjudication docket, family-C stack/router, completion-bid stack, witness and empirical-contact routers, cross-family audit, canonical homes, trajectory map, bridge experiments, README, context, status, and receipt.
- No lane was promoted or demoted; the followthrough queue remains empty.

## rev0239 — 2026-05-15 — identifiability conflict-adjudication docket

- Added `docs/40-model/candidate-native-identifiability-conflict-adjudication-docket.md`.
- Added `CL-0138` and updated `OQ-0057` so unresolved disagreements exposed after intake, supersession / decay, and dependency propagation now have an explicit local-repair / scope-split / precedence / retag / quarantine / freeze / cross-lane-separation / witness-escalation path before route posture changes.
- Wired adjudication control into the identifiability template, route ledger, promotion gate, promotion-readiness matrix, evidence-intake docket, supersession docket, dependency-propagation docket, family-C stack/router, completion-bid stack, witness and empirical-contact routers, cross-family audit, canonical homes, trajectory map, bridge experiments, README, context, status, and receipt.

## rev0238 — 2026-05-15 — identifiability dependency-propagation docket

- Added `docs/40-model/candidate-native-identifiability-dependency-propagation-docket.md`.
- Added `CL-0137` and updated `OQ-0057` so route updates now have a three-stage lifecycle: evidence intake, supersession / decay review, and dependency propagation.
- Wired propagation control into the identifiability template, route ledger, promotion gate, promotion-readiness matrix, evidence-intake docket, supersession docket, family-C stack/router, completion-bid stack, witness and empirical-contact routers, cross-family audit, canonical homes, trajectory map, bridge experiments, README, context, status, and receipt.
- No lane was promoted or demoted; the followthrough queue remains empty.


## rev0237 — 2026-05-15 — identifiability supersession / decay docket

- Added `docs/40-model/candidate-native-identifiability-supersession-decay-docket.md`.
- Added `CL-0136` and updated `OQ-0057` so prior identifiability credit now has a controlled retained / refreshed / narrowed / superseded / contradicted / demoted / quarantined / retired path after new artifacts or reaudits.
- Wired supersession control into the route ledger, promotion gate, promotion-readiness matrix, evidence-intake docket, family-C stack/router, completion-bid stack, witness and empirical-contact routers, canonical homes, trajectory map, bridge experiments, README, context, status, and receipt.
- No lane promoted or demoted; the followthrough queue remains empty.

## rev0236 — 2026.05.15.14.35 — identifiability-evidence-intake-docket

- Added `docs/40-model/candidate-native-identifiability-evidence-intake-docket.md` as the intake classifier for future `OQ-0057` evidence.
- Added `CL-0135` so new papers, experiments, simulations, datasets, code releases, formal results, and public artifacts must be classified as no-update, local sharpening, field-local delta, coupled-field delta, readiness-class delta, promotion attempt, or witness-package escalation before route or readiness posture changes.
- Updated `OQ-0057`, the identifiability template, route ledger, promotion gate, promotion-readiness matrix, cross-family audit, family-C stack/router, completion-bid credit stack, witness and empirical-contact routers, canonical homes, README, trajectory map, workstreams, bridge experiments, and release surfaces.
- No live lane was promoted; the followthrough queue remains empty.

## rev0235
- Added `docs/40-model/candidate-native-identifiability-promotion-readiness-matrix.md` as the live-lane application of the route-level promotion gate.
- Added `CL-0134` to separate field-local gains, route-level promotion rules, and current live-lane readiness classes.
- Updated `OQ-0057` so the unresolved identifiability problem now has a readiness-matrix readout: no lane reaches `S4` or `S5`; family C remains the strongest bounded `S3` row.

## rev0234 — 2026.05.13.21.10 — identifiability-promotion-gate

- Added `docs/40-model/candidate-native-identifiability-promotion-gate.md` as the route-level no-compensation rule above the field protocols.
- Added `CL-0133` and updated `OQ-0057` so a field-local improvement cannot be averaged into candidate-native identifiability closure without a declared promotion state, field-code vector, dominant blocker, coupled dependencies, and remaining witness-package debt.
- Wired the new promotion gate into the identifiability template, route ledger, threshold gate, cross-family audit, family-C stack/router, witness and empirical-contact routers, completion-bid credit stack, canonical homes, trajectory map, README, workstreams, bridge experiments, and release surfaces.
- No live lane was promoted; the followthrough queue remains empty.

## rev0233 — 2026.05.13.20.25 — public-bridge-challenge-protocol

- Added `docs/40-model/candidate-native-public-bridge-challenge-protocol.md` as the field-8 counterpart to the equivalence, acquisition, inverse / stability, and abstention protocols.
- Added `CL-0132` and updated `OQ-0057` so publication, code release, hosted replay, boundary access, laboratory publicness, or private native route confidence cannot be upgraded without a public bridge row.
- Wired the new protocol into the identifiability template, route ledger, threshold gate, cross-family audit, family-C stack/router, witness and empirical-contact routers, completion-bid credit stack, program mirrors, canonical homes, trajectory map, and release surfaces.
- No live lane was promoted; the followthrough queue remains empty.

## rev0232 — 2026.05.13.19.40 — abstention-no-verdict-protocol

- Added `docs/40-model/candidate-native-abstention-no-verdict-protocol.md` as the field-7 counterpart to the equivalence, acquisition, and inverse / stability protocols.
- Added `CL-0131` and updated `OQ-0057` so soft confidence, calibrated bundles, null results, no-acquisition states, no-inversion states, policy deferral, and forced best-answer outputs cannot be upgraded without a no-verdict row.
- Wired the new protocol into the identifiability template, route ledger, threshold gate, cross-family audit, family-C stack/router, witness and empirical-contact routers, completion-bid credit stack, program mirrors, canonical homes, trajectory map, and release surfaces.
- No live lane was promoted; the followthrough queue remains empty.

Installed a candidate-native inverse-completeness / stability protocol, sharpening fields 5 and 6 of the identifiability route by requiring future inverse upgrades to declare target quotient, record domain, completeness claim, deficiency map, stability budget, separation / tie margin, robustness transport, no-inversion zone, and public audit handle before reconstruction, fit, regularized success, or benchmark performance can count as stable candidate-native identification; no current lane is promoted.

## rev0298 — 2026.05.27.15.30 — Hilbert representation spectrum registry schema audit

- Added executable Hilbert-space, representation-map, and spectral-reconstruction ledgers under `OQ-0096`.
- Added registered-ledger schema-property coverage audit so row required fields across registered ledger schemas cannot drift from property declarations.
- No route was promoted; all Hilbert/state-space, representation-equivalence, spectrum, spectral-density, and spectral-geometry language remains route-local and rollback-bound.
