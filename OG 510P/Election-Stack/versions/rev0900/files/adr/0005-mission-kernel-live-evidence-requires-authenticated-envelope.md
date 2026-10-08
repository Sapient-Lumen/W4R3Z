# ADR 0005: Mission-kernel live evidence requires an authenticated EvidenceEnvelope

**Track:** A (deployable mission kernel) / Shared trust boundary

- Status: **Accepted**
- Date: **2026-06-18**

## Context

The mission-kernel submitter can hash operator-supplied files and attach review metadata. In v891-v893, the intake path could treat a syntactically valid SHA-256 digest plus a free-text `approving_role` as `live_valid` and advance a complete row to `STAGED_PENDING_AUTHORITY_REVIEW_NOT_LIVE_READY`.

That state exceeded what the evidence proved. A digest binds claimed bytes but does not authenticate the issuer, prove authority delegation, bind the record to a jurisdiction and election, or establish that the supplied role approved the object. The archive already defines canonical signed `EvidenceEnvelope` objects and strict external trust-profile verification. The mission-kernel path must not create a weaker parallel meaning of “live evidence.”

## Decision

1. A bare digest submission is an **unauthenticated live candidate**, never authenticated live evidence.
2. `valid_live_evidence_object_count` and `valid_live_evidence_class_count` remain zero until the intake path verifies a canonical signed `EvidenceEnvelope` against an external trust profile and checks jurisdiction, election, payload-schema, issuer, signer authorization, and authority-scope binding.
3. A shape-complete candidate receives `CANDIDATE_COMPLETE_AUTHENTICATION_REQUIRED`; the overall decision remains `NO_GO_LIVE_EVIDENCE_AUTHENTICATION_REQUIRED`.
4. Free-text roles, local paths, ambiguous locators, duplicate work items, duplicate evidence classes, conflicting redaction/boundary values, missing retention context, and non-UTC capture timestamps fail closed.
5. Non-production drill records may exercise the same plumbing but never increment live-evidence counters or create a live-readiness claim.

## Consequences

- The mission-kernel intake now has one trust meaning consistent with `EvidenceEnvelope`, rather than a digest-only bypass.
- Existing operators can still hash and stage records, but their output is explicitly a candidate pending authentication.
- Integrating envelope verification and jurisdiction trust governance is now a named precondition for any live pilot.
- The stricter boundary may reveal incomplete operator plans that v893 accepted; this is intentional.
