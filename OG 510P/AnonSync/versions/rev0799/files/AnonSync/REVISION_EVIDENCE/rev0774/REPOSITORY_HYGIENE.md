# AnonSync rev0774 — repository hygiene and refactor assessment

## Measured condition

- `src/sync_domain.cpp`: 24,523 lines and 45 inventoried raw transaction
  controls.
- `src/sync_peer_ingress_lifecycle.cpp`: 3,794 lines and 5 raw controls, all in
  the selftest portion after the production/selftest marker.
- New invariant owner `src/sync_sqlite_connection_authority.cpp`: 832 lines.
- Legacy raw transaction controls outside the new owner: 95.
- The tree also carries multiple historical evidence hierarchies beside active
  source. They are useful for provenance but make broad searches noisy.

## Waste observed in this cloudtainer

Fresh Debug compilation completes normally. Complete Release and sanitizer
builds repeatedly exceed the command ceiling while compiling the unchanged
`sync_domain.cpp`; focused revised targets finish quickly. This is direct cost:
validation becomes profile-fragmented, compiler feedback arrives late, and a
small authority change is coupled to a very large unrelated translation unit.

Historical copies and evidence are a second cost. Search results mix active
code, prior patches, validation logs, and revision reports. A reviewer can edit
or reason from an obsolete copy unless every tool is carefully scoped.

## Refactor performed

Rev0774 removes transaction implementation from generic
`sync_sqlite_support.cpp` and gives it an invariant-owned translation unit.
Connection callback/client-data/generation state remains in the connection
authority owner. The split reduced conceptual coupling without introducing a
second transaction policy implementation.

The audits were also refactored. They now enumerate source ownership explicitly
and fail if transaction methods drift back into generic support or direct
`sqlite3_set_authorizer` calls spread outside the owner.

## Recommended sequence

1. Extract the replay-ledger transaction repository (15 raw boundaries) with
   its own exact schema and crash semantics.
2. Move reporting fixtures to consume that shared owner rather than copying SQL
   control patterns.
3. Partition `sync_domain.cpp` by durable state machine: checkpoint, effect
   outbox, restoration, manifest verification, and operator projection. Each
   slice should own one repository API and one transition oracle.
4. Put historical revision evidence under a generated/source-distinct package
   boundary or exclude it from default search tooling.
5. Add a fast boundary-only build preset and a slower full-cube preset, while
   keeping full Debug CTest required.

The wrong response would be a mechanical 24k-line split that leaves shared
ambient SQLite handles and transaction strings everywhere. The target is fewer
owners, not merely smaller files.
