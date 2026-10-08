# AnonSync rev0807 — pre-mutation review fence, pure scheduler policy, and stale-owner compass

## Lineage

Rev0807 is derived from the complete uploaded archive
`AnonSync-rev0806-2026.07.16.16.46-domaincorpus-fixturebridge-focusedgraph-tracecompass.zip`,
SHA-256 `ae2bc945052b7b477bd66858e977c35405c273d12f55e42f2d82d5cf9a69ccf5`.
The exact parent archive passes **25/25** checks in its packaged verifier and
contains 44 production C++ implementation files, 32 production headers, and 28
test C++ files. No build output, recovered object, or generated tree was used as
source lineage.

## Heart of the mission

AnonSync is an **evidence-authorized convergence engine**:

> Make every replicated state transition carry enough owner-verified evidence
> to remain safe under concurrency, replay, crash, compromise, and partial
> failure; reject invalid authority before unrelated valid state is destroyed;
> then prove the authorized transitions converge.

A successful syscall, callback, query, returned row, signature, PID comparison,
pointer lookup, lock acquisition, or commit is an observation. It becomes
authority only when the invariant owner verifies the exact bytes, identity,
process incarnation, owner generation, lifetime, policy, relationship, schema,
resource budget, and durability evidence required for that transition.

Rev0807 applies the rule to scheduling. A planner-produced action is not mutation
authority merely because its enum says “execute.” The persisted state, lease,
review, retry, chunk, and idempotency-key relationships must agree, and a safety
review must be evaluated before any mutation capability is constructed.

## Severe defect: “stop on review” happened after mutation

The parent scheduler planner emitted terminal-review actions as nonmutating
entries. The daemon executor then:

1. planned all actions;
2. built execution-idempotency-key filters;
3. invoked claim/reclaim/abandon and owned-claim mutators;
4. returned the pass result; and only then
5. evaluated `stop_on_terminal_review` in the daemon loop.

This made the option's name materially misleading. A durable abandoned or
quarantined row could coexist with runnable claimed work. The daemon would
observe the review and stop, but unrelated runnable work could already have
changed database state, staged bytes, receipts, or materialized output in the
same pass.

The issue was not theoretical. The existing domain corpus already had the
necessary durable quarantine fixture, but it asserted only that a review action
was present. Rev0807 extends that fixture with runnable claimed rows and proves
the parent ordering would have allowed selected mutation authority before the
post-pass stop.

## Correction: terminal review is a pre-mutation authority fence

`SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions` now has:

```cpp
bool block_mutating_actions_on_terminal_review = true;
```

The executor evaluates terminal review immediately after the scheduler plan and
before it constructs claim/abandon or execution-key vectors. When the default-on
fence is active:

- every terminal-review action remains observable;
- every selected mutating group is counted as blocked;
- no mutation action is copied into a key filter;
- no key filter is built;
- neither mutator is called; and
- the result preserves explicit evidence explaining why the pass was idle.

The result and daemon aggregate expose:

- `terminal_review_present`;
- `mutations_blocked_by_terminal_review`;
- terminal-review action count;
- blocked mutating group count; and
- blocked mutating action count.

The daemon maps its existing `stop_on_terminal_review` policy to the executor's
pre-mutation fence. It still stops after receiving the pass result, but by then
the executor has already withheld all mutation authority. The heartbeat state
becomes `scheduler-pass-terminal-review-fenced`, and operator JSON reports the
same evidence.

## Durable regression proof

The sync-domain corpus now creates a checkpoint with:

- one quarantined terminal-review row and its review event;
- multiple otherwise runnable claimed workorder rows; and
- valid source, staging, checkpoint, lease, and chunk evidence for those rows.

The direct executor regression proves:

- review is present and ordered first;
- all runnable mutation actions are planned but blocked;
- no execution-key filters are constructed;
- claim/abandon and owned-claim mutator run counts remain zero;
- no workorder changes state;
- no chunk, receipt, or byte write occurs; and
- the claimed/quarantined row counts and review-event count remain unchanged.

