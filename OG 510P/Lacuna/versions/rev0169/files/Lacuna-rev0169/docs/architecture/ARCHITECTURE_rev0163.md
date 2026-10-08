# Architecture — rev0163

## Purpose

Revision 0163 closes a boundary that the managed checkpoint and scenario layers previously stopped short of enforcing: **the model that continues the story after a checkpoint must cross the compression bottleneck too**.

Rev0160 made generator → judge → compressor → verifier an exact managed walk. Rev0161–rev0162 made serial versus role-separated execution an auditable comparative treatment. But a long-lived narrator could still remember rejected candidates, rollout beats, score rationale, and parent discussion after those workers finished. Distinct checkpoint workers alone therefore did not test Gwern's “compress and forget” step.

Rev0163 adds one deterministic post-commit continuation artifact, makes it the committed checkpoint's next action, and strengthens scenario topology so controls intentionally retain one context while the separated treatment starts a new capsule-bound narrator segment.

Database schema 8 and event schema 1 remain unchanged. The new capsule is a private exchange/host artifact, not a story-ledger event or write grant.

## Layering

```text
managed checkpoint run
  request -> candidates -> judgment -> compression
          -> parent proposal -> verifier -> kernel review -> commit
                                                        │
                                                        v
                              authenticated accepted request/proposal/receipt
                                                        │
                                                        v
                           checkpoint narrator capsule v1
                              ├─ accepted previous narration
                              ├─ post-commit audience context
                              ├─ selected state-card body + digest
                              ├─ retained/omitted elements
                              ├─ preserved unknown IDs
                              ├─ forbidden contradictions
                              └─ next pressures
                                                        │
                                      fresh narrator context + next player input
                                                        │
                                                        v
                                          new source-bound ordinary turn
```

The parent may retain the complete private checkpoint sidecar. The continuing narrator receives the capsule, not the full checkpoint chain.

## Capsule contract

`lacuna.checkpoint-narrator-capsule.v1` is strict and version-bound. It includes:

- run, checkpoint, cube, audience, actor, and post-commit-head identity;
- canonical digests of the retained request, proposal, receipt, compression, state card, and audience context;
- the accepted checkpoint narration and exact post-commit audience projection;
- the winner-only private planning card and its bounded continuation fields;
- fixed operating instructions, exclusions, and nonclaims.

The builder interface accepts only:

```text
run ID
request
assembled proposal/compression
accepted checkpoint receipt
retained request/proposal/receipt digests
```

It does not accept candidates, judgment, rejected rollouts, worker provenance, or verifier findings. This is a construction-level least-context boundary rather than a request that a coordinator remember to redact a larger object.

Validation recomputes the audience-context digest and state-card digest, checks the accepted turn receipt and post-commit head, requires exact fixed instructions/nonclaims, and refuses version reinterpretation.

## Managed-run integration

A committed checkpoint now renders this deterministic next action:

```bash
./lacuna checkpoint run narrator-capsule RUN_PATH --format markdown
```

The command:

1. resolves and locks the exact managed run;
2. performs the complete existing run audit, including durable receipt authentication;
3. refuses unless status is `committed`;
4. reads the exact retained request, proposal, and receipt through the hardened sidecar boundary; and
5. returns a deterministic capsule without mutating the run or cube.

`NEXT.md` remains derived from `run.json`. The capsule itself is generated on demand rather than added as a new authoritative managed-run member, avoiding a second post-commit durability state and keeping the committed run's existing receipt authoritative.

## Scenario continuation topology

Every condition driver now fixes `continuation_mode`:

| Condition | Checkpoint work | Continuation topology |
|---|---|---|
| `forward-only` | none | one persistent context for the complete cell |
| `prompt-only-retcon` | one monolithic call per checkpoint | one persistent context for narration and checkpoint work |
| `lacuna-serial` | four ordered managed roles | one persistent context for narration and all roles |
| `lacuna-role-separated` | four fresh pairwise-distinct role contexts | one narrator context per story segment; after each checkpoint, a new context bound to the exact capsule |

Invocation custody adds:

- `managed_checkpoint_id` for every managed checkpoint attempt;
- `continuation_checkpoint_id` for the first narrator segment after a completed separated checkpoint; and
- `continuation_capsule_sha256` for the exact capsule supplied to that segment.

Topology validation enforces stage order, retry locality, one accepted output per role, distinct checkpoint IDs, persistent controls, fresh role contexts, fresh post-checkpoint narrator contexts, and exact checkpoint/capsule pairing on every attempt of the first subsequent turn.

These fields remain host declarations. They make inconsistent claims refuse; they do not attest what a provider retained or what bytes were actually supplied.

## Observable-continuation invariant

A scenario checkpoint is now invalid after the final script step. Every checkpoint must have at least one subsequent scripted ordinary turn.

Without this rule, a condition could complete all checkpoint machinery after the last rated narration while producing no player-visible continuation influenced by the checkpoint. Such a block would measure protocol execution rather than the claimed treatment. The template now contains a checkpointed off-script step followed by an explicit post-checkpoint continuation step.

## Player and operator entrances

The ordinary player path remains one sentence: “Will you DM?”

`OPERATE_LACUNA.md` is the short root entrance for:

- chat-only play;
- one tool-capable parent;
- bounded worker dispatch;
- the clean fresh-narrator condition;
- state-card retention; and
- recovery/trust boundaries.

Detailed product and experiment guidance remains in focused operator documents. The rev0160 all-in-one field manual is treated as research input, not copied into a second version-locked documentation tree.

## Authority matrix

| Actor/artifact | May do | May not do |
|---|---|---|
| checkpoint workers | return one exact role object | accept, assemble, commit, recover, or continue play |
| parent | route, validate, commit, compile capsule, start fresh narrator, open next turn | claim provider attestation or let capsule bypass ordinary turn authority |
| capsule | convey exact accepted public context and compact private guidance | mutate the cube, canonize the state card, prove forgetting, or reconstruct excluded artifacts |
| fresh narrator | propose an audience-safe continuation from capsule + next input | inspect checkpoint sidecars, commit, recover, or present unaccepted prose as fact |
| kernel | validate and commit typed source-bound changes | invoke models, judge artistic sufficiency, or erase provider memory |

## Unchanged foundations

Rev0163 does not change:

- database schema 8 or event schema 1;
- managed checkpoint request, candidate, judgment, compression, proposal, verifier, review, receipt, or invocation semantics;
- ordinary turn packet/run/preparation/receipt semantics;
- scenario randomization, cloning, blinding, rating, bundle witnessing, sealing, or delayed unblinding;
- commitment, consequence, particle, factor, fair-play, projection, or access semantics; or
- parent-only mutation and presentation authority.

## Public-context parity boundary

The capsule can authenticate typed audience context and the accepted checkpoint narration because those objects exist in the committed run. Lacuna intentionally does not retain full transcript bodies. A host that needs transcript-level continuity must bind and supply the same player-visible history across conditions outside the capsule command. This remains experiment custody rather than inferred kernel truth.

## Residual risks

- A parent can record a valid digest while supplying extra context to a narrator.
- A provider can correlate nominally fresh contexts through hidden state, tools, filesystem access, account memory, or logs.
- Scenario continuation fields are declarations rather than direct provider or sidecar attestations.
- A compact state card can be incomplete, overcommitted, or artistically poor.
- The usable state-card body remains private sidecar/capsule content; a ledger digest cannot reconstruct it.
- The capsule excludes known artifact classes but does not prove semantic nonleakage through the selected card or public context.
- A checkpoint after the final script step now refuses, but scenario quality and checkpoint timing remain experiment-design duties.
