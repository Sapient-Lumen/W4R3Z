# TimeSync rev0103 audit — transport integrity binding refactor

## Focus

rev0103 continues FT-0090 by targeting a transport-envelope integrity seam rather than adding doctrine or registry surface.

The risky pattern was an envelope whose adapter stub claimed `signed_payload` or `authenticated_transport` binding while the `integrity` block did not actually protect `semantic_payload`, or protected only `profile_reference` in a way that could be mistaken for a profile-binding substitute.

## What changed

- Added `tools/transport_integrity.py`.
- Wired that helper into `check_transport_envelope` after `tools/transport_envelope_temporal.py`.
- Added checks for:
  - `semantic_only` envelopes must not claim transport authentication or payload signature.
  - `authenticated_transport` envelopes must carry `integrity.protection: transport_authenticated` and cover `semantic_payload`.
  - `signed_payload` envelopes must carry `signed_payload` or `detached_signature` protection and cover `semantic_payload` or `semantic_payload_digest`.
  - `profile_reference` cannot be the only integrity cover; profile digest obligations remain in the semantic payload.
- Added three derivation-checked negative fixtures and semantic vectors `TV-N276` through `TV-N278`.

## Why this was risky

Earlier transport work correctly prevented envelope `sent_at` from becoming freshness and prevented transport metadata from satisfying profile obligations. But the binding-strength claim itself was still under-enforced: a syntactically valid envelope could advertise stronger carriage while failing to protect the semantic payload it was carrying.

That is a real confusion boundary because signed/authenticated transport can be useful, but it must not become an implied TimeState provenance credential or a replacement for payload profile digests.

## Waste/refactor note

The new helper is intentionally small. It removes transport-integrity semantics from the monolithic validator without introducing new schema fields or a transport registry. The three new negatives are rendered JSON fixtures for audit review and derivation-checked from existing positive transport examples.

## Boundary retained

rev0103 does not validate cryptographic signatures. It validates only the semantic coherence of the envelope's declared binding strength and coverage labels.

Transport integrity still does not update TimeState, freshness, profile assessment, policy acceptance, or actionability.

## Remaining risk

FT-0090 remains open. The remaining work is mostly maintainability: continue extracting validator concern families only where code gets smaller, more testable, or harder to misuse, and keep converting bulky fixture families to derivation-checked rendered examples where that prevents real drift.
