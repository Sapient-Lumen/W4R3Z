# AnonSync rev0901 revision notes

Package: `AnonSync-rev0901-2026.07.26.01.04-sealedgenesis-identityfirstadmission-memoryimage-ivorybridge.zip`

## Complete SQLite genesis before pathname visibility

- Replaced selected-path SQLite creation with private `:memory:` construction.
- Exact deployment binding and complete role genesis are committed and inspected
  before any selected main-file pathname becomes visible.
- Added bounded sealed-image capture and immutable create-new/no-replace
  publication for SQLite genesis.
- Reproved the main plus `-journal`/`-wal`/`-shm` namespace immediately before
  publication; a late entry is never adopted or replaced.
- Reopened the exact published image without create authority, attested its
  binding, reconciled exact file-and-parent durability, promoted it to WAL, and
  re-attested the operational profile.

## Recovery admission and retained authority

- Added bounded SQLite header admission for complete rollback `1/1` and WAL
  `2/2` candidates.
- Rollback-mode candidates reject every sidecar before SQLite can interpret or
  mutate the namespace; WAL candidates reject a conflicting rollback journal.
- `init-resume` identity-attests all present resources on retained handles before
  WAL promotion, role-owner construction, or missing-store creation.
- Present bootstrap candidates retain SQLite locking across identity, durability
  reconciliation, promotion, and role-state classification.
- Missing resources remain creatable only when every present resource and the
  files root are at exact bootstrap genesis.
- Expanded the shipped-executable process corpus from nine to twelve scenarios:
  sealed rollback recovery, rollback-sidecar refusal, and unbound-main refusal.

## Detached authority narrowing

- Added explicit durable-named versus detached-bootstrap dispositions for TLS
  policy SQLite owners.
- Detached membership owners can construct and inspect genesis but cannot publish
  membership authority or advance the membership anchor.
- Hardened the detached deployment-binding primitive to require a writable,
  schema-empty main database using MEMORY journaling.
- Added adversarial coverage proving that an anonymous disk-backed temporary
  database with an empty filename and a prepopulated in-memory database are both
  rejected.

## Audit and refactor

- Removed a meaningless five-second busy timeout from the private single-
  connection in-memory genesis builder.
- Refactored bootstrap, open-policy, deployment-binding, and outbox source audits
  around semantic authority frontiers rather than stale enum/layout spellings.
- Extended the deployment-binding audit to 26 checks, including true detached
  memory-image and schema-empty preconditions.
- Preserved explicit nonclaims for rogue writers, pathname replacement, broken
  SQLite/VFS locking, storage flush behavior, and cross-database atomicity.
- Documented the clean-build fan-out problem and recommended a measured product
  lane, compiler cache, and dependency-fan-out work rather than broad test
  suppression or global unity builds.

## Validation

- Full GCC 14 Debug registry: **221/221**.
- Bootstrap/resume process proof: **12 scenarios**.
- Separate focused GCC 14 ASan/UBSan lane: **4/4**.
- Deployment-binding source audit: **26/26**.
- Database-open, bootstrap, snapshot-seal, bounded-reader, payload-store, TLS
  membership, outbox-clock, busy-handler, and release-path audits passed.
- Release package verified both as a directory and as the final ZIP.

## Explicit nonclaims and next work

Rev0901 does not provide descriptor-rooted deployment authority, resistance to a
hostile writer that can rewrite every resource, cross-store transactions,
automatic residue quarantine, forensic read-only status, a production
supervisor, complete causal filesystem semantics, chunked transfer resume,
reachability/GC, at-rest encryption, or an anonymity/privacy threat model.

The bundled SQLite remains 3.53.3. SQLite 3.53.4 was released on 2026-07-24 with
fixes for problems in the 3.53.0–3.53.3 line; that dependency update is
recommended as the next isolated, fully revalidated revision rather than being
mixed into this bootstrap cutpoint change.

The detailed mission analysis, cutpoint matrix, research, and recommended order
are in
`ATOMIC_SQLITE_GENESIS_IMAGE_AND_RECOVERY_ADMISSION_AUDIT_rev0901.md`.
