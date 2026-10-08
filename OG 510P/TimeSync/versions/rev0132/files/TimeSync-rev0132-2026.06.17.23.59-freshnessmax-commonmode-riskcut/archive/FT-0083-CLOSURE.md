# FT-0083 closure — correction-authority lifecycle, revocation, emergency withdrawal, and contestation

FT-0083 asked whether aggregate correction-authority references should carry lifecycle and revocation posture, emergency-withdrawal handling, and post-publication contestation semantics without becoming an authority registry, publication repository, or provenance system.

rev0084 answers yes, but only as aggregate publication-interpretation metadata.

## Decision

Add required `authority_lifecycle` inside `aggregate_correction_authority_reference`.

The surface records compact lifecycle state, revocation-check posture, emergency-withdrawal posture, contestation posture, and explicit non-leakage/non-upgrade boundary flags.

## Non-goals preserved

rev0084 does not define or export:

- correction-authority rosters,
- key material,
- revocation endpoints,
- repository topology,
- emergency-response plans,
- incident forensics,
- legal-process details,
- contesting-party identities,
- external lifecycle record semantics,
- TimeSync provenance.

## Validator-backed closure

rev0084 adds positive fixtures for active lifecycle and emergency-withdrawn historical interpretation, plus negative fixtures for revoked-current, expired-current, emergency-current, contested-current, lifecycle leakage, malformed discovery, and evidence-class misuse.

FT-0083 is closed in rev0084.
