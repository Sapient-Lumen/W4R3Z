# rev0769 deep audit — SQLite authority, concurrency, and manifest completeness

## Executive finding

The connection-incarnation and canonical-manifest work closes two real ABA classes, but it should be understood as a **local authority fence**, not durable evidence. A process-local incarnation can reject stale pointers and stale authorizer generations; it must never become a restart-stable claim identifier. The canonical container manifest can detect authority-surface drift; it does not by itself serialize the observation with the peer-ingress transaction.

The strongest architectural correction remains isolation: give peer ingress a dedicated SQLite connection and preferably a dedicated database file. Cohosting can be supported, but every cohost feature expands the attested authority surface and the number of races that must be fenced.

## Source-grounded inventory

- C++ differences from rev0768: **unknown**
- Fallback boundary module injected: **unknown**
- Postprocess validation passed: **unknown**
- `sqlite3_set_authorizer` lexical call count: **unknown**
- Raw `sqlite3*` lexical mentions: **unknown**
- `schema_version` lexical mentions: **unknown**
- Connection-incarnation mentions: **unknown**
- Authorizer-generation mentions: **unknown**
- Manifest mentions: **unknown**
- Cohost mentions: **unknown**
- Direct authorizer call paths observed by the audit: `none found by lexical scan`

These counts are navigation evidence, not proofs. Runtime tests and exact ownership rules remain authoritative.

## What the manifest must cover

A DDL-only digest of one `sqlite_schema` view is incomplete whenever the connection can observe more than one authority source. The attestation input should explicitly version and bind:

1. The ordered `PRAGMA database_list` identity set, including `main`, `temp`, and every attached schema; attachment itself changes name resolution and authorization.
2. Canonical rows from each relevant schema table, including tables, indexes, triggers, views, virtual tables, and SQLite-created shadow objects under an explicit policy.
3. Recognized cohost authority metadata. Each record needs an authority class, owner, schema/object identity, policy version, and exact bounded payload. Unknown classes fail closed.
4. Connection configuration that can change semantics without changing DDL: defensive mode, trusted-schema policy, foreign-key enforcement, recursive triggers, query-only state, extension loading policy, and any other option on which ingress correctness relies.
5. Construction-time capabilities that SQLite cannot enumerate later, such as registered functions, collations, virtual-table modules, VFS behavior, and hooks. The practical answer is a dedicated connection factory whose typed recipe is itself versioned and attested.

Exact SQL text is a safe conservative input: cosmetically different but equivalent DDL causes a false-positive drift event. Parser-free “normalization” is dangerous because it can collapse semantically distinct statements. Any future semantic normalization should use SQLite's own parser or a separately versioned grammar and retain the exact source bytes alongside the normalized form.

## Concurrency boundary that remains easy to get wrong

SQLite serializes individual API calls in serialized mode; that does not make a multi-call sequence atomic. A sequence such as install authorizer → probe ownership → read manifest → prepare ingress statement can race with another thread that replaces the callback or mutates connection configuration between steps.

The peer-ingress path therefore needs an exclusive logical lease over the connection for the full sequence. All APIs capable of replacing the authorizer, preparing statements, attaching schemas, changing relevant pragmas/configuration, or closing the handle must pass through the same lease. A probe is evidence only for the instant and generation in which it ran. The eventual statement preparation/commit must consume that exact generation or re-attest.

Prepared statements deserve a dedicated adversarial matrix: prepared before fence installation, after installation, before replacement, after replacement, and across schema/configuration changes. Even where SQLite expires statements after an authorizer change, AnonSync should test the behavior it relies upon against the bundled SQLite build rather than treating it as folklore.

## Crash and durability boundary

The manifest is an observation. To authorize convergence after a crash, persist a domain-separated manifest digest and format version in the same SQLite transaction as the durable ingress receipt, then bind that receipt to the exact payload digest and claim generation. A process-local connection token must not be serialized as authority. On restart, a new incarnation reconstructs and verifies durable evidence; it never “continues” the old pointer lifetime.

Filesystem-backed payloads still require the explicit ordering contract:

`write temp → fsync file → atomic rename → fsync directory → SQLite receipt transaction → acknowledgement`

Reconciliation must handle every crash cut in that sequence and preserve contradictions rather than guessing which side won.

## Resource and ambiguity controls

- Count limits alone are insufficient; bound field bytes, encoded total bytes, schema count, attached database count, SQL text bytes, and elapsed scan work.
- Length-prefix every field, use fixed-endian integers, a manifest format version, and an unambiguous domain separator before hashing.
- Reject duplicate canonical records. Deduplicating silently can hide corruption or authority overlap.
- Fail closed on integer overflow and on an output that would exceed the configured budget before appending it.
- Distinguish “unknown authority class,” “budget exceeded,” “alien authorizer,” “stale incarnation,” “manifest drift,” and “storage failure” in durable incident evidence; collapsing these into a generic mismatch destroys repair guidance.

## Refactor direction

The lifecycle monolith should not own these details. Recommended invariant-owned modules are:

- `SqliteConnectionIncarnation`: process-local lifetime and exact authorizer generation.
- `SqliteConnectionRecipe`: construction/configuration capabilities that are not schema rows.
- `CanonicalAuthorityManifest`: deterministic bounded serialization only.
- `PeerIngressAttestor`: obtains an exclusive lease and combines current recipe, manifest, and authorizer evidence.
- `DurableIngressReceiptRepository`: transactionally persists the payload/claim/manifest evidence envelope.
- `ReconciliationLedger`: records contradictions and operator-visible repair state without becoming a second scheduler.

## Adversarial tests to add or retain

The minimum matrix includes same-address close/reopen, stale registration destruction after reuse, generation overflow, alien callback client data, callback disablement, callback replacement after probe, cohost metadata insertion/deletion/update, restored `schema_version`, reordered rows, duplicate rows, embedded NULs, enormous SQL text, attached/temp schema drift, pragma/config drift, precompiled statements, concurrent prepare, and crash cuts around receipt commit.

## Online research notes and speculation

The SQLite authorizer API is explicitly connection-scoped and callback based; the schema cookie is an internal coordination value rather than a cryptographic identity. SQLite also exposes defensive/trusted-schema controls precisely because schema content and application-defined functions can form an authority boundary. Those facts support the dedicated-connection design above.

Speculatively, AnonSync could make cohosting safer with a **connection recipe digest**: a versioned description produced only by a sealed factory after registering functions/collations/modules and setting all relevant db-config switches. The recipe digest plus the canonical schema/authority manifest becomes the transient attestation input. The durable receipt stores only its domain-separated digest and version. This does not prove a hostile process has not called raw SQLite APIs; preventing that requires ownership/isolation, not hashing.

Primary references:

- SQLite `sqlite3_set_authorizer`: https://sqlite.org/c3ref/set_authorizer.html
- SQLite schema table: https://sqlite.org/schematab.html
- SQLite PRAGMAs, including schema/data version behavior: https://sqlite.org/pragma.html
- SQLite database-connection configuration options: https://sqlite.org/c3ref/c_dbconfig_defensive.html
- SQLite threading modes: https://sqlite.org/threadsafe.html
- CWE-367 TOCTOU taxonomy: https://cwe.mitre.org/data/definitions/367.html
