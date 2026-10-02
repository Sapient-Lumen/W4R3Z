# ADR 0145: Verify synchronization source objects before offering them

Date: 2026-08-24

Status: accepted

## Context

A valid signed HEAD names immutable artifact and manifest digests, but durable publisher storage can
rot after publication. A provider that trusts only the pathname could offer bytes that no longer
match the signed identity. The subscriber would eventually reject those bytes, but it would consume
transport, staging, and verification capacity first, and the provider would continue advertising a
revision it cannot honestly serve.

The existing publisher seam verifies each requested object under the namespace transaction before
creating a file offer. Local `sync-repair` can quarantine mismatched objects, and deterministic
publication can reconstruct the same digest-named objects from unchanged source content. Those
properties need one explicit recovery contract and genuine carrier evidence.

## Decision

- Verify every immutable publisher object against its requested digest immediately before offering
  it. A missing or mismatched object is unavailable; its bytes and a file offer do not leave the
  provider.
- Treat publisher unavailability as a terminal failure of that subscriber job. Clear its private
  staging and preserve accepted HEAD, activation, immutable inventory, and visible tree truth.
- Keep repair explicit. `sync-repair NAMESPACE` quarantines every mismatched private object without
  changing the signed HEAD or silently manufacturing replacement bytes.
- Permit exact duplicate publication from unchanged source to recreate quarantined artifact and
  manifest objects. The signed generation and all three revision identities must remain unchanged.
- Require an explicit subscriber retry after the provider reports recovery. The retry still verifies
  both objects, accepts the HEAD last, and activates only through the exact token.
- Bind refusal, predecessor preservation, quarantine counts and bytes, exact republication,
  convergence, and activation into both guest receipts and the content-free pair manifest over
  observed direct UDP and forced TCP.

## Consequences

Publisher-side bit rot fails near its origin and does not consume subscriber object admission. A
signed HEAD can remain durable while its local serving set is temporarily incomplete; operators can
retain forensic quarantine bytes and reconstruct the exact revision without inventing a new signed
generation. Recovery is observable and deliberately retried rather than hidden inside an ambiguous
request.

This does not make one publisher highly available, repair source content, discover corruption before
an object is requested, prove every filesystem or storage fault, or add multi-source fallback.
Periodic scrubbing and source-independent replication remain separate work.
