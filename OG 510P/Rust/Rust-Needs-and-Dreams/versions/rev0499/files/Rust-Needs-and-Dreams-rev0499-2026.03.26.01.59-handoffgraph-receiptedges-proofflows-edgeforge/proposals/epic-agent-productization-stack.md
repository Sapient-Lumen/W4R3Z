# Epic Proposal: Agent Productization Stack (`cargo agent-product`, `agent-product-pack/v0`)

## One-sentence pitch
Build a thin Rust companion layer for **agent-enabled products** that links **workflow/prompt/tool/resource truth**, **model/retrieval attachments**, **runtime/identity activation**, **eval/trace evidence**, **support/docs truth**, and **migration evidence** into one portable review boundary without pretending one framework, provider, or MCP lane has already won.

## Deliverables
- reference command:
  - `cargo agent-product`
- schemas:
  - `agent-product-brief/v0`
  - `agent-product-subject/v0`
  - `agent-product-pack/v0`
  - `agent-product-diff/v0`
  - `agent-product-handoff/v0`
- adapters/importers for:
  - `agent-surface/v0`
  - `prompt-catalog/v0`
  - `tool-catalog/v0`
  - `resource-surface/v0`
  - `provider-capability-profile/v0`
  - `agent-session-profile/v0`
  - model / retrieval / runtime-settings / identity / observability attachments
  - eval / trace / scenario / mismatch-report attachments
  - support-envelope / docproof / canonical-learning attachments
- docs:
  - workflow-support-policy guide
  - provider / MCP capability-lossiness guide
  - traces-versus-black-box-evals guide
  - migration / deprecation / consumer-lossiness guide

## Why now (signals)
- The 2025 State of Rust survey says online documentation remains the canonical reference, says some learning traffic appears to be shifting toward LLM tooling, and says editors with agentic support are on the rise.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- MCP has become a real product surface: the specification distinguishes tools, prompts, and resources, and the official Rust SDK (`rmcp`) is now the Rust lane for building MCP clients and servers.
  https://modelcontextprotocol.io/specification/2025-11-25
  https://github.com/modelcontextprotocol/rust-sdk
  https://modelcontextprotocol.io/docs/develop/build-server
- The Rust-side framework landscape is already heterogeneous in a durable way rather than a toy way. `rig` focuses on ergonomic modular LLM applications and already exposes agents, tools, provider integrations, and eval support. `swiftide` spans indexing/query pipelines plus agents, tools, hooks, and agent-to-agent patterns.
  https://docs.rs/rig-core
  https://docs.rs/rig-core/latest/rig/evals/index.html
  https://swiftide.rs/
  https://swiftide.rs/agents/overview/
  https://swiftide.rs/agents/lifecycle-hooks/
- Provider/runtime surfaces are now operationally explicit and visibly unstable. OpenAI’s current agent documentation treats structured outputs, traces, and trace grading as first-class features, while the Responses migration docs say the Assistants API is deprecated with a shutdown date of August 26, 2026. Anthropic distinguishes client tools from server tools, documents fine-grained tool streaming, documents multi-environment tool-execution pitfalls, and its MCP connector currently supports only tool calls over public HTTP rather than full local-MCP parity.
  https://developers.openai.com/api/docs/guides/agents/
  https://developers.openai.com/api/docs/guides/structured-outputs/
  https://developers.openai.com/api/docs/guides/trace-grading/
  https://developers.openai.com/api/docs/guides/migrate-to-responses/
  https://docs.anthropic.com/en/docs/build-with-claude/tool-use
  https://docs.anthropic.com/en/docs/build-with-claude/streaming
  https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/code-execution-tool
  https://docs.anthropic.com/en/docs/agents-and-tools/mcp-connector

## The missing seam
Rust now has the ingredients for agentic applications, but not the **portable product boundary** that answers:

