## rev0378 update — Family-C OAQEC diamond / reference amplification / Choi refactor

Current linked revision: `rev0378` (`familyc-oaqecdiamond-referenceamplification-choirefactor`). Bundle: `Theory-of-Everything-rev0378-2026.06.18.22.09-familyc-oaqecdiamond-referenceamplification-choirefactor.zip`. rev0378 adds a reference-stable Family-C OAQEC completion using the complementary-channel diamond defect and Bény's two-sided recovery theorem; derives recovery-target and dimension-aware state-to-diamond budgets; constructs a sharp transpose-dephasing reference-amplification failure and an exact erasure-channel common-decoder positive control; exposes the conditional nonperturbative rate wedge c>s; factors Choi/operator mechanics into shared route-local helpers; strengthens Family-C forecast, decision, decoder, and policy surfaces for diamond/cb norm, external-reference, and code-dimension obligations; and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

The new theorem cell distinguishes unassisted state control from arbitrary-reference recovery. In the exact transpose-dephasing family, the state envelope is `2/(d+1)` while the complementary-channel diamond defect is `(d-1)/(d+1)`; at `d=4096` these are `4.88162e-4` and `0.999512`, so Bény's theorem leaves recovery error at least `0.249756`. The positive erasure control has `delta_A=E_A=2p(1-1/d^2)`. A generic dimension lift makes a target `tau` require `epsilon_state<=tau^2/(4 d_code)`, and the exponential schedule `d_code~exp(s/G)`, `epsilon_state~exp(-c/G)` converges only for `c>s`. Physical CFT diamond/cb scaling and the same-domain source join remain unpaid.

## rev0377 update — Family-C Condition-2 routing / coherent split / policy refactor

Historical rev0377 note: linked revision was `rev0377` (`familyc-condition2-routing-coherentsplit-policyrefactor`). Bundle: `Theory-of-Everything-rev0377-2026.06.18.19.56-familyc-condition2-routing-coherentsplit-policyrefactor.zip`. rev0377 converts REF-0735 Definition 7 Condition 2 into an executable sharp fixed-region sector-diagonal common-decoder bound with numeric target inversion; separates epsilon_sub-tr, epsilon_OD, and epsilon_iso,small through two exact-isometry coherent-sector controls; adds a one-bad-sector average-to-supremum failure; factors source-conditioned routing into tools/familyc_source_routing.py; hardens the finite-N audit against notation-only spelling drift; re-execs lint and package-smoke orchestrators without site initialization and stages lint output in file-backed logs to reduce long-lived cloudtainer pressure; and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

The retained-block premise now has an operational consequence rather than remaining a named debt: on sector-diagonal/direct-sum inputs, `epsilon_common <= epsilon_block + 2 epsilon_sub-tr/(1-epsilon_iso,small)`, and the owned family saturates the source term with fitted power one. At `epsilon_iso,small=0.001`, a `0.01` target requires `epsilon_sub-tr<=0.004995` for a dominant-block decoder certificate. Exact-isometry coherent controls show that `epsilon_OD` and the full Condition-2 term pay distinct failures, while a one-bad-sector control blocks replacement of the source supremum by an average. Whole-domain coherent OAQEC, physical scaling, and actual dominant-block decoders remain unpaid.

## rev0376 update — Family-C commutant gluing / algebra quotient / source correction

Historical rev0376 note: linked revision was `rev0376` (`familyc-commutantgluing-algebraquotient-sourcecorrection`). Bundle: `Theory-of-Everything-rev0376-2026.06.18.17.24-familyc-commutantgluing-algebraquotient-sourcecorrection.zip`. rev0376 corrects the Family-C source scope by recognizing that REF-0735 fixes one boundary-region pair and a block-diagonal direct-sum wedge algebra; adds an executable fixed-region operator-algebra decoder-gluing cell that verifies the OAQEC commutant criterion, exact coherent and algebra decoders, a sharp 2 p_max worst-sector confusion budget, and a hidden-frame common-decoder obstruction; quarantines the old wedge-switch code as a generic comparator; refactors decoder-gluing mechanics out of generic operator algebra; and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

The source correction is substantive: the cited large-code construction already holds the boundary region fixed and reconstructs a block-diagonal direct-sum algebra. The new exact cell verifies the OAQEC commutant condition, one coherent common decoder, and one direct-sum algebra decoder. The algebra decoder may dephase off-diagonal sector coherence without failing its declared target; the stronger coherent decoder succeeds when the sector tag remains coherently available. A symmetric sector-instrument error saturates `2 p_max`, while a hidden-frame control proves a linear common-decoder obstruction when the tag is lost.

## rev0375 update — Family-C factor blocks / wedge switching / decoder refactor

