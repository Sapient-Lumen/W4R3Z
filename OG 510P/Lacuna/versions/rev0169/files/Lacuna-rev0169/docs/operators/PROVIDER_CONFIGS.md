# Provider configuration and dispatch

Provider files are discovery adapters. Generated task cards are the per-invocation prompts. The four dispatch surfaces are intentionally distinct:

| Surface | Envelope | Route binding |
|---|---|---|
| ordinary managed turn | `lacuna.agent-dispatch.v1` | chosen when `turn run dispatch` is rendered |
| managed retcon checkpoint | `lacuna.checkpoint-run-agent-dispatch.v1` | fixed per role in `run.json` at `checkpoint run begin` |
| fresh post-checkpoint continuation | `lacuna.checkpoint-continuation-dispatch.v2` | chosen when `checkpoint run next-turn` or `continuation` is rendered |
| lower-level stateless checkpoint | `lacuna.checkpoint-agent-dispatch.v1` | supplied to each manual `checkpoint dispatch` call |

New operators should use managed runs. The stateless checkpoint envelope remains for custom hosts that own their own manifest, invocation custody, and resume semantics.

## Ordinary-turn routing

```bash
./lacuna turn run dispatch RUN_PATH --provider PROVIDER --format markdown
```

Supported route labels and ordinary-role aliases:

| Route | Planner alias | Narrator alias | Builder alias | Verifier alias |
|---|---|---|---|---|
| `portable` | `lacuna-planner` | `lacuna-narrator` | `lacuna-proposal-builder` | `lacuna-verifier` |
| `codex` | `lacuna_planner` | `lacuna_narrator` | `lacuna_proposal_builder` | `lacuna_verifier` |
| `claude-code` | `lacuna-planner` | `lacuna-narrator` | `lacuna-proposal-builder` | `lacuna-verifier` |
| `gemini-cli` | `lacuna-planner` | `lacuna-narrator` | `lacuna-proposal-builder` | `lacuna-verifier` |
| `chatgpt` | role-dedicated planner context | audience-only narrator context | builder-only context | verifier-only context |

The dispatch embeds the exact complete task card. A chat worker does not need local path access.

## Managed-checkpoint routing

Freeze one default provider or heterogeneous routes when the run is created:

```bash
./lacuna checkpoint run begin CUBE \
  --root .lacuna-checkpoint-runs \
  --trigger "Compare bounded explanations." \
  --provider portable \
  --generator-provider chatgpt \
  --judge-provider codex \
  --compressor-provider claude-code \
  --verifier-provider gemini-cli \
  --format markdown
```

The role aliases are:

| Route | Generator | Judge | Compressor | Checkpoint verifier |
|---|---|---|---|---|
| `portable` | `lacuna-retcon-generator` | `lacuna-retcon-judge` | `lacuna-retcon-compressor` | `lacuna-retcon-verifier` |
| `codex` | `lacuna_retcon_generator` | `lacuna_retcon_judge` | `lacuna_retcon_compressor` | `lacuna_retcon_verifier` |
| `claude-code` | hyphenated canonical name | hyphenated canonical name | hyphenated canonical name | hyphenated canonical name |
| `gemini-cli` | hyphenated canonical name | hyphenated canonical name | hyphenated canonical name | hyphenated canonical name |
| `chatgpt` | role-dedicated generator context | provenance-blind judge context | compressor-only context | verifier-only context |

Render the current role using the frozen route:

```bash
./lacuna checkpoint run dispatch RUN_PATH --format markdown
```

Do not override the route later by editing `run.json` or changing the alias in prose. Audit recomputes the exact dispatch from the fixed route and exact role card. Every accepted or failed attempt records that card digest, dispatch digest, route, alias, model declaration, and outcome in one ordered invocation receipt.

Provider mixing can add procedural diversity and reduce direct self-preference. It does not prove independence, semantic anonymity, calibration, or quality. A single provider may execute every role serially while preserving the same typed boundaries.


## Fresh-continuation routing

After a committed checkpoint, render the exact next-turn handoff:

```bash
./lacuna checkpoint run next-turn RUN_PATH \
  --player-input-file next-player-input.txt \
  --provider PROVIDER \
  --format markdown
```

All providers use the dedicated canonical role `lacuna-fresh-narrator`:

| Route | Fresh narrator alias |
|---|---|
| `portable` | `lacuna-fresh-narrator` |
| `codex` | `lacuna_fresh_narrator` |
| `claude-code` | `lacuna-fresh-narrator` |
| `gemini-cli` | `lacuna-fresh-narrator` |
| `chatgpt` | fresh post-checkpoint narrator context |

The dispatch embeds the authenticated compact state, exact ordinary turn packet, exact next player input, optional public history, proposal template, save path, and parent accept command. The provider is chosen at rendering time because the continuation is a new worker invocation rather than one of the four checkpoint routes frozen at checkpoint begin. The alias still grants no accept or commit authority.

## Common parent/worker contract

Every managed host follows the same custody path:

1. The parent starts or resumes one run.
2. `run.json` and `NEXT.md` identify the sole next owner.
3. The parent renders a self-contained dispatch for that stage.
4. One worker receives the embedded complete card and returns one JSON object.
5. The parent saves and accepts the exact return, or records the failed attempt without advancing.
6. Only the parent reviews, commits or recovers, and presents accepted narration.

