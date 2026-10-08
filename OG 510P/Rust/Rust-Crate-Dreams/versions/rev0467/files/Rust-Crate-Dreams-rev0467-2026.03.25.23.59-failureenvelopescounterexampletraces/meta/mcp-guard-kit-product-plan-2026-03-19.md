# MCP Guard Kit — product plan (2026-03-19)

This note sharpens **P-0071 MCP Guard Kit** into an implementation-ready `0.1` shape.

## Main judgment

A worthwhile `0.1` should **not** try to become a whole MCP platform, proxy, or general enterprise gateway.
It should be a **small crate family plus CLI** that helps teams publish one reviewable answer to:

- what transport exposure they actually have,
- what auth boundary they actually enforce,
- what risky operations actually require approval or limitation,
- and what evidence another maintainer can inspect without reading every config file and security memo.

The missing value is the **boring deployment guard contract** above the current MCP SDK and spec/security substrate.

## What the crate should provide other people

For server maintainers, host teams, security reviewers, and platform operators, the crate should provide:

1. **One transport exposure receipt** instead of local/remote deployment folklore.
2. **One auth-boundary receipt** instead of “we use OAuth” hand-waving.
3. **One operation-guard contract** instead of scattered per-tool notes.
4. **One drift workflow** that explains what changed between deployments.
5. **One compact guard bundle** that can travel between teams and review systems.

## Three first-class review objects

### 1. Transport exposure receipt

Named classes for `0.1` should focus on exposure truth such as:

- `stdio_local_only`
- `http_localhost_only`
- `http_origin_validation_missing`
- `remote_http_auth_required`
- `remote_http_tls_expected`
- `local_startup_consent_required`
- `manual_review_required`

This object should answer:

- which transport families are in play,
- which bind/interface posture is claimed,
- whether origin validation and auth are present,
- and whether local startup commands are entering through a reviewable path.

### 2. Auth-boundary receipt

Named classes for `0.1` should focus on auth truth such as:

- `oauth_boundary_declared`
- `resource_indicator_required`
- `token_audience_validated`
- `token_passthrough_forbidden`
- `progressive_scope_model`
- `per_client_consent_required`
- `manual_review_required`

This object should answer:

- whether the deployment is really using the MCP auth model,
- whether tokens are bound to the intended resource,
- whether token passthrough is blocked,
- and whether scopes/consent are narrow enough to review honestly.

### 3. Operation-guard contract

Named classes for `0.1` should focus on risky-operation truth such as:

- `tool_allowlist_enforced`
- `sampling_user_approval_required`
- `sampling_loop_limit_present`
- `roots_boundary_enforced`
- `resource_size_limit_present`
- `audit_redaction_default`
- `manual_review_required`

This object should answer:

- what operations are low-risk versus gated,
- what size/content-type/iteration limits exist,
- what approval/elevation points exist,
- and where manual review starts because a host/product owns the final UX.

## Recommended `0.1` command surface

### `cargo mcp-guard inspect-transport`
Inspect deployment metadata and emit:
- `transport-exposure.receipt.json`
- `mcp-guard.transport.report.json`

### `cargo mcp-guard inspect-auth`
Inspect auth configuration and emit:
- `auth-boundary.receipt.json`

### `cargo mcp-guard inspect-operations`
Inspect tool/resource/prompt/sampling policy and emit:
- `operation-guard.contract.json`

### `cargo mcp-guard diff`
Compare two guard bundles and emit:
- `mcp-guard-drift.diff.json`

### `cargo mcp-guard bundle`
Produce one compact `.mcpguardbundle.zip` containing receipts, notes, and selected audit/redaction facts.

## Recommended crate/workspace split

- `mcp_guard_model`
- `mcp_guard_rmcp`
- `mcp_guard_policy`
- `mcp_guard_audit`
- `mcp_guard_bundle`
- `cargo-mcp-guard`

## `0.1` artifact set

Core artifacts should be:
- `mcp-guard.toml`
- `transport-exposure.receipt.json`
- `auth-boundary.receipt.json`
- `operation-guard.contract.json`
- `mcp-guard.transport.report.json`
- `mcp-guard-drift.diff.json`
- `notes.md`

## Discovery order

1. **Transport import**
   - stdio / local HTTP / remote HTTP / mixed
   - bind/interface posture
   - origin and TLS posture
2. **Auth boundary inspection**
   - OAuth presence
   - audience/resource binding
   - token passthrough prohibition
   - scope/consent model
3. **Operation guard inspection**
   - per-tool/resource/prompt/sampling classes
   - approvals and limits
   - audit and redaction posture
4. **Bundle export**
   - receipts
   - selected notes
   - manual-review markers

## Ranking discipline

A good `0.1` should not treat “the server can answer requests” as the verdict.
It should keep separate:

- `transport_exposure_known`
- `auth_boundary_known`
- `operation_guard_known`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- official MCP auth/security guidance
- official Rust SDK deployment/runtime facts
- tool/resource/prompt/sampling/roots capability declarations
- optional proxy/gateway or interceptor adapter facts
- selected audit/redaction configuration

### Do not flatten into one fake verdict
- “OAuth exists”
- “the server is secure”
- “tool approval probably happens somewhere”
- “localhost means safe”
- “the reference server example is production-grade”

## Preferred proving grounds

- a local Streamable HTTP deployment missing origin validation
- a remote OAuth deployment that accidentally accepts token passthrough or skips audience validation
- a high-risk tools deployment with progressive scope escalation
- a sampling-enabled deployment without user approval or loop limits
- a local one-click server install flow where startup-command consent matters

## Non-goals

- not a new MCP SDK
- not a full enterprise policy platform
- not a general-purpose SIEM
- not a perfect prompt-injection prevention system
- not a substitute for host/product trust decisions

## MVP API sketch

```rust
pub fn inspect_transport_exposure(input: &TransportInput) -> Result<TransportExposureReceipt>;
pub fn inspect_auth_boundary(input: &AuthInput) -> Result<AuthBoundaryReceipt>;
pub fn inspect_operation_guards(input: &GuardInput) -> Result<OperationGuardContract>;
pub fn diff_guard_bundles(old: &McpGuardBundle, new: &McpGuardBundle) -> Result<McpGuardDiff>;
pub fn write_bundle(bundle: &McpGuardBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Track the official spec/security docs and `rmcp` evolution explicitly.
- Preserve a visible distinction between normative MCP requirements and local policy overlays.
- Keep experimental interceptor integration optional and clearly labeled.
- Keep the kit small and receipt-first.

## Sources

- https://modelcontextprotocol.io/docs/sdk
- https://github.com/modelcontextprotocol/rust-sdk
- https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
- https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
- https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
- https://modelcontextprotocol.io/specification/2025-11-25/server/tools
- https://github.com/modelcontextprotocol/servers
- https://github.com/modelcontextprotocol/experimental-ext-interceptors
- https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/