Historical rev0375 note: linked revision was `rev0375` (`familyc-factorblocks-wedgeswitch-decoderrefactor`). Bundle: `Theory-of-Everything-rev0375-2026.06.18.15.07-familyc-factorblocks-wedgeswitch-decoderrefactor.zip`. rev0375 extends the Family-C large-code recovery audit from the commutative sector center to the full direct-sum operator algebra; verifies exact center-plus-factor relative-entropy and domain-tax decompositions; exposes a noncommuting modular-frame false convergence where state error vanishes but operator-log error stays order one; proves that sector-wise exact wedge decoders need not assemble into one fixed-region decoder and that adaptive routing can erase cross-sector coherence; refactors shared quantum-matrix mechanics; and promotes no route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, operational head, or citation head.

The exact direct-sum probe has decomposition residual `2.22e-16`; in its declared product domain the center supplies only `0.4610` of `D_max` and `0.4904` of `L_K^osc`, so center stationarity cannot certify the full noncommuting algebra. With `lambda=exp(-1/G)` and basis rotation `theta=G`, trace-norm state error vanishes while operator-log error tends to one nat; `theta=G^2` is the constructive control. A separate two-sector code reconstructs each sector exactly on a different region but proves minimax trace recovery error at least `1` for either fixed region on the other sector. Adaptive routing recovers the block algebra and loses cross-sector coherence by error `1`; the fixed union region decodes exactly.

## rev0374 update — Family-C FLM isometry / weighted transport / smoothness refactor

Historical rev0374 note: linked revision was `rev0374` (`familyc-flmisometry-weightedtransport-smoothnessrefactor`). Bundle: `Theory-of-Everything-rev0374-2026.06.18.13.18-familyc-flmisometry-weightedtransport-smoothnessrefactor.zip`. The trajectory now closes the source's optional full-system-FLM isometry branch and identifies the remaining global smoothness condition. Appendix C plus Lemma 4 turns `eps_FLM~G^a` into `delta_iso~G^(a/2)` up to `eps_OD`, so exponential sector growth `K~exp(c/G^gamma)` requires `a>max(t,2 gamma)` through the flagged bridge. On the commuting center, log-smoothness is exactly a relative sector-inflow condition, not a raw leakage bound: a tiny local leak can hide an 83-nat tail error, while `p`-stationary transport removes it. The next denominator is a physical same-domain source tuple and sector dynamics, not a new control surface. No route is promoted.

## rev0373 update — Family-C sector weights / domain wedge / geometry refactor

Historical rev0373 note: linked revision was `rev0373` (`familyc-sectorweights-domainwedge-geometryrefactor`). Bundle: `Theory-of-Everything-rev0373-2026.06.18.10.45-familyc-sectorweights-domainwedge-geometryrefactor.zip`. The trajectory now replaces an abstract “growing domain” warning with exact reduced-algebra geometry and an executable direct-sum obstruction. At fixed total sector floor mass, the sector center contributes `D_max,L_K^osc=Theta(log K)`. Consequently `K~exp(c/G^gamma)` and `delta_iso~G^b` require `b>gamma` through the flagged bridge; the power-matched `b=gamma=1` cell remains order one even while local source errors vanish, whereas `b=2` restores convergence. The next denominator is a physical same-region sector-count/weight law plus source constants. No route is promoted.

## rev0372 update — Family-C flagged channel / tail wedge / theorem split

Historical rev0372 note: linked revision was `rev0372` (`familyc-flagchannel-tailwedge-theoremsplit`). Bundle: `Theory-of-Everything-rev0372-2026.06.18.08.42-familyc-flagchannel-tailwedge-theoremsplit.zip`. The trajectory now has a constructive genuine-channel completion rather than an unpriced polar placeholder: a contraction-scaled flagged CPTP map reproduces the source normalized state exactly on success while exposing failure, domain-diameter, modular-oscillation, and decoder-conditioning costs. A noncommuting Kraus/Choi audit now verifies the completion outside the diagonal corner while keeping the failure flag explicitly auxiliary. The source tail estimate yields an executable convergence wedge requiring `a>t` and positive domain-corrected exponent before any operational finite-resource scaling can be claimed. The next denominator is a physically derived same-domain source tuple. No route is promoted.

## rev0371 update — Family-C channel premise / polar join / numeric refactor

Historical rev0371 note: linked revision was `rev0371` (`familyc-channelpremise-polarjoin-numericrefactor`). Bundle: `Theory-of-Everything-rev0371-2026.06.18.07.03-familyc-channelpremise-polarjoin-numericrefactor.zip`. The trajectory now distinguishes a projected-JLMS statement about a normalized non-isometric map from a theorem input about a genuine quantum channel. Exact/scalar encoding has a direct `2 eta` bridge; approximate encoding must pass through polar channelization with explicit output-modular and bulk-similarity transport costs. The next denominator is a physical uniform scaling law for that channelization tuple on one state domain. No route is promoted.

## rev0370 update — Family-C JLMS budget / rare-sector / generator refactor

