# FamilyC finite-N QEC / island decoder source-role audit

Revision: `rev0334`

## Risk targeted

The FamilyC entanglement-wedge/code route is the strongest live route, so it is also the lane most likely to be overcredited. Current finite-N, black-hole-interior QEC, modular/Krylov area-operator, and island work is important, but it sharpens denominators rather than closing observed-sector authority.

## Change made

- Added `DF-0022-FAMILYC-FINITE-N-QEC-ISLAND-DECODER-REPLAY` as a route-local public-record requirement for finite-N/interior-QEC/island decoder replay.
- Added `ED-0028-FAMILYC-FINITE-N-QEC-ISLAND-PRESSURE` as S3 pressure on the FamilyC route.
- Added `DX-0015-FAMILYC-FINITE-N-QEC-ISLAND-DECODER-REPLAY` as a route-only decision experiment, avoiding the older multi-route FamilyC learned-inverse decision row.
- Reciprocally hooked `ED-0028-FAMILYC-FINITE-N-QEC-ISLAND-PRESSURE` into `EU-0001-FAMILYC-EW-RECONSTRUCTION` while keeping `REF-0691` through `REF-0694` out of acquired evidence-unit `source_refs`.
- Wired `tools/familyc_finite_n_reconstruction_policy.py` into generated-surface sync and archive lint.
- Compacted frontier-source isolation output so it retains counts, per-ref summaries, and failures rather than hundreds of PASS rows.

## Non-promotion boundary

The new references are pressure refs. They require explicit finite-N/code-subspace size, backreaction convention, island/QES or area-operator target, modular-flow/Krylov domain, massless or massive graviton boundary condition, algebra quotient, recovery channel, error norm, and independent replay before decoder language can be spent. They do not promote `R-OQ0057-FAMILYC-EW-CODE` above `S3` and do not support `S4/S5`, observed-sector closure, or Theory-of-Everything identity.

## Audit/refactor note

The wasteful part corrected this turn is retained audit exhaust: frontier-source isolation had become a large table of successful placements. The evaluator still checks every placement, but the generated surface now records compact per-ref summaries and failures.

## rev0369 operational-norm correction

The route now owns `FAMILYC-APPROXIMATE-RECOVERY-SCALING-BENCHMARK.json`, which replaces the prior free leakage sweep as the cross-size error baseline. It reports an exact complementary-channel diamond norm and exact worst-case entanglement fidelity for the declared decoder, with an analytic small-leakage anchor and a fixed-leakage negative control.

The negative control catches a severe metric error: max-entry Knill–Laflamme residuals fall as `1/D` even when operational leakage and decoder infidelity do not improve. Cross-size source intake and decoder replay may therefore use entrywise residuals only as fixed-dimension diagnostics; scaling language now requires an operational norm or dimension-aware theorem plus a declared recovery criterion.

This correction changes the accepted denominator, not route authority. The resource `D` is not identified with CFT `N`, `1/G`, central charge, area, bond dimension, or backreaction, and the Family-C route remains capped at `S3`.

## rev0370 JLMS budget and state-quantifier correction

The route now owns `FAMILYC-JLMS-RECOVERY-BUDGET-BENCHMARK.json`. It does not derive a physical finite-`N` remainder; it executes the conditional theorem bridge that was previously only named. A supplied uniform pairwise relative-entropy defect now yields explicit universal-recovery fidelity, trace-norm, and normalized-observable budgets, and the benchmark inverts target operational errors into the maximum admissible defect.

The substantive scaling correction is that `epsilon_R=O(R^-p)` gives only `O(R^-p/2)` trace/observable accuracy through the current sufficient theorem, while squared-fidelity infidelity remains `O(R^-p)`. Thus an `O(1/N)` JLMS remainder cannot be reported as `O(1/N)` trace reconstruction absent a stronger result.

A rare-sector direct-sum control catches a second severe source-intake error. The defect of a uniform reference mixture can vanish as `1/K`, yet a state concentrated in one bad sector retains order-one relative-entropy defect and order-one recovery error. Source intake must therefore preserve whether a remainder is a uniform supremum, restricted state-class bound, weighted average, sample estimate, or single-reference result. Average-to-uniform promotion is now explicitly barred.

The refactor this turn is deliberately mechanical rather than another policy registry: the qutrit, operational-scaling, and JLMS-budget generators share one small write/check/CLI harness in `tools/generated_benchmark_artifact.py`, while their scientific calculations and acceptance tests remain local. This removes three copies of release-artifact plumbing and ensures source-tree and extracted-package replay use the same generated-text semantics.

The physical denominator remains unpaid. The large-code source carries multiple approximation parameters plus log-stability, alignment/smoothness, approximate-isometry, and sector-orthogonality conditions; rev0370 does not collapse those into a fabricated scalar `epsilon_R(N)`. Computational `D`, abstract bridge resource `R`, and physical `N`/`G` remain unmapped, and route authority remains `S3`.

