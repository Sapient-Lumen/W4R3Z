# 670 — Release ZIP deflate-stream canonicality and verifier rebuild

**Track:** Shared / Release engineering

This document records a v795 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

By v794 the release ZIP verifier checked member names, manifest closure, canonical control-file bytes, local/central-directory layout, timestamps, modes, and other ZIP metadata. One raw-byte seam remained: a ZIP can carry the same member payload bytes and the same manifest hashes while using a different legal deflate stream.

That shape is not a content-integrity failure in ordinary ZIP usage, but it is a release-artifact canonicality failure. If the Election Stack ZIP is treated as an evidence-bearing release object, the compressed byte stream is part of the object being distributed, cited, mirrored, and hashed.

## Reconstruction rule

A deterministic release ZIP must be byte-for-byte equal to the canonical rebuild produced from its own sealed member payload bytes under the release ZIP writer rules:

1. read each member payload from the archive;
2. order members by canonical release path;
3. write each member through the fixed ZIP metadata policy;
4. use `ZIP_STORED` so member bytes are not compressor-runtime dependent;
5. require the rebuilt ZIP bytes to equal the original archive bytes exactly.

This rule complements, rather than replaces, `MANIFEST.sha256`: the manifest proves payload bytes; the verifier rebuild comparison proves the surrounding ZIP byte stream is the canonical encoding of those payloads.

## Enforcement surfaces

v795 extends `scripts/verify_release_zip.py` with a canonical rebuild comparison. The verifier now rebuilds a ZIP in memory from the in-archive member bytes using the same metadata and compression settings as the deterministic release builder, then rejects the archive if the rebuilt byte stream differs.

v795 also extends `scripts/check_release_zip_verifier.py` with a negative probe that preserves valid member bytes and manifest hashes but rewrites the archive with a different legal deflate stream. That probe must fail with a canonical-rebuild diagnostic.

## Operator effect

No new recipient command is required. The existing archive verifier is stricter:

```bash
python3 scripts/verify_release_zip.py The-Election-Stack-revNNNN-*.zip
```

A passing result now means the archive is not merely a valid ZIP containing the sealed files; it is the canonical ZIP byte stream for those sealed files under the release writer policy.

## v801 supersession note

`docs/676-release-zip-stored-member-compressor-independent-canonicality.md` supersedes the DEFLATE-specific portion of this rule. The canonical rebuild comparison remains, but release members are now stored without compression so recipients do not depend on matching DEFLATE encoder output.

## Non-claims

This does not add signing, timestamping, supply-chain attestation, or transport authentication. It does not claim that every ZIP implementation in the world emits identical deflate bytes. It says that this release verifier and release builder treat the deterministic ZIP byte stream itself as the object to be reproduced and rejected on drift.

## Compression posture

This revision adds one compact maintainer-control document and extends existing stdlib verifier/gate code. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/659-release-archive-self-verification-and-single-source-packaging-predicate.md`
- `docs/660-release-zip-canonical-byte-layout-overlay-and-preamble-firewall.md`
- `docs/663-release-zip-permission-canonicalization-and-extraction-rebuild-invariance.md`
- `scripts/verify_release_zip.py`
- `scripts/check_release_zip_verifier.py`
- `scripts/build_release_zip.py`
