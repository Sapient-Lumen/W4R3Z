# Architecture — rev0162

## Purpose

Revision 0162 adds a preregistered, multi-block custody layer above the single four-condition scenario run introduced in rev0161. The new layer is designed to prevent the experiment itself from being quietly retconned: the complete block roster, private order, child identities, assignment seeds, exact seed clones, rating contract, inclusion rule, primary dimensions, and optional external-witness threshold are fixed before any condition result is accepted.

The ordinary player path is unchanged. “Will you DM?” still opens a request-scoped play run; a scenario bundle is an experiment-owner sidecar and never a prerequisite for play.

Database schema 8 and event schema 1 remain unchanged. Seven new public JSON exchange/sidecar schemas describe the bundle protocol.

## Layering

```text
verified seed cube + validated single-block capsule, repeated 2..128 times
        │
        └─ scenario-bundle plan v1
              ├─ complete block roster and descriptive strata
              ├─ fixed rating contract and primary dimensions
              ├─ all-scheduled-block inclusion rule
              └─ optional external-receipt threshold
                    │
                    └─ private master schedule
                          ├─ randomized fixed block order
                          ├─ child scenario run ID per block
                          └─ child assignment seed per block
                                │
                                └─ atomic whole-tree publication
                                      ├─ public commitment
                                      ├─ every child scenario run
                                      ├─ every private assignment
                                      └─ four exact seed clones per child block
                                            │
                                            ├─ optional witness gate
                                            ├─ one active block at a time
                                            ├─ complete blind ratings
                                            ├─ immutable block seal
                                            └─ all blocks sealed before any unblind
                                                  │
                                                  └─ crash-resumable all-child unblind
                                                        └─ rater-level JSON/CSV report
```

A bundle reuses the rev0161 child scenario state machine rather than implementing a second condition runner. The bundle controls when each child may advance and when child unblinding is permitted.

## Authoritative topology

```text
10-preregistration.json
20-PRIVATE-schedule.json
30-public-commitment.json
witnesses/
    witness-NNNN-<witness-id>.json
blocks/<opaque-block-label>/
    scenario-runs/<fixed-run-id>/
        10-capsule.json
        20-PRIVATE-assignment.json
        cells/<opaque-cell-label>/...
        ratings/...
        run.json
        NEXT.md
        .run.lock
    60-block-seal.json
90-bundle-report.json
bundle.json
NEXT.md
.bundle.lock
```

`bundle.json` is authoritative. `NEXT.md` is a deterministic convenience pointer and may be rebuilt only after the entire parent and every child pass audit.

The public commitment names opaque block labels, child run IDs, exact seed boundaries, capsule digests, and assignment digests. It does not disclose condition mappings. The private schedule and child assignments remain owner-private.

## Preregistration contract

The plan contains every block's normalized absolute seed path, complete validated capsule, story/model strata, replicate label, and tags. It also fixes:

- the primary rating dimensions;
- whether preference rank is primary;
- all-scheduled-block inclusion;
- inclusion of terminal failures;
- rater-by-condition-within-block as the retained analysis unit; and
- an ordinal-data nonclaim.

All child capsules must have exactly the same rating scale, dimension prompts, and required rater count. A bundle with incomparable rating contracts refuses before publication. Story, model, script, and execution policy may differ when the plan records those differences as strata; the report does not pretend such blocks are exchangeable.

There is no v1 block-exclusion field. Every scheduled child and every terminal cell status enters the final report.

## Private schedule and commitment

`begin` generates one 32-byte master seed and deterministically orders blocks by SHA-256. It derives a collision-resistant opaque block label, fixed child run ID, and independent 32-byte assignment seed for every block. Each child assignment uses the bundle-supplied seed rather than sampling at child execution time.

The public commitment binds canonical digests of the complete private plan and schedule plus each block's seed boundary, capsule digest, and hidden assignment digest. A later retained-byte edit is detectable. This does not prove the randomness source, prevent a same-host owner from discarding an unwitnessed bundle, or establish trusted time.

## Atomic all-child publication

Every child is staged before the bundle becomes visible:

1. verify the source cube and capsule boundary;
2. construct the private schedule;
3. create each child scenario run under a hidden bundle staging tree;
4. create and verify all four exact SQLite seed clones per child;
5. preflight each child using its final authority path;
6. build the commitment, parent manifest, and deterministic pointer; and
7. rename the complete owner-private tree to its final path on the same filesystem.

Failure while staging any child removes the staging tree and leaves no visible final bundle. This narrows selection opportunities after one child has been observed. It is not a transaction across remote services, hostile filesystems, provider calls, or a story ledger.

Rev0162 consolidates clone creation in `clone_cube_exact`, sidecar member resolution and private directory creation in `sidecars`, and child construction in `stage_scenario_run`. Two competing draft experiment modules were removed so one bundle implementation and one vocabulary own the protocol.

## State machine

```text
awaiting-witnesses
    threshold met -> block-active

block-active
    child ready-to-unblind -> block-ready-to-seal

block-ready-to-seal
    freeze exact child/rating digests -> next block-active
    last seal                    -> ready-to-unblind

ready-to-unblind
    durable unblinding marker -> unblinding

unblinding
    idempotently unblind each sealed child
    publish deterministic aggregate -> unblinded
```

Exactly one block is active during execution. Earlier blocks form a sealed prefix and must remain `ready-to-unblind`; later blocks remain pristine. Directly changing a future child, advancing before a witness threshold, or unblinding an earlier child is detected by the parent audit.

