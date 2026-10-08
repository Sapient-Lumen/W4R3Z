# 676 — Release ZIP stored-member compressor-independent canonicality

**Track:** Shared / Release engineering

This document records a v801 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

By v800, `scripts/verify_release_zip.py` treated the raw release ZIP bytes as canonical and rebuilt the archive from sealed member payloads. That closed alternate legal deflate-stream encodings, but it also made verifier acceptance depend on the local ZIP/DEFLATE writer producing exactly the same compressed bytes.

That is a portability smell for an offline recipient verifier. Payload hashes, member names, metadata, local/central-directory layout, and publication shape should be strict; compressor-runtime drift should not be an ambient dependency that recipients must guess.

## Reconstruction rule

A deterministic Election Stack release ZIP now stores member payload bytes with `ZIP_STORED` rather than `ZIP_DEFLATED`:

1. member order remains canonical release-path order;
2. timestamps remain fixed at `1980-01-01T00:00:00`;
3. modes remain canonical `0644`;
4. local and central directory metadata remain byte-checked;
5. compressed size must equal uncompressed size for every stored member;
6. the verifier still rebuilds the whole ZIP byte stream from sealed member payloads and requires byte-for-byte equality.

The archive is larger, but the canonical byte stream no longer depends on a local zlib version or compression-level implementation detail.

## Enforcement surfaces

v801 changes `scripts/build_release_zip.py` to write release members as `ZIP_STORED` entries. It changes `scripts/verify_release_zip.py` to reject deflated entries, require stored local/central sizes to agree, and keep the canonical rebuild comparison over stored payload bytes.

v801 also updates `scripts/check_release_zip_verifier.py` so the negative probe rewrites a good stored archive as a deflated ZIP while preserving member payload bytes and `MANIFEST.sha256`; the verifier must reject that archive by compression method.

## Operator effect

Recipient commands are unchanged:

```bash
python3 scripts/verify_release_zip.py The-Election-Stack-revNNNN-*.zip
python3 scripts/extract_release_zip.py The-Election-Stack-revNNNN-*.zip ./election-stack-vNNNN
python3 scripts/verify_manifest.py ./election-stack-vNNNN
```

The ZIP artifact grows because it no longer compresses member payloads. The benefit is that archive byte-canonicality is now independent of DEFLATE encoder behavior.

## Non-claims

This does not add signing, timestamping, transport authentication, or a hostile-filesystem sandbox. It does not make `MANIFEST.sha256` optional. It narrows the release-archive encoding so the official verifier and builder agree without depending on compressor-specific byte output.

## Compression posture

This revision adds one compact release-engineering document and updates existing stdlib builder/verifier smoke checks. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/659-release-archive-self-verification-and-single-source-packaging-predicate.md`
- `docs/660-release-zip-canonical-byte-layout-overlay-and-preamble-firewall.md`
- `docs/670-release-zip-deflate-stream-canonicality-and-verifier-rebuild.md`
- `scripts/build_release_zip.py`
- `scripts/verify_release_zip.py`
- `scripts/check_release_zip_verifier.py`
