# Rev0632 security-material framing and ingress ambiguity correction

## Scope

Rev0632 changes the byte construction used for normalized proof binding, effect idempotency, CloudEvents replay identity, compatibility effect keys, and new SQLite ledger identity seeds. It also rejects ambiguous security metadata and control characters before authorization.

It does **not** migrate historical replay-entry, snapshot, or transition material. Those require explicit format/schema versions and are listed as remaining debt.

## Reproduced collision

Legacy labeled-line proof and effect material embedded raw values after `name=`. The following distinct pairs were equal after serialization:

```text
A: source = "A\ncloud_event_id=B", id = "C"
B: source = "A", id = "B\ncloud_event_id=C"
```

The package validator calculates the same legacy HMAC for both:

```text
8fedb159920d09f7909364e17ee53c48653493f60b4969fbbcba332779eb6ec8
```

A separate legacy replay key used `source + "\n" + id`, so these pairs also collapsed:

```text
A: source = "A\nB", id = "C"
B: source = "A", id = "B\nC"
```

## New framing

`length_prefixed_security_tuple(domain, fields)` emits:

```text
"anonsync-length-prefixed-tuple-v1"
LEN(domain) ":" domain
LEN(field_1_name) ":" field_1_name
LEN(field_1_value) ":" field_1_value
...
```

Concatenation is byte-for-byte with no implicit text normalization. `LEN` is the ASCII decimal byte length produced from `std::string::size()`. Domain and field names are authenticated/hashed components, not comments.

The fixed prefix and each length make the component sequence parseable without searching for a delimiter inside values. Separate protocol domains prevent cross-protocol reuse.

## Domains

| Purpose | Rev0632 material domain/profile |
|---|---|
| Object/event proof | `anonsync-proof-binding-v2`; HMAC profile `anonsync-proof-binding-v2-lp-hmac-sha256` |
| Normalized external effect | `anonsync-effect-idempotency-v2` |
| CloudEvents replay identity | `anonsync-cloud-event-identity-v2` |
| Pre-normalized compatibility effect | `anonsync-effect-idempotency-legacy-v1` |
| New SQLite ledger identity seed | `anonsync-sqlite-ledger-instance-v2` |

The proof remains HMAC-SHA256 because this revision preserves fixture behavior. The framing correction does not turn it into proof-of-possession.

## Changed paths

- `include/anonsync_core_internal.hpp`
  - declares tuple framing and control detection;
  - imports OpenSSL RNG support.
- `src/json_codec_crypto.cpp`
  - implements byte-length framing and ASCII-control detection.
- `src/normalizer_envelopes.cpp`
  - switches proof and effect material to v2 domains;
  - rejects case-insensitive duplicate metadata and controls;
  - quarantines control-bearing route/event identity before proof evaluation.
- `src/replay_ledger.cpp`
  - switches JSONL event identity and compatibility effect fallback to framed domains.
- `src/sqlite_replay_ledger.cpp`
  - switches SQLite event identity and compatibility effect fallback to the same framed domains;
  - uses `RAND_bytes` and fails closed for new ledger identities.
- `src/reporting_selftests.cpp`
  - adds exact collision, duplicate-metadata, control, event-identity, and cross-backend fallback regression coverage.
- `src/runner.cpp`
  - requires exact capability-v27 framing, fallback, metadata, and RNG claims.
- `fixtures/rev0618/*`
  - preserves the inherited 390-case semantics while regenerating 378 proof HMACs under the v2 profile.
- `tools/validate_rev0632_security_material_boundary.py`
  - independently reconstructs both legacy and v2 material and exercises both backends.

## Compatibility

### Proof input

The v2 proof profile intentionally invalidates legacy proof digests. Clients or fixture generators must recompute the HMAC over v2 material. The controls file explicitly names the profile, so a v1 digest cannot be silently interpreted as v2.

### Existing ledger rows

SQLite schema remains v8 and existing row hashes are unchanged. CloudEvents source/id are stored in separate columns, and the in-memory replay index is rebuilt with v2 framing. Existing valid rows therefore load without rewriting their entry hash.

JSONL entry hash material also remains unchanged for compatibility. Only the derived in-memory event identity key and newly generated fallback effect key change.

### Compatibility fallback

Pre-normalized callers that omit `effect_idempotency_key` receive a newly derived legacy-v1 framed key. This may differ from a key derived by older code. Such callers should migrate to supplying the normalized v2 key explicitly. Both persistence backends now agree.

### New ledger identity

Existing SQLite ledgers retain their stored `ledger_instance_id`. Newly initialized ledgers use OpenSSL RNG and the v2 seed domain. No migration is needed, and byte-for-byte clones still retain the original stored identity.

## Fail-closed metadata rules

The boundary rejects:

- exact duplicate JSON object keys;
- case-insensitive duplicate normalized metadata keys;
- non-string normalized metadata values;
- ASCII bytes `0x00`–`0x1f` and `0x7f` in metadata keys/values;
- those controls in HTTP method/path, event channel/action, and CloudEvents source/id.

This is intentionally narrower than full Unicode confusable or normalization handling. Transport adapters should define an ASCII header-name profile and pass canonical bytes rather than reconstructing metadata from lossy framework maps.

## Validator evidence

The validator performs these independent checks:

1. exact v27 capability and rev0631 parent lineage;
2. all packaged C++ selftests, including framed fallback equivalence;
3. the full inherited 390-case fixture stream with 326 accepted rows;
4. equality of the legacy proof/effect material for the crafted pair;
5. equality of the legacy raw event identity for its crafted pair;
6. inequality of all corresponding v2 framed tuples and SHA-256 digests;
7. quarantine of four control-character probes on JSONL and SQLite/WAL;
8. rejection of duplicate `Authorization`/`authorization` metadata on both backends before append;
9. inherited signed-transition, stale-head, tamper, wrong-ledger, raw-API, and downgrade checks.

The release suite contains 22 CTests. Sanitizer and fresh-extraction results are recorded separately under `audit/`.

## Remaining material migration debt

The following custom newline-delimited inputs remain and are not covered by the v27 claim:

- `ReplayLedger::entry_hash_material`;
- SQLite effect-transition chain material;
- signed terminal transition intent input;
- signed snapshot manifest input;
- any historical helper not routed through the tuple function.

A future migration should use a new material version, schema/capability version where persistence changes, adversarial cross-field collision tests, and explicit old-ledger handling. It should not mutate existing rows in place while preserving the old version label.

## Design references

DSSE’s pre-authentication encoding is the closest design precedent: it length-frames the signed payload type and payload because multiple fields need an unambiguous serialization. RFC 8785 is relevant when the object itself should remain JSON and a standardized canonical form is required. Rev0632 uses a small typed tuple because these inputs are a fixed field sequence rather than a general JSON document.
