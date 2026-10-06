# Canonical JSON for hashing (restricted JCS/I-JSON profile)

DeriveBSD relies on digests everywhere: manifest digests, policy digests, closure digests, plan/receipt joins, and attestation payload digests. To avoid “same data, different bytes,” the archive needs one boring canonical JSON byte rule.

## Current DeriveBSD rule: `derivebsd-jcs-ijson-no-float-v1`

Hash-bound JSON objects use `derivebsd-jcs-ijson-no-float-v1`, implemented by `tools/cube_digest_lib.py` and guarded by `tools/check_canonical_json_digest_contract.py`.

This is a restricted JCS/I-JSON subset, not a vague “whatever Python `json.dumps(sort_keys=True)` emits” rule:

- reject duplicate object member names when loading JSON;
- sort object member names recursively in JCS UTF-16 code-unit order;
- do not reorder arrays;
- emit no insignificant whitespace;
- emit UTF-8;
- escape strings with RFC 8785-compatible lower-case control escapes and no Unicode normalization;
- reject lone surrogate code points;
- reject non-string object member names in in-memory objects before sorting;
- admit only exact safe JSON integers for hash-bound numeric values;
- reject JSON floating-point numbers for hash-bound v1 objects.

JSON floating-point numbers are not hash-bound in v1. Values such as ratios, percentages, durations, money, or high-precision counters should be represented as strings with explicit schema semantics when they participate in a canonical digest. Measurements that are useful as evidence but not part of the digest identity may remain ordinary JSON numbers in non-hash-bound receipts.

`tools/check_canonical_json_digest_contract.py` also ratchets legacy local digest helpers at 26 checker files so new checkers do not casually reintroduce per-file `json.dumps(sort_keys=True)` hashing.


## r563 implementation finding

The shared-helper refactor found that `time.sync.snapshot`, `time.sync.receipt`, and `time.event` examples still carried JSON floating-point millisecond measurements inside hash-bound evidence. r563 converts those measurements to schema-defined decimal strings and recomputes dependent incident-bundle digests. This keeps the restricted-JCS no-float profile intact instead of making the helper silently accept ambiguous number rendering.

## Why the restriction exists

RFC 8785 JCS requires ECMAScript-compatible primitive serialization, including the ECMAScript/Ryu-style number-rendering behavior. Python sorted compact JSON is deterministic for many ASCII/string/integer fixtures, but it is not a proof of full RFC 8785 behavior. The old posture was too easy to overclaim.

The current helper therefore makes the safe subset explicit: it implements duplicate rejection, non-string in-memory key rejection, UTF-16 object member ordering, string escaping, no whitespace, UTF-8 output, and no-float/no-unsafe-int admission. A future full-JCS implementation can expand the profile only after it carries number-serialization vectors and an explicit profile/version change.

## Where this applies

Use this profile for content identity and portable digest joins, including Spec/Lock/Plan identity, runtime manifest identity, policy context digests, and receipt joins that say `sha256(utf8(JCS(...)))` or equivalent.

Do not use this profile for arbitrary telemetry snapshots with JSON floats unless those floats have first been transformed into schema-defined strings or excluded from the hash-bound object.

See `adrs/ADR-0022-canonical-json-jcs.md`.

Last updated: 2026-06-12r563
