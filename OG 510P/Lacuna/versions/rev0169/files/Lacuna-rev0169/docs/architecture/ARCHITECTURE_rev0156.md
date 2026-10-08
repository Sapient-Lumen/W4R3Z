# Architecture — rev0156

## Architectural thesis

Revision 0156 turns Lacuna’s model-facing orchestration from a set of individually correct low-level commands into one request-scoped, resumable sidecar state machine.

The kernel boundary remains unchanged:

- SQLite and the immutable event ledger own durable epistemic mutation;
- a source-bound turn packet describes one proposed interaction at one expected head;
- only `turn commit` semantics can accept a proposal and produce a passing receipt;
- model invocation, prose policy, provider authentication, and host scheduling remain outside the kernel.

The new run layer owns **workflow custody**, not world truth. It records which exact artifact exists, which exact role owns the next step, which schema must come back, and which command may advance the chain. This is the missing bridge between “the protocol is documented” and “a fresh or weaker model can actually traverse it over several invocations.”

## Control planes

Lacuna now has four explicit planes.

| Plane | Authority | Durable in cube? | Primary artifacts |
|---|---|---:|---|
| Epistemic kernel | Accept/reject typed world mutation | Yes | events, projections, receipts |
| Turn contract | Bind one player input and proposal to one head/grant | Request source yes; packet/proposal external | packet, proposal, receipt |
| Orchestration protocol | Manufacture least-context roles and digest-bound handoffs | No | plan, task cards, role returns |
| Turn-run sidecar | Retain request progress and expose one audited next action | No | `run.json`, `NEXT.md`, staged artifacts |

The sidecar never upgrades an advisory artifact into authority. `ready-to-commit` means only that the workflow has an accepted proposal and, for `full`, a passing advisory verifier return. The kernel can still refuse stale head, malformed operations, scope violations, or any other invariant.

## Request-scoped run directory

A run is created under an operator-selected root, normally `.lacuna-runs/`, with mode `0700` on the run directory. Its identity is a generated `run_*` ID. Version 1 records absolute paths and therefore does not claim relocation portability.

The stable file layout is:

```text
RUN_PATH/
├── 00-player-input.txt
├── 10-turn-packet.json
├── 11-orchestration-plan.json
├── 20-planner-card.json
├── 21-planner-return.json
├── 30-narrator-card.json
├── 31-narrator-return.json
├── 40-proposal-builder-card.json
├── 41-proposal-draft.json
├── 42-turn-proposal.json
├── 50-verifier-card.json
├── 51-verifier-return.json
├── 60-turn-receipt.json
├── run.json
└── NEXT.md
```

Only the artifacts appropriate to the selected topology and current stage may exist. Missing required artifacts and unexpected future-stage artifacts both refuse.

`run.json` is the strict machine-readable authority for sidecar state. `NEXT.md` is a deterministic human/model-readable rendering. An edited `NEXT.md` does not become instruction; audit refuses it because it no longer matches `run.json` and the recomputed state.

## Lifecycle

The public state machine is intentionally small:

```text
turn run begin
      │
      ├─ solo ───────────────► awaiting-solo-proposal
      │                              │ accept proposal
      │                              ▼
      │                        ready-to-commit
      │                              │ commit
      │                              ▼
      │                           committed
      │
      ├─ pair ───────────────► awaiting-planner
      │                              │ accept planner return
      │                              ▼
      │                        awaiting-narrator
      │                              │ accept narrator return
      │                              ▼
      │                     awaiting-pair-proposal
      │                              │ accept parent proposal
      │                              ▼
      │                        ready-to-commit ─► committed
      │
      └─ full ───────────────► awaiting-planner
                                     │
                              awaiting-narrator
                                     │
                         awaiting-proposal-builder
                                     │
                              awaiting-verifier
                                  ┌──┴──┐
                              refuse   pass
                                │        │
                    verifier-refused  ready-to-commit
                                         │
                                      committed
```

The public commands are:

```bash
./lacuna turn run begin REFERENCE --root .lacuna-runs --player-input-file PLAYER.txt --director --mode auto
./lacuna turn run status RUN_PATH
./lacuna turn run accept RUN_PATH MODEL_RETURN.json
./lacuna turn run commit RUN_PATH
```

Every transition first performs a complete audit of the current run. A return is accepted only when its root schema is exactly the schema expected at that stage and its packet/upstream bindings validate. There is no generic “put a JSON file into the run” path.

