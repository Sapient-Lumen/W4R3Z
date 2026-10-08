# 28 — Profile digest canonicalization

Profile digests bind normative profile rules. They do not bind rendered markdown, source packets, transport envelopes, operator aliases, or external compliance certificates.

## Canonical input

For each profile applicability map, compute the digest over the JSON object after removing only this field:

```text
normative_rules_digest
```

All other profile fields are normative for the digest, including:

```text
authority
id
version
lifecycle_state
purpose
dominant_timing_pressure
obligations
applicability_labels
fallback_mappings
reference_policy
evidence_policy
```

## Serialization

The canonical serialization used by this archive is the TimeSync JCS/RFC 8785 subset implemented in `tools/jcs.py`:

```text
JSON object
I-JSON duplicate-member rejection before validation
lone-surrogate string rejection
UTF-8 output
sort object member names lexicographically by UTF-16 code units
separators: comma and colon with no extra whitespace
non-ASCII strings emitted as-is, without normalization
safe-integer JSON numbers only for current TimeSync-owned digest surfaces
hash: SHA-256 over the serialized bytes
hex lowercase representation
```

In Python terms, the validator uses:

```text
tools/jcs.py canonicalize(obj).encode('utf-8')
```

A future profile rule that needs fractional or higher-precision numeric values must encode those values as strings or move the commitment to an external byte envelope. The current digest-bound profile catalog intentionally fails closed rather than relying on Python or ECMAScript number edge behavior.

## Rendered markdown

Profile markdown files render the catalog digest for human review. They are not the canonical digest input.

The validator checks that each `profiles/P*.md` rendered digest matches `profiles/profile-catalog.json` so humans do not see stale profile-rule hashes.

## Compatibility use

A compatibility statement may compare profile digests. Exact digest equality is deterministic equivalence only for the canonical digest scope above. Any non-identical compatibility relation is an authority assertion and remains subject to local policy acceptance.
