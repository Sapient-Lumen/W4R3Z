---
id: P-0392
title: MCP Protocol Conformance, Transcript & Capability Kit — spec-pinned traces, transport-neutral evidence, and server/client drift receipts
status: idea
domains: [ai, protocol, interoperability, validation, tooling, security]
last_reviewed: 2026-03-06
evidence:
  - https://modelcontextprotocol.io/specification/2025-03-26
  - https://modelcontextprotocol.io/specification/2025-03-26/changelog
  - https://modelcontextprotocol.io/docs/sdk
  - https://github.com/modelcontextprotocol/rust-sdk
---

# Problem

MCP is no longer just a thought experiment. The specification has a real versioned surface, official SDKs are documented and tiered, and the official Rust SDK already exposes client/server building blocks, local and remote transports, typed capabilities, subscriptions, and OAuth-related support.

That means the basic substrate exists. But the operational failures are still concentrated at the seam between:

- **what the spec says a client/server pair should negotiate and what a real implementation actually advertises**,
- **stdio transcripts and remote/HTTP transcripts that describe the same logical session in very different shapes**,
- **tool/resource/prompt schema evolution and what older hosts silently tolerate**,
- **authorization, roots, sampling, subscriptions, and notifications that interact in subtle ways**,
- and **bug reports that currently amount to “my MCP server works in host A but not host B” with no shareable receipt**.

The missing Rust contribution is not another SDK. It is a **conformance, transcript, and evidence kit** that turns MCP compatibility failures into boring, spec-pinned artifacts.

# What it provides

- `mcp.lock` — pins specification revision, transport profile, auth expectations, capability set, schema hashes, and redaction policy.
- `mcptrace` IR — a transport-neutral transcript model for initialize/notify/request/response lifecycles across local and remote transports.
- `capability-diff` — explains how two hosts/clients/servers differ at the level of capabilities, schema, message ordering, and optional features.
- `schema-pack` — snapshots tool/resource/prompt schemas and hashes them for later comparison.
- `cargo mcp-evidence` — emits `*.mcpbundle.zip` with lockfile, transcript slices, redaction map, capability diffs, and notes.

# What the crate should provide other people

1. **A boring incident bundle for MCP incompatibility bugs**.
2. **A transport-neutral transcript format** that survives host handoff.
3. **Schema and capability pinning** instead of “tested against whatever was current last week”.
4. **Explainable failures** for mismatched capabilities, unsupported methods, and ordering bugs.
5. **A narrow conformance layer above existing SDKs** rather than pressure to rewrite them.

# Persona / who it’s for

- Rust maintainers building MCP clients, servers, proxies, or host integrations
- Teams embedding the official Rust SDK but needing compatibility diagnostics
- Tooling authors shipping MCP support across several host products
- Security reviewers who need bounded, redactable session receipts

# Users & user stories

- **Server author**: “Show me why my server works over stdio but fails over remote transport in one host.”
- **Host integrator**: “Pin the exact capability and schema set a plugin server exposed during qualification.”
- **SDK maintainer**: “Prove whether a breakage is due to spec revision drift, optional-feature handling, or host bugs.”
- **Security team**: “Share a transcript that explains the bug without leaking full prompts, resource contents, or secrets.”

# Prior art (and why it’s insufficient)

- The official MCP specification defines the normative message model.
- The official SDK page now documents supported SDKs, tiers, and the shared expectations around local/remote transports and protocol compliance.
- The official Rust SDK already provides substantial protocol and runtime substrate.

What Rust still lacks is a **single evidence-grade coordination layer** for transcript normalization, capability diffing, schema pinning, and redactable receipts.

# Design goals

1. **Spec-pinned** — every bundle states the MCP revision it targets.
2. **Transport-neutral** — stdio and remote transport sessions must normalize into one comparable IR.
3. **Schema-aware** — tool/resource/prompt signatures are first-class and hashable.
4. **Redaction-first** — prompts, resources, and secrets must be safely reducible.
5. **SDK-adapter, not SDK-replacement** — work above existing Rust implementations.

