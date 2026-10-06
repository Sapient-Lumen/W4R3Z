# In-toto / SLSA attestation export as an adapter lane (interop without forking evidence)

**Tier:** E (Adapter)
**Profiles:** A, B, C, D
**Pillars:** supply-chain, operability
**Patterns:** Adapter→Shadow→Replace, Bundles

Many ecosystems now expect **standard attestations**:

- DSSE envelopes + in-toto Statements (generic container)
- SLSA build provenance predicates (common “what built this artifact?” shape)

DeriveBSD already produces **richer, typed receipts** for its own pipeline.
The goal is not to replace DeriveBSD evidence with external formats.
The goal is to provide **killable interop** so downstream tooling can bootstrap.

This doc defines a conservative adapter lane:

- map a bounded subset of DeriveBSD receipts into an in-toto Statement (optionally DSSE wrapped)
- keep the adapter output **digest-addressed** and policy-governed by `export.policy`
- emit a DeriveBSD-native report (`attestation.adapter.intoto.report`) so exports remain queryable and bundle-friendly

## Why this is an adapter lane (not “the new evidence format”)

External formats are valuable, but they are **not DeriveBSD’s coherence spine**:

- DeriveBSD receipts encode **plans, policies, and join keys** that don’t fit cleanly into one Statement.
- Many ecosystems only verify *some* fields (subject digests + builder id), leaving gaps.

So we treat standard attestations as:

- **Adapter**: export a projection for consumers.
- **Shadow**: keep exporting while verifiers compare against DeriveBSD evidence.
- **Replace**: only if/when a standard truly covers our needs (unlikely; prefer keep adapter killable).

## The evidence artifact: `attestation.adapter.intoto.report`

When the adapter emits external attestations, it also emits a DeriveBSD evidence object that records:

- which DeriveBSD receipts were mapped (digests)
- which export policy / redaction transform governed the emission (digests)
- which statement/envelope bytes were produced (digests + optional refs)
- whether the mapping was **lossy** (and why)

Schema: `spec/attestation.adapter.intoto.report.schema.json`
Example: `spec/examples/attestation.adapter.intoto.report.json`

This keeps the export **auditable and supportable** without shipping the entire evidence vault.

## Wiring (what to include in drift/support bundles)

When support bundles or drift bundles include external attestations, include:

- `attestation.adapter.intoto.report` (the join key)
- the referenced statement/envelope bytes (if policy allows)
- the DeriveBSD receipts referenced by the report (or their digests + retrieval hints)

This keeps the bundle self-describing:

- *what was exported?* (report)
- *what bytes were shipped?* (statement/envelope digests)
- *what did we base it on?* (receipt digests)

## Policy + killability

- Exports are always governed by `export.policy`.
- The adapter lane itself must be killable via `adapter.kill.policy`.

Strict profiles typically require:

- explicit operator consent before exporting attestations
- redaction transforms for bundle-min / incident workflows
- two-person integrity when enabling new export scopes

See: `docs/251-export-policies-and-support-bundle-portal.md`, `docs/402-adapter-lanes-and-strangler-discipline.md`, `docs/444-adapter-kill-policy-diff-as-review-surface.md`.

## References (primary)

- in-toto Statement v1 spec: https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md
- in-toto Envelope (DSSE) v1 spec: https://github.com/in-toto/attestation/blob/main/spec/v1/envelope.md
- SLSA spec v1.2: https://slsa.dev/spec/v1.2/
- SLSA Build Provenance (predicate): https://slsa.dev/spec/v1.2/build-provenance
- Cosign attestation verification (ecosystem verifier example): https://docs.sigstore.dev/cosign/verifying/attestation/

Last updated: 2026-02-28r176
