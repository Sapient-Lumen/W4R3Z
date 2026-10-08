# Family-C three-qutrit reconstruction benchmark (generated)

This is the first owned executable reconstruction stress cell for the strongest live Family-C route. It is deliberately small: exact finite-dimensional quantum error correction, not a finite-N holographic result.

- Route: `R-OQ0057-FAMILYC-EW-CODE`
- Decision experiment: `DX-0015-FAMILYC-FINITE-N-QEC-ISLAND-DECODER-REPLAY`
- Status: owned finite-dimensional toy-model stress cell; route-local S3 pressure only
- Replay: `python3 tools/familyc_qutrit_reconstruction_benchmark.py --check`
- Validation failures: `0`

## Exact code result

| Quantity | Result |
|---|---:|
| Isometry residual | `2.22044604925031e-16` |
| Single-erasure Knill-Laflamme residual | `0.0` |
| One-share logical-basis record spread | `0.0` |
| One-share coherence leakage | `0.0` |
| Minimum any-two-share decoder fidelity | `1.0` |

## Same-restricted-record discriminator

The named logical record `0` is assigned two rival dictionaries: encoded `|0>` versus encoded `(|0>+|1>+|2>)/sqrt(3)`. Every one-share reduced record collides, but the declared decoder on any retained pair separates them.

| Quantity | Result |
|---|---:|
| Maximum one-share record distance | `1.92296268638356e-16` |
| Minimum any-two-share logical-zero witness gap | `0.666666666666667` |
| Global state overlap squared | `0.333333333333334` |

This is a concrete demonstration of record-relative distinguishability. It is not evidence that a physical boundary dictionary, finite-N code subspace, or bulk observer map has been identified.

## Declared leakage sweep

The deformation mixes each exact codeword with an orthogonal marker. It is a diagnostic stress parameter, not a physical `1/N` expansion.

| epsilon | KL residual | one-share record distance | decoder fidelity | pair witness gap |
|---:|---:|---:|---:|---:|
| `0.0` | `0.0` | `1.92296268638356e-16` | `1.0` | `0.666666666666667` |
| `0.01` | `0.00577321400954442` | `0.00666683333125005` | `0.9999` | `0.6666` |
| `0.03` | `0.0173127120925637` | `0.0200044994938639` | `0.9991` | `0.666066666666667` |
| `0.1` | `0.0574456264653803` | `0.0668331255192114` | `0.989999999999999` | `0.66` |
| `0.2` | `0.113137084989848` | `0.134660065844828` | `0.96` | `0.64` |
| `0.35` | `0.189291441961859` | `0.240372974077093` | `0.8775` | `0.585` |

## Negative control

The isometric repetition encoding `|i> -> |iii>` fails as a quantum erasure code:

- Knill-Laflamme residual: `0.666666666666667`
- One-share basis-record spread: `1.4142135623731`
- Minimum fidelity under the exact-code decoder: `0.0`

## Acceptance checks

| Check | Passed | Detail |
|---|---:|---|
| exact encoding is isometric | `true` | residual=2.22044604925031e-16 |
| exact code satisfies every single-erasure Knill-Laflamme condition | `true` | residual=0.0 |
| exact decoder recovers all declared probes from every retained pair | `true` | minimum_fidelity=1.0 |
| rival dictionaries collide on every one-share record | `true` | maximum_distance=1.92296268638356e-16 |
| rival dictionaries separate after any-two-share decoding | `true` | minimum_gap=0.666666666666667 |
| declared rival global overlap remains one third | `true` | overlap_squared=0.333333333333334 |
| repetition-code control fails the quantum erasure condition | `true` | residual=0.666666666666667 |
| repetition-code control leaks basis records to one share | `true` | spread=1.4142135623731 |
| exact-code decoder rejects the repetition-code control | `true` | minimum_fidelity=0.0 |
| declared leakage monotonically worsens the erasure residual | `true` | [0.0, 0.00577321400954442, 0.0173127120925637, 0.0574456264653803, 0.113137084989848, 0.189291441961859] |
| declared leakage monotonically lowers decoder fidelity | `true` | [1.0, 0.9999, 0.9991, 0.989999999999999, 0.96, 0.8775] |
| declared leakage monotonically exposes the formerly hidden dictionary difference | `true` | [1.92296268638356e-16, 0.00666683333125005, 0.0200044994938639, 0.0668331255192114, 0.134660065844828, 0.240372974077093] |

## Hard limits and next denominator

- The benchmark is a 3-qutrit exact toy code, not a finite-N CFT or gravitational calculation.
- The leakage deformation is diagnostic and carries no physical 1/N or backreaction interpretation.
- Its max-entry Knill-Laflamme residual is a same-dimension diagnostic only; cross-size scaling must use the operational norm in FAMILYC-APPROXIMATE-RECOVERY-SCALING-BENCHMARK.json.
- No island choice, area operator, edge-mode quotient, local observer map, or non-AdS transport is implemented.
- Passing the cell does not create acquired evidence, public-record closure, observed-sector recovery, or Theory-of-Everything identity.

Next kernel step: Use FAMILYC-APPROXIMATE-RECOVERY-SCALING-BENCHMARK.json as the exact cross-size norm baseline and FAMILYC-JLMS-RECOVERY-BUDGET-BENCHMARK.json as the theorem-translation layer; next instantiate one same-domain full-system/subregion FLM and sector-transport tuple, prove weighted log-smoothness, and then test algebraic, state-dependent-wedge, and non-AdS observer transport.