- what workflows are officially supported;
- which prompts, tools, and resources belong to each workflow;
- what model, retrieval, and structured-output assumptions they import;
- what providers, MCP transports, secrets, permissions, confirmations, and user/operator contexts must be activated;
- what traces, evals, or scenario reports prove the claims;
- what changed after a provider swap, MCP upgrade, prompt change, tool-schema change, or deprecation;
- and what release/support/policy/atlas/assistant consumers may safely conclude.

Without that layer, teams keep reconstructing support truth from prompt files, framework registration code, provider dashboards, MCP manifests, and issue-thread archaeology.

## Reference CLI shape
- `cargo agent-product record`
  - emit `agent-product-subject/v0` for one concrete product/workflow review subject
- `cargo agent-product attach-surface`
  - import workflow / prompt / tool / resource declarations
- `cargo agent-product attach-runtime`
  - import provider / retrieval / runtime-settings / identity / permission posture
- `cargo agent-product attach-evidence`
  - import traces, evals, mismatch reports, and scenario results
- `cargo agent-product diff --against <prior-pack|ref|path>`
  - emit `agent-product-diff/v0`
- `cargo agent-product render --for <release|support|policy|atlas|assistant>`
  - emit `agent-product-handoff/v0`
- `cargo agent-product pack`
  - produce `agent-product-pack/v0`
- `cargo agent-product verify-pack <path>`
  - verify schema versions, checksums, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace `rig`, `swiftide`, `rmcp`, provider SDKs, observability systems, or hosted agent platforms.

## What `agent-product-pack/v0` should contain
- `manifest.json`
- `agent-product-brief.json`
- one or more `agent-product-subject.json`
- imported workflow / prompt / tool / resource attachments
- imported model / retrieval / runtime / identity attachments
- imported trace / eval / mismatch / scenario evidence
- optional docs/support / migration / release handoffs
- optional `agent-product-diff.json`
- one or more `agent-product-handoff.json` summaries
- checksums, provenance, freshness, and generator identity

## Design principles
- **Workflow truth first.**
- **Prompt identity is not prompt text.**
- **Tool identity is not execution environment.**
- **Agent support truth is not model truth.**
- **Runtime activation is not support truth.**
- **Traces do not replace black-box checks, and black-box checks do not replace traces.**
- **Provider and MCP partial support stay explicit.**
- **Migration evidence matters because upstream surfaces are still moving.**
- **Consumer summaries are intentionally lossy and say so.**
- **The stack remains thin.**

## Early implementation order
1. workflow / prompt / tool / resource lane
2. model / retrieval / structured-output attachment lane
3. runtime / identity / permission / confirmation lane
4. eval / trace / mismatch-report lane
5. migration / deprecation / downstream-handoff lane

That order follows the real pressure in the ecosystem: first make one workflow legible, then make its dependencies explicit, then make runtime posture visible, then attach evidence, then keep supportable change history.

## Non-goals
- a Rust LangChain clone
- one true MCP runtime
- a hosted agent-control plane
- a universal prompt registry for the whole ecosystem
- flattening provider dashboards, traces, and workflow support into one score
- pretending client tools, server tools, MCP tools, and local tools are interchangeable

## Success bar
This becomes worthy when a maintainer, support engineer, policy reviewer, or downstream tool can answer:
- what exact workflow/product subject is under review;
- which prompts, tools, and resources it officially supports;
- what provider / retrieval / runtime assumptions it imports;
- what permissions and confirmations actually apply;
- what evidence exists for the claimed behavior;
- what changed versus the prior review point;
- and what a given consumer may safely summarize,

without scraping prompt directories, runtime glue, provider consoles, or issue history.

## Read this with
- `gaps/agentic-application-surfaces-and-tooling-contracts.md`
- `design/agent-productization-stack.md`
- `design/agent-productization-pilot-program.md`
- `design/agent-surface-kit.md`
- `design/model-surface-kit.md`
- `design/retrieval-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/identity-surface-kit.md`
- `design/observability-kit.md`
- `design/support-envelope-kit.md`
