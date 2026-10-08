# Remedy-hardening-attestation downstream audience reliance review page — did the governed audience actually stop relying on stale state?

## Purpose

This page is the forced-review surface for deciding whether stale state stopped influencing the named audience.
It exists to stop the operator from exiting with a comfortable beneficiary-local story while downstream dependents, delegated consumers, or exported artifacts still drive stale behavior.

## Opening question

The page must ask, in plain language:

**did the governed audience actually stop relying on stale state, or do some downstream dependents, exports, caches, or delegates still consume it?**

## Required reviewer prompts

The reviewer must answer at least:

1. What is the exact governed audience boundary?
2. Which direct dependents were positively refreshed?
3. Which transitive dependents remain inferred rather than proved?
4. Which stale-artifact classes remain active?
5. Did we only revoke future updates, or did we also retire already-landed stale copies?
6. Which downstream nodes still carry unresolved stale-dependency risk?
7. What is the strongest honest audience-wide sentence now?
8. What stronger sentence is still blocked, and by what missing coverage?

## Required answer states

The page must support at least:

- beneficiary repaired only
- direct dependents refreshed only
- direct plus delegated dependents refreshed
- stale exports still active
- stale caches still active
- transitive audience coverage under-proven
- named audience retired, broader public reach unproven
- later contradiction reopened downstream reliance risk

## Evidence discipline

For every answer, the review page must show:

- positive evidence
- contradictory evidence
- coverage gap
- sentence consequence

If any answer relies on inference rather than direct proof, that inference must be labeled and must cap the strongest sentence.

## Decision rail

The review must end with a forced choice among at least:

- only beneficiary-local repair proven
- narrow downstream retirement proven
- audience-wide stale-dependency retirement proven for named boundary only
- reliance truth still blocked by unresolved residue
- later contradiction reopened the question

## Comparison rail

The page must keep these pairs visibly separate:

- beneficiary-local adherence / audience-wide reliance
- future revocation / stale-copy retirement
- direct coverage / transitive coverage
- named audience / broader public
- no contradiction seen / positive retirement proof

## Interaction requirements

The reviewer must be able to:

- click any uncovered downstream node and see why it remains unresolved
- open a fan-out coverage drawer that shows direct, delegated, and transitive percentages separately
- downgrade the strongest sentence in one gesture when any unresolved stale class is marked active
- compare several candidate audience boundaries before locking the receipt sentence

## Hard rules

The page must never allow:

- the audience boundary to remain implicit
- a disconnect action to erase landed residue
- a clean direct-dependent view to hide transitive uncertainty
- `most likely refreshed` to render as `audience retired` without an explicit inference badge
