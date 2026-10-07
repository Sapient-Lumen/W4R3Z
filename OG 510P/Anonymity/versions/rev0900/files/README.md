# Anonymity datacube rev0900

This revision publishes nothing. It moves four Boss Fight papers to `hold` after finding that the cube treated a scalar observation probability as though it defined an independent erasure channel. It does not. Privacy claims need the conditional observation law—or a proved wrapper that induces it—not merely an average reveal rate. `publication_authorized=false`.

## Highest-risk correction: equal reveal rates can still leak perfectly

The hostile control has three equiprobable secrets and three two-element cover pairs. Each secret selects either pair containing it with probability one half. A cyclic, pair-dependent gate reveals only one endpoint of each pair and otherwise emits `bottom`.

Every secret has the same reveal probability:

```text
Pr[revealed | secret=i] = 1/2  for every i.
```

Yet direct enumeration gives:

```text
actual maximal leakage:       1 bit
actual exact-guess success:   2/3
```

The former scalar-erasure substitution instead reports:

```text
log2(1 + p(2^w-1)), p=1/2, w=1:  0.321928094887 bits
scalar exact-guess prediction:      5/12
```

Equal reveal marginals therefore do not imply a secret-independent reveal gate, an erasure channel, or the claimed leakage certificate.

## Correlation and composition boundaries

Independent-contact arithmetic is now named as a control model. With ten contacts and equal marginal visibility `rho=0.1`, independence gives

```text
1-(1-rho)^10 = 0.6513215599.
```

With arbitrary dependence and the same equal marginals, the any-hit probability can be anywhere in `[0.1, 1]`.

The repaired surfaces also distinguish:

- a retrospective leakage **odometer** from a prospective no-overshoot **filter**;
- design allocation `B/Q` from an empirically certified per-query budget;
- per-tier marginal leakage from joint leakage—the included one-time-pad control leaks zero in either tier alone and one bit jointly;
- secret-independent path selection from a selector whose branch itself carries secret information.

## Proof-carrying boundary

A verifier can recompute arithmetic perfectly while certifying the wrong scientific model. The proof-carrying paper now requires a source-bound channel-witness digest and limits the verdict to:

```text
VALID-UNDER-MODEL(d_M)
```

That verdict means the arithmetic is valid under the identified model. It does not prove that runtime telemetry implements that model.

## Propagation repair

The evaluation-series consumer and Paper 17 worked example no longer export independent-contact or independent-erasure numbers as deployment certificates. Their values remain only as explicit control-model sensitivity calculations with missing channel witnesses and `publication_eligible=false`.

Queue posture is now:

```text
Candidate:         5
Published-ready:   8
Hold:             61
Published:         7
```

The affected Boss Fight theorem, dial sheet, evidence-table addendum, and proof-carrying companion are all on Hold.

## Audit and refactor

- Paper 17’s validator now resolves queue notes from `source_tex`, enforces the corrected channel boundary, and reached a deterministic fixed point after three bounded materialization passes.
- Its seven gzip payload pointers remained offloaded instead of expanding roughly 7.76 MB into the hot path.
- The Paper 17 Hold chronicle was cut from 59,409 to 3,051 bytes while retaining machine-checked current-state boundaries.
- The receipt-schema paper was cut from 28,200 to 16,839 bytes and now requires a channel-witness digest rather than allowing scalar observation telemetry to stand in for a mechanism.
- The queue-index rebuilder now follows the actual latest decision instead of preserving a stale predecessor pointer.
- No new registry or report family was added.

Run the core checks from the extracted root:

```bash
python3 -S -B publishing/check_hostile_review_vectors.py --root .
python3 -S -B publishing/check_external_hostile_review_packet.py --root .
python3 -S -B publishing/run_verify_surfaces.py --root .
python3 -S -B series/synthesis/paper17_worked_example_receipt_interlock/tools/validate_example.py
```

Inspect the linked zip and unsigned package attestation with:

```bash
python3 -B publishing/check_package_attestation.py --zip ../Anonymity-rev0900-2026.06.18.11.54-obschannel-counterexamples-modelbinding-validatorcut.zip --expected-public-key-sha256 9015959ef93385a5e9e4cdfdc8e70f9752d6ad9a9ca4ef0a7f6f0a27e20f8b81 --require-public-key-pin
```

The stricter release-evidence verifier additionally requires a `.package.dsse.json` signature envelope. No private signing key is present in this cloudtainer, so the package attestation is unsigned.

Filename contract: `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`. This revision uses `Anonymity-rev0900-2026.06.18.11.54-obschannel-counterexamples-modelbinding-validatorcut.zip`.
