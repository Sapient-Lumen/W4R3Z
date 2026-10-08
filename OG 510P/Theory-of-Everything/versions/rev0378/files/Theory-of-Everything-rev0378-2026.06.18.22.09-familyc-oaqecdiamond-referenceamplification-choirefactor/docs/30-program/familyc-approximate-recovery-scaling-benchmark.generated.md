# Family-C approximate-recovery scaling benchmark (generated)

This owned finite-resource code family replaces a free leakage sweep with an explicit resource parameter, an exact complementary-channel diamond norm, and an exact worst-case entanglement fidelity for the declared decoder. It remains a quantum-information toy model, not finite-N holography.

- Route: `R-OQ0057-FAMILYC-EW-CODE`
- Decision experiment: `DX-0015-FAMILYC-FINITE-N-QEC-ISLAND-DECODER-REPLAY`
- Status: owned finite-resource approximate-QEC stress cell; route-local S3 pressure only
- Replay: `python3 tools/familyc_approximate_recovery_scaling_benchmark.py --check`
- Validation failures: `0`

## Construction

For each prime `D > 5`, the encoder uses

`V_D|i> = sum_j sqrt(p_D(j-3i)) |j, j+i, j+2i>`,

with `p_D(x) = [1 + delta_D cos(2*pi*x/D)]/D`. Any retained pair algebraically identifies the logical label and erased-share label, but the erased share carries weak logical information whenever `delta_D != 0`.

The complementary channel is classical-quantum, so its distance from the uniform constant channel is available exactly in diamond norm. The declared decoder yields a circulant dephasing channel, whose exact worst-case entanglement fidelity is attained by uniform logical populations.

## Resource-scaled family

Declared rule: `delta_D = 0.8 D^(-0.5)`.

| D | delta | complement diamond norm | max-entry KL residual | decoder infidelity | restricted-record distance | richer witness gap |
|---:|---:|---:|---:|---:|---:|---:|
| `7` | `0.302371578407382` | `0.194120791264355` | `0.0431959397724831` | `0.0116495353441758` | `0.0970603956321775` | `0.857142857142857` |
| `11` | `0.241209075662211` | `0.154081598612827` | `0.0219280977874737` | `0.00736091460490906` | `0.0770407993064135` | `0.909090909090909` |
| `13` | `0.221880078490092` | `0.141597547810663` | `0.0170676983453917` | `0.00621673276160484` | `0.0707987739053315` | `0.923076923076923` |
| `17` | `0.194028500029066` | `0.123698321337553` | `0.0114134411781804` | `0.00474246735892003` | `0.0618491606687765` | `0.941176470588235` |
| `19` | `0.183532587096449` | `0.116973678974217` | `0.00965960984718155` | `0.00423976315050745` | `0.0584868394871085` | `0.947368421052632` |
| `23` | `0.16681153124566` | `0.106278118166687` | `0.00725267527155044` | `0.00349816106111966` | `0.0531390590833435` | `0.956521739130435` |
| `29` | `0.148556270541641` | `0.094620119845879` | `0.00512263001867729` | `0.00277110648465673` | `0.0473100599229395` | `0.96551724137931` |
| `31` | `0.14368424162142` | `0.0915113839465848` | `0.00463497553617483` | `0.00259156502624991` | `0.0457556919732924` | `0.967741935483871` |
| `37` | `0.131519189844286` | `0.0837528729349691` | `0.00355457269849421` | `0.00216981636174318` | `0.0418764364674845` | `0.972972972972973` |
| `43` | `0.121998856266084` | `0.0776841605784881` | `0.00283718270386241` | `0.00186612630589322` | `0.0388420802892441` | `0.976744186046512` |
| `47` | `0.116691993198316` | `0.0743022616879662` | `0.00248280836592161` | `0.00170686362486849` | `0.0371511308439831` | `0.978723404255319` |
| `53` | `0.109888451158951` | `0.0699674034389291` | `0.00207336700299908` | `0.00151315582393863` | `0.0349837017194645` | `0.981132075471698` |
| `59` | `0.104151128784659` | `0.0663125015547806` | `0.00176527336923151` | `0.00135893395913567` | `0.0331562507773903` | `0.983050847457627` |
| `61` | `0.102429503946317` | `0.0652158547034713` | `0.00167917219584126` | `0.00131428312066895` | `0.0326079273517356` | `0.983606557377049` |
| `67` | `0.0977355554850442` | `0.0622260874080076` | `0.00145873963410514` | `0.00119635625219761` | `0.0311130437040038` | `0.985074626865672` |
| `71` | `0.0949425326555083` | `0.060447224555991` | `0.00133721876979589` | `0.00112883173359446` | `0.0302236122779955` | `0.985915492957746` |
| `73` | `0.0936329177569045` | `0.0596131669695533` | `0.00128264270899869` | `0.00109784943640046` | `0.0298065834847767` | `0.986301369863014` |
| `79` | `0.0900070320740819` | `0.0573040320873094` | `0.00113932951992509` | `0.00101433049538902` | `0.0286520160436547` | `0.987341772151899` |
| `83` | `0.0878114079917523` | `0.0559058157615727` | `0.00105796877098497` | `0.000965370133425236` | `0.0279529078807863` | `0.987951807228916` |
| `89` | `0.0847998304005088` | `0.0539880515733097` | `0.000952807083151786` | `0.000900193471820021` | `0.0269940257866549` | `0.98876404494382` |
| `97` | `0.0812276932106895` | `0.0517134157393262` | `0.000837398899079272` | `0.000825850759989533` | `0.0258567078696631` | `0.989690721649485` |

