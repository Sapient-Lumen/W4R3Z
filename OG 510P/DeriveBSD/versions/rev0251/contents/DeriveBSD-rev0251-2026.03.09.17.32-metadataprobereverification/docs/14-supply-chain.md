# Supply chain security

Curated refs: `docs/32-curated-references.md`.

## Source integrity

- All sources pinned in `derive.lock` with cryptographic hashes.
- Prefer immutable refs: content-addressed tarballs, git commits (not branches/tags).
- Fetching through a dedicated fetcher with TLS verification and mirror/fallback rules.

## Artifact integrity

- Store paths are hash-addressed (input-graph keyed) and always verified.
- Binary cache artifacts must be signature-verified before use.

## Closure integrity

Distribution/activation should rely on a closure manifest + signature (“closure proof”) so that what runs is fully declared and verifiable.
See `docs/90-closure-proof.md`.

## Provenance (minimum viable)

Record: Spec/Lock/Plan digest, toolchain id, sandbox policy, source hashes, builder identity.

## Attestation (next tier)

- Signed attestations bound to artifact hash.
- Optional transparency log.
- For high-value artifacts: multi-builder or reproducibility checks.

## Policy gates

- trusted cache key allowlists
- channel metadata with anti-freeze/rollback (TUF-inspired) — see `docs/61-channel-metadata-tuf-inspired.md`
- forbid unsigned artifacts
- forbid network builds
- vuln gates / blocklists

## Interop formats (recommended)

- Provenance attestations: in-toto Statement + DSSE envelope (see `docs/31-provenance-and-sbom.md`).
- Optional SBOM emission: SPDX or CycloneDX (policy-controlled).

## Firmware is supply chain too

Supply-chain integrity cannot stop at packages. Firmware (driver blobs, device updates, platform capsules) must be treated as digest-first inputs and receipted operations so A–D postures remain auditable.

See: `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`.

Last updated: 2026-02-27r125

## Source availability (URL-rot resilience)

Integrity is not enough if sources disappear. DeriveBSD should optionally record archival identities (e.g., **SWHID**) and support policy-governed fallback resolvers (mirrors, mirror kits, Software Heritage) while remaining **hash-first**.

See: `docs/403-swhid-fallback-and-long-term-source-availability.md`.

