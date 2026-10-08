# Gap: agentic application surfaces, prompts, tools/resources, and migration-aware support contracts

## What is missing
Rust now has credible building blocks for LLM-powered and agent-enabled applications:
- Rust crates that expose tool-calling and provider abstractions,
- Rust agent frameworks with tool hooks, pipelines, sessions, and guardrails,
- an official Rust SDK for the Model Context Protocol (MCP),
- provider SDKs for structured outputs and function/tool calling,
- and rapidly growing product-level expectations around traces, evals, permissions, and safety reviews.

What it still lacks is a **boring, reviewable contract** for the agent surface itself.

Today teams can separately:
- define prompts and system instructions,
- register local tools,
- expose or consume MCP tools/resources/prompts,
- wire providers with different tool/JSON/streaming capabilities,
- build sessions, memory, or handoff flows,
- and run ad hoc agent tests or traces.

What is still missing is the shared layer that answers:
- which prompts, tools, MCP resources, and workflows a Rust application officially supports,
- which parts are local tools versus remote/MCP/provider-hosted tools,
- which provider capabilities and retrieval/runtime assumptions the application depends on,
- what session/state/memory/confirmation/permission expectations exist around execution,
- what evidence shows the declared agent surface still matches actual behavior,
- and what changed when providers, MCP connectors, prompts, schemas, or runtime assumptions drift.

## Why it matters
Agent-enabled applications are increasingly a **composed interface**, not a single model call.

The real contract often spans:
- prompt families,
- tool schemas,
- MCP server discovery,
- provider-specific structured-output/tool-call behavior,
- context/resource injection,
- session state,
- multi-step traces,
- eval/guardrail logic,
- and migration/deprecation pressure from upstream providers.

Without a shared artifact layer, those truths get scattered across:
- provider setup code,
- handwritten tool registries,
- prompt templates in random directories,
- MCP manifests/configs,
- product dashboards,
- eval notebooks,
- and tribal memory about which tools are safe, stable, local-only, or merely demo-grade.

That is the same pattern this archive keeps finding elsewhere: strong point tools, weak portable artifacts.

## Existing building blocks worth composing
- The MCP spec now clearly treats **resources, prompts, and tools** as separate server features, and the official Rust SDK (`rmcp`) is the Rust lane for that surface.
  https://modelcontextprotocol.io/specification/2025-11-25
  https://github.com/modelcontextprotocol/rust-sdk
  https://modelcontextprotocol.io/docs/develop/build-server
- `rig` already provides a Rust framework for LLM-powered apps with tools, provider integrations, agents, and eval support.
  https://docs.rs/rig-core
  https://docs.rs/rig-core/latest/rig/evals/index.html
- `swiftide` already spans prompt completion, indexing/query pipelines, and agents that can use tools and call other agents, with explicit lifecycle-hook points.
  https://swiftide.rs/
  https://swiftide.rs/agents/overview/
  https://swiftide.rs/agents/lifecycle-hooks/
- Provider/runtime APIs are also growing more opinionated about agent behavior. OpenAI’s current APIs expose agents, structured outputs, and trace grading, and its migration docs now say the Assistants API is deprecated with a shutdown date of August 26, 2026.
  https://developers.openai.com/api/docs/guides/agents/
  https://developers.openai.com/api/docs/guides/structured-outputs/
  https://developers.openai.com/api/docs/guides/trace-grading/
  https://developers.openai.com/api/docs/guides/migrate-to-responses/
- Anthropic’s docs distinguish client tools from server tools, document fine-grained tool streaming, explain that multi-computer tool environments can confuse the model, and say the current MCP connector supports only tool calls over public HTTP.
  https://docs.anthropic.com/en/docs/build-with-claude/tool-use
  https://docs.anthropic.com/en/docs/build-with-claude/streaming
  https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/code-execution-tool
  https://docs.anthropic.com/en/docs/agents-and-tools/mcp-connector
- The 2025 State of Rust survey says online docs remain the canonical reference, says some learning traffic appears to be shifting toward LLM tooling, and says editors with agentic support are on the rise. That means Rust increasingly needs machine-usable workflow truth rather than only more wrappers around model APIs.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Why existing tools are not yet the whole answer
The ecosystem has **agent frameworks, model SDKs, tool protocols, and provider APIs**, but not the **shared contract / capability / evidence / migration layer**.

`rmcp` helps standardize one protocol lane.
`rig`, `swiftide`, and related crates help build Rust-side orchestration.
OpenAI/Anthropic/provider APIs keep evolving their own tool and eval capabilities.

But teams still have to invent their own answers for:
- stable workflow identities,
- stable prompt identities,
- stable tool and namespace identities across local and MCP lanes,
- distinctions between checked tools and illustrative/demo-only tools,
- explicit provider-capability and retrieval assumptions,
- explicit session/memory/compaction posture,
- explicit local-only versus hosted/remote connector limitations,
- and diffable review artifacts when prompts drift, tool schemas change, MCP servers gain or lose capabilities, or a provider/API migration silently breaks a workflow.

That is exactly the kind of missing substrate this archive is trying to identify.

## Target outcome
A project should be able to say:
- “these are the prompts, tools, MCP resources, and workflows we officially support,”
- “these are the provider/runtime/tool-execution assumptions they rely on,”
- “these are the session/state/confirmation/permission expectations,”
- “these are the traces/evals/checks that back the claim,”
- “this is what changed after a provider, prompt, or connector migration,”
- and “this is the portable bundle CI, release review, operators, support, and later archaeology can consume.”

That is bigger than one agent framework and smaller than a hosted agent platform.
