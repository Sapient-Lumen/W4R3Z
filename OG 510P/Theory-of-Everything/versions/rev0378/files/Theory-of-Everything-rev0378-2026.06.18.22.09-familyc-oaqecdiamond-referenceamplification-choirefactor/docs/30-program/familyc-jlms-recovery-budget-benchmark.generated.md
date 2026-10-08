# Family-C JLMS-to-recovery budget benchmark (generated)

This cell audits the full source-to-recovery chain. It distinguishes (1) an operator-norm projected-JLMS residual, (2) a pairwise relative-entropy bound for the source's normalized map, and (3) the stronger channel-level hypothesis required by universal recovery. It does **not** invent a physical finite-`N` remainder.

- Route: `R-OQ0057-FAMILYC-EW-CODE`
- Decision experiment: `DX-0015-FAMILYC-FINITE-N-QEC-ISLAND-DECODER-REPLAY`
- Status: owned theorem-translation and quantifier-stress cell; route-local S3 pressure only
- Replay: `python3 tools/familyc_jlms_recovery_budget_benchmark.py --check`
- Validation failures: `0`

## Recovery theorem contract

The load-bearing input is a **genuine quantum channel** and an absolute relative-entropy defect bounded for every ordered pair in one declared convex state domain. A state average, one reference mixture, or a nonlinear normalized filter is not that premise.

For a valid base-2 defect `epsilon_R`, root fidelity is at least `2^(-epsilon_R/2)` and the arbitrary-code-state trace/normalized-observable guarantee used here is `3.17741002251547 sqrt(epsilon_R)`.

### Unit conversion probe

A `0.1`-nat defect becomes `0.144269504088896` bits. The base-2 and natural-exponential fidelity evaluations both give `0.951229424500714`.

## Source envelopes and the exact algebraic join

REF-0735 supplies three distinct envelopes. None is silently renamed a recovery-theorem defect.

| Source result | Symbolic envelope | Norm / state quantifier | Direct channel input? |
|---|---|---|---:|
| `Dong-Marolf-Rath Theorem 3, Eq. (4.50)` | `eps_pJLMS + eps_iso + eps_enhanced + eps_sub_log + eps_l_align` | expectation-value bound for a pair rho,sigma satisfying enhanced log-stability and log-alignment | `false` |
| `Dong-Marolf-Rath Theorem 5, Eq. (4.85)` | `eps_pJLMS + eps_iso + eps_enhanced + eps_sub_log + eps_l_smooth` | operator-norm bound for a reference state rho that is enhanced-log-stable against every sigma and log-smooth | `false` |
| `Dong-Marolf-Rath Theorem 6, Eq. (4.88)` | `eps_eJLMS(s) + |s| eps_iso + eps_OD + eps_sub_tr + eps_sub_exp(s) + eps_e_smooth(s)` | operator-norm bound at modular parameter s for log-stable small-code components and an exponentiated-smooth state rho | `false` |

The source's displayed small-code inputs are now kept explicit rather than compressed into an unexplained `eta`:

- Eq. (3.17): `sqrt(eps_FLM/eps_tail) + eps_iso_small |log eps_tail|, up to the source's suppressed O(1) coefficients`
- Eq. (4.24): `eps_iso_small + eps_OD`
- Appendix-C branch: If approximate FLM with the same eps_FLM is separately available on the entire small-code system, Appendix C gives eps_iso_small <= 2 sqrt(eps_FLM); Lemma 4 then gives delta_iso <= 2 sqrt(eps_FLM)+eps_OD for the large code.
- Power boundary: Without the extra full-system premise, eps_iso_small~G^b remains independent and the displayed square-root term vanishes only for a>t. With the Appendix-C branch and nonperturbative eps_OD, b=a/2; for K~exp(c/G^gamma), the flagged sector-geometry route further requires a>2 gamma.

Residual: `J_rho = V^dagger K_{W(rho)_R} V - M (A/4G + K_{rho_r}), with M=V^dagger V and z_sigma=Tr(M sigma).`

Exact identity: `D(W(sigma)_R || W(rho)_R) - D(sigma_r || rho_r) = z_sigma^-1 Tr[sigma (J_rho-J_sigma)] + Tr[sigma (M/z_sigma-I)(K_{rho_r}-K_{sigma_r})]. The area operator cancels between J_rho and J_sigma.`

Exact/scalar-norm corollary: If M=I (or M is scalar and V is rescaled), W is a genuine channel. If ||J_rho||_infinity <= eta for every reference rho in the declared domain, its all-ordered-pairs defect is at most 2 eta in the same logarithm units and may enter the recovery theorem after unit conversion.

### Exact-isometry executable probe

The `binary symmetric channel on a declared full-rank 41-state grid; it has an exact Stinespring isometry and no area term` checks `41` states. Its maximum identity residual is `8.60422844084496e-16`; maximum pairwise defect is `0.102493095991637` nats against the valid `2 eta` bound `0.196148780381373` nats.

## Severe channel-premise failure and correction

The source explicitly normalizes a non-isometric linear map. Unless `M=V^dagger V` is scalar on the domain, that normalization is nonlinear and therefore is not a quantum channel.

In the owned midpoint probe, `delta_iso=0.001` and the affine defect is `0.000999999999999945` in trace norm. Channel status: `false`.

**Correction:** the approximate normalized-map defect cannot be fed directly into universal recovery. Use exact/scalar norm, or channelize explicitly.

### Polar channelization

`Let U=V M^(-1/2), N_U(rho)=Tr_complement[U rho U^dagger], H_rho=A/4G+K_{rho_r}, and J^U_rho=U^dagger K_{N_U(rho)_R} U-H_rho. Then J^U_rho=M^(-1/2)J^V_rho M^(-1/2)+U^dagger(K_{N_U(rho)_R}-K_{W_V(rho)_R})U+(M^(1/2)H_rho M^(-1/2)-H_rho).`

Conditional bound: `If the last two terms are uniformly bounded by chi_out and chi_bulk, then ||J^U_rho|| <= eta/(1-delta_iso)+chi_out+chi_bulk and the genuine polar channel has epsilon_pair,nats <= 2[eta/(1-delta_iso)+chi_out+chi_bulk].`

The diagnostic polar cell closes with residual `0.0`. It also shows why source `eta` cannot be spent alone: the transformed source term is cancelled by an output-modular transport term in this toy, and that cancellation is not encoded in the scalar source bound.

### Flagged channel completion: constructive path without free transport symbols

`Set alpha=(1+delta_iso)^-1 and define Phi(rho)=alpha V rho V^dagger on an orthogonal success block plus Tr[(I-alpha V^dagger V)rho]|fail><fail|. Phi is CPTP, p_rho lies in [(1-delta_iso)/(1+delta_iso),1], and its conditioned success state is exactly W_V(rho).`

Block identity: `D(Phi(sigma)||Phi(rho)) = p_sigma D(W_V(sigma)||W_V(rho)) + D_Ber(p_sigma||p_rho).`

Channel defect: `If the declared reduced bulk-wedge/reconstructed-algebra domain has D(sigma_r||rho_r)<=D_max, then epsilon_flag,nats <= 2(eta+delta_iso L_K^osc)/(1-delta_iso) + [2 delta_iso/(1+delta_iso)] D_max.`

Success decoder transfer: `If a recovery channel for Phi has trace/normalized-observable bound T_flag, its restriction to the success block obeys T_success <= (T_flag+2 q_max)/p_min = [(1+delta_iso)T_flag+4 delta_iso]/(1-delta_iso). This yields one decoder on the source normalized success states without identifying W_V itself as a channel.`

The executable `Three-outcome diagonal approximate encoding with M=diag(1+delta,1,1-delta) on the 0.1-spaced full-rank simplex; the completion appends one orthogonal failure flag.` checks `36` states. Affinity residual is `1.11022302462516e-16` and the conditioned-success state residual is `0.0`. The exact block-relative-entropy identity closes to `4.44089209850063e-16`.

Its actual maximum flagged-channel information loss is `0.00221487940630727` nats. The generic bound using the measured normalized-map loss is `0.00351040579342272` nats; the source-residual bound is `0.0104776526605229` nats. The resulting success-conditioned theorem bound is `0.395440322761088`.

#### Noncommuting Kraus / Choi audit

The `Noncommuting full-rank qubit states with a complex-rotated metric M=U diag(1+delta,1-delta) U^dagger and an explicit three-dimensional success/failure Kraus completion.` uses `2` explicit Kraus operators. Kraus-completeness residual is `8.88178419700125e-16`, the minimum Choi eigenvalue is `-1.70461534414143e-16`, and maximum output-trace residual is `4.44089209850063e-16`.

On `5` noncommuting full-rank states, the affine residual is `7.85046229341887e-17`, conditioned-success residual is `3.33066907387547e-16`, and the quantum block-relative-entropy identity closes to `8.04911692853238e-16`. Actual flagged information loss `0.00033921839923523` nats is below the generic domain-diameter bound `0.000849097699699111` nats.

**Proof-device boundary:** The orthogonal flag is an auxiliary channel-completion device, not an asserted physical boundary degree of freedom. The recovery consequence used by the bridge is the restriction of the theorem decoder to the original success block.

#### Isometry budgets after success conditioning (`eta=0`)

These inversions isolate the isometry/domain cost. They are conditional theorem requirements, not estimates of physical `delta_iso`.

| spectral floor | target success trace error | max delta_iso | D_max (nats) | L_K^osc (nats) |
|---:|---:|---:|---:|---:|
| `0.1` | `0.1` | `8.61685738890933e-05` | `1.75777966186898` | `2.19722457733622` |
| `0.1` | `0.01` | `8.67359295483956e-07` | `1.75777966186898` | `2.19722457733622` |
| `0.01` | `0.1` | `3.76108923831638e-05` | `4.5032174531319` | `4.59511985013459` |
| `0.01` | `0.01` | `3.77185679086524e-07` | `4.5032174531319` | `4.59511985013459` |
| `0.001` | `0.1` | `2.48240913264808e-05` | `6.89294126909126` | `6.90675477864855` |
| `0.001` | `0.01` | `2.48709615069398e-07` | `6.89294126909126` | `6.90675477864855` |
| `1e-06` | `0.1` | `1.24107951332553e-05` | `13.8154819269447` | `13.8155095579638` |
| `1e-06` | `0.01` | `1.24225026210123e-07` | `13.8154819269447` | `13.8155095579638` |

## Approximate-normalization spectral stress

If ||M-I||_infinity <= delta_iso < 1 and L_K^osc = sup_{rho,sigma} inf_c ||K_{rho_r}-K_{sigma_r}-cI||_infinity, then the normalized map W obeys epsilon_pair,nats <= 2(eta + delta_iso L_K^osc)/(1-delta_iso). This is not yet a recovery-theorem input because W is generally nonlinear.