Historical rev0370 note: linked revision was `rev0370` (`familyc-jlmsbudget-raresector-generatorrefactor`). Bundle: `Theory-of-Everything-rev0370-2026.06.18.05.03-familyc-jlmsbudget-raresector-generatorrefactor.zip`. The trajectory now connects the owned operational QEC cell to a theorem-level JLMS budget without pretending to have derived physical finite-`N` data. A uniform pairwise relative-entropy defect is converted into fidelity and trace/observable guarantees, the square-root exponent loss is explicit, and a rare-sector control blocks state averages from masquerading as whole-code recovery. The next denominator is a source-derived remainder with its units, state class, region, and quantifier structure preserved. No route is promoted.

## rev0369 update — Family-C operational norm / scaling / dilution refactor

Historical rev0369 note: linked revision was `rev0369` (`familyc-operationalnorm-scaling-dilutionrefactor`). Bundle: `Theory-of-Everything-rev0369-2026.06.18.02.54-familyc-operationalnorm-scaling-dilutionrefactor.zip`. The trajectory now has a growing approximate-recovery baseline rather than only an exact small code: operational environment leakage and declared-decoder error have exact norms, analytic asymptotic anchors, and a fixed-leakage control that catches dimension-diluted false convergence. The next denominator is a physical finite-N/JLMS or tensor-network remainder mapped into this norm, followed by state-dependent wedge and observer transport tests. No route is promoted.

## rev0368 update — Family-C qutrit cell / same-record / helper refactor

Historical rev0368 note: linked revision was `rev0368` (`familyc-qutritcell-samerecord-helperrefactor`). Bundle: `Theory-of-Everything-rev0368-2026.06.18.00.38-familyc-qutritcell-samerecord-helperrefactor.zip`. The trajectory moves from a positive testcard to an owned result: the strongest Family-C route now has an exact three-qutrit erasure/decoder baseline, a same-restricted-record discriminator, a declared leakage sweep, and a negative control. The next denominator is no longer “build any cell”; it is a physically declared large-code approximate-recovery and non-AdS observer transport test. No route is promoted.

## rev0367 update — Executable kernel testcard / smoke-share refactor

Historical rev0367 note: linked revision was `rev0367` (`kerneltestcard-executable-smokeshare-refactor`). Bundle: `Theory-of-Everything-rev0367-2026.06.17.18.01-kerneltestcard-executable-smokeshare-refactor.zip`. The trajectory now has a constructive compression surface: `docs/40-model/positive-kernel-testcard.md` states the primitive, dynamics, quotient, coarse-graining, public-record map, negative control, discriminator observables, dominant debt, and next kernel work for every current OQ-0057 route. Package smoke now reuses the same lint-step inventory as `make lint`. No route is promoted.

## rev0366 update — Heartscan / online-waste / kernel-testcard triage

Historical rev0366 note: linked revision was `rev0366` (`heartscan-onlinewaste-kerneltestcard`). Bundle: `Theory-of-Everything-rev0366-2026.06.17.16.25-heartscan-onlinewaste-kerneltestcard.zip`. The trajectory recorded a stricter mission-control posture: archive-control is useful only when it feeds a positive kernel testcard, public-source custody, discriminator observables, or replayable negative controls. `docs/30-program/cloudtainer-heart-online-waste-audit.md` named the remaining waste and promoted no route.

## rev0365 update — Release provenance / smoke-progress refactor

Historical rev0365 note: linked revision was `rev0365` (`provenance-smokerefactor`). Bundle: `Theory-of-Everything-rev0365-2026.06.14.17.58-provenance-smokerefactor.zip`. This archive-control refactor converts the highest-risk rev0364 followthrough into generated provenance sidecars, observable replay steps, and duplication/helper refactors without route promotion.

rev0365 adds generated RO-Crate/PROV-facing release provenance sidecars, timed lint/smoke progress checks, a candidate-native docket duplication audit/common block, and a source-role helper-boundary refactor; it preserves compact public-source custody and promotes no route, evidence unit, forecast, decision outcome, public-record credit, or observed-sector recovery state.

Current-head ordering is unchanged; this revision promotes no route.
## rev0364 update — Mission triage / heartscan audit

Historical rev0364 note: linked revision was `rev0364` (`missiontriage-heartscan`). Bundle: `Theory-of-Everything-rev0364-2026.06.14.17.21-missiontriage-heartscan.zip`. This archive-control audit recorded mission-heart, missing-control, and waste-correction guidance without route promotion.

rev0364 records a cloudtainer mission-heart / missing-controls / waste audit, identifies interoperability and replay-hardening changes for future passes, preserves ACT/DESI/GWTC/SPT/NANOGrav compact custody state, and promotes no route, evidence unit, forecast, decision outcome, public-record credit, or observed-sector recovery state.

This is an archive-control audit pass and promotes no route.

## rev0363 update — ACT DR6 inventory-control replay refactor