## rev0373 reconstructed-algebra domain and sector-growth correction

The state-domain placeholders in the flagged-channel budget are now evaluated exactly on a finite spectral-floor reconstructed algebra. For `rho >= lambda I` in dimension `d`, the relative-entropy diameter is `D_max=(1-d lambda) log[(1-(d-1)lambda)/lambda]` and the centered modular oscillation is `L_K^osc=log[(1-(d-1)lambda)/lambda]`. Explicit extremizers close both formulas numerically. Restricting to the classical center of a `K`-sector direct sum with fixed total floor mass makes both costs grow as `Theta(log K)` even when all internal sector states are identical.

The new executable negative control isolates a severe whole-code failure. Under the adversarial schedule `K~exp(1/G)` and `delta_iso~G`, every displayed local source remainder tends to zero, but the flagged-channel defect and success-conditioned recovery bound remain order one because `delta_iso D_max` and `delta_iso L_K^osc` do not vanish. Polynomial sector growth converges under the same local powers, while `delta_iso~G^2` restores convergence for the exponential schedule. Therefore this sufficient theorem route needs a global sector-count/weight theorem, or equivalent reduced-algebra bounds, satisfying `delta_iso log K -> 0`; a within-sector tail floor cannot pay that debt.

The audit/refactor is route-local rather than another registry. Exact spectral-floor and direct-sum geometry now lives in `tools/familyc_state_domain.py`; the channel-completion helper consumes those quantities, and the benchmark retains the source-tail, channel, and recovery-policy checks. The sector schedules are theorem stress vectors rather than a physical CFT fit, and no route authority changes.

## rev0374 full-system FLM and weighted log-smoothness correction

The source's stronger approximate-isometry branch is now propagated explicitly instead of assigning the isometry exponent independently. Appendix C requires approximate FLM on the entire small-code system and gives `eps_iso,small <= 2 sqrt(eps_FLM)` after rescaling; Lemma 4 then gives `delta_iso <= eps_iso,small + eps_OD` for the large direct sum. Under `eps_FLM~G^a`, `eps_tail~G^t`, and `K~exp(c/G^gamma)`, with the other source terms nonperturbative on the same domain, the flagged sufficient bridge closes only for `a>max(t,2 gamma)`. The corresponding success-conditioned trace exponent is `min((a-t)/4,a/4-gamma/2)` up to logarithms. This branch cannot be invoked from a subregion FLM estimate alone.

The second missing source term, global log-smoothness, is now exact on the commuting sector center. If sector confusion sends `p` to `q=T p`, then `eps_l_smooth=max_alpha |log(q_alpha/p_alpha)|`. A nearest-neighbor kernel with only `1e-8` leakage leaves total variation at `9.32050e-10` but drives the operator-log error to `83.08617` nats for a 513-sector Gaussian tail. Distance decay and tiny trace leakage therefore do not certify the source's global log-smoothness condition. The correct dimension-free object is relative incoming flux: if `zeta=max_alpha |(T p)_alpha/p_alpha-1|<1`, then `eps_l_smooth <= -log(1-zeta)`. Exact detailed balance with `p` is stronger than necessary but removes the commuting tax, and the executable positive control reaches a residual below `4.1e-13`.

The refactor remains scientific and route-local: ordinary slope fitting is shared in `tools/benchmark_numeric.py`, exact sector transport remains in `tools/familyc_state_domain.py`, and the source isometry/exponent algebra remains in `tools/familyc_channel_completion.py`. No new registry, route family, or authority state was created.

## rev0375 full operator algebra and common-decoder correction

The commuting sector center is now explicitly separated from the noncommuting factor blocks of `A=direct_sum_alpha M_2`. The executable probe verifies the exact direct-sum relative-entropy identity and an additive product-domain split for both `D_max` and `L_K^osc`. In the declared cell, center-only accounting pays less than half of either tax. A `p`-stationary sector kernel can therefore remove the center contribution while leaving the within-sector quantum modular term untouched.

A noncommuting qubit stress exposes the missing condition. With spectral floor `lambda=exp(-1/G)` and eigenbasis rotation `theta=G`, the trace-norm state perturbation falls linearly to zero but the operator-log error approaches one nat. The repair `theta=G^2` makes the log error fall as `G`. Source intake must therefore carry a factor-block spectral condition and modular-frame/eigenbasis transport theorem, not merely small state distance or sector stationarity.

The state-dependent wedge cell catches a separate operational failure. Sector 0 is exactly reconstructible from `AC` and sector 1 from `BC`, yet each fixed region maps an orthogonal logical pair in the other sector to the same record, forcing minimax trace recovery error at least `1`. Measuring the sector and switching regions recovers the direct-sum block algebra but dephases cross-sector coherence with trace error `1`; only the fixed union `ABC` decodes arbitrary coherent code states exactly. A route claim must therefore name one fixed carrier region and common decoder, or explicitly declare the weaker target algebra and license the coherence quotient.