| bulk eigenvalue floor | eta (nats) | centered modular oscillation | actual defect | naive eta-only bound | corrected normalized-map bound | naive violated? |
|---:|---:|---:|---:|---:|---:|---:|
| `0.1` | `0.00180162032435638` | `1.09861228866811` | `-0.000298932118103945` | `0.00360684749620896` | `0.00580627149754652` | `false` |
| `0.001` | `0.00199999666533539` | `3.45337738932428` | `-0.00245587506023481` | `0.00400399732799878` | `0.0109176657750944` | `false` |
| `1e-06` | `0.00200199866332994` | `6.90775477898189` | `-0.0059082564438997` | `0.00400800533199186` | `0.0178373442288525` | `true` |
| `1e-12` | `0.00200200066733228` | `13.8155105579638` | `-0.0128160102248831` | `0.00400800934400857` | `0.0316666891397318` | `true` |

**Severe failure:** At fixed delta_iso=1e-3 the projected residual eta stays near 2e-3 nats, but the omitted normalization term grows with centered bulk modular oscillation. The naive residual-only normalized-map bound first fails at lambda_min=1e-6 and worsens as the spectral floor falls.

**Correction:** A finite-N normalized-map claim must budget eta, delta_iso, and L_K^osc together. A recovery claim may pay polar transport chi_out+chi_bulk, or use the explicit flagged channel and pay q_max D_max plus the success-conditioning transfer. Small isometry error alone is neither a state-uniform nor a channel-level guarantee.

## Polar-channel comparison budgets

These legacy comparison rows retain the polar admissible region. The flagged completion above is now the constructive default because it replaces unpriced transport symbols with explicit failure/domain costs.

| target trace/observable error | required pairwise defect (bits) | exact-channel residual budget (nats) | max source eta if polar transport vanishes at delta=1e-3 | max chi_out+chi_bulk if eta=0 |
|---:|---:|---:|---:|---:|
| `0.5` | `0.0247624428633979` | `0.0085820087272705` | `0.00857342671854323` | `0.0085820087272705` |
| `0.25` | `0.00619061071584949` | `0.00214550218181763` | `0.00214335667963581` | `0.00214550218181763` |
| `0.1` | `0.000990497714535918` | `0.000343280349090821` | `0.00034293706874173` | `0.000343280349090821` |
| `0.05` | `0.000247624428633979` | `8.5820087272705e-05` | `8.57342671854323e-05` | `8.5820087272705e-05` |
| `0.01` | `9.90497714535918e-06` | `3.43280349090821e-06` | `3.4293706874173e-06` | `3.43280349090821e-06` |

## Scaling consequence after a valid channel join

A base-2 relative-entropy/JLMS remainder epsilon_R=O(R^-p) guarantees only O(R^-p/2) full-code trace-norm and normalized-observable accuracy through this theorem, while squared-fidelity infidelity remains O(R^-p). When epsilon_R itself inherits the source term sqrt(eps_FLM/eps_tail), recovery introduces a second square root: eps_FLM~G^a and eps_tail~G^t contribute only G^((a-t)/4) trace accuracy before other errors and domain growth.

| Conditional channel-level remainder | defect slope | squared-fidelity infidelity slope | local trace slope | full-code trace/observable slope |
|---|---:|---:|---:|---:|
| `epsilon_R = 0.25 R^(-1)` | `-1.0` | `-0.999216272775454` | `-0.499608136387727` | `-0.5` |
| `epsilon_R = 0.25 R^(-2)` | `-2.0` | `-1.99996021615086` | `-0.999980108075431` | `-1.0` |

**Correction:** Do not transfer a quoted O(1/N) JLMS remainder directly into O(1/N) reconstruction error. Also do not read eps_FLM's power directly as a reconstruction power: Eq. (3.17)'s tail ratio and universal recovery can halve the exponent twice, while D_max or L_K^osc growth can remove convergence altogether.

## Source-tail and growing-domain exponent wedge

Eq. (3.17): `eps_pJLMS = sqrt(eps_FLM/eps_tail) + eps_iso_small |log eps_tail|, up to suppressed O(1) factors`

Conditional transfer: If non-displayed source terms are nonperturbative, eps_iso_small~G^b, D_max~G^-d, and L_K^osc~G^-ell, then the flagged-channel defect power is min((a-t)/2,b,b-d,b-ell) up to logarithms, and the success-conditioned trace guarantee carries half that power.

| scenario | a | t | b | D growth d | L growth ell | flagged-defect power | success-trace power | convergent? |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `open_balanced` | `3.0` | `1.0` | `1.0` | `0.0` | `0.0` | `1.0` | `0.5` | `true` |
| `open_narrow_tail` | `2.0` | `1.5` | `1.0` | `0.0` | `0.0` | `0.25` | `0.125` | `true` |
| `closed_at_tail_boundary` | `1.0` | `1.0` | `1.0` | `0.0` | `0.0` | `0.0` | `0.0` | `false` |
| `domain_growth_erases_isometry_gain` | `3.0` | `1.0` | `1.0` | `1.0` | `0.0` | `0.0` | `0.0` | `false` |
| `open_with_controlled_domain_growth` | `4.0` | `1.0` | `2.0` | `0.5` | `0.5` | `1.5` | `0.75` | `true` |

**Severe failure:** Choosing eps_tail to vanish at least as fast as eps_FLM closes the displayed source ratio: for eps_FLM~G^a and eps_tail~G^t, a<=t gives no vanishing sqrt(eps_FLM/eps_tail). Even when a>t, growth of the same-domain relative-entropy diameter or modular oscillation can erase the delta_iso gain before recovery.

The synthetic `eps_FLM=G^2`, `eps_tail=G`, `eps_iso_small=G` transfer fits slopes `0.500000019763835` for `eps_pJLMS`, `0.500000056210865` for the flagged defect, and `0.250000028105473` for success-conditioned trace error. This is the executable double-square-root loss `G^(1/2) -> G^(1/4)`, not a physical fit.

## Exact reconstructed-algebra geometry

The JLMS comparison uses reduced bulk-wedge states. For the full-rank domain `rho >= lambda I` in dimension `d`, the benchmark now computes the exact domain taxes rather than inserting an ad hoc `-log lambda` upper bound:

- `D_max=(1-d lambda) log(a/lambda)`
- `L_K^osc=log(a/lambda)`

| dimension | floor | maximum eigenvalue | exact D_max (nats) | extremizer replay | exact L_K^osc (nats) | extremizer replay |
|---:|---:|---:|---:|---:|---:|---:|
| `2` | `0.1` | `0.9` | `1.75777966186898` | `1.75777966186898` | `2.19722457733622` | `2.19722457733622` |
| `3` | `0.0666666666666667` | `0.866666666666667` | `2.05195948596923` | `2.05195948596923` | `2.56494935746154` | `2.56494935746154` |
| `5` | `0.04` | `0.84` | `2.43561795017874` | `2.43561795017874` | `3.04452243772342` | `3.04452243772342` |
| `8` | `0.025` | `0.825` | `2.79720604917318` | `2.79720604917318` | `3.49650756146648` | `3.49650756146648` |

Formula residuals: relative entropy `4.44089209850063e-16`; centered modular oscillation `4.44089209850063e-16`.

## Direct-sum sector-proliferation negative control

The reduced bulk-wedge algebra is restricted to the classical center of K direct-sum sectors. Every admissible sector weight obeys p_alpha >= mu/K with fixed total floor mass mu=0.1; internal sector states may be identical, so this is already a lower-complexity subdomain of the large code.

At fixed total sector floor mass `mu=0.1`, both exact domain taxes grow as `Theta(log K)`. A within-sector `eps_tail` therefore does not control the classical center of the large direct sum.

| scenario | sector law | final source eta | final D_max | final flagged defect | defect slope vs G | final success trace | trace slope vs G |
|---|---|---:|---:|---:|---:|---:|---:|
| `exponential_sectors_power_matched_isometry` | `K=2^m with G=(m ln 2)^-1, hence log K=G^-1 exactly` | `0.00350503508516431` | `2557.19526853578` | `3.81002435893021` | `0.010781965030059` | `7.45611230933413` | `0.0100101672817929` |
| `polynomial_sectors_power_matched_isometry` | `K=ceil(G^-2)` | `0.00350503508516431` | `16.2897579759097` | `0.0312383561524609` | `0.871995360155367` | `0.676419913974062` | `0.442423615112984` |
| `exponential_sectors_stronger_isometry` | `K=2^m with G=(m ln 2)^-1, hence log K=G^-1 exactly` | `1.23454510144248e-06` | `2557.19526853578` | `0.00134194270866183` | `1.01064059358845` | `0.139807080696191` | `0.505414273495532` |

### Power-matched exponential-sector replay

| G | K | source eta | exact D_max | exact L_K^osc | flagged defect | success trace bound |
|---:|---:|---:|---:|---:|---:|---:|
| `0.0901684400555602` | `2^16` | `0.397288981802064` | `11.9588230455434` | `13.2875811617149` | `5.48528539537109` | `11.1064991000311` |
| `0.00563552750347251` | `2^256` | `0.040455561362629` | `161.678612520614` | `179.642902800682` | `3.92968653931325` | `7.67395689042848` |
| `0.000352220468967032` | `2^4096` | `0.00350503508516431` | `2557.19526853578` | `2841.32807615087` | `3.81002435893021` | `7.45611230933413` |

**Severe failure:** In the exponential-sector, power-matched cell every displayed local source quantity tends to zero: eps_FLM~G^3, eps_tail~G, eps_iso_small=delta_iso~G, and eta~G|log G|. Nevertheless log K=1/G makes delta_iso D_max and delta_iso L_K^osc order one. The executable flagged defect and success-conditioned recovery bound plateau instead of converging. Sector-local log stability therefore cannot certify whole-large-code recovery.

**Correction:** Declare and prove the sector-weight geometry on the same reconstructed algebra as the JLMS comparison. For K~exp(c/G^gamma) and delta_iso~G^b, this bridge needs b>gamma (plus a>t and uniform residual control); b=gamma is only order-one. A direct bound on D_max and L_K^osc may replace an explicit K law, but a within-sector epsilon_tail cannot.

**Authority boundary:** The K(G) schedules are adversarial theorem test vectors, not claims about the physical CFT sector count. They show which additional scaling theorem is necessary before the source envelope can carry recovery authority.

## Source-grounded full-system FLM isometry closure

delta_iso <= 2 sqrt(eps_FLM) + eps_OD; this requires a full-system FLM premise and cannot be inferred from a subregion estimate alone.

For eps_FLM~G^a, eps_tail~G^t, K~exp(c/G^gamma), and nonperturbative eps_OD plus remaining Theorem-5 terms, this flagged sufficient route requires a>max(t,2 gamma). Its success-trace power is min((a-t)/4, a/4-gamma/2), up to logarithms.