Historical rev0363 note: linked revision was `rev0363` (`actdr6-inventorycontrol-replayrefactor`). Bundle: `Theory-of-Everything-rev0363-2026.06.13.17.42-actdr6-inventorycontrol-replayrefactor.zip`. The trajectory now records ACT DR6 custody as executable compact product-inventory replay rather than locator-only pressure: ACT DR6.02 public product tables and ACT DR6 lensing-likelihood identity are retained as local inventory-control JSON while bulky maps, chains, likelihood tarballs, notebooks, and code remain external with no authority promotion.

## rev0361 update — GWTC md5 anomaly replay refactor

Historical rev0361 note: linked revision was `rev0361` (`gwtcmd5-anomaly-replay-refactor`). Bundle: `Theory-of-Everything-rev0361-2026.06.13.08.17-gwtcmd5-anomaly-replay-refactor.zip`. The trajectory recorded a stricter custody class: retained upstream integrity maps can have declared upstream anomalies, but the anomaly must be exact and replayed. GWTC-5 custody no longer rests only on Zenodo component-md5 inventory; the official md5 manifest is locally hashed and parsed while bulky candidate-data payloads remain external with no authority promotion.

## rev0360 update — DESI SHA-256 manifest replay refactor

Historical rev0360 note: linked revision was `rev0360` (`desisha256-manifest-replay-refactor`). Bundle: `Theory-of-Everything-rev0360-2026.06.13.05.58-desisha256-manifest-replay-refactor.zip`. The trajectory gained compact integrity-map retention: DESI DR2 chain custody no longer rests on directory inventory alone; the official SHA-256 manifest is retained and parsed while bulky chain/posterior payloads remain external with no authority promotion.

## rev0359 update — Local payload hash / version-pin audit refactor

Historical rev0359 note: linked revision was `rev0359` (`localhash-versionpin-auditrefactor`). Bundle: `Theory-of-Everything-rev0359-2026.06.13.05.06-localhash-versionpin-auditrefactor.zip`. The trajectory now records payload custody as executable replay rather than only locator accounting: SPT-3G small text bandpowers are locally hashed, GWTC-5 is version-pinned to Zenodo v2 instead of a drifting/latest public record, and bulky payloads remain external with no authority promotion.

## rev0358 update — Payload custody source-gap audit/refactor

Historical rev0358 note: linked revision was `rev0358` (`payloadcustody-sourcegap-auditrefactor`). Bundle: `Theory-of-Everything-rev0358-2026.06.13.03.20-payloadcustody-sourcegap-auditrefactor.zip`. The trajectory now records source custody as a payload/question-of-record layer rather than a fresh-source narrative layer: GWTC-5, DESI DR2, SPT-3G, and Euclid Q1 are accounted for by checksum availability, inventory/no-checksum state, local non-retention, and zero-placement receipts without route authority changes.

## rev0357 update — ACT/PTA source snapshot pressure refactor

Historical rev0357 note: linked revision was `rev0357` (`actpta-snapshot-pressure-refactor`). Bundle: `Theory-of-Everything-rev0357-2026.06.12.19.44-actpta-snapshot-pressure-refactor.zip`. The trajectory recorded the first source-snapshot custody lane and concrete ACT/PTA pressure intake: public sources were placed, event-replayed, and capped S0 rather than left as a source-gap note. No route authority changed.

## rev0356 update — Deep-read router debt / source-gap audit

Historical rev0356 note: linked revision was `rev0356` (`deepread-routerdebt-sourcegap-audit`). Bundle: `Theory-of-Everything-rev0356-2026.06.12.17.22-deepread-routerdebt-sourcegap-audit.zip`. The trajectory now records a control-layer correction: stale fixed-revision currentness wording is retired, a lint guard prevents recurrence, and unresolved source-custody / revision-churn / ACT-PTA intake / replay-cost debt is queued without changing any route authority.

## rev0355 update — Credit-cap warning / replay-mode / compression refactor

Historical rev0355 note: linked revision was `rev0355` (`creditcap-warning-replaymode-compression-refactor`). Bundle: `Theory-of-Everything-rev0355-2026.06.10.15.09-creditcap-warning-replaymode-compression-refactor.zip`. The trajectory now records the post-replay cleanup: source-role event caps distinguish retained acquired public-record custody from S0 source-custody, human warning metrics are tied to the generated 31-assertion / 547-event-row replay state, and generated route-condition ceiling output is compacted without weakening checks.

## rev0354 update — Mixed-role freshness replay / Euclid watchlist refactor

Historical rev0354 note: linked revision was `rev0354` (`mixed-role-freshness-replay-euclid-watchlist-refactor`). Bundle: `Theory-of-Everything-rev0354-2026.06.10.10.24-mixed-role-freshness-replay-euclid-watchlist-refactor.zip`. The trajectory now records the last high-risk freshness replay gap as closed: DESI acquired custody, Lyman-alpha/String-M denominator pressure, and Euclid release-timeline runway are replayed under row-scoped typed policies rather than one coarse source role. Euclid/CERN watchlist refs remain zero-placement only.

