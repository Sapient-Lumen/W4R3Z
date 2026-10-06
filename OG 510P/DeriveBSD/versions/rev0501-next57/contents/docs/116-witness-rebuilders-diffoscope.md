# Witness rebuilders + deep diffs (independent verification lane)

Reproducible-build ecosystems increasingly rely on **independent rebuilders** and deep diffs to detect divergence.
This maps directly to DeriveBSD’s “treat builders hostile” stance.

References:
- `diffoscope` (deep artifact comparisons). https://diffoscope.org/
- Arch/independent rebuilder tooling example: `rebuilderd`. https://github.com/kpcyrd/rebuilderd
- Reproducible Builds tools index. https://reproducible-builds.org/tools/
- reprotest (variation testing harness). https://salsa.debian.org/reproducible-builds/reprotest
- OSS-Rebuild stabilization docs (optional functional equivalence helpers). https://docs.oss-rebuild.dev/stabilizers/
- Debian buildinfo files (recording build environments): https://wiki.debian.org/ReproducibleBuilds/BuildinfoFiles
- reproduce.debian.net (rebuilds from `.buildinfo`): https://reproduce.debian.net/

## DeriveBSD direction

Optional policy requirement:
- an artifact is only “promotable” if N independent witnesses can rebuild and attest:
  - same Plan digest
  - same Build Record digest (buildinfo-like)
  - same closure manifest digest
  - same artifact digest (or explainable, policy-allowed divergence)

Witnesses emit DSSE/in-toto attestations bound to artifact digests.

## When diffoscope is useful

If witness rebuilds differ:
- produce a diff report object (large diffs stored as CAS objects; summaries surfaced in JSON)
- allow humans (or LLM tooling) to see the *why* of divergence

## v1 minimalism

- only do this for high-value targets (base sets, microVM runtimes)
- keep witness requirements policy-controlled

Toolchains are a special case: for compilers, high-assurance channels may add **DDC** as an extra lane.
See: `docs/191-diverse-double-compiling-and-bootstrappable-toolchains.md`.

See RFC-0084.
