# Design: Agent Productization Stack (Agent Surface + Model Surface + Retrieval Surface + Runtime Settings + Identity Surface + Observability + Support Envelope)

## Goal
Turn Rust agent-enabled applications into a **portable productization stack** instead of leaving each application to publish its agent story as a tangle of prompt files, MCP manifests, provider dashboards, local tool glue, retrieval wiring, session-memory heuristics, and README prose.

The stack should **not** replace `rmcp`, `rig`, `swiftide`, provider SDKs, eval tooling, observability backends, or application frameworks.
It should make them compose better and make supported agent behavior reviewable.

## Why this note is needed now
Rust’s current signals say the missing problem is no longer “can Rust call a model?” They say the missing problem is **what a Rust agentic product can honestly claim to support**:
- the 2025 State of Rust survey says official docs remain canonical, says some learning traffic appears to be shifting toward LLM tooling, and says editors with agentic support are on the rise;
- MCP now has an official Rust SDK in `rmcp`, which means Rust has a real protocol substrate rather than only ad hoc JSON-RPC glue;
- Rust-side frameworks are proliferating: `rig` focuses on ergonomic modular LLM apps and ships agent, tool, provider, and eval lanes, while `swiftide` spans indexing/query pipelines and agents that can use tools and call other agents;
- provider platforms are also making agent behavior more operationally explicit: OpenAI documents agents, structured outputs, and trace grading as first-class features, while also deprecating the Assistants API in favor of the Responses direction; Anthropic distinguishes client tools from server tools, documents fine-grained tool streaming and multi-environment tool pitfalls, and its current MCP connector supports only tool calls over public HTTP rather than full local-MCP parity.

Together, those signals argue that the missing contribution is **not** another model wrapper, MCP helper, or fashionable agent runtime. It is the **boring portable boundary above the ingredients**.

## Stack layers

### 1) Agent Surface: declared workflow, prompt, tool, and resource truth
Agent Surface owns the **declared supported agent surface** for a product, service, binary, or workspace:
- workflow identities and operation classes,
- stable prompt ids and prompt families,
- tool catalogs and side-effect/confirmation posture,
- MCP resources/prompts/tools and local equivalents,
- session-state and memory posture,
- and checked workflow evidence.

Agent Surface answers questions like:
- “Which assistants, workflows, or copilots are officially supported?”
- “Which prompts, tools, and MCP resources are part of that promise?”
- “Which workflows are public, internal, best-effort, or experimental?”
- “What does the workflow remember, and for how long?”

Design rule: **prompt blobs, MCP manifests, and framework-local registration code must not be the only durable description of the agent surface**.

### 2) Model Surface + Retrieval Surface: dependency attachments, not hidden assumptions
Most real agents depend on model/runtime and retrieval/context choices that live outside the prompt catalog.
This layer imports:
- model/runtime identities,
- tokenizer and structured-output posture,
- provider capability profiles,
- corpora/index/query/ranking contracts,
- retrieval-backed memory or context sources,
- and fallback or no-retrieval lanes.

This layer answers questions like:
- “Which workflows depend on structured outputs or tool calling?”
- “Which ones require retrieval, search, or ranking semantics to behave as claimed?”
- “Which workflows were tested on one model family but only documented for another?”
- “What is part of the agent product surface versus merely a lower-layer capability?”

Design rule: **agent support truth must stay separate from model and retrieval truth, even when it imports both**.

### 3) Runtime Settings + Identity Surface: activation, permission, and trust posture
Agent products only become real when runtime and access posture are explicit:
- provider and endpoint configuration,
- API key / secret activation,
- MCP transport and remote-server configuration,
- user/account/tenant/operator context requirements,
- local-tool permission and confirmation policies,
- protected-surface imports from services, commands, or clients,
- and environment-specific activation across local, CI, staging, and production.

This layer answers questions like:
- “Which providers or MCP servers were actually activated?”
- “What side effects require confirmation or operator review?”
- “Which workflows are tenant-aware, user-aware, or machine-only?”
- “Which permissions were documented versus actually configured?”
- “Which local-only assumptions were silently invalid in a hosted or remote connector lane?”

Design rule: **agent support claims must not silently depend on unstated secrets, local shells, browser state, or invisible permission defaults**.

### 4) Observability + diagnostics + evals: runtime evidence and regression truth
Agentic systems need stronger evidence than one green demo:
- traces and step-level observations,
- tool-call and resource-access reports,
- eval datasets and graders,
- structured-output and schema-violation reports,
- refusal/fallback/error reason codes,
- latency/cost/budget evidence,
- and mismatch reports across provider swaps, MCP upgrades, or prompt/tool drift.

This layer answers questions like:
- “Did the supported workflow still behave as declared?”
- “Which step regressed: prompt, model, tool, resource, or session policy?”
- “Was a failure a black-box quality miss or a trace-visible contract break?”
- “What changed when we swapped model/provider/MCP/tooling lanes?”