## Witness gate

A plan may require zero to 64 external receipt descriptions before execution, and v1 retains at most 64. The bundle emits one exact public commitment and accepts receipts that bind its digest. The cap is checked before publishing the next receipt or changing the manifest. Each local witness record retains:

- witness and external receipt identities;
- receipt kind and service description;
- either an external locator or receipt SHA-256 digest;
- claimed witnessed time; and
- an explicit “operator-supplied, unverified” declaration.

Lacuna does not contact the service, verify signatures, validate timestamps, or prove availability. The gate is useful because an independent holder can later notice mutation or disappearance of the retained commitment. It cannot reveal an unwitnessed experiment that was created and discarded before anyone else saw it.

## Block execution and context separation

The bundle exposes only the current child's exact driver, return schema, rating form, or seal command. The child enforces condition-specific script, role, budget, transcript, and within-block context topology. The parent additionally scans every retained invocation across all blocks and refuses:

- reuse of a declared `context_id` across blocks;
- reuse of any non-null provider `invocation_id`; and
- duplicate non-null invocation IDs inside the candidate return.

The preflight check runs before active-child mutation. Full audit repeats the global check. These are consistency checks over host declarations, not provider attestations or proof of independent memory.

## Seal-before-any-unblind

A block seal is permitted only when its child has all fixed blind ratings and is `ready-to-unblind`. It binds the child run ID/path, capsule and assignment digests, blind-packet digest, and ordered rating artifact digests.

The seal does not call child unblind. The child remains structurally blind while later blocks execute. The parent audit now uses one shared sealed-child predicate for both the completed prefix and the all-block-ready state, and emits a typed `scenario-bundle-premature-unblinding` refusal when a direct child command crosses that boundary.

This design avoids sequential outcome leakage: an experiment owner cannot legitimately observe block 1's condition mapping and report before deciding how to operate block 2.

## Crash-resumable aggregate unblinding

When every block is sealed, the parent first writes `status = unblinding` and one fixed `unblinded_at`. It then unblinds children in preregistered order. After each child report, the parent durably records that child's report digest. A retry adopts already-valid child reports and continues; it never samples a new schedule or assignment.

After every child is unblinded, the parent deterministically joins all reports and publishes `90-bundle-report.json`. This is resumable construction, not one atomic cryptographic reveal. A same-host owner with private filesystem access can still inspect assignment files outside the cooperative workflow.

## Report model

The aggregate report retains one observation per rater × condition × block. Each observation contains:

- registered block/story/model/replicate identity;
- rater ID, condition, opaque cell label, and terminal cell status;
- exact integer dimension scores and preference rank;
- comments and transcript digest;
- final cube head and event-count delta; and
- host-declared invocation, time, token, cost, and completeness totals.

The descriptive summary emits counts and sums only. It performs no significance test, multiplicity correction, interval-scale claim, exclusion, causal estimate, or automatic winner selection.

JSON is the exact canonical export. CSV is a convenience view and prefixes text beginning with spreadsheet formula triggers (`=`, `+`, `-`, `@`, tab, carriage return, or newline) so opening the report in common spreadsheet software does not silently execute rater or stratum text as a formula.

## Locking and recovery

The parent always acquires `.bundle.lock` before invoking a child transition. Child operations acquire the selected `.run.lock`; the intended order is parent then child. Audits acquire child locks one at a time while the parent lock is held. Locks coordinate cooperative same-host processes only.

`scenario bundle recover` may:

- refresh parent status after a valid direct active-child transition;
- adopt an already-unblinded sealed child only after the parent durably entered `unblinding`; and
- rewrite deterministic `NEXT.md` and cached manifest state.

It may not invent witnesses, returns, ratings, seals, assignments, reports, or exclusions. Direct premature unblinding before the parent phase is contamination, not recoverable cache drift.

## Hyperlegible model entrance

The bundle parent can be a person, Codex, Claude Code, Gemini-oriented coding agent, ChatGPT with a connected tool, or another frontier host. The semantic protocol does not depend on provider-specific subagent syntax:

1. read only `NEXT.md` or `status`;
2. run the one printed parent command;
3. give a worker only the complete emitted handoff;
4. save exactly one schema-conforming return; and
5. return transition authority to the parent.

Native subagents are useful for the role-separated treatment. Separate chats or API contexts can implement the same topology. A weaker coordinator does not need to infer the experiment: every transition states one owner, one complete input, one expected schema, and one exact next command.

The cube can strongly prompt delegation, declare forbidden context, and verify identifier topology. It cannot force a product to create subagents or prove that their hidden memory and tools are independent.

## Residual risks

- A same-host owner can inspect private schedules/assignments or discard a bundle before an external party retains the commitment.
- Witness records are descriptions, not verified external proofs.
- Direct child commands can contaminate a bundle; audit detects them but cannot reverse already-published child reports.
- Cooperative file locks are not a hostile-user or distributed concurrency boundary.
- Structured labels do not guarantee semantic blinding.
- Context, provider, model, invocation, timing, token, cost, and failure metadata remain host declarations.
- Blocks can differ in unmodeled ways; strata are labels, not automatic statistical control.
- Rater identity, independence, masking, calibration, and ethics remain outside the kernel.
- The report is an auditable dataset, not a completed Gwern evaluation or evidence of general superiority.