Aliases route work; they do not grant authority or attest provider identity.

## Codex

The repository includes `.codex/config.toml` and `.codex/agents/` role definitions with read-only or empty-tool policies. Codex supports specialized subagent workflows; the parent should invoke only the alias named by the current dispatch and provide the embedded card unchanged.

The worker returns data only. The parent process invokes `turn run accept` or `checkpoint run accept`, records failures when needed, and alone commits. In the clean checkpoint-continuation treatment, the parent runs `checkpoint run next-turn` and routes its complete dispatch to the configured `lacuna_fresh_narrator` child.

## Claude Code

The repository includes `.claude/agents/` definitions. Route each dispatch to the matching hyphenated role. Do not give the narrator or checkpoint compressor the planner card, rejected candidates, or full run directory merely because the workspace is readable.

## Gemini CLI

The repository includes `.gemini/agents/` definitions with the same portable role names. Treat the generated dispatch as controlling over generic repository instructions for that worker stage.

## ChatGPT

A ChatGPT conversation may have no local filesystem access. The generated dispatch embeds the exact card and explicitly tells the worker not to request the retained local path.

A fresh conversation, workspace agent, connected action/app, or agent-mode task can be used as transport when actually available. Capability and permission vary by product and workspace. A Project's shared memory is useful operationally but is not the clean isolation boundary; Temporary Chat can still apply enabled Custom Instructions. Context separation is not provider-signed confidentiality or independent-model attestation. See [`CHATGPT.md`](CHATGPT.md) and [`FRESH_NARRATOR.md`](FRESH_NARRATOR.md).

## Provider without native workers

Choose one of:

- an ordinary `solo` turn with one parent proposal;
- serial role execution in separate chats or API calls;
- serial execution inside one parent while preserving each exact card boundary; or
- a human paste bridge using the complete generated dispatch.

Do not claim hard subagent isolation when none exists. The card, dispatch, artifact, and digest protocol still makes the intended information flow reproducible.

## Dispatch and invocation nonclaims

A dispatch does not:

- call or authenticate a provider;
- prove model identity, version, tool denial, timing, or memory isolation;
- prove that the worker followed instructions;
- authorize acceptance or mutation; or
- turn a verifier into kernel authority.

A managed checkpoint invocation receipt is likewise a host declaration, not a vendor attestation. It proves only that the retained sidecar binds a declared invocation record to one exact card, dispatch, and accepted output or failure classification under Lacuna’s canonicalization rules.

## Configuration-source drift

These checked-in adapters follow public provider documentation inspected for this revision:

- Codex subagents: <https://developers.openai.com/codex/subagents>
- Claude Code subagents: <https://code.claude.com/docs/en/sub-agents>
- Gemini CLI subagents: <https://geminicli.com/docs/core/subagents/>
- ChatGPT Projects: <https://help.openai.com/en/articles/10169521-projects-in-chatgpt>
- ChatGPT agent: <https://help.openai.com/en/articles/11752874-chatgpt-agent>
- ChatGPT workspace agents: <https://help.openai.com/en/articles/20001143-chatgpt-workspace-agents-for-enterprise-and-business>
- ChatGPT Temporary Chat: <https://help.openai.com/en/articles/8914046-temporary-chat-faq>
- OpenAI API conversation state: <https://developers.openai.com/api/docs/guides/conversation-state>

Provider syntax and capabilities may change. Treat these files as reviewed adapters, not permanent claims. Re-check primary documentation before changing syntax, and keep the portable dispatch contract usable when native discovery drifts.

## Scenario-cell configuration

For a comparative run, the capsule's `model_policy` is fixed across all four cells. Use a fresh provider conversation/session per cell and record a unique declared `context_id`; the runner refuses declared cross-cell reuse. The condition controls checkpoint topology, not provider preference.

- `forward-only`: narration uses one persistent declared context for the complete cell.
- `prompt-only-retcon`: monolithic checkpoint and narration use one persistent declared context for the complete cell.
- `lacuna-serial`: generator/judge/compressor/verifier and narration use one persistent declared context for the complete cell.
- `lacuna-role-separated`: checkpoint roles use fresh pairwise-distinct declared contexts; the first narrator after commit uses a new context and records the exact checkpoint ID plus narrator-capsule digest.

Codex parents should explicitly spawn the named subagent because native orchestration is not inferred from the existence of a card. Claude Code and Gemini-oriented definitions should likewise receive only the exact generated card. ChatGPT without a native agent surface can use fresh conversations as a human bridge. For the role-separated treatment, use a separate fresh narrator conversation after every checkpoint and avoid shared Project memory where practical. Any fallback must be declared honestly rather than relabeled as independent role separation.

## Comparative canary routing

Provider aliases do not change the canary boundary. The private scenario driver belongs to the parent/cell coordinator. Each nested provider role receives only the exact generated card or continuation dispatch. A filesystem-readable native worker is a distinct treatment risk, so the filesystem-only canary exists outside the driver and the final scenario scan reports any exact-token appearance without attributing the cause to the provider.