Design rule: **evals, traces, and workflow diagnostics must not be flattened into one vague ‘agent quality’ score**.

### 5) Support Envelope + DocProof + Canonical Learning: support and docs truth
Agent-enabled products need an explicit support boundary:
- supported providers, model families, MCP transports, and targets,
- public versus internal workflows,
- checked examples, guides, and disclosure posture,
- source-build versus hosted/runtime-managed differences,
- docs that distinguish supported tools/resources from illustrative ones,
- and canonical-learning imports for docs hosts, CI, editors, and assistants.

This layer answers questions like:
- “Which workflows are officially supported versus experimental?”
- “Which provider or MCP combinations are documented, checked, or only aspirational?”
- “What does the public guide promise that the runtime actually enforces?”
- “What can downstream assistants or docs consumers safely import as canon?”

Design rule: **one notebook, one prompt playground, or one screenshot of a successful agent run is not the support contract**.

### 6) Transition and archaeology truth
Agent products change quickly and often painfully:
- provider/model swaps,
- API migrations and deprecations,
- MCP server additions or removals,
- remote-connector limitations,
- tool schema changes,
- prompt or rubric drift,
- memory/session-policy changes,
- and new confirmation or least-privilege posture.

This lane answers questions like:
- “What changed in the supported workflow boundary?”
- “Did the system gain or lose capabilities?”
- “Was the change additive, breaking, or merely internal?”
- “Which evidence proves the migration instead of merely restating intent?”
- “What stayed local-only versus what remained supportable on a hosted connector path?”

Design rule: **agent changes are product and support events, not just prompt edits or framework upgrades**.

### 7) Downstream consumers
The stack becomes ecosystem-shaping when real consumers can import it honestly:
- **service/client/command** consumers can attach workflows to protected surfaces without becoming the new source of truth;
- **support/incident** consumers can answer “what did the agent actually promise?” from artifacts instead of chat transcripts and team memory;
- **release/policy/security** consumers can review workflow/tool/resource changes without scraping runtime glue;
- **atlas/learning** consumers can compare real Rust agentic lanes without pretending one framework, provider, or MCP pattern has already won.

Design rule: **consumers import selected agent-productization facts; they do not redefine the stack**.

## What an epic contribution should look like in practice
A worthy contribution here is not “Rust gets its own LangChain clone”, “the one true MCP runtime”, or “the one true agent framework”.
It is a portable boring stack with clear boundaries:

1. **workflow/prompt/tool/resource truth first**
   - prove `agent-surface/v0`, `prompt-catalog/v0`, `tool-catalog/v0`, `resource-surface/v0`, and one linked `agent-check-report/v0` on a real product;
2. **model/retrieval attachments second**
   - import model/runtime and retrieval contracts without flattening them into agent truth;
3. **runtime/identity activation third**
   - attach provider, permission, confirmation, tenant/operator, and secret posture through `runtime-settings` and identity imports;
4. **eval/trace evidence fourth**
   - prove workflow behavior through evals, traces, and mismatch reports rather than only black-box demos;
5. **support/docs and transition consumers fifth**
   - prove public support claims, migration reports, and downstream release/support/policy imports.

An eventual aggregate artifact may exist, but it should be a **thin pack of linked artifacts**, not a mega-schema that erases the lane boundaries.

The proposal-layer candidate is now [`proposals/epic-agent-productization-stack.md`](../proposals/epic-agent-productization-stack.md): a thin `cargo agent-product` / `agent-product-pack/v0` layer above Agent Surface + model/retrieval/runtime/identity/evidence/support imports rather than a new universal Rust agent platform.

## Ranked first execution lanes
1. **Workflow / prompt / tool / resource lane**
   - best first exporter because real Rust agent products can already declare these before the rest of the stack is fully stable.
2. **Model / retrieval attachment lane**
   - proves agent products can import model/runtime and retrieval truth without pretending one provider or RAG pattern owns the whole workflow.
3. **Runtime / identity / permission lane**
   - proves provider activation, tool confirmation, tenant context, and MCP transport posture are reviewable.
4. **Eval / trace lane**
   - proves supported workflows can be checked and regressions explained with portable evidence instead of screenshots and anecdotes.
5. **Support / docs / transition lane**
   - proves supported combinations, migration realities, and bounded consumer imports can stay honest while upstream provider/MCP surfaces keep moving.

## What this stack must not do
- It must not become a hidden framework preference.
- It must not flatten provider/runtime support into workflow support.
- It must not silently encode local-only assumptions as product promises.
- It must not turn traces/evals into one giant quality score.
- It must not make docs/support pages the source of truth instead of imported artifacts.
- It must not pretend current provider/MCP capabilities are stable enough to remove migration evidence.

## References (signals)
- 2025 State of Rust survey results:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- MCP specification / architecture / Rust SDK:
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