A separate daemon regression disables only the owner lock fixture requirement
and proves `stop_on_terminal_review` has the same pre-mutation effect through the
full loop: one completed idle pass, a review stop, explicit fence evidence, no
selected mutation, no mutator call, and unchanged durable rows.

The domain model grows from **588 to 592 checks** and passes **592/592**.

## Refactor: durable loading, pure policy, and mutation execution have separate owners

The parent `sync_domain.cpp` owned durable queue loading, action policy,
execution, daemon orchestration, status reporting, and most checkpoint
persistence. Rev0807 extracts the scheduler slice without pretending that all
checkpoint control-plane concerns are solved.

### Runtime executor

`src/sync_checkpoint_scheduler.cpp` now owns the two public scheduler entry
points:

- `plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass`; and
- `execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass`.

The planner delegates durable queue loading to the existing queue selector and
calls the pure policy exactly once. The executor independently validates the
policy output before it creates mutation filters or calls mutation entry points.

### Pure policy owner

`src/sync_checkpoint_scheduler_policy.cpp` is built as the dedicated static
library `anonsync_sync_checkpoint_scheduler_policy`. It has no SQLite,
filesystem, crypto, wall-clock, or mutator dependency. Its input is a vector of
durable queue facts; its output is a bounded ordered action plan.

For every fact it verifies:

- nonempty path evidence;
- an authorized resume/retry source action;
- lowercase SHA-256 chunk evidence;
- nonzero, overflow-safe chunk geometry;
- nonzero lease generation and coherent claim/expiry/retry timing;
- exact agreement between terminal-review flag and queue kind;
- exact agreement among queue kind, persisted work state, worker ownership,
  expiry, and retry-window state; and
- exact mutation-key namespace plus 64-hex digest shape before a mutating action
  can be minted.

Terminal-review rows deliberately remain reviewable even if their historical
mutation keys are malformed. Rejecting such a row would hide the very evidence
that requires operator attention. The policy therefore separates “authority to
surface evidence” from “authority to mutate.”

### Ordering and bounded groups

Priority classes are explicit:

1. terminal review;
2. mutation;
3. passive observation; and
4. completed observation.

Mutation actions sharing one execution idempotency key form one atomic group.
The policy refuses a group that mixes action kinds. Review and observation
entries are singleton groups because they carry no mutation atomicity.

A bounded pass never splits a group. If a higher-priority group does not fit,
its priority class forms a barrier: lower-priority groups cannot bypass it to
fill the remaining action cap. This avoids a limit turning “review first” or
“mutation group atomicity” into a best-effort ordering hint.

### Executor distrusts its adjacent policy

The executor verifies before mutation:

- returned count equals vector size;
- action priorities are contiguous;
- group priorities are contiguous;
- no group is split or repeated;
- every group has a nonzero declared size;
- every member agrees on group kind, mutating status, execution key, and size;
- each group is complete; and
- observed group count equals the planner's reported count.

This defense is intentional. Linkage adjacency is not authority, and a future
policy bug must not silently become a mutation-key capability.

### Source-private exact helpers

Exact worker-lease ID derivation and unique execution-key filtering moved from
the monolith to `src/sync_checkpoint_resume_internal.hpp`. That private header
has exactly two users: the runtime scheduler and the remaining domain unit. It
is not installed or exposed through public headers.

## Exhaustive focused policy proof

`tests/sync_checkpoint_scheduler_policy_test.cpp` links only the pure policy
library. It does not link `anonsync_core_lib`.

The test covers:

- every one of the **8! = 40,320** orderings of all queue kinds;
- zero/unbounded and positive action caps;
- terminal-review precedence;
- mutation-group atomicity;
- deferred-priority barriers;
- singleton observations;
- mixed-key and mixed-kind group rejection;
- malformed state/ownership/expiry/retry relationships;
- malformed hashes, ranges, lease evidence, and mutation keys; and
- the distinction between reviewable malformed historical evidence and valid
  mutation authority.

Final result: **1,975,744/1,975,744 assertions passed**.

