# rev0107 audit — discovery binding refactor

## Problem

Discovery freshness, semantic-version negotiation, and digest binding were checked in separate places. That allowed a current-use result to be fresh and version-approved while not actually digest-bound.

The dangerous pattern was:

```json
{
  "version_negotiation": {
    "decision": "accepted_exact",
    "current_use_allowed": true
  },
  "freshness": {
    "freshness_status": "fresh_for_current_use"
  }
}
```

with no `digest_binding` block. The result was recent, but not bound.

## Refactor

`tools/discovery_binding_semantics.py` now owns the discovery result binding checks. `tools/validate_archive.py` keeps orchestration and nested fixture dispatch, but no longer owns semantic-version parsing, downgrade proof checks, or current digest binding metadata rules.

## New executable rules

```text
current discovery result requires digest_binding metadata
version-negotiated current discovery result requires digest_binding.current_use_allowed true
digest-bound current discovery result requires version_negotiation.current_use_allowed true
request require_digest_binding_policy requires digest_binding_policy_digest for current results except digest_binding_policy itself
```

## Boundary preserved

`freshness` remains a discovery-interpretation gate only. It does not update TimeState, profile assessment, or actionability, and it does not substitute for digest binding.

## Next useful target

The next extraction should probably be either:

```text
digest-binding policy / semantic-version policy helper extraction
```

or a selective derivation cleanup of old discovery/aggregate copied negatives. Avoid adding a new discovery registry unless a concrete invariant cannot be enforced without one.