| scenario | a | t | gamma | derived b=a/2 | defect power | fitted defect slope | trace power | fitted trace slope | convergent? |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `full_system_FLM_critical_a_equals_2gamma` | `2.0` | `1.0` | `1.0` | `1.0` | `0.0` | `0.0150964491417954` | `0.0` | `0.0162044093600203` | `false` |
| `full_system_FLM_open_a_3` | `3.0` | `1.0` | `1.0` | `1.5` | `0.5` | `0.514760773167871` | `0.25` | `0.25831366319184` | `true` |
| `full_system_FLM_open_a_5` | `5.0` | `1.0` | `1.0` | `2.5` | `1.5` | `1.51473677855696` | `0.75` | `0.757399379326325` | `true` |

**Correction to the prior stress:** The rev0373 b=gamma plateau remains a valid independent-isometry stress, but it is not the strongest source-closed branch when full-system FLM is available. Appendix C ties b to a/2 and can reopen the wedge when a>2 gamma.

**Authority boundary:** The schedule uses unit coefficients, a synthetic exp(-1/G) eps_OD, and zero for other nonperturbative source terms. It proves exponent bookkeeping only, not a physical CFT remainder.

## Sector-transport log-smoothness audit

For q=T p on the classical sector center, epsilon_l_smooth=max_alpha |log(q_alpha/p_alpha)| exactly.

If zeta=max_alpha |(T p)_alpha/p_alpha-1|<1, then epsilon_l_smooth <= -log(1-zeta). The dimension-free quantity is relative incoming flux, not total trace leakage.

| radius L | sectors | symmetric leakage | total variation | symmetric eps_l-smooth (nats) | p-stationary eps_l-smooth (nats) |
|---:|---:|---:|---:|---:|---:|
| `8` | `17` | `1e-08` | `9.32049732739685e-10` | `9.54276796003527e-08` | `6.51708017329921e-16` |
| `16` | `33` | `1e-08` | `9.32049683612079e-10` | `2.45874218596373e-06` | `3.3432198613215e-15` |
| `32` | `65` | `1e-08` | `9.32049683612079e-10` | `0.00148168958212605` | `1.28660870010686e-14` |
| `64` | `129` | `1e-08` | `9.32049683612079e-10` | `6.28803221777467` | `5.28341159719467e-14` |
| `128` | `257` | `1e-08` | `9.32049683612079e-10` | `31.8861720754876` | `5.28341159719467e-14` |
| `256` | `513` | `1e-08` | `9.32049683612079e-10` | `83.0861720754892` | `4.01913234914517e-13` |

The bad-tail fitted slope is `0.39999169579337` nats per radius against the exact asymptotic prediction `0.4`.

**Severe failure:** A fixed, tiny nearest-neighbor trace leakage can leave total variation near zero while operator-log error diverges in Gaussian tails. Gaussian sector weights plus distance-only decay therefore do not, by themselves, certify global log-smoothness.

**Constructive completion:** Require a p-weighted incoming-flux or approximate-stationarity theorem. Exact detailed balance is stronger than necessary but makes the commuting log-smoothness tax identically zero at any sector count.

## Direct-sum operator-algebra center/factor audit

A = direct_sum_{alpha=1}^K M_2; its center is the commutative algebra generated by sector projectors, while each M_2 factor is noncommutative.

**Terminology correction:** A center is commutative by definition. The unpaid quantum debt is noncommuting factor-block and edge-mode transport, not a 'noncommuting center'.

| full relative entropy | center contribution | weighted factor contribution | decomposition residual | factor commutator trace norms |
|---:|---:|---:|---:|---|
| `0.580897564238039` | `0.261036783715283` | `0.319860780522755` | `2.22044604925031e-16` | `[0.198305320150519, 0.173168992605489, 0.10470195795686]` |

D(direct_sum q_alpha sigma_alpha || direct_sum p_alpha rho_alpha) = D(q||p) + sum_alpha q_alpha D(sigma_alpha||rho_alpha).

| domain tax | center | factor | full predicted | full observed | residual | center-only fraction |
|---|---:|---:|---:|---:|---:|---:|
| relative-entropy diameter | `2.26657067524497` | `2.6499950812498` | `4.91656575649477` | `4.91656575649477` | `8.88178419700125e-16` | `0.46100688722628` |
| centered modular oscillation | `2.83321334405622` | `2.94443897916644` | `5.77765232322266` | `5.77765232322266` | `0.0` | `0.490374495652571` |

**Correction:** A p-stationary sector kernel can remove the commutative center tax while leaving the within-sector noncommuting modular contribution untouched. The recovery budget must price both on the identical reconstructed algebra.

## Noncommuting modular-frame stress

One full-rank qubit factor with eigenvalue floor lambda(G)=exp(-1/G); the state is conjugated by a real basis rotation.

| G | adversarial state trace error (theta=G) | adversarial operator-log error | repaired state error (theta=G^2) | repaired operator-log error |
|---:|---:|---:|---:|---:|
| `0.125` | `0.249182171915678` | `0.997356036351411` | `0.031227762888638` | `0.124989671529443` |
| `0.03125` | `0.0624898279706506` | `0.999837247530434` | `0.00195312468955911` | `0.0312499950329465` |
| `0.00390625` | `0.00781248013180023` | `0.99999745687043` | `3.05175781238158e-05` | `0.00390624999984842` |

Fitted last-six slopes: `{'adversarial_state_trace_vs_G': 0.999961179752731, 'adversarial_operator_log_vs_G': -3.882024726763e-05, 'repaired_state_trace_vs_G': 1.99999998444313, 'repaired_operator_log_vs_G': 0.999999984443134}`.

**Severe failure:** With theta=G and lambda=exp(-1/G), the trace-norm state perturbation vanishes linearly while the operator-log error tends to one nat. Exact sector-weight stationarity does not touch this within-factor failure.

**Constructive control:** In the declared theta=G^2 schedule, the operator-log error falls as G. More generally, a same-domain proof needs a modular-frame/eigenbasis transport bound weighted by the within-sector log condition number, not only sector inflow or trace leakage.

## Fixed-region direct-sum decoder gluing

Two direct-sum logical sectors share one fixed boundary carrier. An orthogonal sector tag and sector-conditioned logical frames are both contained in that carrier; a fixed environment is discarded.

The source-specific correction is load-bearing: REF-0735 already fixes one boundary-region pair across sectors and its wedge state is block diagonal in the direct-sum algebra. The relevant debt is therefore one fixed-region CPTP decoder with worst-sector control—not an invented region switch or an automatic demand for off-diagonal sector coherence.

| exact fixed-region check | direct-sum algebra | full-subspace algebra / coherent target |
|---|---:|---:|
| OAQEC commutant residual | `1.8882991164529e-18` | `1.8882991164529e-18` |
| Kraus completeness residual | `1.8882991164529e-18` | `1.8882991164529e-18` |

| one fixed-region decoder test | result |
|---|---:|
| coherent controlled-decoder full-state error | `1.90290181794592e-16` |
| algebra decoder block-state error | `2.08166817117217e-17` |
| direct-sum algebra expectation residual | `1.11022302462516e-16` |
| algebra-decoder cross-sector coherence error | `1.0` |

The dephasing decoder is exact for the direct-sum operator algebra even though it is not full-Hilbert recovery. The coherent controlled decoder shows that full coherence is also recoverable when the sector tag itself is coherently available on the same carrier.

### Approximate sector-instrument budget

epsilon_common <= epsilon_local + mu_nondemolition + 2 p_max for block-diagonal target states

| worst-sector confusion p | state trace error | center-observable error | gluing bound |
|---:|---:|---:|---:|
| `0.2` | `0.4` | `0.4` | `0.4` |
| `0.02` | `0.04` | `0.04` | `0.04` |
| `0.001` | `0.002` | `0.002` | `0.002` |

Fitted confusion-error slope: `1.0`.

### REF-0735 Condition-2 routing translation

For every sector alpha and every state in that sector, hat rho_R^alpha = hat rho_Ralpha^alpha + hat rho_R,sub^alpha with ||hat rho_R,sub^alpha||_1 <= epsilon_sub-tr, using one alpha-independent epsilon_sub-tr.

On the sector-diagonal/direct-sum state domain, if each dominant block has one sector decoder with trace-norm error epsilon_block, the projective block instrument followed by those decoders obeys epsilon_common <= epsilon_block + 2 epsilon_sub-tr/(1-epsilon_iso,small).

If a sector decoder is certified only on the normalized full sector output, transporting that certificate to the dominant block and then routing gives the looser sufficient bound epsilon_common <= epsilon_full + 4 epsilon_sub-tr/(1-epsilon_iso,small).

| epsilon_sub-tr | normalized wrong-block probability | common-decoder error | sharp bound |
|---:|---:|---:|---:|
| `0.2` | `0.2002002002002` | `0.4004004004004` | `0.4004004004004` |
| `0.02` | `0.02002002002002` | `0.0400400400400399` | `0.04004004004004` |
| `0.001` | `0.001001001001001` | `0.00200200200200187` | `0.002002002002002` |

Fitted source-routing slope: `1.00000000000001`.

The target inversion is operational: a decoder certified on the dominant block buys twice the source `epsilon_sub-tr` budget of a certificate stated only on the full sector output under this conservative transport chain.

| target common-decoder error | epsilon_sub-tr max, dominant-block certificate | epsilon_sub-tr max, full-sector certificate |
|---:|---:|---:|
| `0.1` | `0.04995` | `0.024975` |
| `0.05` | `0.024975` | `0.0124875` |
| `0.01` | `0.004995` | `0.0024975` |

### Coherent-sector completion split

Here epsilon_sub-tr=r, but the block-instrument error is 2 sqrt(r(1-r)); the source's separate epsilon_OD for the coherent input is exactly the same quantity. Substituting epsilon_sub-tr alone as a linear whole-code coherent bound loses a square root.

| wrong mass r | epsilon_sub-tr | epsilon_OD | block-instrument center error |
|---:|---:|---:|---:|
| `0.1` | `0.1` | `0.6` | `0.6` |
| `0.01` | `0.01` | `0.198997487421324` | `0.198997487421324` |
| `0.0005` | `0.0005` | `0.0447101778122163` | `0.0447101778122164` |

Here epsilon_OD is zero because the complement carries no sector record, while Condition 2's full trace-norm subleading term already includes the carrier coherence and upper-bounds the block-instrument error. The two source errors have distinct, non-interchangeable roles.

| wrong mass r | epsilon_sub-tr | epsilon_OD | block-instrument center error |
|---:|---:|---:|---:|
| `0.1` | `0.608276253029822` | `0.0` | `0.6` |
| `0.01` | `0.199248588451713` | `0.0` | `0.198997487421324` |
| `0.0005` | `0.0447129735088151` | `0.0` | `0.0447101778122164` |

