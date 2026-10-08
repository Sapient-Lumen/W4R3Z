# AnonSync rev0891 implementation audit

## Mission boundary

AnonSync's heart remains exact authority accounting: identity, policy,
causality, delivery, retry, receipt, visible effect, and recovery must advance
only from exact evidence owned at an explicit cutpoint. Derived summaries and
labels may accelerate or explain; they do not mint authority.

Rev0890 froze a canonical callback-free membership snapshot before accept, but
any caller could still construct such a snapshot. Rev0891 closes that gap for
the accepted TLS path by making committed membership a move-only capability
emitted only by a stationary SQLite owner.

## C++ implementation

`SyncReplicaTlsMembershipSqliteOwner` owns one folder/local-actor history. It:

- creates and attests three exact `STRICT` tables;
- reconstructs the full append-only history and every retained canonical entry;
- binds genesis and every update with domain-separated digests;
- publishes through `BEGIN IMMEDIATE` and an exact expected-anchor compare-and-swap;
- requires strictly increasing policy epoch;
- emits accepted-session authority only after commit;
- accepts an optional externally retained generation/digest anchor to detect rollback or divergence through that cutpoint; and
- enforces hard ceilings of 65,536 history records and 4,194,304 retained entry rows.

The accepted TLS server now consumes that move-only authority by value and
attributes every terminal result to generation, policy epoch, entry count,
snapshot digest, previous chain digest, and current chain digest.

`SyncReplicaFileTlsServerContext` retains an OpenSSL context reference with
`SSL_CTX_up_ref`/`SSL_CTX_free`. A runtime fixture destroys the caller's original
reference before server entry and still reaches the bounded accept outcome.
This proves the wrapper owns lifetime in that tested path; concurrent context
mutation remains prohibited and unclaimed.

## Defects found and corrected during audit

### Ceiling-crossing append could brick future restoration

The first implementation bounded history only while reading. An append that
crossed a ceiling could commit and make every subsequent reconstruction reject
the database. Publication now recomputes exact retained totals under its writer
transaction and rejects the candidate before any insert. The pure boundary
predicate is tested at every limit edge but is not treated as publication
authority.

### Post-commit allocation ambiguity

The first implementation committed and then allocated the caller-visible
authority object. Allocation failure could therefore advance durable policy
without returning the capability. Return-state allocation now occurs before
`COMMIT`; failure rolls the transaction back, while the capability is returned
only after successful commit.

### Prefix-only schema closure was incomplete

An arbitrary-named index or trigger attached to an owned table could evade a
reserved-prefix-only inventory. Main schema attestation now covers both names
and owned-table attachment. TEMP schema closure rejects connection-local
objects attached to authority tables.

### Durability policy overclaim

SQLite's current documentation distinguishes WAL `FULL` from rollback-journal
`EXTRA` for strongest power-loss behavior. Rev0891 requires WAL at least `FULL`
or `DELETE`/`TRUNCATE`/`PERSIST` at least `EXTRA`; `OFF`, `MEMORY`, unnamed,
read-only, and weaker configurations cannot mint durable membership authority.
This remains a policy observation, not proof of the physical storage stack.

### Raw OpenSSL context lifetime

The accepted server previously borrowed `SSL_CTX*`. Rev0891 replaces it with a
move-only retained reference and adds an exact lifetime regression. It does not
pretend reference counting serializes mutation.

### Lexical audit drift

Four source audits were refactored to follow the actual committed-authority,
immutable-snapshot, and retained-context boundaries. They explicitly disclaim
semantic proof and remain hygiene gates subordinate to compiled negative and
restart tests.

## Validation

- Exact parent archive: **26/26 package checks**, **5832-file exact Git import match**.
- GCC 14.2 Debug complete target graph: complete, final `ninja: no work to do`.
- Registered CTest: **209/209** in one invocation.
- Audit/policy CTest: **81/81** in one invocation.
- Focused real TLS/SQLite matrix: **1,973/1,973** independently under GCC Debug, Clang 17 Release C++ `-Werror`, and GCC ASan/UBSan with leak detection and bundled SQLite instrumentation.
- Repeated process stress: **10/10 Debug runs (19,730 checks)** and **3/3 sanitizer runs (5,919 checks)**.
- Selected source audits: **109/109**; package-path and verifier policies: **27/27**.
- Active projection: **422 files, 20627508 bytes**, SHA-256 `7bfe3e99e0d08c52d123d3861061036c25c863cfbec084268c8a11246d87b7b8`.

## Audit/refactor finding: the cube's build cost remains structurally wasteful

The build now has 87 literal libraries,
100 executables, and
212 literal `add_test` declarations, yet
several semantic centers remain giant translation units. The complete build
again spent almost all meaningful compilation time in legacy monoliths while
the new focused owner and its tests were small leaf work.

The correction should remain incremental: split giant files by durable authority
and state-machine ownership, replace repetitive CMake declarations with reviewed
declarative helpers, keep a fast affected-authority gate, and preserve periodic
full regression closure. Target count alone is not modularity.

## Largest remaining gaps

1. The shipped `anonsync_core` executable still does not make the causal SQLite/file/TLS path its sole durable replica authority.
2. The external membership anchor store, atomic crash ordering with the database, signed update provenance, enrollment, revocation, recovery, and freshness for already-issued capabilities remain absent.
3. The full-history owner is an O(history + retained entries) correctness oracle, not a production-scale indexed reader.
4. Outbound `SyncReplicaFilePayloadSource` still executes arbitrary caller code while a durable outbox lease exists; it should become a bounded content-addressed reader capability.
5. Bounded accept pools, peer/folder fairness, total disk accounting, staging expiry/garbage collection, dead-letter ownership, causal-stability compaction, and rejoin policy remain open.
6. “Anon” is not yet an implemented anonymity, unlinkability, endpoint-hiding, or traffic-analysis-resistance property.

## Nonclaims

Rev0891 does not claim signed membership provenance, an external anchor store,
atomic database/anchor publication, malicious same-process writer defense, live
revocation, freeze-attack protection, compaction, production-scale membership
reads, stable SQLite path/device identity, a production daemon, bounded
concurrent sessions, exactly-once network delivery, anonymity, formal proof,
ThreadSanitizer coverage, full-project Clang `-Werror`, full-project sanitizer
coverage, or externally trusted signed build provenance.
