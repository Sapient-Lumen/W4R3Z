# Architecture — rev0161

## Purpose

Revision 0161 adds an executable comparative-scenario layer around Lacuna's ordinary turn and managed checkpoint machinery. It is designed to test, rather than assume, the central retcon-planning claim: a source-bound generate → judge → compress → verify loop may improve off-script continuation while controlling rubber reality, coincidence inflation, mystery unfairness, and agency loss.

The revision also refactors initial turn-run and checkpoint-run publication. The supplied path must resolve to the exact open `Cube`, and a complete private sidecar directory is now built off-path and published by one same-filesystem rename.

Database schema 8 and event schema 1 are unchanged. All scenario contracts are exchange/sidecar schemas.

## Layering

```text
verified seed cube
    │
    └─ scenario capsule v1
          ├─ fixed script/model/budget/rubric/rater count
          ├─ hidden random condition assignment
          └─ four exact SQLite backup clones
                 │
                 ├─ forward-only
                 ├─ prompt-only-retcon
                 ├─ lacuna-serial
                 └─ lacuna-role-separated
                        │
                        ├─ one active opaque cell at a time
                        ├─ condition-specific driver
                        ├─ exact transcript + invocation declaration
                        ├─ verified frozen clone receipt
                        └─ transcript-only blind packet
                                  │
                                  ├─ fixed complete ratings
                                  └─ deterministic unblinded report
```

The seed cube is never changed by the experiment. A cell clone intentionally preserves the seed cube ID; cell label and path provide experiment separation, not an ontological fork.

## Scenario state machine

```text
collecting-results
    pending prefix transition -> one active cell
    active + accepted return  -> recorded
    fourth recorded cell      -> awaiting-ratings

awaiting-ratings
    complete unique rating    -> awaiting-ratings
    fixed rating count        -> ready-to-unblind

ready-to-unblind
    deterministic join        -> unblinded

unblinded
    audit only
```

Recorded cells form a prefix, at most one cell is active, and pending cells must remain at the exact seed head/event count. A recorded clone must remain at its frozen receipt state.

## Private topology

```text
10-capsule.json
20-PRIVATE-assignment.json
cells/<opaque-label>/
    cube/
    turn-runs/
    checkpoint-runs/
    30-driver.json
    DRIVER.md
    40-cell-return.json
    50-cell-receipt.json
70-blind-rating-packet.json
ratings/rating-NNNN-<id>.json
90-unblinded-report.json
run.json
NEXT.md
.run.lock
```

`run.json` is authoritative and strict to the creating Lacuna version and absolute path. Private driver and assignment files remain in owner custody. Raters receive only the blind packet.

## Exact seed clones

Begin verifies the source cube, binds cube ID/head, event count, and a canonical semantic-snapshot digest, then uses SQLite backup into four private directories. Every clone is reopened and required to pass:

- deterministic cube verification;
- same cube ID;
- same head;
- same semantic snapshot digest; and
- same initial event count through later audit.

This is stronger than copying a prompt. Every condition starts from the same durable epistemic state.

## Hidden assignment

A 32-byte host random seed determines a SHA-256 sort of the four fixed condition names and opaque cell labels. The private assignment is written and digest-bound before any cell return is accepted. The public manifest contains labels and driver digests but no condition strings.

This detects later edits to one retained run. It does not prove externally witnessed randomness or that the owner never discarded an unpublished run. External commitment/witness integration remains future work.

## Condition contracts

All cells use the same capsule script, model declaration, sampling policy, and budgets. Topology differs only as declared:

- `forward-only`: ordinary narrator calls; checkpoint calls forbidden.
- `prompt-only-retcon`: exactly one accepted `monolithic-retcon` call per completed checkpoint.
- `lacuna-serial`: exactly one accepted generator/judge/compressor/verifier call in order, sharing one declared context per checkpoint.
- `lacuna-role-separated`: the same four accepted roles in order with pairwise-distinct declared contexts per checkpoint.