## rev0353 update — Core freshness replay / public-custody refactor

Historical rev0353 note: linked revision was `rev0353` (`core-freshness-replay-public-custody-refactor`). Bundle: `Theory-of-Everything-rev0353-2026.06.10.08.08-core-freshness-replay-public-custody-refactor.zip`. The trajectory now records core public-source replay after helper factoring: freshness checks no longer accept core public-record rows as bare source_refs when their typed custody events are absent or weakened, and no route authority changes.

# Trajectory map

## Current north star

Find the smallest theory spine that can recover known physics across scales without cheating on observables, entropy, or measurement.

## Current spine

Historical rev0354 note: rev0354 was the linked revision (`mixed-role-freshness-replay-euclid-watchlist-refactor`). The active spine is typed public-source custody replay with row-scoped mixed-role freshness policies: DESI public-chain custody, Lyman-alpha/String-M denominator pressure, and Euclid release-timeline runway are checked under their own event dispositions, and freshness alone still cannot promote a route.

- invariants-first discipline
- EFT / renormalization as baseline, not embarrassment
- gravity as both geometry and quantum-pressure surface
- horizon entropy and thermodynamics as load-bearing clues
- entanglement as a bridge quantity rather than a universal solvent
- duality / atlas thinking: multiple formalisms may cover overlapping regions of one deeper space
- observer / measurement / record formation as physical, not merely verbal, structure
- witness borrowing measured explicitly rather than left as a vague debt
- family-specific no-climb and witness-closure gates stay preserved canonically, so neither better-tagged dissipation nor sharper reconstruction language gets mistaken for candidate-native witness progress
- default current-head control now routes through `docs/40-model/current-head-control-router.md`, and trajectory/program mirrors should not stack that parent router with child routers unless a revision is changing a child lane directly
- measure / population / typicality work survives only as a bounded package-credit lane under `CL-0049`, with revisit controlled by standby threshold `AS-0035`
- no current live lane clears candidate-native identifiability closure; `docs/10-method/candidate-identifiability-state-machine.md` now owns the shared `OQ-0057` state semantics, while the prior candidate-native-identifiability dockets remain route / evidence / stress / carrier / authority worksheets; broad live-family pressure still routes through `docs/40-model/current-family-readout-router.md`, leaving family-C witness-ceiling and identifiability debt explicitly unpaid
- family-C ambiguity is now explicitly triaged: apparent multiplicity should first be scored as frame/gauge redescription, then map-side observer/dictionary drift, and only then residual empirical collapse
- executable ledgers rather than only prose now carry route states, empirical deltas, negative controls, decision-experiment outcomes, cross-candidate quotient pressure, defeaters, rollback rules, severity tests, and generated authority-dependency edges
- archive compactness as a scientific enabler rather than clerical preference

## Current preservation priorities (while archive-control repair is active)

1. Preserve the Family-B minimum-gain and no-climb gates so better-tagged dissipative traces do not get mistaken for explanatory or witness progress.
2. Preserve the witness-borrowing ladder and Family-C witness-closure gate so sharper interfaces or reconstruction language do not get mistaken for candidate-native record closure.
3. Preserve the local-law / cosmological-boundary split and the canonical vacuum-energy proposal-class stack so package-conditioned gains do not get retold as generic local threshold relief.
4. Preserve `docs/40-model/current-head-control-router.md` so broad mirrors do not regrow parent-plus-child head routing as a checklist when one canonical current-head home already captures the burden cleanly.
5. Preserve the subordinate witness-package route inside that broader head/control surface so borrowing score, stage order, and shared gate scaffolding do not get over-credited as later closure stages, local witness closure, or candidate-native identifiability closure.
6. Preserve the measure / population / typicality audit as a bounded package-credit lane rather than a route to unique or locally earned closure.
7. Preserve `W-0006` only in compressed canonical form under `CL-0049`; keep it closed unless quantified or genuinely regime-portable evidence appears.
8. Keep `FOLLOWTHROUGH-QUEUE.json` narrow: the rev0315 authority-graph compaction item is now closed by execution, so the queue returns to empty unless a future task has an immediate proof point.
9. Keep the archive citation-rich, mirror-light, and small enough to reopen in one sitting; add new theory material only when it sharpens a discriminating question.
10. Preserve the atlas discipline so a calculational or consistency tool does not quietly get scored as a full ontology.
11. Preserve the completion-bid cash-out discipline so a broad UV framework cannot collect archive-wide credit before recovery, package, observables, wedges, and witness burden are named separately.
12. Preserve the candidate-identifiability state machine so `S0`–`S5`, `AT`, `AR`, `Q`, and `T` remain one semantic ladder rather than many loosely coupled dockets.
13. Preserve record-denominator, residual-cap, and negative-control discipline before any future `S4` / `S5` identifiability spending.
14. Preserve export, reimport, lineage, release, head, authority-transition, and rollback hygiene as worksheet evidence under the state machine, not as independent closure engines.
15. Preserve explicit head semantics so bundle, scientific-current, release-control, operational, and citation heads cannot drift into one overloaded current-head word.
16. Preserve executable route ledgers and empirical-delta rows so future route-state changes pay denominator, control, blocker, and cap fields rather than changing by summary.
17. Preserve `OQ-0058` so candidate sameness/difference is adjudicated through quotient and duality discipline rather than presentation rhetoric.
18. Preserve decision-experiment rows now separate forecasts, protocols, public records, nulls, benchmark artifacts, and route updates before any new outcome changes posture.
19. Preserve defeater, rollback, dependency-graph, and severity rows so an exciting result cannot be repromoted after a support failure unless the repair path is executable and route-local.
20. Preserve evidence-unit, independence-assumption, and credit-allocation rows so apparent convergence cannot be double-counted when it shares a carrier, model, nuisance stack, benchmark, quotient, regulator, or provenance wrapper.

