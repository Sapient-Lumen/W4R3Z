# Diverse double-compiling (DDC) and bootstrappable toolchains

DeriveBSD already treats toolchains as pinned artifacts (`docs/156-toolchain-bootstrap-rust.md`).
This document tightens the “trusting trust” story by making **Diverse Double-Compiling (DDC)**
and **bootstrappable build chains** first-class (optional) verification lanes.

## Why this matters

Even perfectly reviewed source code is not enough if the compiler binary is subverted.
DDC is a practical technique to detect “trusting trust” style compiler backdoors
by demonstrating that a compiler binary corresponds to its claimed source code.

Separately, “bootstrappable builds” reduce dependence on opaque binary seeds by pushing the bootstrap base toward tiny, inspectable components.

DeriveBSD does not require these by default, but it must make them **possible and evidence-bearing**.

## DDC in one paragraph

Given:

- a compiler-under-test binary **A** (the one you want to trust)
- its purported source code **S**
- an independently trusted, diverse compiler **T**

DDC does:

1) compile **S** with **T** to create **B**
2) compile **S** with **B** to create **C**
3) compare **C** to **A** bit-for-bit

If `C == A` (and assumptions hold), then **A corresponds to S**.

## How DeriveBSD models this

### Artifact: `toolchain.bundle`

Toolchains remain first-class artifacts (bundles) that are pinned in Plans and host generations.

### Evidence: `toolchain.ddc.result`

DDC produces a signed result object that binds:

- `subject_toolchain_digest` (the toolchain bundle being justified)
- `source_ref` (repo + revision or source digest)
- `trusted_compiler_digest` (the diverse compiler/toolchain used for step 1)
- `ddc_outputs` (digests for step1/step2 outputs)
- `match` (true if the final output equals the subject)
- optional `diffoscope_digest` when mismatch occurs

Schema + example:

- `spec/toolchain.ddc.result.schema.json`
- `spec/examples/toolchain.ddc.result.json`

### Policy knobs (conceptual)

- `toolchain.requiredDDC = true|false`
- `toolchain.ddcTrustedCompilers = [ ... ]`
- `toolchain.ddcRequiredWitnesses = N` (independent DDC runs)

This composes naturally with witness rebuilders and reproducibility harnesses:

- `docs/116-witness-rebuilders-diffoscope.md`
- `docs/148-reproducibility-variation-harness-reprotest.md`

## Bootstrappable toolchain lane (optional)

DDC detects certain classes of attack even when you must start from a binary seed.
Bootstrappable build chains aim to **shrink and simplify** that seed.

Practical DeriveBSD posture:

- keep a Tier 0 “vendor stage0” path for pragmatic bootstrap
- support an *alternate* chain that uses bootstrappable projects where feasible
- record the chain as evidence so trust boundaries are explicit

Typical building blocks in the ecosystem:

- Stage0-style minimal seeds
- GNU Mes / mescc as a bootstrap C path
- distribution work (e.g., Guix) that documents full-source bootstrap pathways

DeriveBSD can treat “bootstrappable chain used” as a policy-recognizable attribute
of a `toolchain.bundle` and/or its provenance attestations.

## Notes and caveats

- DDC requires an assumption: the diverse compiler **T** must not share the same injected backdoor.
  Diversity can be: different implementation, different version lineage, different language implementation, or different toolchain stack.
- Full-source bootstrap is expensive; treat it as a **high-assurance channel feature**, not a default requirement.

## References

- DDC dissertation site (Wheeler): https://dwheeler.com/trusting-trust/
- ACSAC paper abstract: https://www.acsac.org/2005/abstracts/47.html
- arXiv entry: https://arxiv.org/abs/1004.5534
- Bootstrappable Builds project (Mes): https://www.bootstrappable.org/projects/mes.html
- Guix full-source bootstrap writeup: https://guix.gnu.org/blog/2023/the-full-source-bootstrap-building-from-source-all-the-way-down/
- LWN stage0 overview: https://lwn.net/Articles/841797/

Last updated: 2026-02-24
