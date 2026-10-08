# AnonSync rev0790 — exact scalar evidence, NUL-safe hash chains, and one conversion owner

Prepared from the supplied and independently verified parent archive
`AnonSync-rev0789-2026.07.14.23.34-rowstate-aliasproof-fuzzgraph-projectiontruth.zip`.
Its SHA-256 is
`31e3196dddddcf8355148c0ca39640e6c617e2496ec77a5de94b0db2a396b0ea`,
and the current package verifier passes all 25 parent checks.

## Mission

AnonSync's heart is **evidence-authorized convergence**: converge replicas while
preventing observations from silently acquiring more authority than their
provenance supports. A SQLite row is not a typed C++ object. Asking SQLite for
an integer does not prove the durable value was an integer. A text pointer is
not a byte sequence unless its length is preserved. A hash chain binds only the
bytes actually supplied to the hash function.

## Severe acceptance defects corrected

### Hidden durable bytes escaped the effective hash chain

Several production readers constructed strings from
`sqlite3_column_text()` as null-terminated C strings. SQLite TEXT may contain
embedded NUL bytes. The preserved rev0789 reproducer appends
`NUL + "hidden"` to `ledger_entries.case_id` without changing the row's stored
entry hash. The old read-only snapshot verifier truncated the modified value,
recomputed the original prefix-only hash, and accepted it:

```text
read-only snapshot verifier accepted hash-chain text with a hidden NUL suffix
```

Rev0790 reads the TEXT pointer first, then SQLite's explicit byte count, and
constructs a length-aware `std::string`. The suffix now participates in hash
verification and the modified snapshot is rejected.

### A fractional durable count was accepted as an integer

`sqlite3_column_int64()` performs SQLite's documented REAL-to-INTEGER
conversion. The old verifier read `metadata.line_count=2.75` as `2` and accepted
it when two ledger rows existed:

```text
read-only snapshot verifier accepted a fractional durable row count
```

Rev0790 checks the initial storage class and requires `SQLITE_INTEGER` before
reading an integer. REAL, TEXT, BLOB, and NULL cannot masquerade as a required
integer. The repaired integration selftest reports `passed=6 failed=0`; the
parent implementation reports `passed=4 failed=2`.

## Refactor: one exact scalar authority boundary

`src/persistence/sqlite_exact_value.*` is an independently linked library and
the only production location permitted to call SQLite result-value APIs
directly. Required and optional readers cover TEXT, BLOB, signed 64-bit
integers, and nonnegative SQLite integers represented as `std::uint64_t`.

Every read verifies:

1. a non-null statement;
2. a current result row, using
   `sqlite3_data_count(statement) == sqlite3_column_count(statement)`;
3. an in-range column index;
4. the exact initial SQLite storage class;
5. explicit TEXT/BLOB byte length; and
6. an inclusive caller-provided byte ceiling when nonzero.

Typed failures are `invalid_statement`, `statement_not_positioned`,
`invalid_column_index`, `null_value`, `wrong_storage_class`,
`negative_unsigned`, `allocation_failure`, and `byte_limit_exceeded`.
Diagnostics retain the caller's field label, index, and reason but not observed
value bytes.

The projection decoder delegates extraction to this boundary while preserving
its own one-to-one column-map and canonical-field rules. Generic support,
runtime policy, runner metadata, replay-ledger verification, ingress
lifecycle/schema paths, the domain, and reporting selftests were migrated.

The production inventory changed from **80 direct scalar calls in nine files**
to **six calls in one file**. The new 30-check source audit recognizes the full
known result-value API family, strips comments/literals before scanning, and
fails CTest on any unauthorized production call.

## Focused build-graph correction

The exact-value proof compiles:

- 6 Ninja actions;
- 2 first-party translation units;
- 523 first-party lines; and
- 22,136 first-party bytes.

The full core compiles 45 actions, 35 first-party translation units, and 53,355
first-party lines. That is a 102.02× line-exposure ratio. Configure-time guards
reject both source reabsorption into `anonsync_core_lib` and reverse dependency
from the exact boundary or its test onto the core.

## Validation

Required rev0790 gates passed:

- fresh GCC 14 Debug with `-Werror`, full build, **46/46 CTest**;
- exact-value 39-check and decoder 69-check proofs, **20/20**;
- focused GCC ASan/UBSan, **5/5**;
- fresh Clang 17 full-core Debug/`-Werror` build, focused proofs **5/5**, and
  snapshot verifier `passed=6 failed=0`;
- Clang focused `-Wconversion -Wsign-conversion -Werror`, **5/5**;
- GCC 14 focused `-O3 -DNDEBUG -Werror`, **5/5**;
- Clang libFuzzer/UBSan, 100,000 runs, coverage 1190, feature count 2878,
  160-entry/8610-byte final corpus, no finding; and
- eight deterministic authority audits with zero required violation.

The tested v2 implementation projection is **96 files / 14,761,320 bytes** with
SHA-256
`e15ef38a5f481e4e8e5e1c98d1fff8f90b03927853272e7dcdf093f078a9c404`.

## Explicitly unresolved

No full-core ASan/UBSan completion is claimed; the attempted lane remained in
the 24,531-line `sync_domain.cpp` translation unit after four command windows.
The focused first-party boundary passed ASan/UBSan, and the bundled SQLite
amalgamation was not instrumented in that lane.

The exact reader does not encode a thread-affine current-row capability in its
C++ type. A concurrently reset/finalized statement would still violate SQLite's
contract. Current production use relies on function-local statements and the
existing serialized connection/statement ownership machinery; a future typed
row borrow would make that premise explicit.

Exact storage class is not full semantic validity. UTF-8 policy, canonical path
rules, digest syntax, identifier grammar, timestamps, schema epoch, and
field-specific ranges remain the responsibility of their semantic owners.

`maximum_bytes=0` means unlimited at this boundary. A complete untrusted-
snapshot resource profile, STRICT/versioned schema migration, progress/VM
budget, page/file ceiling, and connection heap budget remain open.

The highest-value next work is still a fault-injecting VFS plus protocol state
oracle, followed by an explicit privacy/adversary model, executable convergence
contract, and further decomposition by invariant ownership rather than
line-count cosmetics.
