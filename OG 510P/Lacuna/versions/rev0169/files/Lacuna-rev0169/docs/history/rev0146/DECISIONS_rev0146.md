# Decisions — rev0146

## D-0146-01: Introduce campaign libraries outside epistemic state

**Decision:** Add strict library and campaign manifests that select a cube and register default participants.

**Reason:** Humans need names and selection. Those preferences do not belong in story canon.

**Consequence:** Campaign metadata is not protected by the cube event chain. This is explicit.

## D-0146-02: One context projection, multiple renderers

**Decision:** Build JSON context once, then render Markdown from it.

**Reason:** Duplicate filtering logic created a hidden-world disclosure bug.

**Consequence:** New adapters should consume the structured projection rather than querying tables independently.

## D-0146-03: Refuse perspective plus candidate-world scope

**Decision:** `agent_id` and `world_id` cannot coexist in one context request.

**Reason:** The combination is semantically ambiguous and was previously unsafe.

**Consequence:** Directors receive an audience context and separate privileged planner context.

## D-0146-04: Add a turn adapter, not an LLM client

**Decision:** Emit head-bound packets and accept strict proposals; do not choose or call a model.

**Reason:** Vendor integration and generation policy are replaceable outer concerns. Atomic epistemic custody is not.

## D-0146-05: Use sequential aliases in turn proposals

**Decision:** Permit `as` and `@alias` in adapter operations, then normalize to strict kernel operations.

**Reason:** Models should not be required to calculate deterministic claim hashes or coordinate generated IDs manually.

**Consequence:** Aliases are adapter syntax only. Event payloads and change receipts contain final IDs.

## D-0146-06: Treat narration as a source, not truth

**Decision:** Commit a SHA-256-linked utterance source for every accepted narration, but do not store its body.

**Reason:** The prose is evidence-bearing presentation. It is neither a claim nor automatic canon. Full transcript storage is an application concern until a stronger custody design is justified.

## D-0146-07: Require declared disclosure linkage

**Decision:** New audience-visible assertions sourced from narration and declared reveals must match bidirectionally.

**Reason:** A narration interface without a link to epistemic changes recreates the “memory paragraph” failure.

**Nonclaim:** Runtime validation does not prove semantic entailment between prose and assertions.

## D-0146-08: Preserve schema version 1

**Decision:** Do not alter cube database schema in rev0146.

**Reason:** Campaigns, context projection, and turns can be implemented as outer adapters over existing events and projections. Avoiding a migration keeps the kernel cut focused.
