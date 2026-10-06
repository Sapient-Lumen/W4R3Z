# RFC-0126: Diverse double-compiling (DDC) toolchain trust lane

Status: **draft**

## Motivation

Toolchains are a trust anchor.
Even a fully reproducible system can be subverted if the compiler binary is compromised (“trusting trust”).

Diverse Double-Compiling (DDC) is a practical technique to detect this class of attack
by demonstrating correspondence between a compiler binary and its purported source.

DeriveBSD should make DDC possible and evidence-bearing for high-assurance channels.

## Goals

- Define a `toolchain.ddc.result` evidence object.
- Bind results to DeriveBSD toolchain bundles (digests).
- Allow policy to require DDC (and optionally multiple independent runs).

## Non-goals

- Mandating full-source bootstrap for all users.
- Proving the diverse compiler is correct.
- Specifying a universal set of “trusted diverse compilers”.

## Proposal

### Evidence object: `toolchain.ddc.result`

Fields (v0):

- `subject_toolchain_digest` (the toolchain under justification)
- `source_ref` (repo + revision and/or source digest)
- `trusted_compiler_digest` (diverse compiler/toolchain)
- `ddc_outputs`:
  - step1 compiler output digest
  - step2 compiler output digest
- `match` (boolean)
- optional `diffoscope_digest` when mismatch occurs
- `issued_at` + signature

### Policy integration

- `toolchain.requiredDDC`
- `toolchain.ddcTrustedCompilers`
- `toolchain.ddcRequiredWitnesses`

## References

- DDC dissertation site (Wheeler): https://dwheeler.com/trusting-trust/
- ACSAC paper abstract: https://www.acsac.org/2005/abstracts/47.html