### Fitted scaling

| Metric | Fitted slope | Declared expectation |
|---|---:|---:|
| Complement diamond norm | `-0.502019741943602` | `-0.5` |
| Decoder worst-case entanglement infidelity | `-1.00548992015747` | `-1.0` |
| Max-entry residual | `-1.5` | `-1.5` |

The operational leakage falls as `D^-1/2`, while declared-decoder infidelity falls as `D^-1`. The same restricted-record collision improves with size, while the decoded logical-zero witness gap remains large and tends to one.

### Analytic asymptotic anchor

For small leakage, the cosine family gives `||N_c-S||_diamond -> 2 delta/pi`, declared-decoder infidelity `-> delta^2/8`, and max-entry residual exactly `delta/D`. Thus `delta=0.8 D^-1/2` predicts prefactors `1.6/pi`, `0.08`, and `0.8`, together with `infidelity/diamond^2 -> pi^2/32`. The largest-D computation is checked against all four anchors; this makes the fitted slopes a replay of an analytic limit rather than a free regression story.

## Fixed-leakage negative control

The control holds `delta_D = 0.3` while increasing `D`.

| Metric | Fitted slope | Correct reading |
|---|---:|---|
| Complement diamond norm | `-0.00201974194360382` | no operational convergence |
| Decoder infidelity | `1.62705824294128e-06` | no recovery convergence |
| Max-entry residual | `-1.0` | false `1/D` convergence from entry dilution |

## Severe metric failure corrected

A max-entry Knill-Laflamme residual is valid as a same-dimension diagnostic but unsafe as a growing-dimension convergence norm. In the fixed-leakage control it shrinks by the dimension ratio while the exact complementary-channel diamond norm and decoder infidelity stay constant.

Across `D=7` to `D=97`, the max-entry residual improves by a factor of `13.8571428571429`, while the exact diamond norm changes only by a factor of `1.00839801317686`.

**Correction:** Cross-size Family-C recovery claims must report an operational channel norm or a dimension-aware bound plus a declared recovery fidelity; max-entry residuals may not carry scaling language by themselves.

## Acceptance checks

| Check | Passed | Detail |
|---|---:|---|
| dimension schedule uses distinct primes above every decoder coefficient | `true` | [7, 11, 13, 17, 19, 23, 29, 31, 37, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97] |
| all code-family probability laws are normalized and positive | `true` | max_normalization_residual=0.0 |
| encoding support is collision-free and every retained-pair decoder map is bijective | `true` | max_support_collisions=0; max_decoder_pair_collisions=0 |
| all three erased-share translation maps stay invertible | `true` | coefficients=3,4,5 |
| closed-form and Gram-matrix decoder fidelities agree | `true` | max_residual=2.22044604925031e-16 |
| erased-share operational metrics are symmetric | `true` | max_spread=0.0 |
| scaled family complementary-channel diamond norm follows D^-1/2 | `true` | -0.502019741943602 |
| scaled family declared-decoder infidelity follows D^-1 | `true` | -1.00548992015747 |
| scaled family max-entry residual follows the dimension-diluted D^-3/2 law | `true` | -1.5 |
| fixed-leakage diamond norm does not falsely converge | `true` | -0.00201974194360382 |
| fixed-leakage decoder infidelity does not falsely converge | `true` | 1.62705824294128e-06 |
| fixed-leakage max-entry residual falsely falls as D^-1 | `true` | -1.0 |
| scaled same-record collision improves monotonically | `true` | [0.0970603956321775, 0.0258567078696631] |
| scaled richer-record witness gap survives and grows | `true` | [0.857142857142857, 0.989690721649485] |
| large-D operational prefactors approach the analytic small-leakage anchors | `true` | {'observed_at_D_max': {'diamond_prefactor': 0.509318078061788, 'max_entry_prefactor': 0.799999999999999, 'decoder_infidelity_prefactor': 0.0801075237189847, 'information_disturbance_ratio': 0.308812679659956}, 'analytic_limit': {'diamond_prefactor': 0.509295817894065, 'max_entry_prefactor': 0.8, 'decoder_infidelity_prefactor': 0.08, 'information_disturbance_ratio': 0.308425137534042}} |
| information-disturbance ratio remains finite and stable | `true` | [0.309146616426382, 0.308812679659956] |

## Hard limits and next denominator

- This is a deterministic polynomial-code family with a chosen amplitude modulation, not a boundary CFT or gravitational code.
- The resource D is not a physical finite-N/JLMS parameter and no map to G, central charge, area, bond dimension, or backreaction is supplied.
- The benchmark treats one-share erasure only; it does not implement operator-algebra centers, edge modes, islands, QES competition, or state-dependent wedge changes.
- The declared algebraic decoder is evaluated exactly, but no claim of globally optimal recovery is made.
- Passing the cell creates no acquired evidence, observed-sector recovery, public-record closure, or Theory-of-Everything identity.

Next kernel step: Use FAMILYC-JLMS-RECOVERY-BUDGET-BENCHMARK.json to join separate full-system/subregion FLM control, eps_OD, the remaining projected-JLMS terms, and a p-weighted sector-inflow/log-smoothness bound on one state domain; then relate the source-closed flagged recovery budget to this complementary-channel norm without setting D=N and test whether the exponent and same-record discriminator survive code-subspace growth and a non-AdS observer map.
