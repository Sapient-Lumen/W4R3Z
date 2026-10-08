# Architecture — rev0164

## Purpose

Revision 0164 makes the post-checkpoint information bottleneck an exact ordinary-turn handoff rather than an operator convention. Rev0163 authenticated the winner-only checkpoint capsule. Rev0164 binds that capsule to the next exact player input, a least-authority ordinary turn packet, an exact proposal template, and an optional ledger-authenticated public-prose history.

The database remains schema 8. Immutable event envelopes remain schema 1. The new contracts are host-side exchange artifacts only.

## Context path

```text
committed checkpoint run
    │ full audit + durable receipt authentication
    ▼
checkpoint narrator capsule v1
    │ selected state card + typed audience context
    │ no candidates / rejected rollouts / scores / verifier findings
    ▼
optional public-history v1 (parent/auditor only)
    │ exact player/narrator bytes + run/source/ledger custody
    │ authenticated back to durable request and narration sources
    ▼
public-history-view v1 (fresh narrator only)
    │ ordered public prose + digest
    │ no run/request/proposal IDs, receipt hashes, or event positions
    ▼
checkpoint run next-turn
    │ exact next player input
    │ audience-only, play-turn, solo, no-anchor packet
    ▼
checkpoint continuation dispatch v1
    │ one lacuna-fresh-narrator worker
    │ one exact turn-proposal.v2 template
    │ one save path + parent accept command
    ▼
ordinary turn run
    │ accept → exact rollback preparation → parent commit/recovery
    ▼
accepted turn receipt narration
```

The checkpoint sidecar and ordinary turn sidecar remain separate authority domains. The continuation dispatch is recomputed from both; it is not stored as a third mutable state machine.

## One-command continuation

`begin_checkpoint_continuation_turn`:

1. locks and fully audits the checkpoint run;
2. requires status `committed`;
3. rebuilds and validates the authenticated narrator capsule;
4. opens the bound cube and requires its live head to equal the checkpoint post-commit head;
5. authenticates checkpoint chronology and any supplied full public-history artifact **before creating the turn run**;
6. opens one ordinary run with `input_kind=play-turn`, `director=False`, `mode=solo`, `allow_anchor=False`, and no privileged planner context; and
7. invokes the lower-level two-run bridge to emit the exact continuation dispatch.

Validation-before-creation matters: malformed, forged, wrong-cube, wrong-audience, or chronologically invalid history cannot leave an orphan continuation turn.

## Lower-level two-run bridge

`build_checkpoint_continuation_dispatch` is useful when a parent already opened the exact turn. It acquires locks in fixed checkpoint-then-turn order and requires:

- committed checkpoint;
- fresh ordinary state `awaiting-solo-proposal`;
- selected mode `solo`;
- same cube ID and canonical cube path;
- active source-bound request opened directly from the checkpoint post-commit head;
- `play-turn` input, audience-only context, no director grant, and no anchor authority;
- live cube head equal to the turn packet expected head; and
- authenticated same-cube/audience public history ending before the checkpoint request, when supplied.

It writes no file, invokes no provider, accepts no model output, and mutates no cube.

## Continuation dispatch

`lacuna.checkpoint-continuation-dispatch.v1` contains:

- checkpoint run/checkpoint/receipt/capsule identity;
- turn run/request/packet identity;
- provider route and dedicated `lacuna-fresh-narrator` alias;
- `context_requirement: fresh-post-checkpoint`;
- canonical digest of the embedded continuation input;
- one exact proposal template and ordinary-turn accept command;
- fixed instructions and worker/parent authority split; and
- explicit exclusions and nonclaims.

The embedded continuation input carries:

- checkpoint request and post-commit event positions;
- state-card, compression, proposal, request, receipt, and audience-context digests;
- accepted previous checkpoint narration;
- exact next player input and digest;
- typed audience context rebound only at the turn head;
- selected private state card and bounded planning fields;
- ordinary turn response rules; and
- either `typed-only` public context or one `lacuna.public-history-view.v1` prose projection.

