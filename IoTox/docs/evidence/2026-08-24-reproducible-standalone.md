# Same-toolchain clean standalone reproducibility evidence

Date: 2026-08-24

Status: accepted founding-host construction evidence

## Claim

`tools/compare-standalone-builds.sh` built source commit
`04e06532e2fecc3ba466679dae50e20eea82a38e` twice under the pinned Nix development toolchain.
Each side used a distinct empty CMake/Ninja product build root and a distinct distribution root while
sharing only the same checked, pinned dependency prefix. Both builds generated and strictly verified
their SPDX inventory before comparison.

The following release surfaces were byte-identical:

- the source-linked `iotox` executable;
- deterministic `iotox.spdx.json`;
- `build-info.txt` and `verification.txt`;
- `THIRD_PARTY.md`; and
- the complete license directory shape and bytes.

The temporary roots were removed by the comparator's exit trap. No build tree or duplicate
distribution was retained in the repository.

## Accepted result

```text
schema=iotox.reproducible-standalone.v1
source-commit=04e06532e2fecc3ba466679dae50e20eea82a38e
source-date-epoch=1787601647
baseline=fresh-empty-build-directory
candidate=fresh-empty-build-directory
binary-sha256=d2d5845957535652d29f2624bc9e0e0419fd753b2385a90d13cc6f691bd0f824
spdx-sbom-sha256=235c2cb1f1d2c8d0dc0932868c57b3e66f3a85d2892ed9b88d39606122400798
comparison=byte-identical
scope=same-host-same-toolchain-distinct-product-build-roots
```

## Construction findings

The first attempted harness invocation lacked its declared Ninja/compiler environment. It also
revealed that Bash `errexit` was insufficient inside command substitution; the comparator now checks
each nested build result explicitly and cannot compare a failed build. The first valid two-root run
then found that `build-info.txt` embedded its absolute distribution path. Canonicalizing that checksum
record to relative `iotox` removed the path leak. Neither failed attempt was accepted as evidence.

Separately, post-package inspection found that a Nix `postInstall` SBOM bound the executable before
Nix's fixup/strip phase. Generation and strict verification now run in `postFixup`, and the final Nix
store executable externally reverified against the installed SBOM.

## Exact nonclaims

This does not compare independent machines, compilers, libc implementations, CPU architectures, Nix
stores, or source mirrors. It does not provide bit-for-bit reproducibility of a complete deployment
image, prove source-to-binary correspondence, sign the result, establish license compliance, or
replace hosted CI. An independent-builder comparison remains an M0 distribution gate.
