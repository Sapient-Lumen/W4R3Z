# AnonSync rev0833 — fresh-image crash campaigns, exact raw-fork fence, preallocation-free fail-stop

## Executive result

Rev0833 removes application and SQLite execution from four raw post-`fork()` test campaigns. Concurrent atomic writers, atomic-publication crash cutpoints, payload-store commit/rollback crash recovery, and peer-schema owner-close fail-stop now begin in fresh self-exec images owned by the existing Linux test-only process boundary.

The revision also corrects a production authority boundary: an inherited prepared immutable-publication capability no longer constructs a dynamic exception and unwinds C++ state in the child. Process-incarnation mismatch now takes the shared direct fail-stop path using a static diagnostic label before filesystem mutation.

## What changed

- Added exact self-exec helper protocols for four focused test executables, each dispatched before ordinary test setup.
- Bound helper instructions to normalized absolute paths, exact helper versions, bounded numeric fields, reconstructed fixture digests, expected cutpoint names, and fresh-image descriptor/environment/signal/process-group verification.
- Replaced four lexical raw-fork call sites with `SelfExecTestProcess` and bounded exact-exit ownership.
- Retained one raw fork in the prepared-publication test because inherited capability invalidation is the fact under test; its parent now owns a monotonic timeout, `SIGKILL`, and blocking reap.
- Changed prepared immutable-publication process mismatch from exception construction/unwinding to `require_sync_process_incarnation_or_fail_stop` with a static label.
- Added `tools/audit_raw_fork_boundaries.py` as a 120th CTest obligation.
- Strengthened seven related source audits and the release-package verifier.

## Audit result

The active tree now contains **0 production raw-fork calls** and **16 test calls across 9 translation units**, down from **20 calls across 13 translation units** in rev0832. Fifteen remaining calls exercise inherited process/lock/owner/publication evidence. One is a reviewed close/`dup2`/`exec` bridge for allocator-fault output capture; it performs no application or SQLite work before exec and remains an explicit migration target.

The new fail-closed audit passes **10/10**. During final review, its initial prose incorrectly characterized every remaining call as an inheritance probe. The allocator-fault bridge disproved that claim, so the audit was corrected and given a dedicated child-shape check rather than weakening or obscuring the exception.

Focused changed-boundary audits pass **278/278**:

- raw-fork boundary: **10/10**
- self-exec process owner: **30/30**
- atomic publication: **39/39**
- peer-schema owner generation: **26/26**
- reset receipt: **42/42**
- reset crash frontier: **20/20**
- SQLite process authority: **87/87**
- neutral process incarnation: **24/24**

## Runtime proof

- focused direct runtime: **327/327 checks** across five executables;
- focused CTest: **5/5**;
- focused stress: **50/50 executions** (ten consecutive executions of each changed runtime oracle);
- GCC 14.2 Debug all-target build: passed;
- final dependency closure: `ninja: no work to do.`;
- complete post-closure CTest inventory: **120**;
- complete gate: **120/120** in five bounded batches; and
- Clang 17 `-Werror` compile-only projection: **6/6 changed C++ translation units**.

## Lineage and source delta

- parent ZIP: **25/25**; parent directory: **21/21**;
- active patch replay: **207/207 files**, zero mismatches;
- source delta: **15 active files**, **1,041 insertions**, **210 deletions**;
- active projection: **207 files**, **16,583,042 bytes**, SHA-256 `8def4e957231b6adbeba8fc59481142e4ad4fe93726ae32211a6a1ba20a1d583`.

## Claim boundary

The exact inventory is not a claim that every legacy inheritance probe has bounded supervision; several remain explicit follow-up work. No single uninterrupted complete CTest, full-project sanitizer, hostile-worker sandbox, arbitrary VFS/power-loss completeness, Windows runtime result, cross-resource atomic transaction, distributed convergence, confidentiality, anonymity, metadata hiding, key lifecycle, or secure-erasure claim is made.