Candidate-native promotion-readiness still lives in `docs/40-model/candidate-native-identifiability-promotion-readiness-matrix.md`, but its route-state meanings now route through `docs/10-method/candidate-identifiability-state-machine.md`. Public-record pressure now also has dedicated gravitational-locality, locally covariant, QES/island, frame-transport, operational-record, identifiability-theory, negative-control, and worked-example surfaces.

## Current-authority state-machine checkpoint

The current `OQ-0057` custody path is now read through a single state machine. Authority-transition and authority-rollback dockets remain required when the corresponding handles fire, but their function is to supply transition receipts for `AT`, `AR`, `Q`, or `T` states rather than to multiply closure criteria. This keeps the physics spine from being swallowed by authority bookkeeping.

## rev0262 trajectory note

The executable route layer now has three additional control ledgers: promotion gates, observed-sector recovery, and discriminator forecasts. The result is stricter, not more promotional: single-graviton/statistics access is admitted as a route, but only as a capped empirical-discriminator corridor.


## rev0264 trajectory note

The executable route layer now has a loss side: defeaters, rollback propagation, severity tests, and generated dependency edges. This is not a promotion layer. It is a way to recompute route authority when support breaks, when a negative control survives, when a public carrier fails custody, when a protocol fails replay, or when a quotient/model-class/benchmark assumption collapses.


## rev0265 trajectory note

The executable route layer now has a credit-accounting side: evidence units, independence assumptions, credit-allocation rows, and generated evidence-credit summaries. This is not a promotion layer. It is a way to prevent one support chain from being counted as multiple independent confirmations merely because it appears through many public artifacts, carriers, citations, benchmarks, or generated surfaces.


## rev0266 trajectory note

The archive now treats support as contrastive by default. `rev0266` adds contrast-class, likelihood/update, and prior-sensitivity ledgers so records cannot be counted as candidate support without declaring the rival set, update object, prior/nuisance stress dimensions, and maximum authority effect. This continues the conservative sequence: route state → promotion gate → public carrier → defeater/rollback → evidence credit → contrastive update.

rev0267 trajectory: after contrast/update/prior sensitivity, the archive added raw-record-to-observable measurement models, systematic uncertainty budgets, and calibration/traceability chains as the next executable cap layer.


## rev0270 causal-mechanism / intervention / counterfactual posture

The archive now treats mechanism, cause, mediator, intervention, natural experiment, ablation, and counterfactual language as route-local authority spending. `CAUSAL-MECHANISM-LEDGER.json`, `INTERVENTION-PROTOCOL-LEDGER.json`, and `COUNTERFACTUAL-ROBUSTNESS-LEDGER.json` require each route to declare the causal question, proposed structure, manipulability or perturbation gap, intervention status, alternative-world/model-intervention set, invariance or robustness test, failure modes, rollback handle, and maximum authority effect before causal language can affect broad posture. `OQ-0066` remains unresolved; this pass adds a new stop rule and does not promote any route.


## rev0270 selection/multiplicity/reporting-bias layer

This revision adds `SELECTION-FUNCTION-LEDGER.json`, `MULTIPLICITY-CONTROL-LEDGER.json`, and `REPORTING-BIAS-LEDGER.json` so selected-positive, look-elsewhere, surprise, discovery, anomaly, benchmark-win, and file-drawer-insensitive language is blocked unless the route declares its search denominator and maximum authority effect. No route is promoted to `S4` or `S5`.

rev0272: semantic / ontology / language-permission pass. The archive now treats term stability and ontology commitment as executable authority controls rather than prose glosses.

rev0273: social authority / review / consensus pass. The archive now treats peer review, expert testimony, replication claims, citation prestige, institutional endorsement, and consensus as executable social-authority controls rather than promotion channels.