Fitted coherent-routing slopes: `{'environment_tagged_coherent_error_vs_epsilon_sub_tr': 0.491831843689103, 'environment_tagged_coherent_error_vs_epsilon_OD': 0.999999999999999, 'carrier_frame_coherent_error_vs_epsilon_sub_tr': 0.995751044434811}`.

**Remaining theorem join:** A whole-code algebra decoder needs a uniform bound on coherent off-diagonal contamination after the chosen fixed-region block instrument, derived from the same-domain epsilon_OD, epsilon_sub-tr, approximate-isometry, and sector-support assumptions. The present cells do not assert a universal sum rule between those parameters.

**Rare-sector failure:** One bad sector makes the reference-mixture average epsilon_sub-tr and average decoder error fall as 1/K while the worst-sector common-decoder error remains 0.2. Definition 7's alpha-independent bound must remain a supremum, not a sector average.

| K sectors | average epsilon_sub-tr | average decoder error | worst-sector decoder error |
|---:|---:|---:|---:|
| `2` | `0.05` | `0.1` | `0.2` |
| `16` | `0.00625` | `0.0125` | `0.2` |
| `256` | `0.000390625` | `0.00078125` | `0.2` |
| `4096` | `2.44140625e-05` | `4.8828125e-05` | `0.2` |

## Reference-stable OAQEC completion

Whole-code operator-algebra recovery is now measured in the complementary-channel diamond norm rather than an unassisted state trace norm. For target algebra `A`, define `delta_A=||Nhat-Nhat o P_{A'}||_diamond` and optimal reconstruction error `E_A=min_R ||R o N-P_A||_diamond`. REF-0736 gives `delta_A^2/4 <= E_A <= 2 sqrt(delta_A)`.

The sufficient target inversion is therefore `delta_A<=tau^2/4`. If only a state-uniform defect `epsilon_state` is known on a `d_code`-dimensional input, the generic finite-dimensional lift used here is `delta_A<=d_code epsilon_state`; the dimension cannot be silently dropped.

| target OAQEC error tau | d_code | max delta_A | max state-only defect under generic lift |
|---:|---:|---:|---:|
| `0.1` | `16` | `0.0025` | `0.00015625` |
| `0.1` | `256` | `0.0025` | `9.765625e-06` |
| `0.1` | `4096` | `0.0025` | `6.103515625e-07` |
| `0.01` | `16` | `2.5e-05` | `1.5625e-06` |
| `0.01` | `256` | `2.5e-05` | `9.765625e-08` |
| `0.01` | `4096` | `2.5e-05` | `6.103515625e-09` |

### Severe reference-amplification control

Let Nhat_d(rho)=(Tr(rho) I + rho^T)/(d+1), a transpose-depolarizing channel, and let A be the diagonal algebra so P_{A'} is basis dephasing. Then Delta_d=Nhat_d-Nhat_d o P_{A'}=(rho^T-diag(rho))/(d+1).

Its state-level off-diagonal envelope vanishes as `1/d`, but the exact reference-assisted diamond defect tends to one. The Choi Jordan decomposition independently proves the exact value; this is not a numerical SDP guess.

| d_code | state envelope | coherent-state witness | exact diamond defect | minimum recovery-error lower bound | diamond/state ratio |
|---:|---:|---:|---:|---:|---:|
| `2` | `0.666666666666667` | `0.333333333333333` | `0.333333333333333` | `0.0277777777777778` | `0.5` |
| `16` | `0.117647058823529` | `0.110294117647059` | `0.882352941176471` | `0.194636678200692` | `7.5` |
| `256` | `0.00778210116731518` | `0.00775170233463035` | `0.992217898832685` | `0.246124089690987` | `127.5` |
| `4096` | `0.000488162069807176` | `0.000488042889614352` | `0.999511837930193` | `0.249755978540648` | `2047.5` |

Fitted tail slopes: `{'state_envelope_vs_dimension': -0.997984484243517, 'coherent_state_witness_vs_dimension': -0.995954425726877, 'diamond_defect_vs_dimension': 0.00404557427312274, 'reconstruction_lower_bound_vs_dimension': 0.00809114854624619}`.

Maximum Choi exact-formula residual: `1.11022302462516e-16`.

**Severe failure:** The uniform state-level envelope falls as 1/d, yet the exact complementary-channel diamond defect tends to one and Bény's minimum reconstruction-error lower bound tends to 1/4. Reference amplification therefore blocks whole-code OAQEC convergence.

### Positive common-decoder control

d-dimensional erasure channel with receiver output (1-p)rho plus an orthogonal erasure flag; the complement receives rho only on erasure.

For the full matrix algebra, delta_A = E_A = 2 p (1-1/d^2) when the erasure decoder replaces the lost input by I/d.

| d_code | erasure probability | exact complementary defect | exact decoder error | theorem sufficient upper bound |
|---:|---:|---:|---:|---:|
| `2` | `0.1` | `0.15` | `0.15` | `0.774596669241483` |
| `2` | `0.01` | `0.015` | `0.015` | `0.244948974278318` |
| `2` | `0.001` | `0.0015` | `0.0015` | `0.0774596669241483` |
| `16` | `0.1` | `0.19921875` | `0.19921875` | `0.892678553567856` |
| `16` | `0.01` | `0.019921875` | `0.019921875` | `0.282289744765905` |
| `16` | `0.001` | `0.0019921875` | `0.0019921875` | `0.0892678553567856` |

### Nonperturbative rate wedge

d_code(G)=exp(s/G) and epsilon_state(G)=exp(-c/G); the generic reference-stable lift is bounded by exp((s-c)/G), capped at the channel maximum 2.

| scenario | c | final state-only error | final generic diamond bound | outcome |
|---|---:|---:|---:|---|
| `insufficient_state_rate` | `0.75` | `1.42516408274094e-21` | `2.0` | `vacuous` |
| `critical_rate_plateau` | `1.0` | `1.60381089054864e-28` | `1.0` | `plateau` |
| `reference_stable_rate` | `1.25` | `1.80485138784542e-35` | `1.12535174719259e-07` | `convergent` |

**Correction:** This generic route requires c>s. Calling epsilon_OD merely 'nonperturbatively small' is insufficient when the large-code/reference dimension also grows nonperturbatively.

**Source join:** Either derive delta_A directly in complementary-channel diamond norm on the same fixed region and target algebra, or provide an explicit d_code/reference law and a state-to-diamond theorem whose rate clears d_code epsilon_OD -> 0 together with the other normalization, routing, center, and factor errors.

### Hidden-sector frame negative control

The sector label is discarded while the same logical qubit is emitted in two unitary frames separated by theta. Sector-conditioned decoders are exact, but two distinct logical inputs can produce the identical carrier record.

| frame separation | identical-output residual | common-decoder lower bound | midpoint upper bound |
|---:|---:|---:|---:|
| `1.0` | `1.11886302282795e-16` | `0.479425538604203` | `0.494807918509046` |
| `0.125` | `2.22152998685417e-16` | `0.0624593178423802` | `0.0624898279706522` |
| `0.03125` | `1.11194963130561e-16` | `0.0156243642248834` | `0.0156248410547657` |

Fitted small-angle slopes: `{'minimax_lower_bound_vs_frame_separation': 0.989996948566669, 'midpoint_upper_bound_vs_frame_separation': 0.997513442028839}`.

**Correction:** A direct-sum algebra target must not be failed merely because a valid algebra decoder removes off-diagonal sector coherence. The actual gluing debts are a fixed carrier, one CPTP instrument, uniform sector-local decoder errors, nondemolition sector routing, and a worst-sector—not average—confusion bound. Full-Hilbert coherence is a separate stronger target.

## Generic state-dependent-wedge negative control

Generic two-sector comparator: sector 0 stores the logical qubit in A and sector 1 stores it in B; C is an orthogonal sector flag.

This is not the geometry assumed by REF-0735 Definition 6, which fixes the same boundary-region pair for every small-code sector. It remains a negative control for later state-dependent-wedge extrapolations.

| test | result |
|---|---:|
| maximum sector-local reconstruction error | `0.0` |
| fixed AC output distance for sector-1 orthogonal pair | `0.0` |
| fixed BC output distance for sector-0 orthogonal pair | `0.0` |
| exact fixed-region pair minimax recovery-error lower bound | `1.0` |
| adaptive block-algebra error | `0.0` |
| adaptive cross-sector coherence error | `1.0` |
| fixed full-union coherent-state decoder error | `0.0` |
| AC direct-sum OAQEC commutant residual | `1.0` |
| BC direct-sum OAQEC commutant residual | `1.0` |
| ABC direct-sum OAQEC commutant residual | `0.0` |

**Fixed-region obstruction:** Each fixed region maps one orthogonal logical pair to the same record. The OAQEC commutant residual is also one on AC and BC, while it vanishes on ABC.

**Target split:** External sector-dependent routing recovers the direct-sum blocks but is not one fixed-subregion channel. Its coherence loss matters only if full-Hilbert recovery, rather than the direct-sum algebra, is the declared target.

**Correction:** Keep this comparator quarantined from source-specific debts. For a fixed-region direct-sum construction, apply the OAQEC commutant criterion and an explicit common decoder before charging cross-sector coherence as a missing observable.

## Rare-sector quantifier negative control

A classical direct-sum code has K labeled sectors. K-1 sectors transmit a logical bit exactly; one rare sector replaces it by the uniform bit. The sector label is retained. The reference mixture is uniform over sectors.

| K sectors | reference-mixture defect | actual mixture error | bad-sector defect | actual worst-case error | invalid whole-code bound |
|---:|---:|---:|---:|---:|---:|
| `2` | `0.5` | `0.5` | `1.0` | `1.0` | `2.24676817353079` |
| `4` | `0.25` | `0.25` | `1.0` | `1.0` | `1.58870501125774` |
| `8` | `0.125` | `0.125` | `1.0` | `1.0` | `1.1233840867654` |
| `16` | `0.0625` | `0.0625` | `1.0` | `1.0` | `0.794352505628869` |
| `64` | `0.015625` | `0.015625` | `1.0` | `1.0` | `0.397176252814434` |
| `256` | `0.00390625` | `0.00390625` | `1.0` | `1.0` | `0.198588126407217` |
| `1024` | `0.0009765625` | `0.0009765625` | `1.0` | `1.0` | `0.0992940632036086` |
| `4096` | `0.000244140625` | `0.000244140625` | `1.0` | `1.0` | `0.0496470316018043` |

