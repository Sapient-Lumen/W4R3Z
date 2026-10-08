# 64 — Config Proposal Protocol (Plugins, Not Kernel) (v0.19)

You want the system to evolve, potentially driven by LLMs.
But letting agents rewrite the kernel is a complexity and failure amplifier.

This doc defines the low-hanging alternative:
- agents can propose **config/plugin changes**
- MetaLLM/human can apply them
- kernel invariants remain stable (50_)

## 1) Proposal object: CFG#
CFG# is a structured config change proposal.
Fields:
- `target`: budgets|weights|promotion|exploration|verifiers|leases|views
- `change`: minimal diff (JSON patch or key/value set)
- `expected_effect`: one line
- `rollback`: one line
- `evidence_plan`: what would show it worked (telemetry / E#)

## 2) Why this helps
- lets agents “modify the system” without code edits
- makes changes reversible
- keeps the kernel stable and testable
- prevents “spaghetti governance” from living in prose

## 3) Apply path
- Agents propose CFG# in WS (small).
- MetaLLM reviews; human can approve.
- Router applies config update and records:
  - CFG# id
  - before/after config hash
  - timestamp/cursor

## 4) Governance defaults
- CFG# are not decided by protocol elections.
- If a CFG# is urgent (parse failures), MetaLLM can recommend applying immediately.
- Otherwise, apply in the next checkpoint window.

## 5) What cannot be changed by CFG#
- kernel invariants
- view section order
- event log semantics
- cap gating rules

Plugin surface overview: see 81_plugin_api_surface_rust.md.
