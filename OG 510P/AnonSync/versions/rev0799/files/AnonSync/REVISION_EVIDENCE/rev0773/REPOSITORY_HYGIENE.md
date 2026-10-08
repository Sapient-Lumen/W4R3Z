# rev0773 repository hygiene and refactor audit

## Measured shape

Before rev0773 evidence is added, the inherited tree contains approximately:

- `third_party/`: 10.25 MB across 5 files, dominated by the verified SQLite amalgamation;
- active `src/`: 3.66 MB across 44 files;
- historical `audit/`: 4.61 MB across 34 files;
- historical `evidence/`: 0.26 MB across 34 files;
- `REVISION_EVIDENCE/`: 0.32 MB across 19 inherited files.

The largest active C++ units are `src/sync_domain.cpp` (~24.5k lines), `src/reporting_selftests.cpp` (~4.5k), `src/sqlite_replay_ledger.cpp` (~4.3k), and `src/sync_peer_ingress_lifecycle.cpp` (~3.8k).

## Waste and risk

The dominant waste is not storage alone; it is mixed authority. Historical patches, validation logs, notes, and copied audits live beside active source and appear in broad searches. This makes it easy to quote obsolete code, edit evidence instead of implementation, or treat a prior release gate as current truth. rev0771 itself illustrates the danger: its root gate is false and its notes claim a zero source delta despite describing extensive changes.

Large translation units create a second form of waste. A three-line SQL namespace correction forced a costly recompilation and relink of most executables because peer lifecycle remains one multi-thousand-line unit. Mechanical splitting is not enough; boundaries should follow owned invariants.

## Corrective policy used for this package

- Active implementation is validated from source, never from inherited release claims.
- The public revision and verifiable source parent are recorded separately.
- Build directories, object files, executables, CMake caches, nested ZIPs, VCS metadata, and external symlinks are excluded.
- Required and optional gates remain separate; unavailable formatting and any sanitizer failure cannot be rewritten as success.
- One root manifest hashes every packaged regular file except the manifest itself.

## Refactor map

Recommended invariant-owned modules:

1. **transaction authority** — typed BEGIN mode, guard-lifetime lease, commit/rollback, authorizer token;
2. **peer-ingress repository** — queue row, payload row, exact claim generation, and schema snapshot;
3. **payload evidence codec** — canonical frame, digest, byte limits, decode/verify;
4. **retention/reconciliation** — immutable incident history plus current scheduling pressure;
5. **operator projection** — read-only reporting from domain decisions, no parallel policy engine;
6. **test oracle/fault VFS** — executable transition model and crash/power-loss enumeration.

Historical evidence should ultimately move to immutable release bundles or a dedicated evidence tree indexed by manifest, while the active source cube keeps only current contracts and pointers to those bundles.