rev0274 adds a computational evidence boundary: replayable software and stable numerics can improve custody but cannot replace route denominators, observed-sector recovery, or candidate-native public bridges.


## Rev0274 computational artifact control

This revision adds `COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json`, `NUMERICAL-STABILITY-LEDGER.json`, and `SOFTWARE-SUPPLY-CHAIN-LEDGER.json` so runnable code, containers, workflow replay, solver output, generated summaries, dependency locks, software citation, and supply-chain polish cannot be laundered into route promotion or candidate-native closure.

rev0275 adds a formal-proof boundary: machine-checked fragments, proof certificates, theorem statements, derivation traces, and assumption inventories can improve internal rigor but cannot replace public-record bridges, observed-sector recovery, semantic identity, or candidate-native closure.

- Boundary / initial-data / sector-selection controls now prevent selected-boundary, selected-vacuum, selected-regulator, apparatus-window, survey-window, and map-pipeline successes from being retold as global candidate support.


## rev0278 gauge / constraint / observable quotient addition

This revision adds `GAUGE-SYMMETRY-LEDGER.json`, `CONSTRAINT-CLOSURE-LEDGER.json`, `OBSERVABLE-QUOTIENT-LEDGER.json`, and `docs/30-program/gauge-constraint-summary.generated.md`. These surfaces block promotion from gauge-fixed representatives, unclosed constraint algebras, anomaly-contaminated quantization, BRST-exact or pure-gauge artifacts, unreduced coordinates, and metadata wrappers. No route is promoted.

## rev0279 trajectory note

After gauge/constraint/observable-quotient control, the next pressure point is scheme and scale. rev0279 adds regularization-scheme, renormalization-flow, and matching-condition controls so regulator-specific, scheme-dependent, running-parameter, fixed-point, naturalness, and threshold/EFT-matching language cannot promote a route without an invariant target and residual cap.


- rev0280 adds composition-law, interface-compatibility, and global-consistency controls after regularization/matching controls; local successes remain local unless a declared composition law and obstruction-aware global integrability test license stronger language.

rev0281 adds the unitarity / causality / stability viability gate after composition/global-consistency controls: local-to-global assembly is not enough for healthy physical dynamics.

## rev0282 trajectory — quantum/classical correspondence and route-layer audit

After rev0281 made physical viability executable, rev0282 adds quantization-map, classical-limit, and semiclassical-correspondence controls. It also refactors the route-support surface by adding a ledger-family registry and correcting overbroad composition/interface/global handles to route-local-plus-wrapper ownership.

## rev0283 trajectory — information flow, entropy, no-go compliance, and cardinality audit

After rev0282 made quantum/classical correspondence executable, rev0283 adds information-flow, entropy-accounting, and no-go-compliance controls. The new rows block Page-curve, information-recovery, entropy-balance, no-cloning-safe, no-signalling-safe, and data-processing language from raising route authority unless the source/target information objects, entropy budget, no-go assumptions, and rollback handles are declared. The revision also audits `LEDGER-FAMILY-REGISTRY.json` and tightens route-local-plus-wrapper cardinality for many already route-local support families.

## rev0284 note

rev0284 adds symmetry/anomaly/conservation controls and a registry-driven route-state summary refactor; no route is promoted.

## rev0286 note

rev0286 adds executable measure/ensemble/typicality controls (`OQ-0084`) and a binding-control-ledger coverage audit so probability, ensemble-average, naturalness, anthropic, observer-weighted, and prediction language cannot bypass route denominators.


- `rev0287` — Added matter-sector spectrum/coupling/mass controls and program-ID namespace audit; Standard Model recovery remains route-local and nonpromotional.

## rev0289 trajectory marker

Adds cosmology observed-sector controls and an OQ gate-coverage audit. The move deepens observed-sector discipline without promoting any route.


## rev0290 singularity/censorship note

rev0290 adds curvature-regime, singularity-resolution, and censorship/global-hyperbolicity controls under `OQ-0088` plus a constitutional CL/OQ namespace audit. This is archive-control pressure only; no route is promoted.

## rev0291 stress-energy / backreaction gate

`OQ-0089` adds stress-energy/source, semiclassical-backreaction, and energy-condition controls. The layer is a wording gate and rollback handle, not promotion fuel.

rev0292 adds the classical-GR recovery layer and a row-count parity audit so mature route-local-plus-wrapper families cannot silently lose route rows or metadata wrappers.

## rev0293 trajectory note

Added a quantum-record chain layer: state preparation, detector response, and decoherence/pointer records. Also added schema-envelope coverage auditing so registered ledger families cannot silently drift from their schemas and generated summaries.

## rev0294 asymptotic / IR / scattering controls

