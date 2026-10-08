# TimeSync rev0086 — Discovery semantic-version negotiation

Discovery result items can now carry a small semantic-version and digest-binding wrapper.  The wrapper exists because digest-bound items can be syntactically valid while semantically too new, too weakly bound, or bound with the wrong byte profile.

## Request negotiation

A request may include:

```json
{
  "negotiation": {
    "request_semantic_version": "1.0.0",
    "supported_result_semantic_versions": {
      "aggregate_lifecycle_decision_table": ["1.0.0"]
    },
    "unknown_newer_version_policy": "return_metadata_only",
    "require_digest_binding_policy": true,
    "accept_legacy_canonicalization_for_current": false
  }
}
```

The request negotiation object does not require a server to return every requested item.  It tells the server how the requester wants unknown newer result versions handled.

## Result negotiation

A returned item may include:

```json
{
  "semantic_version": "1.0.0",
  "schema_uri": "https://example.invalid/timesync/schema/...",
  "version_negotiation": {
    "decision": "accepted_exact",
    "current_use_allowed": true
  },
  "digest_binding": {
    "binding_mode": "canonical_json_rfc8785",
    "canonicalization": "json_canonicalization_scheme_rfc8785",
    "current_use_allowed": true
  }
}
```

If the item version is newer than every version the requester advertised, the item may be returned as metadata-only or rejected/omitted.  It MUST NOT be accepted as current-use exact semantics.

## Safe fallback decisions

```text
accepted_exact              exact supported version, current use may be allowed
downgraded_to_supported     producer returned an older mutually supported semantic surface
returned_metadata_only      newer/unknown item is visible but not semantically consumed
omitted_unknown_newer       producer suppressed a newer item instead of risking unsafe use
rejected_unknown_newer      producer returned a negative result or error-equivalent posture
```

`accepted_unknown_newer` is intentionally not safe.  The validator rejects it for current-use items.

## Boundary

Version negotiation updates discovery interpretation only.  It does not satisfy profile evidence, reopen assessment, update TimeState, or turn a returned object into TimeSync provenance.
