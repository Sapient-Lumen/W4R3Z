# 683 — Release filename version-token coherence firewall

**Track:** Shared / Release engineering

This document records a v808 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v807 made the internal `VERSION` file canonical: the archive identity is the unpadded semantic form, such as `v807`, while release artifact filenames may keep padded `rev0807` markers for lexical sorting.

The remaining filename seam was token selection. A verifier that reads only the first version-like token in an artifact filename can accept a confusing carrier name such as:

```text
The-Election-Stack-rev0808-v807.zip
```

The ZIP payload may still be byte-canonical, but the filename now carries two different release claims. A human, ticketing system, object store, or mirror index could route the artifact under the wrong release even though the internal `VERSION` entry remains correct.

## Reconstruction rule

Filename version markers are optional for local diagnostic ZIP names. Once present, every release-version token in the filename is evidence-bearing metadata and must cohere.

The accepted token forms are:

- `revNNNN` as an artifact-sort token; leading zeroes are allowed here and normalize by integer value;
- `vNNN` as a semantic token; it must use the same unpadded lowercase grammar as `VERSION`.

Therefore:

- `The-Election-Stack-rev0808.zip` carrying `VERSION` `v808\n` is coherent;
- `The-Election-Stack-rev0808-v808.zip` carrying `VERSION` `v808\n` is coherent;
- `The-Election-Stack-rev0808-v807.zip` is not coherent;
- `The-Election-Stack-v0808.zip` is not coherent, because padded semantic `v` tokens are forbidden even when they normalize numerically to `v808`.

A filename without a release-version token remains acceptable for local negative probes and ad hoc diagnostics; absence of a token is not promoted into a release claim.

## Enforcement surfaces

v808 tightens `scripts/verify_release_zip.py` so the artifact verifier scans all `revNNNN` and `vNNN` tokens in the filename, normalizes them, rejects token disagreement, rejects padded semantic `v` tokens, and compares every token against the internal `VERSION` entry.

v808 also extends `scripts/check_release_zip_verifier.py` with three probes:

- a positive mixed-token probe (`rev0808-v808`) that must pass;
- a conflicting-token negative probe (`rev0808-v807`) that must fail closed;
- a padded semantic-token negative probe (`v0808`) that must fail closed.

## Operator effect

Use one of these carrier styles for published release artifacts:

```text
The-Election-Stack-rev0808.zip
The-Election-Stack-rev0808-v808.zip
The-Election-Stack_v808.zip
```

Do not publish artifacts whose filenames contain conflicting release tokens, padded semantic `v` tokens, or casual extra version markers copied from a previous release name.

## Non-claims

This does not require every local diagnostic ZIP filename to contain a version token. It does not change member bytes, schema semantics, voting-process claims, or the internal release number grammar. It only prevents carrier filenames from making contradictory or non-canonical release-version claims when they choose to carry version tokens.

## Compression posture

This revision adds one compact release-engineering document and two filename-token negative probes. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/682-release-version-number-canonicality-and-leading-zero-firewall.md`
- `scripts/verify_release_zip.py`
- `scripts/check_release_zip_verifier.py`