## Begin boundary and exact player input

`turn run begin` performs these operations in order:

1. resolve and verify the cube;
2. create the request-scoped directory;
3. retain the exact UTF-8 player-input text;
4. open a source-bound turn request in the cube;
5. build and strictly validate the turn packet;
6. compute the deterministic orchestration plan;
7. create either a safe solo proposal draft or the planner card;
8. write `run.json` and deterministic `NEXT.md`;
9. re-audit the complete run before returning it.

`--player-input-file` is the preferred boundary. It avoids shell reinterpretation and preserves line endings and metacharacters as read. `-` means standard input. The packet stores the same text and digest; audit refuses any mismatch between retained text, packet body, or identity digest.

A begin-time crash after the turn request has been opened but before the sidecar is completely written can leave a request in the cube without a usable run. Version 1 documents this recovery boundary rather than claiming a cross-filesystem transaction.

## Manifest and artifact binding

`run.json` uses `lacuna.turn-run.v1` and contains:

- run and cube identity;
- original reference and resolved cube path;
- requested and selected topology;
- exact turn identity (`request_id`, source ID, proposal ID, expected head, player-input digest, packet digest);
- one fixed metadata slot for every possible artifact;
- current status;
- deterministic next action;
- explicit nonclaims.

Every referenced artifact has a fixed filename, media type, schema, role, and SHA-256 digest. Audit rejects:

- missing or additional manifest fields;
- path substitution or directory traversal;
- schema or role relabelling;
- invalid or edited canonical JSON;
- text/packet digest disagreement;
- packet or plan recomputation disagreement;
- stage-inappropriate artifacts;
- role returns from another packet or edited upstream chain;
- proposal identity/grant mismatch;
- receipt identity mismatch;
- manifest status inconsistent with the artifact topology;
- `NEXT.md` inconsistent with the deterministic next action.

For JSON, the digest is over Lacuna’s canonical serialization of the parsed value. Whitespace and object-key order are not treated as semantic custody. Exact byte custody is claimed for the retained player-input text, not for arbitrary JSON file formatting.

## Deterministic next action

At every state, `next_action` contains exactly:

- `owner`;
- `action`;
- `input_path`;
- `expected_schema`;
- `command`;
- `player_visibility`.

This is deliberately more constrained than a generic workflow engine. A fresh parent does not infer which file is current, which role should run, or which CLI flags are needed. A worker receives one complete generated artifact and one exact return contract. The parent advances only with the generated accept or commit command.

Delegated actions also include provider aliases in plain language:

| Portable role | Codex | Claude Code | Gemini CLI | ChatGPT fallback |
|---|---|---|---|---|
| `lacuna-planner` | `lacuna_planner` | `lacuna-planner` | `lacuna-planner` | planner-only context |
| `lacuna-narrator` | `lacuna_narrator` | `lacuna-narrator` | `lacuna-narrator` | audience-only narrator context |
| `lacuna-proposal-builder` | `lacuna_proposal_builder` | `lacuna-proposal-builder` | `lacuna-proposal-builder` | builder-only context |
| `lacuna-verifier` | `lacuna_verifier` | `lacuna-verifier` | `lacuna-verifier` | verifier-only context |

The sidecar prompts the parent to invoke a bounded role when the topology calls for one, but it does not call provider APIs or prove that the provider isolated the context.

## Topology semantics

The deterministic planner from rev0155 remains the source of topology selection.

### Solo

One parent receives the complete packet and constructs the final proposal from `response_contract.proposal_template`. The run also writes a safe, narration-placeholder proposal draft with empty operations. Solo is appropriate for a single tool-capable parent or a human ChatGPT paste bridge.

### Pair

A privileged planner produces an audience-safe observable plan. An audience-only narrator receives a manufactured card containing only allowed context and that plan. The run then produces a narration-only proposal draft for parent review. This is the default “information asymmetry matters more than agent count” shape.

### Full

Planner and narrator are followed by a proposal builder and an advisory verifier. The verifier card starts fail-closed and a refusal closes the v1 run. The parent must begin a fresh run rather than overwrite rejected history in place.

Manual `solo`, `pair`, or `full` remains visible in both requested and selected mode. `auto` uses only explicit packet-visible signals; it does not let a model secretly upgrade its own authority.

## Authority and visibility

The parent/coordinator alone may:

