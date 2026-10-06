# ADR-0022: Canonical JSON hashing uses a restricted JCS/I-JSON producer profile

- Status: accepted-with-v1-implementation-constraint
- Date: 2026-02-23
- Updated: 2026-06-12r563

## Decision

DeriveBSD hash-bound JSON artifacts use the archive profile `derivebsd-jcs-ijson-no-float-v1` for portable digest joins.

The profile keeps the parts of RFC 8785 JCS that are now mechanically enforced in-tree:

- duplicate JSON object members are rejected at load time;
- object member names are sorted recursively by JCS UTF-16 object member ordering, not by Python Unicode code-point ordering; non-string in-memory object keys are rejected before sorting;
- strings are emitted without Unicode normalization, with RFC 8785-compatible escaping for quotes, backslashes, control characters, and UTF-8 output;
- insignificant whitespace is not emitted;
- booleans, null, strings, arrays, objects, and exact safe JSON integers are admitted;
- JSON floating-point numbers are rejected for hash-bound objects in v1.

This v1 profile does not claim full RFC 8785 number serialization. Full JCS requires ECMAScript-compatible number rendering; DeriveBSD must not silently approximate that with Python `json.dumps(sort_keys=True)`. Non-integral measurements or values needing decimal/extended precision must be represented as strings with schema semantics, or kept outside the hash-bound canonical object, until a complete ECMAScript/Ryu-compatible number serializer is admitted and guarded.

## Implementation

`tools/cube_digest_lib.py` is the shared helper for r521+ computed joins. `tools/check_canonical_json_digest_contract.py` guards the helper against the old overclaim class by checking duplicate-key rejection, non-string in-memory key rejection, no-float/no-unsafe-int rejection, RFC-style string escaping, and the RFC 8785 UTF-16 sort-order sample where Python code-point sorting would be wrong. It also ratchets legacy local digest helpers at 26 checker files and proves the hash-bound time evidence examples use decimal strings rather than JSON floats.

This ADR does not bless ad-hoc local JSON serialization. A checker or producer that computes a digest should use the shared helper or prove byte-for-byte compatibility with `derivebsd-jcs-ijson-no-float-v1`.


## r563 note

While moving more digest checkers onto the shared helper, the time-sync bundle check exposed JSON floating-point millisecond fields in hash-bound examples. The accepted fix is to model those measurements as schema-defined decimal strings and recompute dependent digests, not to weaken `derivebsd-jcs-ijson-no-float-v1`.

## Consequences

- Schema validation remains a prerequisite for hashing.
- Producers of hash-bound JSON must avoid JSON floats; use strings for semantic decimals.
- Cross-language implementations must match `derivebsd-jcs-ijson-no-float-v1` exactly before their digests are accepted.
- Existing symbolic fixture digests are not retroactively reinterpreted unless their checker recomputes them through the shared helper.
- A future full-JCS upgrade is possible, but it must be explicit, versioned, and guarded by number-serialization vectors rather than implied by this ADR.
