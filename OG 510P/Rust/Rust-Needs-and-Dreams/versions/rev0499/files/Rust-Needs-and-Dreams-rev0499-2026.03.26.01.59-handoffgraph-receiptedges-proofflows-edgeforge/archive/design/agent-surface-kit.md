# Design: Agent Surface Kit (`cargo agentcheck`, `agent-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust application’s supported agentic surface: prompts, tools, MCP resources/prompts/tools, provider capability assumptions, session/state posture, tool-execution expectations, and evidence that the declared agent behavior still matches reality.

This should **not** replace `rig`, `swiftide`, `neuron`, `rmcp`, provider SDKs, or hosted agent platforms.
It should make them compose better and make support claims reviewable.

## References (signals)
- The MCP specification now explicitly models resources, prompts, and tools as separate server features, and also covers lifecycle management, capability negotiation, authorization, and utilities like logging and completions.
  https://modelcontextprotocol.io/specification/2025-11-25
  https://modelcontextprotocol.io/specification/2025-11-25/basic
  https://modelcontextprotocol.io/specification/2025-11-25/server/resources
  https://modelcontextprotocol.io/specification/2025-11-25/server/prompts
  https://modelcontextprotocol.io/specification/2025-11-25/server/tools
- `rmcp` is now the official Rust SDK for MCP and explicitly covers tools, resources, prompts, sampling, roots, logging, completions, subscriptions, and more.
  https://docs.rs/rmcp
  https://docs.rs/rmcp/latest/rmcp/model/index.html
- `rig` already supports Rust-side tools, pipelines, and prompt/tool-call hooks.
  https://docs.rs/rig-core
  https://docs.rs/rig-core/latest/rig/agent/index.html
  https://docs.rs/rig-core/latest/rig/agent/trait.PromptHook.html
  https://docs.rs/rig-core/latest/rig/pipeline/index.html
- `swiftide` already spans prompt applications, retrieval/indexing pipelines, tools, and agents that can call other agents.
  https://docs.rs/swiftide/latest/swiftide/
  https://docs.rs/swiftide/latest/swiftide/attr.tool.html
  https://docs.rs/swiftide-docker-executor
- `neuron` already treats MCP, sessions, context compaction, guardrails, and tool middleware as first-class production concerns.
  https://docs.rs/crate/neuron/0.3.0
  https://docs.rs/neuron-mcp
- Provider APIs increasingly surface agent-specific operational concerns rather than simple text completion alone:
  - OpenAI Responses supports structured outputs, function calling, and tools.
    https://platform.openai.com/docs/api-reference/responses
  - OpenAI now also treats tool search, agent evals, and trace grading as explicit product surfaces.
    https://developers.openai.com/api/docs/guides/tools-tool-search/
    https://developers.openai.com/api/docs/guides/agent-evals/
    https://developers.openai.com/api/docs/guides/trace-grading/
  - Anthropic’s current docs distinguish client tools from server tools and emphasize tool-definition quality plus fine-grained tool streaming.
    https://docs.anthropic.com/en/docs/build-with-claude/tool-use
    https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use
    https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/fine-grained-tool-streaming
- Rust provider crates such as `async-openai` already expose structured-output and tool-choice/tool arrays directly in typed APIs, which is another sign that these assumptions are part of the real Rust support surface.
  https://docs.rs/async-openai/latest/async_openai/types/responses/struct.Response.html
  https://docs.rs/async-openai/latest/async_openai/types/chat/struct.CreateChatCompletionRequestArgs.html

## Core components

### 1) `agent-surface/v0`
A design-time declaration of the supported agent boundary for a binary/service/workspace.

Required ideas:
- system/application identity
- agent/workflow identities in scope
- supported operation classes:
  - chat assistant
  - tool-using agent
  - MCP client
  - MCP server
  - retrieval-augmented workflow
  - multi-step workflow / orchestrator
  - delegated / multi-agent handoff lane
- support classes:
  - official
  - best-effort
  - experimental
  - deprecated
  - internal
- linked attachments:
  - service surfaces
  - command surfaces
  - runtime settings refs
  - model surfaces
  - retrieval surfaces
  - identity/access surfaces
  - observability / diagnostic ids
  - raw provider/MCP/tool manifests

Design rule: preserve agent/workflow support truth separate from model/runtime support truth. “We use model X” is not the same thing as “we officially support workflow Y with tools Z and constraints Q.”

### 2) `prompt-catalog/v0`
Stable identities for prompts and prompt-like workflows the application officially exposes.

Each entry should support:
- stable prompt id
- kind:
  - system prompt
  - reusable task prompt
  - MCP prompt
  - evaluator/grader prompt
  - hidden orchestration prompt
  - user-visible template
- purpose summary
- parameter schema refs when relevant
- source artifact refs
- linked workflows / tools / resources
- support level
- redaction / disclosure notes
- change-review owner

Design rule: keep prompt identity separate from prompt text blobs. Preserve raw prompt artifacts as attachments; do not pretend every provider or framework prompt can be flattened into one canonical syntax.

### 3) `tool-catalog/v0`
Stable identities for tool surfaces the application officially supports.

Each entry should support:
- stable tool id
- tool lane:
  - local tool
  - local namespace
  - MCP tool
  - MCP server / namespace
  - provider-hosted tool
  - human-confirmed / operator tool
- raw name/provider key/MCP origin
- input schema refs
- output schema refs when known
- side-effect class:
  - read-only
  - external write
  - local mutation
  - code execution
  - networked action
