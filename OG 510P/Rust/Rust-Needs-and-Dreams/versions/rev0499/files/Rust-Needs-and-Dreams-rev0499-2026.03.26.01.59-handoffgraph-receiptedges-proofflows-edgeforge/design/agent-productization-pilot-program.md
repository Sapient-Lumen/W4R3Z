# Design: Agent Productization Pilot Program

## Goal
Run a **ranked, bounded pilot program** for the Agent Productization Stack so the archive can test whether Rust is ready for a portable agent-workflow contract layer above frameworks, MCP wiring, provider SDKs, eval tools, and docs.

This is **not** a call to build a giant agent platform.
It is a plan to prove a few linked artifacts can keep workflow truth, lower-layer attachments, activation posture, runtime evidence, and support claims distinct while still making them composable.

Related stack:
- [`design/agent-productization-stack.md`](./agent-productization-stack.md)
- proposal-layer candidate: [`proposals/epic-agent-productization-stack.md`](../proposals/epic-agent-productization-stack.md)

Existing design anchors:
- [`design/agent-surface-kit.md`](./agent-surface-kit.md)
- [`design/model-surface-kit.md`](./model-surface-kit.md)
- [`design/retrieval-surface-kit.md`](./retrieval-surface-kit.md)
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md)
- [`design/identity-surface-kit.md`](./identity-surface-kit.md)
- [`design/observability-kit.md`](./observability-kit.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/canonical-learning-stack.md`](./canonical-learning-stack.md)

## Why this now deserves a ranked pilot
The ecosystem now has enough raw ingredients that the archive should stop treating agent workflows as only toy wrappers or only research demos:
- the 2025 Rust survey says official docs remain canonical while some learning traffic appears to be shifting toward LLM tooling and agentic/editor workflows;
- MCP now has a richer and more official surface, and Rust has an official SDK for it in `rmcp`;
- Rust agent frameworks are multiplying, but they are not converging on one stable productization boundary;
- providers are exposing agent-specific operational features — structured outputs, tool surfaces, evals, traces, streaming, multi-environment tool execution — which means support truth now spans more than one crate;
- upstream provider surfaces are still moving in ways that directly affect supportable Rust products: OpenAI is deprecating the Assistants API in favor of the Responses direction, and Anthropic’s current MCP connector supports only tool calls over public HTTP rather than full local-MCP parity.

That combination is exactly where a pilot should start: **after the ingredients are real, before framework-local glue hardens into folklore**.

## Ranked pilot order

### 1) Workflow truth pilot
**Question:** Can a real Rust product export a reviewable workflow boundary without flattening frameworks or prompts into one blob?

Required deliverables:
- `agent-surface/v0`
- `prompt-catalog/v0`
- `tool-catalog/v0`
- `resource-surface/v0`
- one linked `agent-check-report/v0`

Success criteria:
- at least one workflow with stable ids for prompts, tools, and resources;
- at least one local-tool lane and one MCP lane or equivalent external-tool lane;
- side-effect class and confirmation posture are explicit;
- public vs internal vs experimental workflows are separated.

Why first:
- it proves the product boundary exists at all.

### 2) Model / retrieval attachment pilot
**Question:** Can agent products import lower-layer capabilities honestly instead of hiding them in prose?

Required deliverables:
- explicit model/runtime capability attachments,
- explicit retrieval/no-retrieval posture,
- structured-output/tool-calling assumptions,
- clear reason codes for unsupported or unchecked provider/model lanes.

Success criteria:
- at least one workflow imports Model Surface truth;
- at least one workflow imports Retrieval Surface truth or explicitly declares none;
- fallback and unsupported lanes are visible;
- no workflow silently redefines tokenizer/model/retrieval semantics as prompt semantics.

Why second:
- many agent regressions are actually lower-layer assumption mismatches.

### 3) Runtime / identity / permission pilot
**Question:** Can provider activation, secret posture, user-context requirements, and tool permissions become durable artifacts?

Required deliverables:
- runtime-settings imports for providers/endpoints/transports,
- identity or protected-surface attachments when relevant,
- confirmation and least-privilege policy for side-effecting tools,
- secret / environment activation notes,
- explicit notes when a workflow depends on local-only MCP or execution assumptions.

Success criteria:
- at least one workflow distinguishes documented from actually activated providers or MCP servers;
- at least one side-effecting tool carries confirmation posture;
- at least one tenant/user/operator distinction is explicit when relevant;
- local-only assumptions are not silently treated as product-wide support.

Why third:
- this is where real deployments stop looking like playground demos.

### 4) Eval / trace / telemetry pilot
**Question:** Can the ecosystem produce portable runtime evidence instead of anecdotes?

Required deliverables:
- scenario ids or datasets,
- trace or step-observation attachments,
- mismatch reason codes,
- latency/cost/budget posture when available,
- black-box and trace-aware checks kept distinct.

Success criteria:
- at least one regression can be attributed to prompt, model, tool, resource, or session policy with explicit artifacts;
- a provider swap or tool/schema drift produces a reviewable mismatch report;
- traces remain linked evidence rather than silently becoming the whole source of truth.

Why fourth:
- this is the proof that productization matters after launch.

### 5) Support / docs / transition / consumer pilot
**Question:** Can agent products be supported, migrated, and consumed by other archive seams without losing truth boundaries?

Required deliverables:
- support levels by workflow/provider/transport,
- checked docs/examples,
- migration note or diff for a changed workflow,
- at least one deprecation or capability-lossiness note when upstream/provider/MCP behavior shifted,
- one downstream consumer import (support, release, policy, atlas, or docs/assistant overlay).

Success criteria:
- docs do not overclaim beyond checked workflows;
- migrations say what changed and what evidence backs the change;
- downstream consumers import selected facts instead of redefining the workflow boundary.

Why fifth:
- it proves the stack is useful for long-lived products, not just for local experimentation.

## Suggested pilot subjects
The archive should deliberately choose materially different agent products instead of five variants of the same chatbot:
1. **MCP-heavy assistant** — proves protocol-level tool/resource/prompt surfaces are not enough on their own.
2. **Retrieval-heavy internal copilot** — proves lower-layer context/index assumptions matter.
3. **Side-effecting operator tool** — proves confirmation, identity, and least-privilege posture must be explicit.
4. **Provider-sensitive workflow** — proves structured-output / trace / eval assumptions belong in durable artifacts.
5. **Migration subject** — proves provider swaps, Responses/Assistants transitions, MCP upgrades, or prompt/tool/schema changes are reviewable.

## What should count as success
A successful pilot program would show:
- teams can review agent changes without diffing raw prompts, framework internals, provider dashboards, and MCP code separately;
- model/retrieval assumptions stay imported rather than hidden;
- side-effect posture and permission/confirmation policies become explicit;
- workflow regressions can be explained with portable artifacts;
- support and docs stop getting ahead of checked reality;
- provider/API and connector churn can be recorded as migration evidence instead of living only in maintainer memory.

## What should count as failure
The archive should treat the pilot as failed or split if:
- every useful artifact collapses back into a framework-specific runtime dump;
- model/retrieval/runtime/support truths cannot be kept separate from workflow truth;
- traces or evals become so vendor-specific that no portable evidence layer remains;
- the result looks like another universal agent runtime or hosted control plane;
- maintainers cannot explain what is official, best-effort, experimental, or merely illustrative.

## Archive implications
If this pilot lands well, the archive should:
- promote Agent Surface work from an isolated Tier 1/2 kit into an explicit cross-stack productization seam;
- prefer attachable workflow/evidence/support artifacts over agent-framework bake-offs;
- keep model, retrieval, runtime, identity, observability, and support layers separate but composable.

If it lands poorly, the archive should:
- keep Agent Surface Kit as a useful narrow kit,
- demote the broader productization synthesis,
- and preserve the lesson that the ecosystem is still too fluid for a coupled stack.

## References (signals)
- 2025 State of Rust survey results:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- MCP specification / Rust SDK:
  https://modelcontextprotocol.io/specification/2025-11-25
  https://github.com/modelcontextprotocol/rust-sdk
  https://modelcontextprotocol.io/docs/develop/build-server
- `rig`:
  https://docs.rs/rig-core
  https://docs.rs/rig-core/latest/rig/evals/index.html
- `swiftide`:
  https://swiftide.rs/
  https://swiftide.rs/agents/overview/
  https://swiftide.rs/agents/lifecycle-hooks/
- OpenAI agents / structured outputs / trace grading / Responses migration:
  https://developers.openai.com/api/docs/guides/agents/
  https://developers.openai.com/api/docs/guides/structured-outputs/
  https://developers.openai.com/api/docs/guides/trace-grading/
  https://developers.openai.com/api/docs/guides/migrate-to-responses/
- Anthropic tool use / streaming / code execution / MCP connector:
  https://docs.anthropic.com/en/docs/build-with-claude/tool-use
  https://docs.anthropic.com/en/docs/build-with-claude/streaming
  https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/code-execution-tool
  https://docs.anthropic.com/en/docs/agents-and-tools/mcp-connector
