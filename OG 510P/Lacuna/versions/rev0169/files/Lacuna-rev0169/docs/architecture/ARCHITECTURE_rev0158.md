# Architecture — rev0158

## Purpose

Revision 0158 makes Lacuna’s model entrance an explicit **context compiler** rather than an implicit repository ritual.

The ledger kernel still decides which typed changes may commit. The request-scoped sidecar still holds exact input, task cards, model returns, proposal, rollback preparation, verifier result, and receipt. This revision adds the missing boundary between those two layers and an actual model invocation:

- typed `session-control` versus `play-turn` input;
- one-command campaign resolution/bootstrap plus run creation;
- a provider-neutral, self-contained delegated-stage envelope;
- descriptor-verified reads for every authoritative sidecar member; and
- explicit recovery that may regenerate only the deterministic human pointer.

Rev0157’s exact rollback rehearsal, frozen event envelope, historical request-head reconstruction, post-commit receipt recovery, and cooperative same-run lock remain unchanged.

## Layered authority

```text
player or operator
    │ exact text + declared input kind
    ▼
request issuance in the cube ledger
    │ request ID, source, digest, grant, expected head
    ▼
request-scoped sidecar run
    │ packet, topology, role cards, exact returns, proposal
    ▼
provider-neutral dispatch (read-only handoff)
    │ complete embedded card + exact return contract
    ▼
external model / human worker
    │ one JSON object, no mutation authority
    ▼
parent accept + exact kernel preparation + commit
    │
    ▼
passing receipt; only its top-level narration is player-visible
```

The external worker never owns request issuance, sidecar state transition, recovery, preparation, commit, or player-visible presentation. Provider aliases route work; they do not grant authority.

## Typed input contract

New packets use `lacuna.turn-request.v3` and include:

```json
"input_kind": "session-control" | "play-turn"
```

The same value is retained in source protocol `lacuna.turn-request-source.v2`, audited before proposal commit, copied into orchestration cards, and exposed in agent dispatches.

`session-control` means the exact text manages the play session rather than asserting an in-world event. `play-turn` means the exact text is offered as an in-fiction player turn, while remaining untrusted input: it can prove an utterance, choice, request, or attempt, not automatic physical success.

Historical request-v2 packets and source-protocol-v1 records remain readable and default to `play-turn`. Compatibility is explicit and one-way; old records are not rewritten and prose heuristics do not upgrade them to session control.

## Direct play start

`./lacuna play start` composes existing entrances without creating a second semantic kernel.

1. Resolve the supplied path.
2. Accept an existing cube or campaign library.
3. When `--bootstrap` is present, initialize only an absent or empty path.
4. Refuse a foreign nonempty path rather than overlaying Lacuna state.
5. Select an existing sole active campaign, use an explicit selected campaign, or create one default campaign when bootstrap permits it.
6. Resolve audience and actor identities from campaign metadata when available.
7. open a director-scoped request with `input_kind = session-control`;
8. map `chat` and `workspace` profiles to a solo run and `orchestrated` to deterministic auto topology; and
9. return `lacuna.play-start.v1` with the complete run and next action.

The default exact text is `Will you DM?`. The command invokes no model and commits no narration.

## Request-scoped run remains the custody spine

`lacuna.turn-run.v2` remains authoritative for sidecar state. Its fixed artifact names, digests, roles, schemas, topology, status, and deterministic next action are audited at every transition.

The state machine is:

```text
solo:
  awaiting-solo-proposal -> ready-to-commit -> committed

pair:
  awaiting-planner -> awaiting-narrator -> awaiting-pair-proposal
  -> ready-to-commit -> committed

full:
  awaiting-planner -> awaiting-narrator -> awaiting-proposal-builder
  -> awaiting-verifier -> ready-to-commit | verifier-refused
  -> committed
```

Only the parent runs `accept`, `recover`, and `commit`. A delegated worker receives one role card and produces one return object. A parent-owned proposal stage stays with the parent even when previous stages used subagents.

## Self-contained delegated-stage dispatch

