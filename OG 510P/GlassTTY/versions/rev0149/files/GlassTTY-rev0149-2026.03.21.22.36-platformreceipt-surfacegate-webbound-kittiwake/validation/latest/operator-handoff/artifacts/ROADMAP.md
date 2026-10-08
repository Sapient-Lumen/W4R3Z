# Roadmap

This roadmap is organized by **capability stream** and **adoption sequence**, not by random backlog accumulation.

## Stream 1 — Canon, doctrine, and migration

Goal: make the repo understandable and writable by future implementers without archaeology.

Deliverables:
- top-level docs rewritten around the larger product
- canonical design docs for workflows, state, support truth, drift, agents, and evidence
- explicit design principles and autonomy ladder
- migration plan for adopting the canon in-tree

Exit condition:
- a new implementer can explain the product model, doctrine, and where the living truth lives without reading handoff history first

## Stream 2 — Shared workflow contract

Goal: define what “support” means in workflow terms.

Minimum shared workflows for every official surface:
- surface-detect
- receiver-resolve
- composer-read
- composer-write
- turn-submit
- generation-read
- latest-turn-read
- support-capture
- route-history-witness when navigation continuity matters

Deliverables:
- workflow catalog
- workflow acceptance checklists
- proof templates for workflow captures

Exit condition:
- every official surface has a support record that reports against the same minimum workflow vocabulary and points to a proof path

## Stream 3 — Structured state contract

Goal: replace ad hoc payloads and surface-specific heuristics with stable state families.

Primary state families:
- session
- surface
- navigation
- receiver
- composer
- generation
- conversation
- turn
- selection
- diagnostics
- support
- evidence
- action outcome

Exit condition:
- at least two official surfaces can emit the same core state families with documented degradation behavior
- workflows that depend on SPA navigation can preserve route/history truth instead of burying it in ad hoc notes

## Stream 4 — Support truth and release gates

Goal: make support claims inspectable, scoped, and promotable.

Deliverables:
- living support records per surface
- promotion and demotion rules
- release-gate checklists
- support-record lifecycle and update procedure

Exit condition:
- stronger support claims require current lane-scoped evidence instead of narrative confidence
- transient cues alone cannot close workflow proof or promotion questions

## Stream 5 — Drift and adaptation program

Goal: treat UI change as expected maintenance work, not surprise failure.

Deliverables:
- baseline capture plans per surface
- drift severity vocabulary
- drift incident and comparison templates
- triage playbook from symptom to next action

Exit condition:
- a changed surface can produce a meaningful comparison bundle and a next recommended move within one operating pass

## Stream 6 — Evidence normalization

Goal: make artifacts and ledgers consistent enough to compare across time and surfaces.

Deliverables:
- artifact family definitions
- evidence-ledger schema
- support-bundle manifest discipline
- traceability from feature themes to artifacts

Exit condition:
- future implementers can answer “what proved this claim?” without scavenger hunts

## Stream 7 — Surface rollout

Goal: move from Claude-first reality to credible multi-surface support.

Rollout order work:
- lock the second adapter target with an explicit decision frame
- prove one non-Claude surface on one lane
- backfill support records and baselines for the remaining official surfaces
- expand from core workflows into secondary workflows only after core proof exists

Exit condition:
- one non-Claude surface reaches experimental support on the shared core workflow set for one real lane

## Stream 8 — Operator and agent execution

Goal: support local/private LLM operation without abandoning visibility, policy, or evidence.

Deliverables:
- policy surfaces
- approval and stop-condition surfaces
- autonomy ladder mapping to runtime permissions
- action plans and execution reports

Exit condition:
- agent-capable operation is bounded by explicit mode, approval, and outcome evidence rather than informal hopes

## Stream 9 — Fused control-plane review

Goal: stop making future implementers manually merge doctor health, readiness, and support-review debt every session.

Deliverables:
- control-plane report command
- support-record parser and review queue
- per-surface fused summary rows
- capture/history flow for freezing one fused operator snapshot

Exit condition:
- a new session can identify the best runtime next action and the best support-truth next action from one report