- confirmation policy
- idempotency / replay notes when relevant
- timeout / budget notes
- support level
- owning team / review owner

Design rule: keep tool identity separate from execution environment. A schema alone does not tell reviewers whether a tool mutates prod state, executes shell code, or requires confirmation.

### 4) `resource-surface/v0`
The non-tool context surfaces the application relies on or exposes.

Each entry should support:
- stable resource id
- lane:
  - MCP resource
  - file/context attachment
  - retrieval-backed context source
  - internal state snapshot
  - generated working memory/context pack
- URI or locator pattern when relevant
- access posture
- freshness / staleness notes
- size/budget notes
- redaction/privacy notes
- linked workflows/prompts/tools

Design rule: keep resources separate from tools and separate from raw retrieval backends. “Model can read this context” is different from “model can execute this tool.”

### 5) `provider-capability-profile/v0`
The provider/runtime features the workflow depends on.

Each profile should capture:
- stable provider-capability-profile id
- provider/runtime identifiers and versions when known
- required capability families:
  - tool calling
  - structured outputs / JSON schema
  - streaming responses
  - tool streaming / partial arguments
  - MCP connectivity
  - deferred tool loading / tool search
  - reasoning trace / step visibility
  - eval/trace export support
  - multimodal inputs
  - background / long-running mode
- optional capabilities used opportunistically
- unsupported or unchecked lanes
- migration / fallback notes

Design rule: do not flatten provider behavior into one fake universal feature matrix. Preserve raw provider docs/SDK facts as attachments and model only the support claims your app depends on.

### 6) `agent-session-profile/v0`
Session, memory, and state assumptions for supported workflows.

Each profile should support:
- stable session-profile id
- linked workflow / prompt / tool ids
- conversation-state posture:
  - stateless
  - ephemeral per request
  - persisted thread/session
  - checkpointed workflow state
- memory/context posture:
  - no memory
  - bounded rolling context
  - summarized/compacted context
  - retrieval-backed memory
  - external store backed memory
- retention / expiration notes
- replay/recovery notes
- privacy/redaction notes
- user-visible versus hidden state notes

Design rule: keep session/state posture explicit. “Agent remembers things” is not a small implementation detail; it changes correctness, privacy, and evaluation assumptions.

### 7) `agent-check-plan/v0`
A plan for validating that the declared agent surface still behaves as claimed.

A plan should capture:
- selected workflows/prompts/tools/resources exercised
- fixed datasets or scenario ids
- provider/runtime lanes exercised
- required confirmations/guardrails
- expected tool sequence windows when relevant
- expected structured-output constraints
- expected failure / refusal / fallback cases
- expected trace assertions
- illustrative-only or unsupported cases

Design rule: distinguish black-box quality checks from trace-aware checks. Agent workflows increasingly need both.

### 8) `agent-check-report/v0`
Portable results from running the agent checks.

A report should capture:
- artifact versions and environment
- models/providers/runtimes exercised
- prompts/tools/resources/workflows exercised
- pass/fail/error outcomes
- optional trace attachments or references
- mismatches and reason codes, e.g.:
  - `prompt-missing`
  - `tool-schema-drift`
  - `resource-unavailable`
  - `provider-capability-mismatch`
  - `tool-confirmation-missing`
  - `structured-output-violation`
  - `session-policy-mismatch`
  - `trace-assertion-failed`
  - `handoff-contract-broken`
  - `context-budget-exceeded`
  - `unchecked-provider-lane`
- optional diff summaries vs baseline

### 9) `agent-pack/v0`
Bundle the agent contract and its evidence.

A pack should be able to include:
- `agent-surface/v0`
- `prompt-catalog/v0`
- `tool-catalog/v0`
- `resource-surface/v0`
- `provider-capability-profile/v0`
- `agent-session-profile/v0`
- `agent-check-plan/v0`
- `agent-check-report/v0`
- raw prompt files, MCP manifests, tool schemas, provider config snapshots, eval datasets, trace references, and linked packs from other kits

## CLI shape
A plausible first CLI could be:

- `cargo agentcheck init`
- `cargo agentcheck export-prompts`
- `cargo agentcheck export-tools`
- `cargo agentcheck export-mcp`
- `cargo agentcheck check`
- `cargo agentcheck diff`
- `cargo agentcheck pack`

This is intentionally adapter-oriented, not framework-monolithic.

## Adapters worth supporting first
- `rmcp` adapters for MCP tools/resources/prompts and capability discovery
- `rig` adapters for prompt/tool registrations, tool-call hooks, and workflow wiring
- `swiftide` adapters for tools, agents, and isolated tool executors
- `neuron` adapters for sessions, compaction, MCP bridges, and guardrails
- provider adapters for OpenAI/Anthropic-style tool calling and structured-output expectations
- a manual/static adapter so teams can describe workflows even when their framework support is partial

## Non-goals
- replacing agent frameworks
- replacing provider SDKs
- pretending every provider has the same tool or trace semantics
- forcing one prompt language or one memory architecture
- standardizing raw reasoning content as a universal artifact

## Why this is strategically useful
This kit would give Rust a portable review layer for one of the ecosystem’s fastest-moving seams.

That matters because the likely failure modes are not just “the model answered badly.”
They increasingly include:
- prompt drift,
- hidden tool-surface growth,
- MCP capability mismatches,
- unsafe tool execution assumptions,
- provider swaps that silently remove needed structured-output/tool behavior,
- and agent upgrades that look fine in demos but regress real traces.

Rust already has many of the building blocks.
What it still lacks is the durable, attachable, cross-tool artifact layer above them.