`turn run dispatch` emits `lacuna.agent-dispatch.v1` only for a currently delegated state. It takes the same run lock used by other transitions and first audits the complete authoritative chain.

The envelope binds:

- run ID/path and exact current status;
- provider route and role-specific alias;
- explicit input kind;
- retained card path, role, schema, media type, and canonical digest;
- the complete task card as `input_document`;
- the exact required return schema;
- a save path and shell-quoted parent accept command;
- worker permissions, worker prohibitions, parent-only actions, and nonclaims.

Supported route labels are `portable`, `codex`, `claude-code`, `gemini-cli`, and `chatgpt`. A route label changes only the discovery alias. The embedded card and return contract remain the semantic boundary.

Embedding the card is important for remote chat contexts: the worker need not access the local filesystem, infer which file is current, or reconstruct a prompt from documentation. The dispatch still does not invoke, authenticate, isolate, or attest a provider.

## Sidecar member integrity

Every authoritative JSON or text read now goes through one descriptor-stable reader.

For each member the reader:

1. opens read-only with close-on-exec and no-follow where available;
2. obtains descriptor and pathname metadata;
3. requires both to name the same regular file;
4. requires a single hard-link count;
5. refuses a declared size above 16 MiB;
6. reads at most the configured bound;
7. rechecks device, inode, link count, size, modification time, and change time on the descriptor;
8. rechecks that the pathname still names that descriptor; and
9. only then decodes/parses and checks the manifest digest.

This closes ordinary symlink, hard-link, nonregular-member, oversized-member, and detected pathname-substitution mistakes. It is not protection against a hostile process with the same operating-system identity or control of the parent filesystem.

## Deterministic pointer recovery

`NEXT.md` is useful for humans and weaker coordinators but is not authoritative. Ordinary audit requires its exact deterministic bytes and refuses a missing, edited, symlinked, or substituted pointer.

`turn run recover` is deliberately narrow:

1. acquire the run lock;
2. audit `run.json` and every authoritative retained artifact while ignoring only the current pointer;
3. regenerate `NEXT.md` from the audited manifest;
4. rerun the complete audit; and
5. return the unchanged authoritative manifest.

Recovery does not reconstruct cards, returns, proposals, preparations, or receipts. An authoritative mismatch remains a refusal.

This is separate from rev0157’s post-commit receipt recovery. Pointer recovery repairs a deterministic view. Receipt recovery authenticates a durable SQLite change against the frozen preparation and historical request-head cube without reapplying events.

## Exact kernel preparation is still the readiness boundary

A sidecar cannot become `ready-to-commit` merely because role contracts agree. The exact final proposal must pass the real mutation engine under rollback. Preparation freezes generated operation IDs, timestamp, event IDs, payloads, event hashes, change receipt, head, and requested post-state contexts.

Direct commit reruns that exact envelope inside the durable transaction and refuses any divergence. If SQLite committed and sidecar publication failed, historical recovery verifies the durable change before materializing a receipt. Later valid ledger heads do not prevent that verification because the request-head prefix is independently reconstructed.

## Context topology

The cube manufactures role-specific information boundaries:

- **planner:** exact input, audience context, separate planner context, grant, and planning return contract;
- **narrator:** exact input, audience context, and approved observable plan, with planner context/private notes/candidate operations omitted;
- **proposal builder:** fresh packet plus accepted upstream artifacts and exact proposal contract;
- **verifier:** fresh packet plus exact candidate proposal and fail-closed review contract;
- **parent:** run custody, acceptance, preparation, commit, and receipt presentation.

This topology is useful when it encodes information asymmetry. More agents with identical context are not treated as stronger evidence.

## Stable boundaries and nonclaims

Revision 0158 does not add a model SDK, network transport, provider credential handling, hard context isolation, provider-signed invocation receipt, per-cube scheduler, distributed lock, run relocation, encryption, retention policy, candidate-world generator, rollout engine, aesthetic scorer, checkpoint compressor, or completed Gwern comparison.

The database remains schema 8 and the event ledger remains schema 1. New behavior is request/exchange, host, sidecar, and documentation evolution rather than a database migration.
