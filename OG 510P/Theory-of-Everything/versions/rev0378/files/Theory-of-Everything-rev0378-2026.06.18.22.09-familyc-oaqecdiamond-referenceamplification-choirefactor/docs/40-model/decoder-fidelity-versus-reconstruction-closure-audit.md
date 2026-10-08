# Decoder fidelity versus reconstruction closure audit

Decoder fidelity is target-, norm-, and noise-model-relative. It can constrain a route, but it cannot become reconstruction closure without a declared code domain, recovery map, public replay, and rollback condition.

## Operational metric rule

For a fixed finite-dimensional code, entrywise Knill–Laflamme residuals can diagnose exact-condition failure. Across a growing family, however, a maximum matrix-entry residual is not a convergence norm: entries can dilute simply because the matrix has more coordinates.

`FAMILYC-APPROXIMATE-RECOVERY-SCALING-BENCHMARK.json` supplies the executable counterexample. With fixed logical leakage, its max-entry residual falls as `D^-1`, while the exact complementary-channel diamond norm and the declared decoder's worst-case entanglement infidelity remain asymptotically constant. The apparent improvement is therefore a coordinate-size artifact, not improved recovery.

Any cross-size Family-C recovery claim must now report both:

1. an operational channel distance, or a dimension-aware theorem bounding one; and
2. a declared recovery map with worst-case fidelity or an equivalent state-uniform error criterion.

A max-entry residual may remain as a same-dimension debugging statistic, but it cannot carry scaling, convergence, finite-`N`, or reconstruction language by itself.

## JLMS remainder-to-recovery rule

`FAMILYC-JLMS-RECOVERY-BUDGET-BENCHMARK.json` now makes the next bridge executable. If a declared state domain satisfies a **uniform pairwise** bulk/boundary relative-entropy defect `epsilon_R`, with `epsilon_R` measured in base-2 relative-entropy units, the universal-recovery construction gives root fidelity at least `2^(-epsilon_R/2)`. The local trace-norm error is bounded by `2 sqrt(1-2^(-epsilon_R))`; for arbitrary code states under the stated theorem assumptions, the sufficient trace-norm and normalized-observable bound used here is

`(2 + sqrt(2 ln 2)) sqrt(epsilon_R)`.

This halves the scaling exponent at the operational trace level: a theorem input `epsilon_R = O(R^-p)` produces an `O(R^-p/2)` trace/observable guarantee, although squared-fidelity infidelity remains `O(R^-p)`. In particular, a quoted `O(1/N)` JLMS remainder is not an `O(1/N)` trace-reconstruction result without stronger structure.

The benchmark also inverts the theorem. A target full-code trace/normalized-observable error of `0.1` requires a uniform defect no larger than about `9.90e-4`; under a purely conditional `epsilon_R=c/R` schedule, that means `R/c >= 1009.59`. A `0.01` target requires about `9.90e-6` and `R/c >= 100959.34`. These are hurdles for a future physical derivation, not claims that CFT data supply such a schedule.

## Quantifier rule and rare-sector failure

A whole-code recovery statement requires the theorem's whole-domain quantifier or an explicit theorem translating a weaker object into it. A weighted average, finite sample, one fiducial state, or one reference mixture cannot silently become a supremum.

The executable negative control uses `K` labeled sectors: `K-1` transmit a logical bit exactly and one rare sector erases it. In base-2 units the uniform reference mixture has relative-entropy defect `1/K` and genuine state-specific trace error `1/K`, but a declared bad-sector probe witnesses a one-bit defect and the channel has minimax trace error `1` on deterministic bit inputs. Thus any whole-domain uniform defect is at least one bit. If the mixture defect is incorrectly fed into the whole-code theorem, the purported upper bound drops below the actual worst-case error beginning at `K=16`. That contradiction diagnoses a quantifier violation, not a recovery-theorem failure.

Therefore every finite-`N`/JLMS decoder claim must label its remainder as one of: uniform supremum on a declared domain, restricted state-class bound, weighted average, sample estimate, or single-reference result. Only the first carries whole-domain universal-recovery credit without a separate coverage or concentration result.

## Fixed-region operator-algebra decoder-gluing rule

The source-specific carrier question is now narrower than rev0375 stated. REF-0735 fixes the same boundary-region pair across its small-code sectors and reconstructs a block-diagonal direct-sum wedge algebra. A valid decoder for that algebra need not preserve off-diagonal sector coherence unless full-Hilbert recovery is separately claimed.

`FAMILYC-JLMS-RECOVERY-BUDGET-BENCHMARK.json` now includes an exact fixed-region control. It verifies the erasure OAQEC condition `P E_i^dagger E_j P in A'`, supplies one coherent controlled decoder, and supplies a weaker dephasing decoder that is exact on the direct-sum algebra. Thus “coherence lost” is not by itself a decoder failure; the target algebra decides. Conversely, exact sector-conditioned decoders do not glue when the sector tag or frame is hidden.

For block-diagonal target states, the owned approximate instrument motivates the explicit budget

`epsilon_common <= epsilon_local + mu_nondemolition + 2 p_max`,

where `p_max` is a worst-sector confusion probability. The toy symmetric confusion channel saturates the `2 p_max` term. This is a constructive finite-dimensional bound, not yet a physical CFT theorem. A Family-C climb must derive all three terms from the same source region and state domain, not from a sector average.

## Current owned result and boundary

Under the deliberately chosen toy law `delta_D = 0.8 D^-1/2`, the benchmark finds complementary-channel diamond distance proportional to `D^-1/2` and declared-decoder worst-case entanglement infidelity proportional to `D^-1`. The computed prefactors approach the analytic small-leakage limits `2 delta/pi`, `delta^2/8`, and `pi^2/32` for the infidelity-to-leakage-squared ratio.

This is an operational approximate-QEC baseline plus a theorem-translation budget, not a physical finite-`N` result. The abstract bridge resource `R` is not identified with the toy dimension `D`, CFT `N`, `1/G`, central charge, area, or bond dimension. A holographic climb still requires one source-derived remainder to be instantiated with its state-domain, region, norm, and resource quantifiers, then related to the complementary-channel norm and tested against state-dependent wedges, algebra/edge modes, backreaction, and observer records. Authority remains capped at `S3`.
