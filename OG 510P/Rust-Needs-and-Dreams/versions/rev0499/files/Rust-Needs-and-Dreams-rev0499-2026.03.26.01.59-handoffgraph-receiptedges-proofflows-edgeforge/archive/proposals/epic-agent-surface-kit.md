# Epic proposal: Agent Surface Kit

## Thesis
Rust’s agentic-application ecosystem is now strong enough that the missing contribution is no longer “yet another OpenAI wrapper,” “yet another MCP helper,” or “yet another single-framework agent runtime.”
The higher-leverage missing piece is a **portable agent-surface contract** that lets teams declare, diff, validate, and ship what an LLM-powered Rust application actually promises: prompt identities, tool catalogs, MCP resources/prompts/tools, provider-capability assumptions, session/memory posture, and checked workflow evidence.

In other words: Rust needs a boring, attachable `agent-pack/v0` more than it needs one more fashionable agent crate.

## Why now
The ecosystem signals line up:
- MCP has matured into a richer protocol surface with resources, prompts, tools, lifecycle/capability negotiation, authorization, and utilities.
- `rmcp` is now an official Rust SDK for that surface.
- Rust agent frameworks (`rig`, `swiftide`, `neuron`, and others) already cover tools, sessions, pipelines, MCP bridges, and guardrails.
- Provider APIs increasingly treat tool calling, structured outputs, tool search, traces, and evals as first-class operational concerns.
- Tool-execution safety and workflow review are becoming more important as agents touch shells, files, browsers, databases, and live services.

The hard part is increasingly not “can Rust call a model?” but “what exactly does this Rust application support as an agent, and what evidence do we have that the support claim still holds?”

Sources:
- https://modelcontextprotocol.io/specification/2025-11-25
- https://modelcontextprotocol.io/specification/2025-11-25/basic
- https://modelcontextprotocol.io/specification/2025-11-25/server/resources
- https://modelcontextprotocol.io/specification/2025-11-25/server/prompts
- https://modelcontextprotocol.io/specification/2025-11-25/server/tools
- https://docs.rs/rmcp
- https://docs.rs/rig-core
- https://docs.rs/swiftide/latest/swiftide/
- https://docs.rs/crate/neuron/0.3.0
- https://platform.openai.com/docs/api-reference/responses
- https://developers.openai.com/api/docs/guides/tools-tool-search/
- https://developers.openai.com/api/docs/guides/agent-evals/
- https://developers.openai.com/api/docs/guides/trace-grading/
- https://docs.anthropic.com/en/docs/build-with-claude/tool-use

## What should be built
A first credible version should ship:
1. `agent-surface/v0`, `prompt-catalog/v0`, `tool-catalog/v0`, `resource-surface/v0`, `provider-capability-profile/v0`, `agent-session-profile/v0`, `agent-check-plan/v0`, `agent-check-report/v0`, and `agent-pack/v0`
2. adapters for `rmcp`, at least one Rust agent framework, and at least one provider-facing Rust SDK lane
3. docs/reference generation for prompts, tools, resources, provider assumptions, and session/guardrail posture
4. validation/reporting support for prompt drift, tool-schema changes, missing confirmations, provider-capability mismatches, and trace-level workflow regressions
5. examples showing packs attached to production assistants, internal operator copilots, coding agents, MCP-powered tools, and hybrid retrieval/tool workflows

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one `rmcp`-only pilot proving MCP servers/clients need durable review artifacts above protocol conformance alone
- one `rig` or `swiftide` pilot proving local-tool and prompt surfaces are worth exporting/diffing
- one provider-heavy pilot proving structured-output/tool-search assumptions belong in explicit capability profiles
- one security-sensitive pilot proving confirmation policy, side-effect class, and trace assertions need to live above raw tool schemas
- one migration pilot where a provider swap or MCP upgrade changes capabilities and the pack catches the drift

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve prompts, tools, resources, provider capabilities, and session posture as separate artifacts
2. **v0.2 adapters**
   - support MCP extraction, one agent-framework adapter, one provider adapter, and one manual/static lane
3. **v0.3 cross-kit integration**
   - integrate with Model Surface, Retrieval Surface, Service Surface, Identity Surface, Runtime Settings, Diagnostic Surface, and Observability workflows
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one exact framework or provider stack

## Success metrics
- Teams can review agent changes as explicit artifacts instead of prompt files, code diffs, provider dashboards, and tribal memory.
- Prompt and tool drift become easier to detect before production regressions.
- Provider swaps and MCP upgrades become easier because support truth lives above one SDK.
- Confirmation/guardrail assumptions become reviewable instead of being buried in runtime glue code.
- Rust agent systems become easier to hand off because prompts, tools, sessions, and trace expectations stop living only in people’s heads.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Model Surface Kit covers model/tokenizer/artifact/runtime truth,
- Retrieval Surface Kit covers corpora/query/ranking semantics,
- Service Surface Kit covers HTTP/service behavior,
- Command Surface Kit covers CLI surfaces,
- Plugin Surface Kit covers host/extension boundaries,
- Runtime Settings Kit covers declared settings and precedence,
- and Observability/Diagnostic kits cover telemetry and failure interfaces.

But none of those is the portable contract for the **agentic workflow boundary itself**.
Agent Surface Kit is the missing substrate that keeps prompts, tools, MCP resources, provider assumptions, session posture, and checked traces attached to one reviewable interface without absorbing the rest of the stack into one mega-format.
