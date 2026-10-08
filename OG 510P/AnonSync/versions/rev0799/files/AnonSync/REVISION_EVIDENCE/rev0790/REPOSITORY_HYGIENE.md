# rev0790 repository hygiene audit

This measurement excludes `MANIFEST.sha256` and this self-describing file. It
includes release evidence and source, but no build directories, binaries, object
files, Python caches, VCS metadata, or symlinks.

The measured handoff contains **701 files / 24,269,927 bytes**. Active
first-party material—`.gitignore`, `CMakeLists.txt`, and `include/`, `src/`,
`tests/`, `tools/`, and `fuzz/`—is **91 files / 4,511,906 bytes**. The pinned
third-party SQLite tree is **5 files / 10,249,414 bytes**.

Historical revision evidence, legacy `audit/` and `evidence/` trees, old root
revision notes, and `revision-notes/` occupy **521 files / 8,805,426 bytes**, or
**1.952×** active first-party material. Current rev0790 evidence is **81 files /
687,442 bytes** under the same exclusions.

## Why this remains correctness debt

Historical evidence is valuable, but keeping every old log and patch in the
active source cube has costs:

- broad searches can surface obsolete implementations or diagnostics before
  the live source;
- repeated evidence increases archive and manifest review work;
- context-limited analysis may spend more attention on old logs than current
  invariants;
- a stale historical pass can be mistaken for the current release gate; and
- large handoffs slow verification even when the active change is narrow.

Four inherited paths have a `.json` suffix but are empty/non-JSON:

- `REVISION_EVIDENCE/rev0774/validation/peer-payload-transaction-authority-audit.stdout.json`
- `REVISION_EVIDENCE/rev0774/validation/transaction-stack-authority-audit.stdout.json`
- `REVISION_EVIDENCE/rev0785/audit/peer_payload_transaction_authority.stdout.json`
- `REVISION_EVIDENCE/rev0785/audit/sqlite_transaction_stack_authority.stdout.json`

Rev0790 deliberately preserves those bytes. Rewriting them into valid JSON would
make lineage cleaner but evidence less truthful. Current machine-readable gates
use current validated JSON files only.

## Safe externalization path

Do not delete historical packs opportunistically. First build a
content-addressed inventory over every historical file and revision root,
verify all lineage references, and make retrieval deterministic. An external
pack should be accepted only after a verifier proves:

1. exact file inventory and per-file digests;
2. revision/root identity and predecessor linkage;
3. safe paths and archive structure;
4. signer/key epoch and policy version where signatures are introduced; and
5. retention/availability expectations.

Then retain in the source cube only the current complete evidence, parent and
historical root digests, and the retrieval/verifier machinery. Content
addressing is not authorization; an external pack must not become trusted merely
because its hash is known.

## Active structural pressure

The largest first-party C++ surfaces remain:

- `src/sync_domain.cpp`: 24,531 lines;
- `src/sqlite_replay_ledger.cpp`: 4,554 lines;
- `src/reporting_selftests.cpp`: 4,509 lines;
- `src/sync_peer_ingress_lifecycle.cpp`: 3,831 lines;
- `include/anonsync_core.hpp`: 3,499 lines; and
- `src/runner.cpp`: 2,198 lines.

Rev0790 demonstrates the preferred correction pattern: identify one invariant,
extract a standalone owner, migrate production inward, link the focused proof
directly, measure the graph, and make recoupling fail configuration. The
unfinished full-core sanitizer experiment shows why this is verification work,
not cosmetic source organization.