A 22-check source audit enforces ownership, build graph direction, policy purity,
validation-before-action order, state/lease/review/chunk/key bindings, priority
and group semantics, planner delegation, private-header users, pre-mutation
fence order, public evidence, daemon and CLI propagation, integration
regressions, focused test registration, sanitizer coverage, and monolith
shrinkage.

## Build graph and compile economics

`src/sync_domain.cpp` falls from 15,840 to 15,329 lines. The new runtime
scheduler is 508 lines and the pure policy is 437 lines.

Direct sequential GCC 14 Debug-equivalent measurements in this cloudtainer:

| Unit | Lines | Wall | Peak RSS | Object bytes |
|---|---:|---:|---:|---:|
| rev0806 domain monolith | 15,840 | 11.06 s | 690,840 KiB | 10,425,320 |
| rev0807 remaining domain | 15,329 | 9.69 s | 621,280 KiB | 9,220,080 |
| rev0807 scheduler executor | 508 | 2.43 s | 304,948 KiB | 1,806,256 |
| rev0807 pure policy | 437 | 0.99 s | 170,524 KiB | 804,112 |

The largest runtime compile is 12.39% faster in this sample, uses 10.07% less
peak memory, and emits an 11.56% smaller object. There is an honest tradeoff:
serially compiling all three rev0807 units takes 13.11 seconds, 18.54% longer
than the parent unit because public headers are parsed repeatedly. This revision
claims a lower maximum per-job cost, correct invariant ownership, independent
scheduling, and a no-core exhaustive proof surface—not lower total compile
work.

## CMake sanitizer correction

Rev0806 placed the `INTERFACE` aggregate `anonsync_selftests_lib` in a list that
receives `target_compile_options(... PRIVATE ...)` when sanitizers are enabled.
CMake does not permit PRIVATE compile options on an INTERFACE library, so the
sanitizer configuration path itself was broken.

Rev0807 applies sanitizer compile options to the two concrete selftest support
libraries instead and adds the pure policy library/test to the sanitizer graph.
The focused test configures, builds, and passes under GCC 14 ASan/UBSan with
`detect_leaks=1` and fail-fast sanitizer options. No complete instrumented
application is claimed.

## Strict compiler findings

The six changed C++ units pass:

- Clang 17 with `-Wall -Wextra -Wpedantic -Wconversion`
  `-Wsign-conversion -Wshadow -Werror`; and
- GCC 14 with the same warnings plus `-O3 -DNDEBUG -Werror`.

The extraction exposed four shadowing lambda parameters in the domain corpus
and one signed-byte iteration in operator portable-ID validation. The final
code uses distinct parameter names and explicit unsigned-byte conversion.

## Deep audit: the daemon owner lock is not yet a fencing token

The owner-lock table and heartbeat improve cooperative single-owner behavior,
but the reviewed path does not yet prove stale-owner exclusion.

### Exact gap

1. The daemon calls owner-lock acquisition with
   `initial_worker_lease_epoch` as `owner_lock_epoch`.
2. Acquisition overwrites a released or expired row but does not require the new
   epoch to exceed the stored epoch and does not mint a generation from
   database state.
3. The owner-lock ID is a digest of caller-supplied session/daemon/worker/epoch
   fields.
4. Scheduler execution, claim/reclaim/abandon, and owned-claim execution option
   structs do not carry the owner-lock ID or generation.
5. Their `BEGIN IMMEDIATE` mutation transactions do not read and verify the
   current owner row inside the same transaction before writes.

SQLite's one-writer serialization prevents simultaneous write transactions, but
it does not establish which process is still authorized to become that writer.
A paused daemon A can hold epoch 7, outlive expiration, and stop executing. A
daemon B can replace the row—potentially also with caller epoch 7—and mutate.
When A resumes, its scheduler can call a mutator that verifies worker-workorder
lease evidence but not the current daemon-owner generation. The old process is
therefore not fenced at the mutation boundary.

### Required correction

The next control-plane revision should:

