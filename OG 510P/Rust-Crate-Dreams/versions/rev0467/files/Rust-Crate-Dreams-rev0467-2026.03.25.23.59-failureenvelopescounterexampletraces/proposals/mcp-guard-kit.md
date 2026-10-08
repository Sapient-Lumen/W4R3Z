---
id: P-0071
title: MCP Guard Kit — transport exposure, auth boundaries, and operation guards for MCP deployments
status: idea
domains: [ai, security, policy, protocols, tooling, enterprise]
last_reviewed: 2026-03-19
evidence:
  - https://modelcontextprotocol.io/docs/sdk
  - https://github.com/modelcontextprotocol/rust-sdk
  - https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
  - https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
  - https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
  - https://modelcontextprotocol.io/specification/2025-11-25/server/tools
  - https://github.com/modelcontextprotocol/servers
  - https://github.com/modelcontextprotocol/experimental-ext-interceptors
  - https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/
---
# Problem

MCP is no longer missing basic Rust substrate.
That changes the shape of the opportunity.

As of March 2026:

- MCP has an official SDK matrix and the Rust SDK is now an **official Tier 2** SDK.
- The official Rust SDK (`rmcp`) has crossed into a real 1.x line and is continuing to add auth and transport support.
- The specification now carries explicit authorization, transport, tools, roots, prompts, and sampling security guidance.
- The official security guide now names concrete attack families: confused deputy flows, token passthrough, SSRF, session hijacking, risky local-server startup commands, and over-broad scopes.
- The official roadmap now explicitly calls out **enterprise readiness** as a 2026 priority.
- The official reference-server repository warns that its servers are educational examples, **not** production-ready defaults.
- There is even an **experimental interceptor extension**, which is useful evidence that the ecosystem feels the need for policy hooks — but it is not yet an official extension.

So the missing Rust contribution is no longer “an MCP SDK exists in Rust?”
The sharper missing crate is the **boring deployment guard layer** above the SDK and the spec.

Teams need one compact, reviewable answer to questions like:

- is this deployment exposed only over local stdio, or also over remote HTTP,
- are origin validation, localhost binding, and auth posture actually in force,
- are tokens audience-bound and explicitly not being passed through,
- which tools/resources/prompts/sampling paths require approval or scope elevation,
- what limits/redaction/audit posture exists,
- and can another maintainer inspect those answers without reading three configs, a gateway policy, and a security review thread.

That is the seam **MCP Guard Kit** should occupy.

# What it should provide

## 1) One transport exposure receipt

Other people should get a compact artifact that states:

- transport family (`stdio`, local HTTP, remote HTTP, mixed),
- bind posture (`localhost` only vs broader exposure),
- origin-validation posture,
- TLS/auth expectation,
- session mode and resumability notes,
- and whether local-startup commands require explicit consent.

This should become `transport-exposure.receipt.json`.

## 2) One auth-boundary receipt

The crate should make authorization truth reviewable instead of folklore.
It should record:

- whether OAuth is in use,
- whether `resource` / audience binding is expected,
- whether token passthrough is forbidden and enforced,
- whether scopes are progressive or omnibus,
- whether consent is per-client and per-user where relevant,
- and whether credentials/tokens are stored or logged safely.

This should become `auth-boundary.receipt.json`.

## 3) One operation-guard contract

The crate should make risky MCP operations boring to review.
It should record:

- per-tool/resource/prompt/sampling/roots guard classes,
- approval requirements,
- size/content-type/iteration limits,
- redaction/audit defaults,
- high-risk operation categories,
- and the manual-review zones where policy cannot be inferred honestly.

This should become `operation-guard.contract.json`.

## 4) One drift-aware review bundle

The crate should bundle the receipts, selected runtime findings, redaction notes, and scenario evidence into one compact `mcpguardbundle.zip` so another maintainer or security reviewer can inspect the deployment posture without replaying the whole system.

# What the crate should provide other people

1. **A boring deployment-security contract** above the MCP SDK.
2. **A reviewable answer for local-vs-remote exposure truth**.
3. **A reviewable answer for audience/consent/token-boundary truth**.
4. **A reviewable answer for tool/resource/prompt/sampling guard truth**.
5. **Compact receipts and scenario bundles** instead of prose-only security claims.

# Users & user stories

- **MCP server maintainer**: “Tell me exactly what transport and auth promises this server is making.”
- **Host/platform team**: “Enforce one policy layer across many MCP servers without rewriting the SDK.”
- **Security reviewer**: “Show me where token passthrough is prevented, where origin validation exists, and what risky tools require approval.”
- **Enterprise integrator**: “I need one support bundle for why this deployment is acceptable — or not.”
- **Tooling author**: “Import `rmcp`, proxy, or gateway configuration and normalize it into one guard report.”

# Prior art (and why it’s insufficient)