Every accepted ordinary call is `lacuna-narrator`, script-step-bound, and must correspond exactly to one retained transcript step. Checkpoint attempts follow the accepted ordinary call for that step and finish before the next accepted ordinary turn.

## Invocation custody

A cell return retains all attempts in sequence with phase, role, script/checkpoint step, provider/model/version, context ID, optional provider invocation ID, input/output digests, optional time/token/cost values, outcome, and failure data.

The runner enforces:

- contiguous one-based sequence;
- exact script-step membership;
- accepted outputs have output digests and no failure fields;
- failed attempts have a fixed failure class and no output digest;
- same-model policy when enabled;
- condition role/context topology;
- exact transcript-to-accepted-turn correspondence;
- fixed cell budgets;
- no declared context ID reuse across cells; and
- no non-null invocation ID reuse anywhere in the run.

These are host declarations. Lacuna does not possess provider-signed request/response receipts.

## Evidence separation

The report keeps three evidence classes distinct:

1. **Lacuna-derived mechanical evidence:** verified clone head, event-count delta, verification digest, retained artifact digests.
2. **Host-declared execution evidence:** model identity, contexts, attempts, latency, tokens, cost, and failures.
3. **Human-authored evidence:** blind ordinal scores, ranks, and comments.

No class silently upgrades another. A high human score is not kernel correctness; a verified cube is not good fiction; declared low cost is not metered fact.

## Blind packet and unblinding

The blind packet is deterministically rebuilt from accepted cell returns and receipts. It contains only opaque labels, status, player-visible transcript, transcript digest, and the fixed rubric. Ratings bind the exact blind-packet digest. Unblinding is refused until the predeclared number of unique raters submits a complete score/rank matrix.

Structured blinding does not prove semantic anonymity. A transcript can reveal its method through style, refusal text, or visible seams.

## Shared atomic initial publication

`publish_private_directory` is now shared by turn runs, checkpoint runs, and scenarios:

1. choose a collision-resistant final ID;
2. create an owner-only hidden staging directory beside it;
3. write lock, members, manifest, and deterministic pointer into staging;
4. rename the whole directory to the final path; and
5. best-effort fsync the parent directory.

Construction failure removes staging and leaves no final run-shaped directory. This narrows partial-publication windows on one filesystem. It is not a cross-resource transaction: ordinary turn/checkpoint request-source events can become durable before sidecar publication, and SQLite plus sidecars remain separate durability domains.

## Path authority refactor

Ordinary `turn run begin`, managed `checkpoint run begin`, and `scenario begin` now resolve `cube.root` and the caller-supplied path with `strict=True` and require exact equality before publication. A caller cannot open one cube while causing a plausible run manifest to name another path.

## Subagent compilation

Scenario drivers and existing task cards make the intended topology executable for weaker coordinators. Each handoff contains the complete least-context input, role, fixed return schema/template, forbidden context, and parent command. Codex, Claude Code, Gemini-oriented local definitions, ChatGPT human bridges, or portable API callers can all consume the same semantic contract.

The parent retains directory access and transition authority. Workers receive only exact cards and return one JSON object. The cube can prompt explicit delegation and bind declarations; it cannot force a product to create subagents or prove independent memory.

## Recovery

`scenario recover` repairs only `NEXT.md` after full authoritative audit. It does not infer missing returns, rewrite assignments, recreate ratings, or advance state. Any mismatch in capsule, assignment, driver, clone, return, receipt, blind packet, rating, or report refuses.

## Residual risks

- same-host owners can rerun/discard unpublished experiments unless an external witness retains a commitment;
- private drivers and assignment coexist in one run directory, so filesystem access control—not cryptography—protects blinding;
- provider/model/context/timing/token/cost claims are declarations;
- semantic blinding, model compliance, and human independence are not machine-provable here;
- execution is serial and one scenario block has one observation per condition;
- no replicate bundle, random-effects analysis, power calculation, or multiplicity policy is implemented;
- initial sidecar publication is atomic only at the directory-name boundary on one cooperative filesystem; and
- hostile same-user mutation of code, database, sidecars, and declarations together remains outside the trust boundary.