- mint a strictly increasing owner generation transactionally in SQLite;
- derive the owner capability from that database-minted generation;
- propagate owner-lock ID and generation through every daemon mutation option;
- verify session, ID, generation, held state, and expiry inside the same
  `BEGIN IMMEDIATE` transaction as every database mutation;
- bind externally visible staging/receipt/materialization effects to a current
  owner check or a transactionally reserved operation capability;
- reject a stale generation independently of the caller's local clock; and
- include a deterministic pause-A / expire / acquire-B / resume-A trace.

Google's Chubby paper describes the same class of delayed request: a request can
arrive after a lock has been lost and reacquired, so a lock sequencer includes a
generation that the recipient validates. TLA+/TLC is a good fit for the small
owner/lease/review state machine because safety violations produce minimal
counterexample traces. These references motivate the roadmap; they do not prove
AnonSync's current owner protocol.

## Online research applied

Primary sources reviewed for this revision:

- SQLite transaction documentation: `BEGIN IMMEDIATE` starts a write transaction
  immediately and SQLite allows only one simultaneous writer. This supports
  transaction-local owner verification but is not itself owner authorization.
  <https://sqlite.org/lang_transaction.html>
- Burrows, *The Chubby lock service for loosely-coupled distributed systems*:
  delayed stale requests require a lock sequencer carrying a generation that
  recipients validate.
  <https://research.google.com/archive/chubby-osdi06.pdf>
- Lamport, *Specifying and Verifying Systems With TLA+*: TLC explores reachable
  states and emits minimal-length traces for safety-property violations.
  <https://lamport.azurewebsites.net/pubs/spec-and-verifying.pdf>
- Microsoft Research, systematic executable distributed-system testing: small,
  controlled schedules and failures can expose subtle protocol bugs before
  production.
  <https://www.microsoft.com/en-us/research/publication/uncovering-bugs-in-distributed-storage-systems-during-testing-not-in-production/>
- Mohan et al., *CrashMonkey and ACE*: bounded workloads and crashes at
  persistence points make systematic crash-consistency exploration tractable.
  <https://www.microsoft.com/en-us/research/wp-content/uploads/2021/10/tos-crashmonkey.pdf>

## Validation

### Required clean debug gate

- GCC 14.2.0
- C++20
- Debug
- bundled SQLite 3.53.3
- `-Wall -Wextra -Wpedantic -Werror`
- complete from-scratch build graph
- final Ninja state: no work pending
- full CTest: **83/83 passed**
- domain model: **592/592 checks**
- pure scheduler policy: **1,975,744/1,975,744 assertions**
- scheduler source audit: **22/22**
- runtime/selftest audits: **9/9** and **13/13**
- CLI help/CTest selftest parity: **38/38**

### Sanitizer scope

The pure scheduler policy and its focused exhaustive test pass GCC 14
AddressSanitizer, UndefinedBehaviorSanitizer, and leak detection. The runtime
scheduler, domain monolith, diagnostic corpus, and complete application were not
built and executed together under sanitizers in this revision. A complete
instrumented executable is therefore not claimed.

## What remains missing

1. **Transactionally enforced owner fencing.** This is now the highest-priority
   checkpoint control-plane correction.
2. **Executable convergence algebra.** The broad corpus still does not classify
   every durable operation or generate duplicate/reorder/partition/restart and
   epoch-change traces against an independent model.
3. **Crash-cut/domain-state oracle.** SQLite validity must be checked together
   with WAL/journal, receipts, sidecars, checkpoints, staging, renames, and
   externally visible effects.
4. **Disposable hostile-database interpreter.** Long-lived in-process parsing
   still exceeds the ideal blast-radius boundary.
5. **Privacy and key lifecycle.** Authentication and replay defenses are not a
   complete payload confidentiality, metadata-hiding, anonymity, forward
   secrecy, or post-compromise-recovery protocol.

## Sealed evidence

`REVISION_EVIDENCE/rev0807/` contains exact lineage, source delta, audit JSON,
focused and integrated test output, complete CTest output, strict compiler logs,
focused sanitizer logs, compile measurements, owner-fencing hazard analysis,
research notes, repository metrics, active implementation projection, and
package verification inputs.
