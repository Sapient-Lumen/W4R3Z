# 176. Reproducibility, Attestation Boundary, Evidence-Chain Custody, Rollback, and Public-Release Packet Governance

## Core thesis

A release decision can pass local gates and still leave an ambiguity about how the package was built, what evidence was actually carried forward, whether any attestation is signed, what must happen if a release claim is defeated, and what a public-facing handoff is allowed to say. Rev0169 asked whether release permission had been laundered. Rev0170 asks whether release **execution** and release **attestation language** have been laundered.

The target is not to claim a mature software supply-chain program. The target is to prevent six narrower substitutions:

1. a build recipe being mistaken for an independently reproducible build;
2. an unsigned local attestation packet being mistaken for a cryptographic attestation;
3. a digest ledger being mistaken for legal chain of custody;
4. an execution summary being mistaken for public CI;
5. a rollback plan being mistaken for downstream recall authority; and
6. a public-release packet being mistaken for external approval.

## What this release adds

Rev0170 adds six control surfaces:

- `BUILD_REPRODUCIBILITY_LEDGER.yml` records local build inputs, generated outputs, command classes, determinism constraints, and non-claims about independent rebuilds.
- `ATTESTATION_BOUNDARY_LEDGER.yml` states that the release packet is unsigned and local, and blocks SLSA, Sigstore, in-toto, SCITT, timestamp, and non-repudiation claims.
- `EVIDENCE_CHAIN_CUSTODY.yml` records package-internal evidence artifacts and local SHA-256 digests while refusing legal or external custody claims.
- `EXECUTION_LOG_LEDGER.yml` records the local sequence of checks and report artifacts without claiming public CI or signed execution logs.
- `ROLLBACK_RETRACTION_PLAN.yml` records local triggers for package quarantine, release-language withdrawal, claim-node revision, and public-use language blocks.
- `PUBLIC_RELEASE_ATTESTATION.yml` provides a bounded, unsigned public-facing packet with explicit positive and negative assertions.

The new checker is `tools/check_repro_attestation.py`. It validates local path existence, digest custody rows, explicit signature absence, execution-report presence, rollback targets, and public-attestation exclusions.

## Build rule

A build recipe must identify the prior package, generated artifacts, local command classes, input artifacts, generated outputs, determinism constraints, and independent-rebuild boundary. The archive may say that a local recipe exists. It may not say that the zip is bit-for-bit reproducible, hermetic, independently rebuilt, externally attested, or SLSA-level compliant.

## Attestation rule

An attestation packet must name its subject, predicate artifact, evidence references, signature state, and forbidden verbs. If there is no cryptographic signature, the packet must say so. The words “attestation,” “provenance,” and “release packet” must not silently imply signer identity, timestamp authority, transparency-log inclusion, or non-repudiation.

## Evidence-chain custody rule

A custody row must identify a package-internal artifact, digest, custodian role, custody state, and mutation rule. A custody row is not legal custody, independent escrow, notarization, immutable storage, or external repository history. Digest rows support local tamper detection only after the package is available for comparison.

## Execution-log rule

A local execution log must name the tools, reports, and expected status families used during release. It must not claim remote runner identity, public CI, signed logs, or independent execution. Missing reports block execution-log claims.

## Rollback and retraction rule

A rollback trigger must name the condition, action, and affected release-language or claim targets. Retraction is local unless an external notification, public issue tracker, downstream registry, or distribution map actually exists. Rev0170 records no such public recall infrastructure.

## Public-release packet rule

A public-release packet must include positive assertions, negative assertions, evidence references, decision reference, signature state, and forbidden claims. Positive assertions may describe local artifacts and checks. Negative assertions must explicitly block signed attestation, external approval, public deployment readiness, formal supply-chain conformance, source-current factual approval, and high-stakes reliance.

## Allowed claims after rev0170

The package may claim that it includes a local build recipe, local attestation-boundary ledger, local evidence-custody digest rows, local execution-log ledger, local rollback/retraction plan, local unsigned public-release packet, and a checker that verifies representative structural integrity among these artifacts.

## Forbidden upgrade claims

The package must not claim bit-for-bit reproducibility, hermetic builds, independent rebuild, signed provenance, Sigstore/cosign signature, in-toto attestation, SCITT transparency receipt, SLSA level, CycloneDX BOM conformance, legal chain of custody, notarized timestamp, public CI, public release-management service, external approval, operational deployment readiness, source currency, regulatory assurance, or domain authority.

## Open debt retained

- Build reproducibility is recipe-level and local, not independent or bit-identical.
- Attestation is an unsigned local packet, not a cryptographic statement.
- Custody is path-and-digest custody inside the package, not legal custody or external escrow.
- Execution logging is summarized locally, not public CI or signed transcript retention.
- Rollback is local language withdrawal and package supersession, not downstream recall.
- Public-release attestation is a warning-retaining handoff packet, not public-use authorization.

## Next likely layer

The next durable layer should be distribution-and-derivative-governance: downstream package identity, derivative summaries, public notice boundaries, user-facing changelog semantics, redaction/withdrawal notices, and external-publication thresholds. Rev0170 prepares for that by separating unsigned local attestation from public-facing release language.