- begin a run and thereby open a source-bound request;
- accept stage returns into the sidecar;
- review or construct parent-owned proposals;
- invoke the kernel commit;
- present accepted narration.

Workers cannot commit by role contract and checked-in provider configuration. The run state machine does not expose a commit transition to a worker-owned state.

The visibility rule is repeated in every next action: proposed narration has not happened. Only the top-level `narration` in a passing `lacuna.turn-receipt.v2` may be presented as accepted play. A task card, role return, proposal draft, proposal, or verifier pass is not a receipt.

Planner context is not included in the commit receipt by default. An operator must explicitly opt into `--include-planner-context`; the generated model entrance no longer requests it automatically.

## Provider entrance architecture

The portable protocol is primary; provider files are discovery adapters.

- `AGENTS.md` routes play versus repository work and teaches the turn-run state machine.
- `.codex/agents/*.toml` map four portable roles to Codex custom agents with read-only sandboxes.
- `CLAUDE.md` imports the common parent instructions; `.claude/agents/*.md` use empty tool allowlists.
- `GEMINI.md` imports the common parent instructions; `.gemini/agents/*.md` use empty tool allowlists.
- ChatGPT project instructions define chat-only play, a human paste bridge, role-dedicated contexts, and a narrow connected-host target without pretending that an uploaded repository is a durable local filesystem.

A provider adapter can fail or drift without changing the exchange contract. The host may downgrade from native subagents to serial role contexts, one workspace parent, a human bridge, or chat-only play while preserving capability honesty.

## Chat-only and governed play

“Will you DM?” is a complete player-level play request, not a CLI request and not an in-world action.

A conversation-only model can begin a scene immediately. Without a connected or human bridge, it must disclose once that the chat is not yet committed to a Lacuna cube. This route provides play, not durable cube mutation.

Governed play requires one of:

- a shell-capable repository host;
- a human moving exact artifacts between ChatGPT and the CLI;
- a narrow Action/App/API host exposing begin, status, accept, and commit equivalents.

The player should never be asked to author JSON, choose task IDs, repair hashes, or understand topology. Those are operator concerns.

## Storage and migration

Revision 0156 does not alter database schema 8, event schema 1, or projection layout. `lacuna.turn-run.v1` is an exchange/sidecar schema, not a database migration.

The run directory is intentionally outside the ledger because it can contain:

- exact transcript text;
- privileged planner cards and returns;
- provider-specific operational custody;
- rejected or advisory artifacts;
- a human-readable pointer.

These are useful for replay and experiment custody but are not all semantic world state. Hosts should retain, protect, expire, or export run directories according to their own privacy policy.

## Failure and recovery semantics

The normal failures are structured and fail closed:

- invalid cube: no run;
- malformed or inconsistent run: no transition;
- wrong-stage schema: no artifact accepted;
- placeholder narration: no proposal accepted;
- verifier refusal: no commit path in that run;
- stale or invalid proposal at commit: kernel refusal, cube unchanged;
- changed cube identity: commit refusal;
- edited `NEXT.md`: audit refusal.

Known version-1 recovery boundaries:

1. **Same-run concurrency:** there is no lock or compare-and-swap around sidecar files. Exactly one parent must advance a run at a time.
2. **Begin crash window:** a source-bound request may exist without a finished run directory.
3. **Commit crash window:** the cube may commit before the receipt/manifest write completes. Inspect cube/request/proposal identity before retrying; blind retry is not promised idempotent.
4. **Absolute paths:** moving a run or cube invalidates recorded paths.
5. **Cleanup:** no automatic retention, redaction, or garbage collection policy exists.
6. **Local trust:** mode `0700` reduces accidental exposure but does not defend against a hostile host, backups, administrators, or provider logging.

## Deliberate limits

Revision 0156 does not claim to:

- invoke an LLM or dynamically provision provider agents;
- prove subagent confidentiality or independence;
- lock or distribute a run across concurrent coordinators;
- atomically transact SQLite state and sidecar files;
- authenticate artifacts from a remote provider;
- prove narration quality, truth, fairness, or absence of hidden rationale;
- generate, roll out, resample, prune, merge, or select candidate worlds;
- optimize checkpoint cards or forget rejected candidates automatically;
- run the comparative Gwern experiment.

Its architectural contribution is narrower and foundational: an exact, auditable entrance through which those higher-level policies can be tested without asking every model to rediscover the protocol.
