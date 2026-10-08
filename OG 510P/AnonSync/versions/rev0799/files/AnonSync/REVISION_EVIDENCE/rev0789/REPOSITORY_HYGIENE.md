# rev0789 repository hygiene audit

This measurement excludes build trees, generated caches, `MANIFEST.sha256`, and
the two self-describing hygiene files. The measured handoff contains
**613 files / 23,525,356 bytes**. Active first-party build,
production, test, fuzz, and tool source is **87 files /
4,469,770 bytes**. Third-party source is **10,249,414
bytes**, dominated by the pinned SQLite amalgamation.

Historical revision evidence, legacy `audit/` and `evidence/` trees, and revision
notes total **8,222,010 bytes**, or **1.839×** active first-party
source. All `REVISION_EVIDENCE` packs alone are **0.864×** active first-party
source; rev0789's current evidence is **0.129×**.

## Why this is correctness debt

- repository-wide searches surface obsolete source patches and logs before live
  code, increasing the chance of reasoning from the wrong revision;
- repeated evidence makes manifests and release review more expensive and can
  hide a failed or stale gate among successful historical copies;
- large archives slow every handoff even when only a few active files changed;
- build trees are excluded, but textual evidence still competes with source for
  reviewer attention and tool context;
- four historical evidence paths carry a `.json` suffix but are empty or
  non-JSON (two in rev0774 and two in rev0785). Rev0789 preserves those bytes
  for lineage truth, records the paths in `repository_metrics.json`, and scopes
  machine-readable release gates to current validated evidence.

## Safe migration

Do not delete old packs opportunistically. First compute one content-addressed
index over every historical file and revision root, verify all existing lineage
references, and make retrieval deterministic. Then move immutable old packs out
of the source cube while retaining:

1. the current revision's complete evidence;
2. parent and historical root digests;
3. a signed/content-bound retrieval index; and
4. a verifier that proves an external pack matches the referenced root.

This is a natural place for a Merkle evidence store, but content addressing is
not authorization. The index must also bind revision, policy, signer/key epoch,
project identity, and retention rules.

## Active structural pressure

The six largest first-party C++ surfaces remain 24,530 lines
(`sync_domain.cpp`), 4,498 (`reporting_selftests.cpp`), 4,466
(`sqlite_replay_ledger.cpp`), 3,833 (`sync_peer_ingress_lifecycle.cpp`), 3,499
(`anonsync_core.hpp`), and 2,198 (`runner.cpp`). Rev0789 demonstrates the desired
correction pattern: extract an invariant-owned library, connect production to
it, link its proof directly, measure the reduced graph, and fail configuration
if the monolith absorbs it again.