**Severe failure:** The uniform reference mixture reports a base-2 defect 1/K and genuine state-specific recovery error 1/K, but a declared bad-sector probe witnesses a 1-bit defect and the channel has minimax trace-norm recovery error 1 on deterministic bit inputs. Thus any whole-domain uniform defect is at least 1 bit. Feeding the reference-mixture defect into the whole-code theorem produces a purported upper bound below the actual worst-case starting at K=16; the contradiction identifies a quantifier violation, not a theorem failure.

**Correction:** Every finite-N/JLMS remainder entering a recovery claim must state its quantifier: supremum over a declared domain, state-class bound, weighted average, sample estimate, or single-reference result. Only the first supports a whole-domain universal-recovery guarantee without an additional concentration or coverage theorem.

## What is now completed—and what remains

- Completed: A direct algebraic join from a uniform projected-JLMS operator-norm residual to the all-pairs relative-entropy defect of the source's normalized map: 2 eta for exact isometry and 2(eta+delta_iso L_K^osc)/(1-delta_iso) for controlled approximate normalization.
- Completed: A channel-premise audit proving that the normalized non-isometric source map is non-affine, so its pairwise bound cannot be spent directly in a universal-recovery theorem.
- Completed: A constructive CPTP flagged completion that preserves the source normalized state exactly on success and replaces free polar-transport symbols by an explicit failure budget q_max D_max; both diagonal and noncommuting Kraus/Choi probes now replay the construction.
- Completed: A decoder-transfer inequality from the auxiliary flagged channel back to one decoder on the original normalized success states: T_success <= [(1+delta_iso)T_flag+4 delta_iso]/(1-delta_iso).
- Completed: An exact finite-dimensional formula for the reduced reconstructed-algebra relative-entropy diameter and centered modular oscillation under a spectral floor, verified on explicit extremizers.
- Completed: An executable direct-sum sector-growth stress showing that exponentially proliferating sector weights can keep the recovery budget order one even while every displayed local source remainder vanishes.
- Completed: A source-grounded optional closure using Appendix C and Lemma 4: full-system FLM gives eps_iso,small <= 2 sqrt(eps_FLM), so the exponential-sector sufficient wedge sharpens to a>max(t,2 gamma) when the other source terms are nonperturbative.
- Completed: An exact classical-center log-smoothness identity and transport stress: fixed 1e-8 nearest-neighbor leakage yields more than 80 nats of operator-log error in Gaussian tails, while p-stationary detailed balance removes the center tax at the same sector count.
- Completed: An exact direct-sum operator-algebra decomposition showing that D_max and L_K^osc contain additive commutative-center and noncommuting factor-block debts; in the declared product cell the center alone pays less than half of either total.
- Completed: A noncommuting modular-frame stress where trace-norm state error vanishes as G but operator-log error remains one nat, plus a G^2 rotation control that restores convergence.
- Completed: An exact fixed-region OAQEC gluing cell: orthogonal sector tags plus sector-conditioned frames admit one common direct-sum algebra decoder with zero commutant residual; algebraic dephasing has unit full-state coherence error but zero algebra-observable error. A worst-sector confusion channel saturates the 2 p_max trace-norm budget, while hiding the sector tag creates a linear frame-mismatch obstruction.
- Completed: A source-conditioned routing sublemma from REF-0735 Definition 7: on sector-diagonal/direct-sum inputs, epsilon_common <= epsilon_block + 2 epsilon_sub-tr/(1-epsilon_iso,small), with an owned family that exactly saturates the bound and an inverted target budget. A decoder certified only on the full sector output pays the looser 4 epsilon_sub-tr/(1-epsilon_iso,small) transport chain.
- Completed: Two exact-isometry coherent-sector cells separating the source roles: an environment-tagged cell where the block-instrument error scales as sqrt(epsilon_sub-tr) but equals epsilon_OD, and a carrier-frame cell where epsilon_OD=0 while the full Condition-2 trace-norm term itself pays the coherent bias. A rare-sector cell keeps the alpha-independent supremum distinct from a vanishing 1/K average.
- Completed: A reference-stable OAQEC completion using REF-0736: delta_A=||Nhat-Nhat o P_{A'}||_diamond obeys delta_A^2/4<=E_A<=2 sqrt(delta_A), with target inversion delta_A<=tau^2/4 and the generic state-to-diamond lift delta_A<=d_code epsilon_state. A transpose-dephasing channel family makes epsilon_state fall as 1/d while delta_A tends to one and E_A stays at least 1/4; an erasure-channel control gives an exact common decoder with delta_A=E_A=2p(1-1/d^2).
- Completed: A generic state-dependent-wedge comparator whose OAQEC commutant residual is one on either sector-local region and zero on the union; it is now explicitly quarantined from REF-0735, which fixes the same boundary region across sectors.
- Completed: An executable source-tail wedge from Eqs. (3.17) and (4.24), exposing the conditional double-square-root exponent loss and the possibility that state-domain growth destroys convergence.
- Completed: Rare-sector, spectral-floor, and sector-proliferation counterexamples separating state averages, small source residuals, approximate normalization, and uncontrolled domains from whole-domain recovery.
- Source conditioning: Theorem 5 is a direct recovery bridge only when V^dagger V is scalar on the declared code domain. Otherwise it controls a nonlinear normalized map. The flagged completion supplies a genuine theorem channel and a decoder on the original success outputs after restriction, but no physical CFT flag is asserted. Full-system FLM can pay the isometry exponent through Appendix C and Lemma 4; subregion FLM alone cannot. REF-0735 fixes one boundary-region pair and a direct-sum reduced wedge algebra. Condition 2 pays a sharp worst-sector sector-diagonal routing budget, while Condition 1 epsilon_OD and the full Condition-2 trace term have distinct coherent-sector roles. Neither state-level parameter is yet the REF-0736 complementary-channel diamond defect: whole-code authority requires a direct cb/diamond estimate or an explicit code/reference dimension law strong enough to pay d_code epsilon_state, on the same channel, region, target algebra, and state domain as the center/factor and decoder budgets.
- Still missing: Derive physical scaling laws and hidden constants for full-system and subregion eps_FLM, eps_tail, eps_OD, eps_enhanced, eps_sub_log, and the resulting eta on one identical region/state domain; verify that the Appendix-C full-system premise actually holds with the needed error.
- Still missing: Prove that every reference state in that domain satisfies enhanced log-stability and log-smoothness with uniform source parameters; one preferred reference state is insufficient.
- Still missing: Derive the same-domain sector-count/sector-weight law, or direct D_max and L_K^osc bounds, for the reduced bulk-wedge/reconstructed algebra. Under the full-system FLM branch and K~exp(c/G^gamma), this sufficient route requires eps_FLM=o(G^(2 gamma)).
- Still missing: Derive a sector-confusion/overlap kernel or equivalent weighted-inflow bound proving max_alpha |(T p)_alpha/p_alpha-1| is uniformly small. Unweighted eps_sub_tr, a Gaussian p_alpha, and distance-only decay are insufficient.
- Still missing: Derive within-sector factor dimension/spectral-floor laws and a noncommuting modular-frame transport bound strong enough that eigenbasis rotation times the factor log-condition number vanishes uniformly.
- Still missing: Derive physical same-domain scaling for the alpha-independent epsilon_sub-tr and epsilon_iso,small that clears the new sector-diagonal target inversion, and certify the sector decoders on the normalized dominant blocks rather than only on full sector outputs.
- Still missing: Derive a same-domain complementary-channel defect Delta=Nhat-Nhat o P_{A'} from epsilon_OD, epsilon_sub-tr, approximate isometry, and sector-support data, and control it in diamond/cb norm with an external reference. The owned cells show that the two source errors are not interchangeable, while the new channel family shows that even a uniform unassisted state error can vanish as 1/d_code with order-one diamond defect.
- Still missing: Provide the physical code/reference dimension or a dimension-free complete-boundedness theorem. Under only the generic lift, a target OAQEC error tau requires epsilon_state<=tau^2/(4 d_code); for d_code~exp(s/G^gamma) and epsilon_state~exp(-c/G^gamma), the sufficient reference-stable wedge needs c>s.
- Still missing: Stress backreaction, non-AdS transport, and local-observer records after the algebra and fixed-region debts close.

## Resource-identity audit

Owned toy resource: `prime logical/local dimension D in FAMILYC-APPROXIMATE-RECOVERY-SCALING-BENCHMARK.json`. Conditional theorem resource: `abstract resource R used only to expose theorem exponents and target budgets`. Physical variables: `G, CFT N/central charge, area-window width, code-subspace/state-class data, and source-specific error parameters`. Identity status: **unmapped**.

## Acceptance checks

| Check | Passed | Detail |
|---|---:|---|
| inverse_resource_remainder preserves the declared relative-entropy exponent | `true` | -1.0 |
| inverse_resource_remainder recovery trace guarantees carry the square-root exponent | `true` | {'local': -0.499608136387727, 'full_code': -0.5} |
| inverse_resource_remainder squared-fidelity infidelity retains the remainder exponent | `true` | -0.999216272775454 |
| inverse_square_resource_remainder preserves the declared relative-entropy exponent | `true` | -2.0 |
| inverse_square_resource_remainder recovery trace guarantees carry the square-root exponent | `true` | {'local': -0.999980108075431, 'full_code': -1.0} |
| inverse_square_resource_remainder squared-fidelity infidelity retains the remainder exponent | `true` | -1.99996021615086 |
| budget inversion exactly saturates the full-code theorem constant | `true` | 3.17741002251547 |
| rare-sector reference mixture defect and its actual state-specific error both converge as K^-1 | `true` | {'reference_mixture_defect_bits': -1.0, 'actual_reference_mixture_error': -1.0, 'invalid_laundered_uniform_bound': -0.5} |
| laundered reference-mixture bound only falls as K^-1/2 | `true` | -0.5 |
| rare-sector worst-case defect and recovery error remain order one | `true` | {'relative_entropy_defect_lower_bound_bits': 1.0, 'trace_norm_error': 1.0} |
| average-to-uniform laundering becomes numerically self-contradictory | `true` | {'sector_count': 16, 'bad_sector_weight_in_uniform_reference_mixture': 0.0625, 'reference_mixture_relative_entropy_defect_bits': 0.0625, 'bad_sector_probe_relative_entropy_defect': 1.0, 'whole_domain_uniform_defect_lower_bound_from_probe': 1.0, 'actual_reference_mixture_recovery_trace_norm_error': 0.0625, 'actual_worst_case_recovery_trace_norm_error': 1.0, 'invalid_uniform_bound_if_reference_mixture_defect_is_laundered': 0.794352505628869, 'invalid_bound_below_actual_worst_case': True} |
| nats-to-bits conversion preserves the recovery fidelity exponent | `true` | {'defect_nats': 0.1, 'defect_bits': 0.144269504088896, 'fidelity_from_bits': 0.951229424500714, 'fidelity_from_nats': 0.951229424500714} |
| large-code source envelopes remain norm- and quantifier-separated from epsilon_R | `true` | ['Dong-Marolf-Rath Theorem 3, Eq. (4.50)', 'Dong-Marolf-Rath Theorem 5, Eq. (4.85)', 'Dong-Marolf-Rath Theorem 6, Eq. (4.88)'] |
| non-isometric normalized source map fails the quantum-channel affinity premise | `true` | {'model': 'Two-level normalized filter with M=diag(1+delta,1-delta); its polar isometry is U=I.', 'delta_isometry': 0.001, 'convex_domain_states': {'rho_0': [1.0, 0.0], 'rho_1': [0.0, 1.0], 'midpoint': [0.5, 0.5]}, 'normalized_filter_midpoint': [0.5005, 0.4995], 'midpoint_of_normalized_filter_outputs': [0.5, 0.5], 'affine_defect_trace_norm': 0.000999999999999945, 'is_quantum_channel_on_declared_convex_domain': False, 'polar_isometry': 'U=V M^(-1/2)=I; N_U(rho)=rho is a genuine channel', 'polar_probe_state': [0.7, 0.3], 'source_residual_after_M_inverse_congruence': [-0.000599580311756553, 0.0014004203549105], 'output_modular_transport_term': [0.000599580311756553, -0.0014004203549105], 'bulk_similarity_transport_term': [0.0, 0.0], 'polar_channel_residual': [0.0, 0.0], 'polar_decomposition_identity_residual': 0.0, 'interpretation': 'The normalized filter fails affinity by exactly delta in this cell. Polar correction restores a channel, but its output-modular transport cancels the transformed source residual; that cancellation is extra information not supplied by the source eta bound alone.'} |
| polar correction decomposition closes exactly in the diagnostic cell | `true` | {'model': 'Two-level normalized filter with M=diag(1+delta,1-delta); its polar isometry is U=I.', 'delta_isometry': 0.001, 'convex_domain_states': {'rho_0': [1.0, 0.0], 'rho_1': [0.0, 1.0], 'midpoint': [0.5, 0.5]}, 'normalized_filter_midpoint': [0.5005, 0.4995], 'midpoint_of_normalized_filter_outputs': [0.5, 0.5], 'affine_defect_trace_norm': 0.000999999999999945, 'is_quantum_channel_on_declared_convex_domain': False, 'polar_isometry': 'U=V M^(-1/2)=I; N_U(rho)=rho is a genuine channel', 'polar_probe_state': [0.7, 0.3], 'source_residual_after_M_inverse_congruence': [-0.000599580311756553, 0.0014004203549105], 'output_modular_transport_term': [0.000599580311756553, -0.0014004203549105], 'bulk_similarity_transport_term': [0.0, 0.0], 'polar_channel_residual': [0.0, 0.0], 'polar_decomposition_identity_residual': 0.0, 'interpretation': 'The normalized filter fails affinity by exactly delta in this cell. Polar correction restores a channel, but its output-modular transport cancels the transformed source residual; that cancellation is extra information not supplied by the source eta bound alone.'} |
| flagged completion is affine and preserves the normalized success state | `true` | {'affine_residual': 1.11022302462516e-16, 'success_state_residual': 0.0} |
| flagged block relative-entropy identity closes on every declared ordered pair | `true` | 4.44089209850063e-16 |
| flagged channel defect is bounded by normalized-map loss plus failure weight times domain diameter | `true` | {'actual_flagged_loss_nats': 0.00221487940630727, 'generic_bound_nats': 0.00351040579342272} |
| source-residual flagged completion bound dominates the executable channel loss | `true` | {'actual_flagged_loss_nats': 0.00221487940630727, 'source_residual_bound_nats': 0.0104776526605229} |
| noncommuting flagged completion is explicitly CPTP | `true` | {'kraus_completeness_residual': 8.88178419700125e-16, 'minimum_choi_eigenvalue': -1.70461534414143e-16, 'maximum_output_trace_residual': 4.44089209850063e-16, 'minimum_test_output_eigenvalue': 0.000639675942581312} |
| noncommuting flagged completion preserves affinity, success states, and the quantum block identity | `true` | {'affine_residual': 7.85046229341887e-17, 'success_state_residual': 3.33066907387547e-16, 'block_identity_residual': 8.04911692853238e-16} |
| noncommuting flagged defect obeys the generic domain-diameter bound | `true` | {'actual_flagged_loss_nats': 0.00033921839923523, 'generic_bound_nats': 0.000849097699699111} |
| exact-isometry projected-JLMS identity closes on every declared ordered pair | `true` | {'model': 'binary symmetric channel on a declared full-rank 41-state grid; it has an exact Stinespring isometry and no area term', 'crossover': 0.01, 'declared_state_grid_size': 41, 'uniform_projected_residual_eta_nats': 0.0980743901906864, 'max_absolute_pairwise_relative_entropy_defect_nats': 0.102493095991637, 'two_eta_bound_nats': 0.196148780381373, 'max_identity_residual': 8.60422844084496e-16, 'argmax_pair': {'sigma': [0.9, 0.1], 'rho': [0.1, 0.9], 'signed_pairwise_defect_nats': -0.102493095991637}} |
| uniform projected residual supplies the exact-isometry two-eta pairwise bound | `true` | {'max_pairwise_defect_nats': 0.102493095991637, 'two_eta_bound_nats': 0.196148780381373} |
| approximate-isometry identity separates residual and normalization transport | `true` | {'row_count': 4, 'max_identity_residual': 1.06858966120171e-15} |
| delta-isometry centered modular-oscillation correction bounds every stress row | `true` | {'row_count': 4, 'minimum_corrected_margin_nats': 0.005507339379442575} |
| omitting delta times centered modular oscillation becomes a false bound | `true` | {'bulk_eigenvalue_floor': 1e-06, 'delta_isometry': 0.001, 'probe_sigma': [0.5, 0.5], 'reference_rho': [0.999999, 1e-06], 'normalization_z_sigma': 1.0, 'uniform_residual_eta_nats_on_declared_three-state_domain': 0.00200199866332994, 'bulk_modular_oscillation_LK_nats': 6.90775477898189, 'actual_pairwise_relative_entropy_defect_nats': -0.0059082564438997, 'residual_difference_term_nats': 0.000999498335081729, 'normalization_transport_term_nats': -0.00690775477898185, 'identity_residual': 4.30211422042248e-16, 'naive_bound_omitting_delta_LK_nats': 0.00400800533199186, 'corrected_bound_nats': 0.0178373442288525, 'naive_bound_violated': True, 'corrected_bound_holds': True} |
| derived channelized projected-JLMS budgets include the two-reference and log-unit factors | `true` | {'target_count': 5, 'tightest_exact_channel_residual_budget_nats': 3.43280349090821e-06} |
| flagged target inversions saturate their declared success-conditioned trace targets | `true` | {'row_count': 20, 'tightest_delta_iso_budget': 1.24225026210123e-07} |
| source tail wedge closes at a=t and domain-diameter growth can erase isometry convergence | `true` | {'open_balanced': {'defect_power': 1.0, 'trace_power': 0.5, 'convergent': True}, 'open_narrow_tail': {'defect_power': 0.25, 'trace_power': 0.125, 'convergent': True}, 'closed_at_tail_boundary': {'defect_power': 0.0, 'trace_power': 0.0, 'convergent': False}, 'domain_growth_erases_isometry_gain': {'defect_power': 0.0, 'trace_power': 0.0, 'convergent': False}, 'open_with_controlled_domain_growth': {'defect_power': 1.5, 'trace_power': 0.75, 'convergent': True}} |
| synthetic source power transfer exhibits the double square-root loss | `true` | {'epsilon_pJLMS_vs_G': 0.500000019763835, 'flagged_channel_defect_vs_G': 0.500000056210865, 'success_conditioned_trace_bound_vs_G': 0.250000028105473} |
| exact reconstructed-algebra spectral-floor geometry closes on explicit extremizers | `true` | {'entropy_formula_residual': 4.44089209850063e-16, 'oscillation_formula_residual': 4.44089209850063e-16, 'overlap_grid_excess': 0.0} |
| exponential sector proliferation defeats vanishing local source errors at b=gamma=1 | `true` | {'ratios': {'source_eta': 0.00882238180698043, 'flagged_defect': 0.694589995653718, 'success_trace': 0.671328763652738}, 'slopes': {'source_eta_vs_G': 0.882365312174833, 'flagged_defect_vs_G': 0.010781965030059, 'success_trace_vs_G': 0.0100101672817929}, 'last_row': {'G': 0.000352220468967032, 'sector_count': '2^4096', 'log_sector_count_nats': 2839.13085157354, 'total_sector_floor_mass': 0.1, 'minimum_sector_weight_log': -2841.43343666653, 'epsilon_FLM': 4.36962102999228e-11, 'epsilon_tail': 0.000352220468967032, 'epsilon_iso_small_and_delta_iso': 0.000352220468967032, 'source_eta_nats': 0.00350503508516431, 'exact_bulk_wedge_relative_entropy_diameter_nats': 2557.19526853578, 'exact_bulk_wedge_centered_modular_oscillation_nats': 2841.32807615087, 'flagged_channel_pairwise_defect_bound_nats': 3.81002435893021, 'success_conditioned_trace_bound': 7.45611230933413}} |
| polynomial sector growth remains compatible with b=1 convergence through the same bridge | `true` | {'ratios': {'source_eta': 0.00882238180698043, 'flagged_defect': 0.00944750257117546, 'success_trace': 0.0776446990728996}, 'slopes': {'source_eta_vs_G': 0.882365312174833, 'flagged_defect_vs_G': 0.871995360155367, 'success_trace_vs_G': 0.442423615112984}} |
| exponential sector growth requires isometry improvement faster than its exponent | `true` | {'ratios': {'source_eta': 3.44624289335174e-05, 'flagged_defect': 0.00277857918771458, 'success_trace': 0.0512389885591865}, 'slopes': {'source_eta_vs_G': 1.88236531217483, 'flagged_defect_vs_G': 1.01064059358845, 'success_trace_vs_G': 0.505414273495532}} |
| Appendix-C and Lemma-4 isometry chain is propagated without an independent b assignment | `true` | {'appendix_C': "Full-system approximate FLM implies eps_iso,small <= 2 sqrt(eps_FLM) after the source's optimal rescaling.", 'lemma_4': 'Large-code delta_iso <= eps_iso,small + eps_OD.', 'combined': 'delta_iso <= 2 sqrt(eps_FLM) + eps_OD; this requires a full-system FLM premise and cannot be inferred from a subregion estimate alone.'} |
| full-system FLM closes exactly at a=2 gamma and leaves the sector tax order one | `true` | {'wedge': {'flm_power_a': 2.0, 'tail_power_t': 1.0, 'exponential_sector_power_gamma': 1.0, 'derived_small_isometry_power_b': 1.0, 'candidate_flagged_defect_powers': {'sqrt_eps_FLM_over_eps_tail': 0.5, 'full_system_FLM_isometry_log_tail': 1.0, 'full_system_FLM_isometry_times_sector_geometry': 0.0}, 'flagged_channel_defect_power_up_to_logs': 0.0, 'success_recovery_trace_power_up_to_logs': 0.0, 'tail_wedge_open': True, 'sector_wedge_open': False, 'convergent_through_this_chain': False, 'closed_form_condition': 'a>max(t,2 gamma), assuming eps_OD and the remaining Theorem-5 terms are nonperturbative on the same domain'}, 'slopes': {'source_eta_vs_G': 0.632386925559622, 'delta_log_K_vs_G': 0.0, 'flagged_defect_vs_G': 0.0150964491417954, 'success_trace_vs_G': 0.0162044093600203}, 'last_row': {'G': 0.000352220468967032, 'sector_count': '2^4096', 'log_sector_count_nats': 2839.13085157354, 'epsilon_FLM': 1.24059258759356e-07, 'epsilon_tail': 0.000352220468967032, 'epsilon_OD_nonperturbative_test': 0.0, 'appendix_C_epsilon_iso_small_upper': 0.000704440937934064, 'lemma_4_delta_iso_large_upper': 0.000704440937934064, 'source_eta_best_case_nats': 0.0250731668696828, 'delta_iso_times_log_sector_count': 2.0, 'flagged_channel_pairwise_defect_bound_nats': 7.65634914945755, 'success_conditioned_trace_bound': 10.5778901055632}} |
| full-system FLM reopens exponential-sector convergence for a=3 and a=5 | `true` | {'a3': {'source_eta_vs_G': 1.13238692555962, 'delta_log_K_vs_G': 0.499999999999999, 'flagged_defect_vs_G': 0.514760773167871, 'success_trace_vs_G': 0.25831366319184}, 'a5': {'source_eta_vs_G': 2.13238692555962, 'delta_log_K_vs_G': 1.5, 'flagged_defect_vs_G': 1.51473677855696, 'success_trace_vs_G': 0.757399379326325}} |
| tiny trace leakage does not control global operator-log smoothness in Gaussian tails | `true` | {'last_row': {'radius': 256, 'sector_count': 513, 'minimum_log_sector_weight': -13108.5770838991, 'symmetric_distance_only_transport': {'maximum_per_source_off_diagonal_leakage': 1e-08, 'total_variation_between_p_and_Tp': 9.32049683612079e-10, 'exact_log_smoothness_nats': 83.0861720754892, 'right_tail_exact_log_ratio_nats': 83.0861720754877, 'maximum_log_relative_inflow_nats': 83.0861720754892, 'normalization_residual': 2.22044604925031e-16}, 'p_stationary_metropolis_transport': {'maximum_per_source_off_diagonal_leakage': 8.18730753077982e-09, 'total_variation_between_p_and_Tp': 8.67361737988404e-18, 'exact_log_smoothness_nats': 4.01913234914517e-13, 'maximum_log_stationarity_residual_nats': 4.01913234914517e-13, 'normalization_residual': 0.0}}, 'fitted_slope': 0.39999169579337} |
| p-stationary detailed-balance transport removes the commuting log-smoothness tax | `true` | {'maximum_log_smoothness_residual': 4.01913234914517e-13, 'constructive_completion': 'Require a p-weighted incoming-flux or approximate-stationarity theorem. Exact detailed balance is stronger than necessary but makes the commuting log-smoothness tax identically zero at any sector count.'} |
| direct-sum relative entropy separates a commutative center from genuinely noncommuting factor blocks | `true` | {'decomposition_residual': 2.22044604925031e-16, 'modular_block_residual': 1.42217702640602e-15, 'factor_commutator_trace_norms': [0.198305320150519, 0.173168992605489, 0.10470195795686]} |
| full reconstructed-algebra domain taxes add center and factor contributions exactly in the declared product cell | `true` | {'diameter_residual': 8.88178419700125e-16, 'oscillation_residual': 0.0, 'center_only_diameter_fraction': 0.46100688722628, 'center_only_oscillation_fraction': 0.490374495652571} |
| vanishing state perturbation can leave order-one noncommuting operator-log error | `true` | {'slopes': {'adversarial_state_trace_vs_G': 0.999961179752731, 'adversarial_operator_log_vs_G': -3.882024726763e-05, 'repaired_state_trace_vs_G': 1.99999998444313, 'repaired_operator_log_vs_G': 0.999999984443134}, 'final_row': {'G': 0.00390625, 'eigenvalue_floor_exp_minus_1_over_G': 6.61626105670949e-112, 'log_condition_number_nats': 256.0, 'adversarial_theta_equals_G': {'rotation_angle': 0.00390625, 'state_trace_norm_perturbation': 0.00781248013180023, 'operator_log_difference_norm_nats': 0.99999745687043}, 'repaired_theta_equals_G_squared': {'rotation_angle': 1.52587890625e-05, 'state_trace_norm_perturbation': 3.05175781238158e-05, 'operator_log_difference_norm_nats': 0.00390624999984842}}} |
| a stronger modular-frame rotation schedule repairs the within-factor log-smoothness stress | `true` | {'slopes': {'adversarial_state_trace_vs_G': 0.999961179752731, 'adversarial_operator_log_vs_G': -3.882024726763e-05, 'repaired_state_trace_vs_G': 1.99999998444313, 'repaired_operator_log_vs_G': 0.999999984443134}, 'final_row': {'G': 0.00390625, 'eigenvalue_floor_exp_minus_1_over_G': 6.61626105670949e-112, 'log_condition_number_nats': 256.0, 'adversarial_theta_equals_G': {'rotation_angle': 0.00390625, 'state_trace_norm_perturbation': 0.00781248013180023, 'operator_log_difference_norm_nats': 0.99999745687043}, 'repaired_theta_equals_G_squared': {'rotation_angle': 1.52587890625e-05, 'state_trace_norm_perturbation': 3.05175781238158e-05, 'operator_log_difference_norm_nats': 0.00390624999984842}}} |
| fixed-region sector decoders glue into one exact direct-sum algebra channel when the coherent sector tag shares the carrier | `true` | {'direct_sum_oaqec': {'target_algebra': 'direct sum of full matrix blocks with dimensions [2, 2]', 'retained_subsystems': [0, 1], 'erased_kraus_count': 2, 'kraus_completeness_operator_norm_residual': 1.8882991164529e-18, 'maximum_commutant_operator_norm_residual': 1.8882991164529e-18, 'maximum_commutant_frobenius_residual': 3.7765982329058e-18, 'argmax_erasure_kraus_pair': [0, 0], 'exactly_correctable_at_tolerance': True}, 'full_subspace_oaqec': {'target_algebra': 'direct sum of full matrix blocks with dimensions [4]', 'retained_subsystems': [0, 1], 'erased_kraus_count': 2, 'kraus_completeness_operator_norm_residual': 1.8882991164529e-18, 'maximum_commutant_operator_norm_residual': 1.8882991164529e-18, 'maximum_commutant_frobenius_residual': 3.7765982329058e-18, 'argmax_erasure_kraus_pair': [0, 0], 'exactly_correctable_at_tolerance': True}, 'decoders': {'region': 'tag-plus-logical carrier R; no sector-dependent region switch', 'coherent_decoder': 'one controlled inverse unitary on R', 'maximum_full_state_trace_norm_error': 1.90290181794592e-16, 'algebraic_decoder': 'the same controlled inverse followed by sector dephasing', 'block_diagonal_state_trace_norm_error': 2.08166817117217e-17, 'maximum_direct_sum_algebra_expectation_residual': 1.11022302462516e-16, 'cross_sector_coherent_state_trace_norm_error_after_algebraic_decoder': 1.0, 'target_interpretation': 'The dephasing decoder is exact for the direct-sum operator algebra even though it is not full-Hilbert recovery. The coherent controlled decoder shows that full coherence is also recoverable when the sector tag itself is coherently available on the same carrier.'}} |
| direct-sum algebra recovery is not failed by licensed off-diagonal sector dephasing | `true` | {'region': 'tag-plus-logical carrier R; no sector-dependent region switch', 'coherent_decoder': 'one controlled inverse unitary on R', 'maximum_full_state_trace_norm_error': 1.90290181794592e-16, 'algebraic_decoder': 'the same controlled inverse followed by sector dephasing', 'block_diagonal_state_trace_norm_error': 2.08166817117217e-17, 'maximum_direct_sum_algebra_expectation_residual': 1.11022302462516e-16, 'cross_sector_coherent_state_trace_norm_error_after_algebraic_decoder': 1.0, 'target_interpretation': 'The dephasing decoder is exact for the direct-sum operator algebra even though it is not full-Hilbert recovery. The coherent controlled decoder shows that full coherence is also recoverable when the sector tag itself is coherently available on the same carrier.'} |
| worst-sector routing confusion enters the common algebra-decoder budget linearly as two p_max in trace norm | `true` | {'slope': 1.0, 'last_row': {'worst_sector_misrouting_probability': 0.001, 'deterministic_sector_trace_norm_error': 0.002, 'center_observable_expectation_error': 0.002, 'gluing_bound_epsilon_local_plus_disturbance_plus_2p': 0.002}} |
| REF-0735 Condition-2 retained-block leakage gives a sharp linear sector-diagonal common-decoder budget | `true` | {'slope': 1.00000000000001, 'last_row': {'epsilon_iso_small': 0.001, 'sector_trace_z': 0.999, 'epsilon_sub_tr': 0.001, 'source_subleading_trace_norm': 0.001, 'normalized_wrong_block_probability': 0.001001001001001, 'normalized_state_to_dominant_block_trace_norm': 0.00200200200200187, 'common_decoder_direct_sum_trace_norm_error': 0.00200200200200187, 'center_sign_expectation_error': 0.00200200200200185, 'condition2_linear_bound': 0.002002002002002, 'bound_saturation_residual': 1.33573707650214e-16}} |
| Condition-2 target inversion distinguishes dominant-block certificates from full-sector certificates | `true` | [{'target_common_decoder_trace_norm_error': 0.5, 'epsilon_iso_small': 0.001, 'required_epsilon_sub_tr_max_if_decoder_is_certified_on_dominant_block': 0.24975, 'required_epsilon_sub_tr_max_if_decoder_is_only_certified_on_full_sector_state': 0.124875, 'dominant_block_bound_at_budget': 0.5, 'full_sector_transport_bound_at_budget': 0.5}, {'target_common_decoder_trace_norm_error': 0.25, 'epsilon_iso_small': 0.001, 'required_epsilon_sub_tr_max_if_decoder_is_certified_on_dominant_block': 0.124875, 'required_epsilon_sub_tr_max_if_decoder_is_only_certified_on_full_sector_state': 0.0624375, 'dominant_block_bound_at_budget': 0.25, 'full_sector_transport_bound_at_budget': 0.25}, {'target_common_decoder_trace_norm_error': 0.1, 'epsilon_iso_small': 0.001, 'required_epsilon_sub_tr_max_if_decoder_is_certified_on_dominant_block': 0.04995, 'required_epsilon_sub_tr_max_if_decoder_is_only_certified_on_full_sector_state': 0.024975, 'dominant_block_bound_at_budget': 0.1, 'full_sector_transport_bound_at_budget': 0.1}, {'target_common_decoder_trace_norm_error': 0.05, 'epsilon_iso_small': 0.001, 'required_epsilon_sub_tr_max_if_decoder_is_certified_on_dominant_block': 0.024975, 'required_epsilon_sub_tr_max_if_decoder_is_only_certified_on_full_sector_state': 0.0124875, 'dominant_block_bound_at_budget': 0.05, 'full_sector_transport_bound_at_budget': 0.05}, {'target_common_decoder_trace_norm_error': 0.01, 'epsilon_iso_small': 0.001, 'required_epsilon_sub_tr_max_if_decoder_is_certified_on_dominant_block': 0.004995, 'required_epsilon_sub_tr_max_if_decoder_is_only_certified_on_full_sector_state': 0.0024975, 'dominant_block_bound_at_budget': 0.01, 'full_sector_transport_bound_at_budget': 0.01}] |
| Condition-1 epsilon_OD exactly pays the environment-tagged coherent-sector center bias in the owned two-sector cell | `true` | {'slopes': {'environment_tagged_coherent_error_vs_epsilon_sub_tr': 0.491831843689103, 'environment_tagged_coherent_error_vs_epsilon_OD': 0.999999999999999, 'carrier_frame_coherent_error_vs_epsilon_sub_tr': 0.995751044434811}, 'last_row': {'wrong_block_probability_per_sector': 0.0005, 'epsilon_sub_tr_per_sector': 0.0005, 'epsilon_OD_for_equal_coherent_superposition': 0.0447101778122163, 'block_instrument_center_trace_norm_error': 0.0447101778122164, 'analytic_coherent_error': 0.0447101778122163, 'encoding_isometry_operator_norm_residual': 2.22470222718613e-16, 'condition2_residual': 0.0, 'epsilon_OD_payment_residual': 1.04083408558608e-16}} |
| Condition-2 full trace-norm leakage itself pays the carrier-frame coherent bias when epsilon_OD vanishes | `true` | {'slopes': {'environment_tagged_coherent_error_vs_epsilon_sub_tr': 0.491831843689103, 'environment_tagged_coherent_error_vs_epsilon_OD': 0.999999999999999, 'carrier_frame_coherent_error_vs_epsilon_sub_tr': 0.995751044434811}, 'last_row': {'wrong_block_probability_per_sector': 0.0005, 'epsilon_sub_tr_per_sector': 0.0447129735088151, 'epsilon_OD_for_equal_coherent_superposition': 0.0, 'block_instrument_center_trace_norm_error': 0.0447101778122164, 'analytic_epsilon_sub_tr': 0.0447129735088151, 'analytic_coherent_error': 0.0447101778122163, 'encoding_isometry_operator_norm_residual': 2.22470222718613e-16, 'condition2_formula_residual': 0.0, 'epsilon_OD_zero_residual': 0.0, 'coherent_error_below_epsilon_sub_tr': True}} |
| an average epsilon_sub-tr can converge as K^-1 while the worst-sector common-decoder obstruction remains fixed | `true` | {'slope': -1.0, 'last_row': {'sector_count': 4096, 'reference_mixture_average_epsilon_sub_tr': 2.44140625e-05, 'reference_mixture_average_decoder_trace_norm_error': 4.8828125e-05, 'bad_sector_epsilon_sub_tr': 0.1, 'worst_sector_common_decoder_trace_norm_error': 0.2, 'invalid_bound_if_average_is_substituted_for_uniform_epsilon_sub_tr': 4.8828125e-05}} |
| Beny OAQEC target inversion preserves the square-root sufficient theorem and the code-dimension lift | `true` | {'contract': 'delta_A(N)^2/4 <= E_A(N) <= 2 sqrt(delta_A(N)).', 'tightest_state_only_budget': 6.103515625e-09} |
| state-level off-diagonal convergence can coexist with order-one reference-assisted OAQEC obstruction | `true` | {'slopes': {'state_envelope_vs_dimension': -0.997984484243517, 'coherent_state_witness_vs_dimension': -0.995954425726877, 'diamond_defect_vs_dimension': 0.00404557427312274, 'reconstruction_lower_bound_vs_dimension': 0.00809114854624619}, 'last_row': {'code_dimension': 4096, 'uniform_state_trace_norm_envelope': 0.000488162069807176, 'maximally_coherent_state_trace_norm_witness': 0.000488042889614352, 'exact_reference_assisted_diamond_defect': 0.999511837930193, 'beny_minimum_reconstruction_error_lower_bound': 0.249755978540648, 'diamond_to_state_envelope_ratio': 2047.5, 'diamond_to_coherent_state_witness_ratio': 2048.0, 'generic_dimension_lift_upper_bound': 1.99951183793019}} |
| transpose-dephasing defect diamond formula closes through independent Choi Jordan marginals | `true` | {'row_count': 5, 'maximum_formula_residual': 1.11022302462516e-16} |
| erasure-channel positive control gives one common decoder with exact complementary-diamond scaling | `true` | {'choi_formula_residual': 8.88178419700125e-16, 'row_count': 20} |
| nonperturbative state error pays the reference dimension only when its exponential rate is stronger | `true` | {'insufficient_state_rate': {'G': 0.015625, 'log_code_dimension': 64.0, 'state_only_error': 1.42516408274094e-21, 'log_unclipped_dimension_lift': 16.0, 'generic_complementary_diamond_upper_bound': 2.0, 'beny_sufficient_reconstruction_upper_bound': 2.0}, 'critical_rate_plateau': {'G': 0.015625, 'log_code_dimension': 64.0, 'state_only_error': 1.60381089054864e-28, 'log_unclipped_dimension_lift': 0.0, 'generic_complementary_diamond_upper_bound': 1.0, 'beny_sufficient_reconstruction_upper_bound': 2.0}, 'reference_stable_rate': {'G': 0.015625, 'log_code_dimension': 64.0, 'state_only_error': 1.80485138784542e-35, 'log_unclipped_dimension_lift': -16.0, 'generic_complementary_diamond_upper_bound': 1.12535174719259e-07, 'beny_sufficient_reconstruction_upper_bound': 0.000670925255805024}} |
| discarding the sector tag leaves a linear common-decoder frame-mismatch obstruction despite exact sector-conditioned decoders | `true` | {'slopes': {'minimax_lower_bound_vs_frame_separation': 0.989996948566669, 'midpoint_upper_bound_vs_frame_separation': 0.997513442028839}, 'last_row': {'sector_frame_separation_radians': 0.03125, 'physical_output_identity_residual': 1.11194963130561e-16, 'indistinguishable_input_logical_trace_norm_distance': 0.0312487284497667, 'any_common_decoder_minimax_trace_norm_lower_bound': 0.0156243642248834, 'midpoint_unitary_decoder_worst_case_upper_bound': 0.0156248410547657, 'sector_conditioned_decoder_error': 0.0}} |
| sector-wise exact reconstruction does not imply one fixed-region decoder | `true` | {'AC_output_distance_for_sector_1_orthogonal_logical_pair': 0.0, 'BC_output_distance_for_sector_0_orthogonal_logical_pair': 0.0, 'input_logical_pair_trace_distance': 2.0, 'exact_pair_minimax_recovery_trace_error_lower_bound': 1.0, 'constant_maximally_mixed_decoder_attains_pair_error': 1.0, 'proof': 'Each fixed region maps one orthogonal logical pair to the same record. The OAQEC commutant residual is also one on AC and BC, while it vanishes on ABC.'} |
| adaptive wedge routing recovers the direct-sum algebra but destroys cross-sector coherence unless it is quotiented out | `true` | {'adaptive': {'block_diagonal_operator_algebra_error': 0.0, 'cross_sector_coherent_state_trace_norm_error': 1.0, 'interpretation': 'External sector-dependent routing recovers the direct-sum blocks but is not one fixed-subregion channel. Its coherence loss matters only if full-Hilbert recovery, rather than the direct-sum algebra, is the declared target.'}, 'fixed_union': {'region': 'ABC', 'arbitrary_coherent_code_state_trace_norm_error': 0.0}} |
| toy dimension and physical finite-N resource remain explicitly unmapped | `true` | No D=N, D=1/G, central-charge, area, or bond-dimension substitution is evaluated. |

## Hard limits and next denominator

- No numerical physical finite-N, G, central-charge, area, or tensor-network scaling is derived or fitted. The source-tail rows propagate declared symbolic powers only.
- The resource schedules, flagged target inversions, full-system-FLM closure rows, and source-power schedule are conditional theorem test vectors, not holographic data.
- The binary-channel, non-affinity, polar-correction, flagged-completion, Kraus/Choi, direct-sum factor, modular-rotation, fixed-region gluing, source-routing, coherent-sector, reference-amplification, erasure, wedge-switching, and spectral-floor cells verify joins and failure modes; they are not models of AdS/CFT dynamics.
- The failure flag is an auxiliary proof-device output. This revision claims only the decoder obtained by restricting the theorem recovery map to the original success block; it does not claim the source supplies a physical flag or free postselection.
- The sector-weight, center-transport, factor-frame, sector-confusion, wedge-switching, and rare-sector schedules are theorem stress tests, not physical fits or models of AdS/CFT dynamics. The Metropolis kernel, coherent controlled decoder, and fixed-union decoder are mathematical controls, not claimed gravitational mechanisms.
- The full-code constant is a sufficient theorem bound and need not be optimal.
- Passing the benchmark creates no acquired evidence, observed-sector recovery, public-record closure, or route promotion.

Next kernel step: On REF-0735's fixed region, construct the actual complementary defect Delta=Nhat-Nhat o P_{A'} for the declared direct-sum algebra and derive either a uniform diamond/cb bound directly or a state-to-diamond lift with explicit d_code/reference growth. Insert the same-domain epsilon_OD, epsilon_sub-tr, approximate-isometry, dominant-block decoder, center/factor geometry, and FLM/JLMS errors; test the new tau^2/(4 d_code) budget and the c>s rate wedge; then compare the resulting genuine OAQEC error with the owned complementary-channel benchmark without identifying computational D with physical N.
