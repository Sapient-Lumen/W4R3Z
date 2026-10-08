# 39 — Orchestration Patterns Crosswalk (v0.19)

This doc is non-normative: it maps your “hacky local router” to known orchestration patterns so we steal good ideas.

## Your architecture (as specified so far)
- WS + Ledger resembles a blackboard (strict working memory + permissive scratch).
- AAR resembles a prompt composer / attention router.
- ADCC resembles governance + resource allocation (modes, votes, leases).
- MetaLLM resembles a supervisor/controller that nudges a runtime based on telemetry.

## Patterns that align
### Supervisor / Subagents
A central controller routes work to subagents (tools).
You implement this with:
- MetaLLM + router CLI
- REQ# tickets
- floor/lease selection

### Handoffs
Behavior changes based on state (e.g., switch to PatchOnly on collisions).
You implement this via:
- mode changes (Gatekeeper ↔ PatchOnly ↔ Freeze)
- strictness ladder + budgets

### Graph/state-machine orchestration
Nodes/states govern what happens next (BOOT/DIVERGE/SELECT/INTEGRATE).
You implement this via:
- Golden Path state machine
- “anytime collapse” rule under truncation

### Event-driven runtime
Agent messages are events; router appends and summarizes.
You implement this via:
- CURSOR + bounded DELTA feed
- compaction SUM# objects

## What’s distinct about your setting
Most frameworks assume you can call agents as tools repeatedly (API).
You *can’t pay for API*, and slice counts are unknown.
So you must:
- treat every output as an anytime packet
- maximize salvageable control-plane data
- compress coordination into single votes + deterministic arbitration

## What to steal (safely)
- Observability: telemetry-first steering
- Deterministic routing rules: fewer “protocol elections”
- Typed request objects instead of freeform DM backchannels

Architectural analogy: blackboard systems (67_blackboard_rationale_anytime_packets.md).
