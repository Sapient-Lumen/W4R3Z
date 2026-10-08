## rev0378 update — Family-C OAQEC diamond / reference amplification / Choi refactor

Current linked revision: `rev0378` (`familyc-oaqecdiamond-referenceamplification-choirefactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0378 adds a reference-stable Family-C OAQEC completion using the complementary-channel diamond defect and Bény's two-sided recovery theorem; derives recovery-target and dimension-aware state-to-diamond budgets; constructs a sharp transpose-dephasing reference-amplification failure and an exact erasure-channel common-decoder positive control; exposes the conditional nonperturbative rate wedge c>s; factors Choi/operator mechanics into shared route-local helpers; strengthens Family-C forecast, decision, decoder, and policy surfaces for diamond/cb norm, external-reference, and code-dimension obligations; and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

The new theorem cell distinguishes unassisted state control from arbitrary-reference recovery. In the exact transpose-dephasing family, the state envelope is `2/(d+1)` while the complementary-channel diamond defect is `(d-1)/(d+1)`; at `d=4096` these are `4.88162e-4` and `0.999512`, so Bény's theorem leaves recovery error at least `0.249756`. The positive erasure control has `delta_A=E_A=2p(1-1/d^2)`. A generic dimension lift makes a target `tau` require `epsilon_state<=tau^2/(4 d_code)`, and the exponential schedule `d_code~exp(s/G)`, `epsilon_state~exp(-c/G)` converges only for `c>s`. Physical CFT diamond/cb scaling and the same-domain source join remain unpaid.

## rev0377 update — Family-C Condition-2 routing / coherent split / policy refactor

Historical rev0377 note: linked revision was `rev0377` (`familyc-condition2-routing-coherentsplit-policyrefactor`). The historical package filename is recorded in `CHANGELOG.md`. rev0377 converts REF-0735 Definition 7 Condition 2 into an executable sharp fixed-region sector-diagonal common-decoder bound with numeric target inversion; separates epsilon_sub-tr, epsilon_OD, and epsilon_iso,small through two exact-isometry coherent-sector controls; adds a one-bad-sector average-to-supremum failure; factors source-conditioned routing into tools/familyc_source_routing.py; hardens the finite-N audit against notation-only spelling drift; re-execs lint and package-smoke orchestrators without site initialization and stages lint output in file-backed logs to reduce long-lived cloudtainer pressure; and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

The retained-block premise now has an operational consequence rather than remaining a named debt: on sector-diagonal/direct-sum inputs, `epsilon_common <= epsilon_block + 2 epsilon_sub-tr/(1-epsilon_iso,small)`, and the owned family saturates the source term with fitted power one. At `epsilon_iso,small=0.001`, a `0.01` target requires `epsilon_sub-tr<=0.004995` for a dominant-block decoder certificate. Exact-isometry coherent controls show that `epsilon_OD` and the full Condition-2 term pay distinct failures, while a one-bad-sector control blocks replacement of the source supremum by an average. Whole-domain coherent OAQEC, physical scaling, and actual dominant-block decoders remain unpaid.

## rev0376 update — Family-C commutant gluing / algebra quotient / source correction

Historical rev0376 note: linked revision was `rev0376` (`familyc-commutantgluing-algebraquotient-sourcecorrection`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0376 corrects the Family-C source scope by recognizing that REF-0735 fixes one boundary-region pair and a block-diagonal direct-sum wedge algebra; adds an executable fixed-region operator-algebra decoder-gluing cell that verifies the OAQEC commutant criterion, exact coherent and algebra decoders, a sharp 2 p_max worst-sector confusion budget, and a hidden-frame common-decoder obstruction; quarantines the old wedge-switch code as a generic comparator; refactors decoder-gluing mechanics out of generic operator algebra; and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

The source correction is substantive: the cited large-code construction already holds the boundary region fixed and reconstructs a block-diagonal direct-sum algebra. The new exact cell verifies the OAQEC commutant condition, one coherent common decoder, and one direct-sum algebra decoder. The algebra decoder may dephase off-diagonal sector coherence without failing its declared target; the stronger coherent decoder succeeds when the sector tag remains coherently available. A symmetric sector-instrument error saturates `2 p_max`, while a hidden-frame control proves a linear common-decoder obstruction when the tag is lost.

## rev0375 update — Family-C factor blocks / wedge switching / decoder refactor

Historical rev0375 note: linked revision was `rev0375` (`familyc-factorblocks-wedgeswitch-decoderrefactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0375 extends the Family-C large-code recovery audit from the commutative sector center to the full direct-sum operator algebra; verifies exact center-plus-factor relative-entropy and domain-tax decompositions; exposes a noncommuting modular-frame false convergence where state error vanishes but operator-log error stays order one; proves that sector-wise exact wedge decoders need not assemble into one fixed-region decoder and that adaptive routing can erase cross-sector coherence; refactors shared quantum-matrix mechanics; and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

The exact direct-sum probe has decomposition residual `2.22e-16`; in its declared product domain the center supplies only `0.4610` of `D_max` and `0.4904` of `L_K^osc`, so center stationarity cannot certify the full noncommuting algebra. With `lambda=exp(-1/G)` and basis rotation `theta=G`, trace-norm state error vanishes while operator-log error tends to one nat; `theta=G^2` is the constructive control. A separate two-sector code reconstructs each sector exactly on a different region but proves minimax trace recovery error at least `1` for either fixed region on the other sector. Adaptive routing recovers the block algebra and loses cross-sector coherence by error `1`; the fixed union region decodes exactly.

## rev0374 update — Family-C FLM isometry / weighted transport / smoothness refactor

Historical rev0374 note: linked revision was `rev0374` (`familyc-flmisometry-weightedtransport-smoothnessrefactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0374 propagates the Family-C large-code source's full-system approximate-FLM branch into the owned recovery budget, deriving delta_iso <= 2 sqrt(eps_FLM)+eps_OD and the exponential-sector convergence wedge a>max(t,2 gamma); solves the commuting sector-center log-smoothness term as a weighted transport problem, exposing 83.086 nats of operator-log error under only 1e-8 local leakage and supplying a p-stationary detailed-balance positive control; refactors shared numeric, state-domain, and channel-completion helpers; and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

This is a source-closure and failure-mode pass, not another registry pass. The owned benchmark now propagates the paper's full-system-FLM isometry implication, derives the exponential-sector wedge `a>max(t,2 gamma)`, and turns Definition-12 log-smoothness into an exact weighted sector-transport test. The severe control shows that `1e-8` local leakage and `9.32e-10` total variation can still hide `83.086` nats of operator-log error; the positive control shows that `p`-stationary detailed balance removes that commuting tax. The next denominator is a physical source tuple and sector-transition theorem.

## rev0373 update — Family-C sector weights / domain wedge / geometry refactor

Historical rev0373 note: linked revision was `rev0373` (`familyc-sectorweights-domainwedge-geometryrefactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0373 derives and executable-verifies exact relative-entropy-diameter and centered-modular-oscillation formulas for finite spectral-floor domains on the reduced reconstructed algebra; exposes an exponential direct-sum sector-growth false convergence in which every displayed local Family-C source remainder vanishes while the flagged recovery bound remains order one, and verifies that stronger isometry scaling restores convergence; factors the state-domain geometry into a route-local helper; and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

This is a substantive domain-closure pass. `FAMILYC-JLMS-RECOVERY-BUDGET-BENCHMARK.json` now computes the exact reduced-algebra domain taxes, then applies them to the classical center of a growing direct-sum code. The decisive failure mode is executable: `K~exp(1/G)` with `delta_iso~G` keeps `delta_iso log K` order one, so local source errors can vanish while the theorem recovery bound remains vacuous. The comparison cells show polynomial sector growth converging under the same local powers and exponential growth recovering only when `delta_iso` improves faster than the sector exponent. The next denominator is a physical sector-count/weight theorem joined to the source remainder—not another registry.

## rev0372 update — Family-C flagged channel / tail wedge / theorem split

Historical rev0372 note: linked revision was `rev0372` (`familyc-flagchannel-tailwedge-theoremsplit`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0372 constructs a contraction-scaled flagged CPTP completion for the Family-C large-code bridge, preserving the source normalized state exactly on success while pricing failure through a same-domain relative-entropy diameter and an explicit decoder-conditioning cost; propagates the source Eq. (3.17) tail ratio into an executable a>t and growing-domain exponent wedge with a conditional double-square-root recovery loss; splits theorem algebra and numeric inversions into a route-local helper; and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

This is a substance-first bridge pass: the owned Family-C benchmark now completes the approximate encoding as a genuine flagged CPTP channel, reproduces the nonlinear source state exactly on its success branch, charges failure and decoder conditioning explicitly, passes an independent noncommuting Kraus/Choi audit, and propagates the source tail ratio through a same-domain convergence wedge. The orthogonal flag is a theorem proof device; only the restricted decoder on the original success outputs is carried forward. The next denominator is one physically derived tuple for the projected residual, isometry defect, tail scale, domain diameter, and modular oscillation—not another registry or a free transport symbol.

## rev0371 update — Family-C channel premise / polar join / numeric refactor

Historical rev0371 note: linked revision was `rev0371` (`familyc-channelpremise-polarjoin-numericrefactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0371 corrects the Family-C JLMS-to-recovery bridge by proving that the source's normalized non-isometric state map is non-affine and therefore is not a recovery-theorem channel; derives the exact/scalar-isometry 2 eta join and an explicit polar-channelization budget eta/(1-delta_iso)+chi_out+chi_bulk; adds a spectral-floor stress where eta-only control fails; refactors three numerical benchmarks onto a shared representation-neutral helper; and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

This is a substance-first correction: `FAMILYC-JLMS-RECOVERY-BUDGET-BENCHMARK.json` now refuses to spend a normalized non-isometric state map as a quantum channel, executes the exact/scalar `2 eta` join, and isolates the additional polar-channelization debts. The next denominator is a source-derived uniform law for `eta`, `delta_iso`, `chi_out`, and `chi_bulk` on one physical state domain—not another exact toy code or an average-case surrogate.

## rev0370 update — Family-C JLMS budget / rare-sector / generator refactor

Historical rev0370 note: linked revision was `rev0370` (`familyc-jlmsbudget-raresector-generatorrefactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0370 adds an executable Family-C JLMS-to-recovery budget that translates a uniform pairwise base-2 relative-entropy defect into fidelity, trace/observable, and target-remainder bounds; makes the theorem-level square-root exponent loss explicit; adds a rare-sector negative control that catches average-to-uniform laundering; keeps toy D, abstract R, and physical N/G unmapped; refactors three generated benchmarks onto a shared deterministic artifact harness; and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

This is a substance-first pass: `FAMILYC-JLMS-RECOVERY-BUDGET-BENCHMARK.json` executes the theorem bridge the prior revision left abstract, quantifies the square-root loss from relative-entropy control to trace/observable control, and makes average-to-uniform laundering fail on a concrete rare-sector model. The next denominator is not another toy code: it is one source-derived physical remainder with units, state-domain, region, and quantifier semantics intact.

## rev0369 update — Family-C operational norm / scaling / dilution refactor

Historical rev0369 note: linked revision was `rev0369` (`familyc-operationalnorm-scaling-dilutionrefactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0369 adds an owned prime-dimension Family-C approximate-recovery benchmark with an exact complementary-channel diamond norm, exact declared-decoder worst-case entanglement fidelity, analytic D^-1/2 and D^-1 anchors, and a fixed-leakage negative control that exposes max-entry Knill-Laflamme false convergence; it integrates the operational metric correction into the kernel, decision, bridge, and decoder-audit surfaces, hardens direct lint subprocesses against bytecode-transient drift and inherited-descriptor stalls, and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

This is a substance-first pass: `FAMILYC-APPROXIMATE-RECOVERY-SCALING-BENCHMARK.json` turns the next Family-C denominator into an owned growing-code calculation, provides analytic asymptotic anchors, and makes a severe false-convergence mode executable rather than rhetorical. The next climb requires a physical finite-N/JLMS or bond-dimension remainder mapped into the same operational norm.

## rev0368 update — Family-C qutrit cell / same-record / helper refactor

Historical rev0368 note: linked revision was `rev0368` (`familyc-qutritcell-samerecord-helperrefactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0368 lands the first owned executable Family-C reconstruction stress cell: exact three-qutrit single-erasure recovery, a same-restricted-record rival-dictionary discriminator, a controlled leakage sweep, and a repetition-code negative control; it integrates the result into the existing kernel and decision surfaces, migrates both Family-C source-role policies onto shared neutral helpers, adds one large-code approximate-recovery denominator, and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

This is a substance-first pass: `FAMILYC-QUTRIT-RECONSTRUCTION-BENCHMARK.json` now records an owned exact-code result and explicit failure controls, while the remaining finite-N/JLMS, non-AdS, and local-observer debts stay visible rather than being hidden by the toy success.

## rev0367 update — Executable kernel testcard / smoke-share refactor

Historical rev0367 note: linked revision was `rev0367` (`kerneltestcard-executable-smokeshare-refactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0367 completes the positive candidate-kernel testcard as an executable compact surface, adds generated kernel coverage audit checks, shares the lint-step inventory with package smoke to prevent check drift, closes the prior kernel-testcard followthrough, preserves compact public-source custody, and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

rev0367 is a substance-first continuation pass. It completes `FT-0366-001` by adding `KERNEL-TESTCARD.json`, generated `docs/40-model/positive-kernel-testcard.md`, and `docs/30-program/kernel-testcard-audit.generated.md`; it also refactors lint-step ownership into `tools/lint_steps_config.py` so extracted-package smoke and `make lint` cannot drift apart.

## rev0366 update — Heartscan / online-waste / kernel-testcard triage

Historical rev0366 note: linked revision was `rev0366` (`heartscan-onlinewaste-kerneltestcard`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0366 recorded a fresh cloudtainer heart / online-pressure / waste audit, added a positive-kernel-testcard followthrough, wired the new audit to WS-0062, preserved compact public-source custody, and promoted no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

rev0366 is a control/audit pass. It turns the session deep read and online-pressure check into `docs/30-program/cloudtainer-heart-online-waste-audit.md`, wires that surface to WS-0062, and adds `FT-0366-001` so the next useful move is a positive kernel testcard rather than another broad router.

## rev0365 update — Release provenance / smoke-progress refactor

Historical rev0365 note: linked revision was `rev0365` (`provenance-smokerefactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0365 adds generated RO-Crate/PROV-facing release provenance sidecars, timed lint/smoke progress checks, a candidate-native docket duplication audit/common block, and a source-role helper-boundary refactor; it preserves compact public-source custody and promotes no route, evidence unit, forecast, decision outcome, public-record credit, or observed-sector recovery state.

rev0365 is a substance-first archive-control pass. It adds generated release-provenance sidecars, timed cloudtainer replay steps, a candidate-native docket duplication audit/common block, and a neutral source-role helper refactor; it promotes no route.
## rev0364 update — Mission triage / heartscan audit

Historical rev0364 note: linked revision was `rev0364` (`missiontriage-heartscan`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0364 recorded a cloudtainer mission-heart / missing-controls / waste audit, identified interoperability and replay-hardening changes for future passes, preserved ACT/DESI/GWTC/SPT/NANOGrav compact custody state, and promoted no route, evidence unit, forecast, decision outcome, public-record credit, or observed-sector recovery state.

rev0364 is an archive-control audit pass. It adds `docs/30-program/mission-heart-missing-waste-audit.md`, wires it to WS-0062, and promotes no route.

## rev0363 update — ACT DR6 inventory-control replay refactor

Historical rev0363 note: linked revision was `rev0363` (`actdr6-inventorycontrol-replayrefactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0363 upgrades ACT DR6 source custody from locator-only pressure to retained compact inventory-control JSON for ACT DR6.02 public product tables and ACT DR6 lensing-likelihood identity, adds semantic inventory-control validation and negative replay, and promotes no route.

rev0363 is a substance-first ACT custody pass. It does not vendor maps, likelihood tarballs, chains, notebooks, NERSC trees, or code checkouts; it records compact local product-inventory controls so future replay cannot treat a landing-page locator as stable payload custody.

## rev0361 update — GWTC md5 anomaly replay refactor

Historical rev0361 note: linked revision was `rev0361` (`gwtcmd5-anomaly-replay-refactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0361 retained the compact GWTC-5 Zenodo v2 `md5sums.txt` manifest locally, validated 4,952 valid md5 entries plus one declared upstream partial-line anomaly under SHA-256/file-md5 replay, expanded anomaly drift coverage, and promoted no route.

## Historical work note

rev0361 was a substance-first custody pass. It does not vendor GWTC candidate-data archives; it retains only the compact Zenodo v2 checksum map, proves file-level md5/local SHA-256 replay, and makes the official final partial-line anomaly explicit instead of quietly normalizing it.

## rev0360 update — DESI SHA-256 manifest replay refactor

Historical rev0360 note: linked revision was `rev0360` (`desisha256-manifest-replay-refactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0360 retained the official DESI DR2 BAO cosmology SHA-256 checksum manifest as a bounded local integrity map, parsed its 1,237 component entries during lint, expanded checksum-manifest negative replay, and promoted no route.

## Current work note

rev0360 was a substance-first custody pass. It did not vendor DESI chains/posteriors; it retained the compact DESI-published checksum manifest, validated entry syntax and declared component-root counts, and kept all route authority unchanged.

## rev0359 update — Local payload hash / version-pin audit refactor

Historical rev0359 note: linked revision was `rev0359` (`localhash-versionpin-auditrefactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0359 turns payload custody from locator/inventory accounting into executable replay: two small NASA LAMBDA SPT-3G bandpower text files are retained with local SHA-256/byte-size/line-count checks, GWTC-5 payload custody is pinned to exact Zenodo v2 identity, and no route is promoted.

## Current work note

rev0359 is a substance-first custody pass. It avoids bulky data vendoring while making the first small public payloads fail-closed under local hash drift and making mutable Zenodo/latest-pointer identity explicit before future checksum refreshes.

## rev0358 update — Payload custody source-gap audit/refactor

Historical rev0358 note: linked revision was `rev0358` (`payloadcustody-sourcegap-auditrefactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0358 extends source-snapshot custody beyond ACT/PTA to GWTC-5, DESI DR2, SPT-3G, and Euclid Q1 public-data surfaces; it records upstream GWTC-5 md5 component checksums, DESI/SPT inventory/no-checksum gaps, Euclid Q1 zero-placement custody, and no route promotion.

## Current work note

rev0358 is a substance-first payload-custody pass. It does not vendor bulky external data products; instead it makes checksum availability, local non-retention, and zero-placement watchlist status explicit so the next pass can hash small payloads and decouple durable revision stamps without adding doctrine.

## rev0357 update — ACT/PTA source snapshot pressure refactor

Historical rev0357 note: linked revision was `rev0357` (`actpta-snapshot-pressure-refactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0357 opened executable ACT DR6 and PTA/NANOGrav S0 public-pressure lanes, added a compact source-snapshot manifest plus lint/generated audit, and promoted no route. The current-head ordering was unchanged.

## Current work note

rev0357 is a substance-first source-custody pass. The archive now has real ACT/PTA source placements and replayed source-role events rather than only a followthrough reminder; broader payload hashes and revision-stamp decoupling remain active work.

## rev0356 update — Deep-read router debt / source-gap audit

Historical rev0356 note: linked revision was `rev0356` (`deepread-routerdebt-sourcegap-audit`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0356 records the cloudtainer deep read, fixes a stale currentness leak, adds a regression lint guard, and opens bounded followthrough for source snapshot/hash custody, durable-ledger revision-stamp churn, ACT/PTA intake gaps, and replay cost. No route is promoted; current-head ordering is unchanged.

## Current work note

rev0356 is a control/audit pass, not a scientific promotion. The archive should next reduce revision-stamp churn, add replayable source-snapshot custody, and intake ACT DR6/PTA frontier pressure only as capped denominator/watchlist rows until source roles and route caps are explicit.

## rev0355 update — Credit-cap warning / replay-mode / compression refactor

Historical rev0355 note: linked revision was `rev0355` (`creditcap-warning-replaymode-compression-refactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0355 closes the stale freshness-warning metric drift, normalizes `no-new-credit` versus S0 source-custody semantics, adds a generated credit-cap audit, expands negative replay, and compresses route-condition ceiling output. No route is promoted; current-head ordering is unchanged.

## Current work note

rev0355 is a substance-first control repair. The archive now fails lint if typed frontier freshness warning text drifts away from the generated 31-assertion / 547-event-row replay state. `no-new-credit` is no longer a generic S0 synonym: it is reserved for retained acquired public-record custody that adds no incremental route authority.

## rev0354 update — Mixed-role freshness replay / Euclid watchlist refactor

Historical rev0354 note: linked revision was `rev0354` (`mixed-role-freshness-replay-euclid-watchlist-refactor`). The package filename is recorded in `RELEASE-MANIFEST.json`. rev0354 closes the remaining mixed DESI/Lyman-alpha/Euclid freshness gap by adding row-scoped typed replay policies for acquired DESI public custody, Lyman-alpha/String-M denominator pressure, and Euclid forecast runway. It also makes the Euclid/CERN watchlist zero-placement boundary executable and expands negative replay; no route is promoted. The current-head ordering is unchanged.

## Current work note

rev0354 is a substance-first replay repair for the exact gap rev0353 deliberately left open. FSF-0022 now checks the role of each row/ref subset instead of forcing public DESI chains, interpretation pressure, and Euclid release timing through one lossy source role. FSF-0003 now fails closed if Euclid Q1 or CERN schedule refs acquire route-bearing placements without a deliberate future row and non-promotion cap.
## Archive-control routing

Use `docs/40-model/current-head-control-router.md` as the durable current-head control surface. Archive-control topology is in `docs/00-meta/router-topology-and-scope-map.md` and `ROUTER-TOPOLOGY.json`; broad cross-family pressure, current-family readout, and broad ToE credit must route through `docs/40-model/current-head-control-router.md` plus the specialized router surfaces (`cross-family-pressure-router.md`, `current-family-readout-router.md`, and `broad-toe-credit-router.md`) before any route-state or claim-language change.

