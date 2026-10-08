# MCP guard-kit lane boundaries (2026-03-19)

This note exists so the archive does not flatten several adjacent MCP lanes into one fake “MCP support” crate.

## Core judgment

**P-0071 MCP Guard Kit** should be the lane for:

- transport exposure truth,
- auth-boundary truth,
- operation-guard truth,
- and compact deployment review bundles.

It should **not** silently absorb:

- full protocol conformance,
- transcript normalization,
- host/product UX ownership,
- general IAM / gateway / SIEM work,
- or experimental extension design itself.

## Keep these lanes separate

### 1. MCP Guard Kit

This lane is about **deployment guard contracts**:

- origin validation
- localhost vs remote exposure
- OAuth audience/resource binding
- token passthrough prohibition
- approval/allowlist/limits for tools, resources, prompts, sampling, and roots
- audit/redaction posture

Primary artifacts:
- `transport-exposure.receipt.json`
- `auth-boundary.receipt.json`
- `operation-guard.contract.json`
- `mcpguardbundle.zip`

### 2. P-0392 MCP Protocol Conformance, Transcript & Capability Kit

This lane is about **protocol evidence and compatibility receipts**:

- transcript normalization
- capability drift
- schema pinning
- spec revision locks
- portability of bug reports across hosts/transports

Primary artifacts there are transcript/capability/schema bundles, not deployment guard contracts.

### 3. SDK/runtime implementation work

The official Rust SDK and related runtime work are the lane for:

- building clients and servers
- transport machinery
- protocol feature implementation
- auth/runtime primitives
- developer ergonomics

MCP Guard Kit should ride that substrate rather than pretending to replace it.

### 4. Experimental interceptor extension work

The interceptor repository is the lane for:

- extension design experiments
- generic interception hook models
- potential future cross-language middleware shapes

MCP Guard Kit may later *adapt to* interceptor hooks, but should not present experimental extension semantics as normative today.

### 5. Host/product trust UX

This separate lane includes:

- final user-facing approval dialogs
- enterprise identity-provider UX
- end-user consent copy and interaction design
- product-specific risk-ranking surfaces

MCP Guard Kit may emit artifacts that hosts consume, but it does not own the entire user-trust surface.

## Anti-collapses to avoid

Do **not** collapse these distinctions:

- “origin validation exists” vs “the server is safe”
- “OAuth is present” vs “audience binding is enforced”
- “tool approval exists” vs “all risky operations are bounded”
- “experimental interceptors exist” vs “Rust already has a standard policy layer”
- “reference server runs” vs “reference server is production-ready”
- “protocol conformance evidence exists” vs “deployment guardrails exist”

## Honest `0.1` scope

A good `0.1` for this lane should focus on:

1. `rmcp` adapters
2. transport-exposure inspection
3. auth-boundary inspection
4. operation-guard inspection
5. compact bundle export

A bad `0.1` would try to become:

- a general MCP proxy platform,
- a universal agent-security product,
- a replacement SDK,
- or a full transcript/conformance lab.