- **Official MCP SDK page** proves Rust now has official substrate, but that is not the same as deployment-grade policy or review artifacts.
- **Official Rust SDK (`rmcp`)** provides client/server/runtime substrate and current auth/transport work, but it is intentionally an SDK, not a full security-policy product.
- **Official authorization specification** defines the normative HTTP auth model, including resource indicators and audience validation, but does not by itself provide a reusable Rust guard layer.
- **Official security best-practices guide** now names concrete attack classes and mitigations, but it is guidance rather than a drop-in crate/workflow.
- **Official transport and tools sections** specify required security behavior, but they do not produce reviewable receipts.
- **Reference servers** are explicitly educational and not production-ready.
- **Experimental interceptors** suggest future hook points, but they are not an accepted official extension and should not be treated as the deployment answer today.
- **P-0392 MCP Protocol Conformance, Transcript & Capability Kit** already covers compatibility/evidence above the protocol itself. MCP Guard Kit should complement that lane, not collapse into it.

# Design goals

1. **Import SDK/proxy/gateway reality rather than replace it.**
2. **Keep transport exposure, auth boundaries, and operation guards visibly separate.**
3. **Work for both local and remote deployments**, with honest manual-review boundaries where the host/product owns the final consent UX.
4. **Emit reviewable artifacts**, not just middleware side effects.
5. **Be adapter-first**: `rmcp` now, other future adapters later.
6. **Compose with evidence/conformance crates** instead of pretending all MCP problems are one lane.
7. **Stay honest about experimental extension status** if interceptor support is added later.

# Non-goals

- Replacing the official MCP Rust SDK.
- Defining a new MCP protocol or competing with the specification.
- Claiming perfect prompt-injection prevention.
- Becoming a general SIEM, IAM, or API gateway.
- Treating experimental interceptors as if they were already normative.

# Architecture & API sketch

## Suggested workspace split

- `mcp_guard_model`
  - core types for transport exposure, auth boundaries, and operation guards
- `mcp_guard_rmcp`
  - adapters for the official Rust SDK
- `mcp_guard_policy`
  - policy evaluators and classification logic
- `mcp_guard_audit`
  - audit/redaction/event helpers
- `mcp_guard_bundle`
  - receipt writer / review bundle export
- `cargo-mcp-guard`
  - cargo subcommand / CLI

## Core commands

- `cargo mcp-guard inspect-transport`
  - emit `transport-exposure.receipt.json`
- `cargo mcp-guard inspect-auth`
  - emit `auth-boundary.receipt.json`
- `cargo mcp-guard inspect-operations`
  - emit `operation-guard.contract.json`
- `cargo mcp-guard diff`
  - compare two deployment bundles
- `cargo mcp-guard bundle`
  - produce `mcpguardbundle.zip`

## Draft API sketch

```rust
pub fn inspect_transport_exposure(input: &TransportInput) -> Result<TransportExposureReceipt>;
pub fn inspect_auth_boundary(input: &AuthInput) -> Result<AuthBoundaryReceipt>;
pub fn inspect_operation_guards(input: &GuardInput) -> Result<OperationGuardContract>;
pub fn diff_guard_bundles(old: &McpGuardBundle, new: &McpGuardBundle) -> Result<McpGuardDiff>;
pub fn write_bundle(bundle: &McpGuardBundle, out: &Path) -> Result<()>;
```

# Security / safety model

- Treat all external inputs, tool outputs, and remote identities as untrusted until policy says otherwise.
- Never equate “OAuth is present” with “audience binding is correct.”
- Preserve a distinct field for “token passthrough forbidden and enforced.”
- Keep local-server startup-command posture separate from remote HTTP posture.
- Record when approval, redaction, or iteration limits are missing rather than guessing.
- Default audit records should be redacted and bounded.

# Maintenance & governance plan

- Track MCP spec/security evolution with explicit adapters and policy classifiers, not giant monolithic logic.
- Start with `rmcp` adapters because that is the official Rust substrate today.
- Keep experimental interceptor support optional and clearly labeled if added.
- Maintain a tiny public fixture corpus covering local-command consent, origin validation, token audience binding, scope escalation, and sampling/tool approval seams.

# Milestones

## 0.1
- inspect one `rmcp` deployment into `transport-exposure.receipt.json`
- inspect one auth configuration into `auth-boundary.receipt.json`
- inspect one tool/resource/sampling policy into `operation-guard.contract.json`
- bundle one compact review artifact

## 0.2
- drift/diff tooling across deployment revisions
- richer audit/redaction imports
- local-startup-command review support
- approval/loop-limit checks for sampling and high-risk tools

## 0.3
- optional interceptor integration adapters if the ecosystem settles
- proxy/gateway import lanes
- stronger enterprise policy presets

# Open questions

- Which review objects should be purely static config inspection versus runtime-observed receipts?
- How much host-owned approval UX can be imported honestly when the MCP server is only one part of the stack?
- Should local-command consent posture be modeled inside the transport receipt or as a parallel “bootstrap posture” object?
- Which policy language integration is worth supporting first, if any?

# Sources

See front matter links.