# MVP surface

- Minimal types: `McpLock`, `TranscriptSlice`, `CapabilityDiff`, `SchemaPack`, `McpBundle`
- Minimal functions:
  - `capture_transcript()`
  - `normalize_session()`
  - `diff_capabilities()`
  - `write_bundle()`
- Feature flags:
  - `stdio`
  - `remote`
  - `schemas`
  - `oauth`
  - `redaction`

# Compatibility story

- Adapts the official Rust SDK instead of competing with it.
- Can ingest raw JSON-RPC logs, SDK-level events, or host-side traces.
- Keeps transport-specific details available while still producing one canonical IR.
- Supports partial bundles when prompt/resource payloads cannot be shared.

# Conformance & fixtures

- Goldens for initialize negotiation, missing capability declarations, notification ordering, subscription updates, and schema drift.
- Tiny fixtures for host/server mismatches on prompts, resources, tools, and optional features.
- Compatibility packs keyed by spec revision and capability profile.
- Public transcript corpus with aggressive redaction examples.

# Path to boring stability

- Stabilize the lockfile and transcript IR before expanding adapters.
- Keep the first release focused on capture, diff, and redaction instead of full fuzzing.
- Treat schema hashing and capability negotiation as core, not optional nice-to-haves.
- Version transport adapters independently if the spec evolves quickly.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and CLI that capture an MCP session, normalize it across transports, pin the spec revision and capability set, compute explainable diffs, and emit compact `*.mcpbundle.zip` artifacts.

# De-risk plan

1. Start with official Rust SDK adapters first.
2. Support digest-only payload evidence before rich body capture.
3. Keep capability negotiation and schema hashing explicit in the lockfile.
4. Delay broad host-specific overlays until the neutral transcript IR is stable.

# Non-goals

- Not a new MCP SDK.
- Not a host product.
- Not a generic agent runtime.
- Not a permanent transcript store.

# Architecture & API sketch

```rust
pub struct McpLock {
    pub spec_revision: String,
    pub transport_profile: String,
    pub capability_profile: Vec<String>,
    pub schema_pack_hash: String,
}

pub fn capture_transcript(input: CaptureInput) -> Result<TranscriptSlice>;
pub fn normalize_session(slice: &TranscriptSlice, lock: &McpLock) -> Result<McpBundle>;
pub fn diff_capabilities(lhs: &McpBundle, rhs: &McpBundle) -> CapabilityDiff;
```

Bundle draft: `mcp.lock`, `transcript.json`, `capabilities.json`, `schemas.json`, `redaction-map.json`, `findings.json`, `notes.md`.

# Security / safety model

- Default to structural message summaries rather than raw payload retention.
- Allow field-level redaction and hashing for prompts, resource bodies, and auth headers.
- Record what was removed so absence is not confused with protocol failure.
- Keep bundle size bounded and deterministic for CI and bug reports.

# Maintenance & governance plan

- Keep the core about lockfiles, transcript normalization, capability diffs, and receipts.
- Version spec overlays separately from transport adapters.
- Publish a small public conformance corpus keyed by spec revision.
- Avoid drifting into “general MCP platform” scope.

# Milestones

## 0.1
- transcript capture
- lockfile format
- capability diff prototype

## 0.2
- schema packs
- redaction policies
- public fixtures

## 1.0
- stable `*.mcpbundle.zip`
- documented compatibility policy across spec revisions
- official Rust SDK adapter maturity

# Open questions

- How much host-specific behavior belongs in stable overlays versus diagnostic notes?
- Which transcript granularity is sufficient for portability without leaking too much?
- How should auth/OAuth support be represented when a host only exposes partial evidence?

# Sources

- MCP specification (2025-03-26): https://modelcontextprotocol.io/specification/2025-03-26
- MCP changelog for the 2025-03-26 revision: https://modelcontextprotocol.io/specification/2025-03-26/changelog
- Official SDKs and tiering: https://modelcontextprotocol.io/docs/sdk
- Official Rust SDK: https://github.com/modelcontextprotocol/rust-sdk