rev0294 adds `OQ-0092` plus `ASYMPTOTIC-STATE-LEDGER.json`, `INFRARED-DRESSING-LEDGER.json`, and `SCATTERING-OBSERVABLE-LEDGER.json`. S-matrix, IR-finite, soft-theorem, memory, BMS-charge, inclusive-rate, finite-time scattering, and asymptotic-completeness language now requires route-local rows and remains non-promotional. The revision also adds a candidate-route schema field coverage audit.

- rev0295 adds discretization-regime, finite-volume/scaling, and continuum-extrapolation controls plus row-ID uniqueness audit; no candidate route is promoted.

## rev0296 correlator / operator / bootstrap controls

rev0296 adds `OQ-0094` plus `CORRELATION-FUNCTION-LEDGER.json`, `OPERATOR-INSERTION-LEDGER.json`, and `BOOTSTRAP-DATA-LEDGER.json`. Correlator, n-point, generating-functional, operator-dictionary, OPE, conformal-block, crossing, bootstrap-island, CFT-data, and bulk-boundary-correlator language now requires route-local rows and remains non-promotional. The revision also adds a generated claim-route binding schema-field audit.

## rev0298 trajectory note

The evidence-control stack now includes a Hilbert/representation/spectrum layer. This closes the gap where one Hilbert space, Fock sector, GNS representation, spectral density, or spectral geometry could be retold as candidate identity without representation-equivalence and inverse-spectrum controls.

## rev0299 trajectory note

rev0299 adds a nonperturbative-sector gate: defects, instantons, Euclidean saddles, bounces, false-vacuum decay, metastability, and tunneling-rate support remains route-local and cannot promote a candidate. It also adds a schema array-type audit for route/binding handle fields.

- rev0302 adds locality / microcausality / cluster-decomposition controls and route-field prefix collision auditing; no route is promoted.


## rev0304 update

Added QEC code-subspace, logical-operator reconstruction, decoder-certification controls, and registered source-kind coverage auditing. No route is promoted to S4/S5.

- `rev0305` extends the route-support stack with complexity-resource controls and a binding controlling-ledger order audit.


## rev0306 hydrodynamic / transport update

rev0306 adds equation-of-state, transport-coefficient, and fluctuation-dissipation route controls plus registered-ledger revision alignment auditing. No route is promoted.

## rev0307 update — perturbative / loop / resummation controls

Added route-local perturbative-expansion, loop-order, and resummation/Borel controls under `OQ-0105`, plus ledger-family order auditing. No candidate route is promoted to S4/S5.

## rev0311 trajectory marker — benchmark/evaluation controls

The route-support stack now includes benchmark-suite, benchmark-metric, and evaluation-protocol denominators plus context-pack release freshness auditing. This reduces leaderboard, metric, and restart-surface overclaim.

## rev0312 trajectory marker — prospective/preregistration/blinding controls

rev0312 adds prospective-prediction, preregistration-protocol, and blinding/deviation controls plus release-navigation freshness auditing under `prospective-preregistration-blinding-navigation-freshness-audit`. This does not promote any route; it prevents prediction, preregistration, blind-analysis, unblinding, confirmatory, severe-test, and protocol-deviation language from being spent without route-local timing and bias-control rows.


## rev0313 trajectory marker — unit/constant/scale-setting controls

rev0313 adds unit-convention, fundamental-constant, and scale-setting controls plus release-chronology consistency auditing under `units-constants-scale-setting-chronology-audit`. It does not promote any route; it prevents natural-unit, Planck-unit, CODATA/SI, dimensionless-ratio, hierarchy, naturalness, and scale-setting language from being spent without route-local unit/constant/scale rows.

## rev0314 trajectory marker — uncertainty/significance/coverage controls

rev0314 adds uncertainty-interval, significance-threshold, and coverage-calibration controls plus bibliography reference-sequence auditing under `uncertainty-interval-significance-coverage-bibliography-audit`. It does not promote any route; it prevents interval, p-value, sigma, discovery, exclusion, coverage, and calibration language from being spent without route-local statistical rows.

<!-- rev0319 release-navigation marker -->
Historical linked revision: `rev0337` (`empirical-delta-route-cmbs4-source-smoke-audit`).

## rev0328 update — QRF frame-transport / cross-route handoff audit

Historical linked revision: `rev0337` (`qrf-frame-transport-crossroute-handoff-audit`). Bundle: `the package named in `RELEASE-MANIFEST.json``. This pass repairs a cross-route pressure leak between FamilyC subregion-state deltas and the QRF frame-transport evidence unit, adds QRF large-gauge / crossed-product source-role pressure as route-local S2 custody, and keeps the relational frame route at S2. No route is promoted.

## Historical release-navigation marker (rev0330; retired currentness wording)

Historical linked release marker: `rev0330` / `familyb-nonequilibrium-entropy-source-dedupe-audit` / `the package named in `RELEASE-MANIFEST.json``. This marker exists only to keep navigation freshness aligned; substantive trajectory routing remains through `docs/40-model/current-head-control-router.md`.
