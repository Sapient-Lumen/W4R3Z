# Evidence Bundle Core Kit — lane boundaries (2026-03-21)

This note exists to keep **P-0256 Evidence Bundle Core Kit** from collapsing back into a vague “signed bundle” idea.

## Main judgment

The missing crate should now be read as a reviewable contract across five distinct truths:

1. **container basis** — deterministic container / digest / canonicalization rules;
2. **entry lineage** — raw vs projected vs generated vs imported vs redacted provenance;
3. **attestation lane** — DSSE / COSE / Sigstore / unsigned posture;
4. **publication route** — local-only vs OCI-attached vs transparency/publication path;
5. **share-safety posture** — private vs redacted-shareable vs encrypted/manual-review.

The sharper product is the compact reusable layer at those five truths plus explicit domain-profile contracts above them.

## Distinct from domain profile crates

Conformance kits, verification campaigns, replay bundles, trusted-publishing packs, and assurance packs may all reuse **P-0256**.
But their domain-specific reports do not become part of the core substrate.

## Distinct from raw attestation standards

in-toto, DSSE, COSE, and Sigstore define attestation/signature semantics.
**P-0256** should import or carry them cleanly, not reinterpret or replace them.

## Distinct from publication infrastructure

OCI referrers, ORAS workflows, and SCITT-style transparency/publication systems are publication lanes.
They are important, but they are not the same thing as the local bundle substrate.

## Distinct from share-safety policy alone

Redaction is necessary but not sufficient.
A bundle may be redacted yet still unsuitable for general sharing because of residual secrets, legal sensitivity, or unreviewed generated summaries.
That is why **share-safety posture** must remain distinct from the redaction receipt.

## Practical rule for future passes

When a proposal wants to emit a portable bundle, it must now say explicitly:

1. what the **container basis** is,
2. how **entry lineage** is preserved,
3. which **attestation lane** is present,
4. whether any **publication route** exists or is entirely out of scope,
5. and what **share-safety posture** the exported pack claims.

Do not let a future pass silently flatten local validation, signatures, OCI attachment, transparency submission, and “safe to email” posture into one fake green result.

## Archive hygiene note

The fixture family currently lives under `fixtures/evidencebundle-core-kit/`.
Treat that path as the canonical legacy fixture root until a deliberate bulk-rename pass happens.
Do not oscillate between `evidencebundle` and `evidence-bundle` spellings within the same revision.

## Sources

- https://github.com/in-toto/attestation/blob/main/spec/v1/envelope.md
- https://github.com/in-toto/attestation/blob/main/spec/README.md
- https://docs.sigstore.dev/about/bundle/
- https://github.com/sigstore/sigstore-go/blob/main/docs/signing.md
- https://oras.land/docs/concepts/reftypes/
- https://github.com/opencontainers/distribution-spec/blob/main/spec.md
- https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/