The full `lacuna.public-history.v1` artifact and its source custody are **not** sent to the fresh narrator. The continuation source retains its full artifact digest, deterministic history ID, public-entry digest, and final event position so the parent can audit which parent artifact produced the view.

Validation recomputes all local canonical digests, requires the public-history mode and nullable custody fields to agree, recomputes the exact save path and parent accept command, requires the exact JSON-only return format and narration-only empty-operation starting template, and rejects any altered fixed instruction, authority, exclusion, or nonclaim list.

## Public-history compiler and authentication

`lacuna.public-history.v1` is a private parent/auditor artifact, not a story-ledger record. `history build` accepts an explicit ordered list of committed managed ordinary turn runs.

For each run, `committed_turn_public_record` performs full turn-run audit under the run lock and exports:

- exact player input and accepted receipt narration;
- input kind and ordinary request purpose;
- run, request, source, proposal, actor, packet, and receipt custody; and
- request/commit ledger heads and event sequences.

It does not export planner context, proposal operations, preparation, verifier return, checkpoint artifacts, or private notes.

The compiler requires one cube, one audience, ordinary request purpose, and strict nonoverlapping ledger order. It separates `public_entries` from `source_custody`, digests both arrays independently, and derives a deterministic history ID from those digests and scope.

Internal self-consistency is not enough. `authenticate_public_history` opens and verifies the cube, then for every entry:

- reloads and validates the immutable source-backed turn request;
- matches request, proposal, actor, audience, narration-source, input-kind, purpose, head, and player-input digest;
- resolves request and post-commit heads to their immutable event sequences;
- authenticates the proposal changeset boundary; and
- authenticates the narration source, metadata, content digest, and first proposal event.

Therefore a host cannot replace player or narrator prose, recompute every artifact-local hash and history ID, and still pass continuation authentication. Run IDs and packet/receipt hashes remain host-sidecar custody; the retained runs are needed to re-audit those fields independently.

## Least-context public-history view

`lacuna.public-history-view.v1` is derived only after the full parent artifact has validated. It contains:

- history/cube/audience identity;
- entry count and public-entry digest;
- exact ordered `player_input` and accepted `narration`; and
- fixed instructions/nonclaims treating all embedded story text as quoted untrusted data.

It omits source-custody identifiers, packet and receipt hashes, proposal IDs, and event positions. This is both a usability and information-minimization refactor: weaker narrators receive prose continuity rather than an audit ledger they do not need.

## Ledger chronology refactor

`Cube.event_sequence(head)` centralizes immutable head-to-sequence lookup. Genesis is sequence zero; a malformed digest or unknown head produces a typed refusal. This removes raw event-table queries from continuation and public-history modules and gives future host artifacts one consistent ancestry primitive.

## Provider roles

A fifth model role is discoverable:

| Route | Alias |
|---|---|
| portable | `lacuna-fresh-narrator` |
| Codex | `lacuna_fresh_narrator` |
| Claude Code | `lacuna-fresh-narrator` |
| Gemini CLI | `lacuna-fresh-narrator` |
| ChatGPT | fresh post-checkpoint narrator context |

The checked-in role definitions are read-only/no-tool behavioral adapters. The exact per-invocation dispatch remains controlling.

## Authority and durability

The fresh narrator may produce one proposal object only. The ordinary turn parent retains all authority to:

- save and accept the return;
- correct or abandon a kernel-invalid proposal;
- manufacture exact rollback preparation;
- commit or authenticate an already-durable commit; and
- present receipt narration.

The continuation command creates an ordinary turn request source, so it is not read-only. It does **not** commit fictional mutation. The generated dispatch itself is deterministic and side-effect-free after that turn exists.

## Explicit nonclaims

Rev0164 does not prove provider identity, fresh memory, tool denial, transcript completeness, prose entailment, state-card sufficiency, artistic quality, or experimental efficacy. Public history is exact only for the runs supplied. The parent or provider can still leak extra information outside the validated dispatch. Provider and context labels remain host declarations.
