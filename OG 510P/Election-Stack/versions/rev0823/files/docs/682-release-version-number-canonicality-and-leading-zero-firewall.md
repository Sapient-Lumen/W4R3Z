# 682 — Release version-number canonicality and leading-zero firewall

**Track:** Shared / Release engineering

This document records a v807 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

Earlier control-file hardening made `VERSION` byte-canonical: single LF-terminated line, no CRLF, no surrounding whitespace, and a `vNNN` shape. The parser still accepted numerically ambiguous forms such as:

```text
v0807
```

That string is syntactically version-like, but it creates two different human and machine readings of the same release number: the archive filename convention uses zero padding in `rev0807`, while the internal release identity uses the unpadded semantic form `v807`. Allowing `v0807` in `VERSION` would make extracted-tree verification more tolerant than the deterministic release naming contract.

## Reconstruction rule

`VERSION` is canonical only when it is exactly:

```text
v<decimal integer without leading zeroes>\n
```

`v0` is reserved as the only zero form. All other numeric forms must begin with `1` through `9`. Therefore:

- `v807\n` is canonical;
- `v0807\n` is not canonical;
- `v00807\n` is not canonical;
- `v807 \n`, ` v807\n`, `v807\r\n`, and `v807\n\n` remain non-canonical.

The archive filename may still carry a padded `rev0807` marker for lexical sorting, but verifiers normalize that filename marker to the semantic internal identity `v807` before comparing it with `VERSION`.

## Enforcement surfaces

v807 tightens `scripts/release_control_files.py` so both text and byte-level `VERSION` parsers use the same no-leading-zero decimal grammar.

v807 also extends `scripts/check_release_control_files.py` with a negative probe for `v0999\n`, keeping this rule covered by the release gate alongside CRLF, whitespace, missing-LF, duplicate manifest, unsorted manifest, uppercase digest, and extraction-shape probes.

The existing verifier surfaces inherit the stricter parser:

- `scripts/verify_release_zip.py`
- `scripts/verify_manifest.py`
- `scripts/build_release_zip.py` default filename generation
- `scripts/check_version_consistency.py` through the checked-in canonical `VERSION`

## Operator effect

Use semantic internal versions such as:

```text
v807
```

Use padded `rev0807` only in release artifact filenames. Do not place the padded form in `VERSION`, changelog headings, packet tool-version fields, or verifier report payloads.

## Non-claims

This does not change the release numbering scheme, create a new schema, change artifact hashes outside the versioned example packet re-addressing, or make semantic claims about election process behavior. It is a parser and verifier strictness rule for release reconstruction.

## Compression posture

This revision adds one compact release-engineering document and one parser negative probe. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/669-release-control-file-byte-canonicality-and-crlf-firewall.md`
- `scripts/release_control_files.py`
- `scripts/check_release_control_files.py`
- `scripts/verify_release_zip.py`
- `scripts/verify_manifest.py`
