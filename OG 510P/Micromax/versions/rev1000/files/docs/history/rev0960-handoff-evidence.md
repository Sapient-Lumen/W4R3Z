# Revision 0960 handoff evidence archive

Preserved from the rev0960 handoff root when rev0961 became current.

---

# Micromax revision 0960

## Outcome

Rev0960 closes the highest-risk daily trust gap: an explicit editor save now
creates and resolves a durable recovery checkpoint, and a failed save can be
reviewed after restart without automatic disk overwrite.

## Product changes

- Integrated the recovery journal into normal save/save-as paths.
- Added bounded interactive `recoveries`, `recover`, and `recoverdismiss`
  commands; startup performs filename-only bounded presence detection.
- Preserved exact pre-normalization editor text separately from encoded commit
  bytes.
- Forced durable file/rename completion before journal retirement and verified
  exact committed bytes and write authority.
- Preserved symlink-target save semantics and prevented retargeted nominal links
  from redirecting recovered content.
- Required explicit `save!` or save-as after target conflict; excluded recovered
  buffers from autosave.
- Retired stale checkpoints from earlier failed save-as attempts after later
  durable success.
- Avoided recovery/fsync overhead for a clean existing-file save.

## Audit/refactor changes

- Bounded recovery directory traversal, record count, aggregate record bytes,
  and aggregate target-comparison bytes; reported partial inventories honestly.
- Replaced check-then-read recovery paths with no-follow descriptor reads and
  rejected a recovery root replaced by a symlink.
- Centralized isolated multiprocessing context selection for filesystem and
  regex workers; multithreaded editor work no longer defaults to `fork`.
- Added the compact versioned `micromax.screen.v1` contract and packaged JSON
  Schema; retained the full screen graph behind explicit diagnostic output.
- Reused the already-open help buffer title during screen composition instead
  of rescanning the complete installed docs catalog for the active page.
- Updated the structural atomic-write audit to recognize the shared timeout witness variable introduced by the save refactor, then regenerated the installed effect/resource contract.
- Hardened `mkrevzip` against mixed-generation archives by rejecting
  symlink/non-regular members, snapshotting verified source bytes, and checking
  live membership/content through publication.
- Removed fifteen rev0959 root evidence/attempt artifacts and replaced them with
  three concise rev0960 handoff files plus one durable audit landing.

## Honest boundary

The recovery protocol has failure, restart, conflict, normalization, symlink,
budget, and cleanup journeys. It has not yet been validated against real sudden
power loss on every supported filesystem. Capabilities and plugins remain
in-process application policy, not an operating-system sandbox.

---

# Revision 0960 focused audit

## Selected risk

The selected risk was interrupted document persistence, because rev0959's
journal engine was not called by the ordinary editor save path. The audit also
followed adjacent authority and availability edges rather than adding another
policy registry.

## Corrected invariants

1. Recovery bytes exist durably before authoritative document mutation.
2. Journal retirement follows a durable, authority-matched, byte-verified
   document commit.
3. Recovery opens a dirty review buffer; it does not overwrite disk.
4. External target change requires an explicit user choice.
5. Symlink-preserving saves and recovery refer to the same concrete authority.
6. Startup recovery presence is bounded and does not read arbitrary targets.
7. Explicit inventory reports every applied truncation or byte limit.
8. Successful resolution clears all valid checkpoints owned by that buffer.
9. Auxiliary journal cleanup failure does not turn a successful durable save
   into a false save failure.
10. Archive publication reads a verified regular-file snapshot, not a mutating
    live worktree.

## Refactors

- `recovery_journal.py` owns records, integrity, classification, bounded
  inventory, selectors, and retirement; `file_write.py` remains the one document
  writer.
- `worker_process.py` owns safe per-operation multiprocessing context choice;
  editor compatibility imports re-export it instead of forking policy.
- `screen_contract.py` owns the stable compact projection; the diagnostic model
  remains internal.
- Active help rendering derives its title from the already-open buffer instead
  of triggering a full docs-catalog inventory for a page already in memory.
- `mkrevzip.py` owns regular-file source snapshot and mixed-generation refusal.

## Severe cloudtainer finding

Orphaned processes from prior worktrees were still running tests and writing
source during this session. They were terminated and the release tree was moved
to an isolated path. The packaging guard was changed so the same class of
mutation is detected rather than silently archived.

## Residual risk

- No real power-loss or kernel/filesystem fault matrix yet.
- A hostile concurrent namespace mutator can still race best-effort quarantine
  and delete operations; no-follow descriptor reads narrow the high-value read
  races.
- Explicit recovery inventory is bounded by bytes/counts, not a separate
  wall-clock worker; special or remote filesystems may still be slow.
- Plugin execution remains in process.
- The compact screen contract needs downstream compatibility consumers and
  golden size budgets before it can be called mature.

See `docs/916-durable-save-recovery-bounded-inventory-lineage-guard.md` for the
full mission, research, speculation, and priority analysis.

---

# Revision 0960 validation

Focused validation is recorded here; it is not a full-suite claim.

## Product journeys

- Recovery journal durability, rev0959 compatibility, exact editor-text payloads,
  bounded inventory, root/record no-follow behavior, selector handling, and
  target-change classification: **27 passed** in
  `tests/test_recovery_journal_journey.py`.
- Editor interrupted-save journeys: failed save/restart/review/commit, changed
  target force choice, concrete symlink authority, exact pre-normalization text,
  autosave exclusion, clean-save fast path, save-as recovery, filename-only
  startup presence, bounded listing, and stale-checkpoint cleanup: **12 passed**
  in focused one- and two-test batches from
  `tests/test_editor_interrupted_save_recovery.py`.
- Compact screen contract, including active-help no-rescan behavior: **6 passed**
  in `tests/test_screen_contract.py`.
- Default compact versus explicit diagnostic CLI output: **2 passed**. A blank
  24x80 run measured **2,110 bytes** for `micromax.screen.v1` versus **214,604
  bytes** for the diagnostic graph (about **101.7x** larger).

## Refactor and release-input guards

- Shared isolated worker-context policy: **6 passed** in
  `tests/test_worker_process.py`.
- Targeted risky-regex worker behavior: **2 passed** with third-party pytest
  plugin autoload disabled so the worker test observes only repository code.
- Archive source snapshot/lineage guard: **4 passed** for symlink rejection,
  source-mutation detection, verified-byte copying, and mutation refusal.
- Revision-index and living-guidance checks: **5 passed**.

## Structural commands

- `python -m compileall -q ...` over changed source, tools, and focused tests:
  **PASS**.
- `python tools/mxcontext.py --check`: **PASS**, revision 960, no missing curated
  paths.
- `python tools/mxaudit.py --check`: **PASS**; reports 908 docs, 121 source
  files, 216 test files, and the remaining 30,470-line `Editor` hotspot.
- `python tools/mxlint.py`: **PASS**.
- `python tools/mxeffects.py --check`: **PASS**, current v1 contract with 23
  rows.
- The bounded timely lane completed context, audit, lint, and all **156/156**
  portability cases. The cloudtainer command wrapper terminated the later doctor
  subprocess before that aggregate command completed, so no complete timely,
  doctor, or full-suite claim is made.

The revision packager performs its own finalized-archive verification; the
linked archive was also checked independently after publication.