The refactor moves representation-neutral quantum-matrix operations into `tools/familyc_operator_algebra.py`. During that audit, an anti-Hermitian commutator was found to have been passed through a Hermitian-only trace-norm helper, falsely returning zero; a general singular-value trace norm now guards the noncommutativity test. No route authority changes.

## rev0376 fixed-region source correction and decoder gluing

A close reread of REF-0735 corrects the preceding source-specific charge. Its large-code definition uses the same boundary-region pair for every small-code sector, and the reduced wedge state is block diagonal in the direct-sum algebra. The source therefore does **not** owe a sector-dependent region switch, and a direct-sum algebra target does not automatically owe preservation of off-diagonal sector coherence. The rev0375 wedge-switching code remains useful only as a generic negative control for later state-dependent-wedge extrapolation.

The new constructive cell asks the narrower operator-algebra question on one fixed carrier. Its direct-sum and full-subspace OAQEC commutant residuals are `1.8883e-18`; one controlled inverse decoder recovers tested coherent code states with maximum trace-norm error `1.9029e-16`; and a dephasing decoder preserves every tested direct-sum algebra expectation to `1.1102e-16` while losing a deliberately off-diagonal coherent state by trace error `1`. That loss is licensed only for the direct-sum algebra target, not for a stronger full-Hilbert claim.

The approximate gluing cell makes the remaining error budget operational. A symmetric sector-instrument confusion of probability `p_max` exactly produces state and center-observable error `2 p_max` with fitted power one. A hidden-frame control then discards the sector tag: two distinct logical inputs produce the same carrier record, forcing any common decoder to incur a minimax error linear in the frame separation even though both sector-conditioned decoders are exact. Source intake must therefore derive a **worst-sector** confusion bound, nondemolition routing disturbance, and uniform sector-local decoder error; an average sector error cannot substitute.

The refactor separates these route-local questions into `tools/familyc_decoder_gluing.py`. Generic matrix logarithms, partial traces, norms, and direct-sum algebra operations remain in `tools/familyc_operator_algebra.py`. No registry family or authority state was added.

## rev0377 Definition-7 routing translation and coherent-sector split

REF-0735 Definition 7 Condition 2 can now pay one previously vague fixed-region debt. Let `epsilon_sub-tr` bound, uniformly in the sector label, the retained-region trace norm outside that sector's declared dominant block, and let `epsilon_iso,small` supply the sector-normalization floor. On sector-diagonal/direct-sum inputs, the normalized wrong-block probability is at most `epsilon_sub-tr/(1-epsilon_iso,small)`, and the normalized full sector output is within trace norm `2 epsilon_sub-tr/(1-epsilon_iso,small)` of its normalized dominant-block state. Therefore a decoder certified on dominant blocks obeys

`epsilon_common <= epsilon_block + 2 epsilon_sub-tr/(1-epsilon_iso,small)`.

The owned family saturates the source term with fitted power one. At `epsilon_iso,small=0.001`, target common-decoder errors `0.1`, `0.05`, and `0.01` require `epsilon_sub-tr <= 0.04995`, `0.024975`, and `0.004995` when the decoder certificate is on normalized dominant blocks. A certificate only on the full sector output pays the conservative round-trip transport cost and halves those admissible budgets.

This is not yet a coherent whole-code theorem. Two exact-isometry controls separate the source errors instead of folding them into a false scalar. In an environment-tagged family, `epsilon_sub-tr=r` while coherent center error is `epsilon_OD=2 sqrt(r(1-r))`, so a linear `epsilon_sub-tr` extrapolation fails. In a carrier-frame family, `epsilon_OD=0` while the full Condition-2 trace-norm term itself upper-bounds the coherent error. The archive therefore preserves `epsilon_OD`, `epsilon_sub-tr`, and `epsilon_iso,small` as distinct quantities and asserts no universal additive completion until one same-domain block-instrument/OAQEC theorem is proved.

A one-bad-sector control closes the remaining quantifier loophole: uniform-mixture average leakage and decoder error fall as `1/K`, while the bad-sector error remains `0.2`. Condition 2's alpha-independent bound must remain a worst-sector supremum rather than an average.

The refactor isolates these source-conditioned calculations in `tools/familyc_source_routing.py`. The existing source-role policy was also hardened to normalize notation-only underscore/hyphen variants and to test scientific concept groups rather than brittle spellings; it now explicitly checks center inflow, modular-frame transport, dominant-block certification, worst-sector routing, and coherent-sector/OAQEC obligations without creating another registry family. A separate cloudtainer audit found that the normal Python site stack kept each long-lived lint/smoke orchestration parent near 290 MiB RSS while heavy validators allocated their own working sets. Both orchestrators now re-exec under `-S`, leaving child validators unchanged; the measured parent fell to about 19 MiB, and lint output is staged in a temporary file rather than a pipe. Route authority remains `S3`.

