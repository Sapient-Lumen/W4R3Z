# AAR/ADCC Draft Specs (v0.19)

These are speculative, operator-first specs for a local, CLI-driven multi-agent system where:
- You broadcast a start prompt to 3–5 LLM CLI terminals.
- A Rust router maintains a strict Working Set (WS) + a permissive Ledger.
- A separate MetaLLM (outside the worker group) steers the router via CLI commands and evolves configs/plugins between runs.

## Core primitives
- **AAR (Adaptive Attention Router):** builds per-agent views (prompt segments) from WS + deltas + budgets.
- **ADCC (Adaptive Deliberation Control Conduit):** governance (modes, leases, voting, CE lifecycle, canonicalization).
- **MetaLLM Steward:** observes telemetry/ledger, issues small reversible CLI actions, proposes config/plugin diffs.

## Reading order (recommended)
1. 00_charter.md (invariants, big picture, what success looks like)
2. 01_bcc_wire_format.md (Boot Compression Contract; how agents must speak)
3. 02_ws_object_schema.md (what goes into the WS)
4. 03_aar_spec.md + 04_aar_hotness_scoring.md + 05_view_budget_profiles.md
5. 06_adcc_governance.md + 07_vote_catalog.md + 08_leases_and_patch_policy.md
6. 09_bandwidth_adapter_plugin.md + 10_plugin_surface_and_telemetry.md
7. 11_router_cli_reference.md + 12_router_cli_grammar_and_errors.md
8. 13_metallm_steward_spec.md + 14_metallm_prompt_and_playbook.md
9. 15_streaming_bridge.md + 16_structured_output_ladder.md
10. 17_exec_request_protocol.md + 18_verifier_registry_contract.md
11. 19_bootstrap_templates.md + 20_golden_path_state_machine.md
12. 21_experiment_matrix.md + 22_failure_modes_and_interventions.md + 23_open_questions_and_forks.md
13. 24_blackboard_contract_net_mapping.md + 25_references.md

## Kernel invariants (do not change lightly)
- Human priority `H0` is always visible first in every view.
- WS is strict/structured; unstructured text lives in the Ledger only.
- Cursor+deltas: agents read state via `CURSOR` and `DELTA(CURSOR)`; full refresh is rare.
- Mandatory channel cannot be muted (mode/strictness changes, lease changes touching your scope, certified CE, selected patch).
- Certifiable counterexamples require **witness + repro recipe + expected signal**.
- Canonical changes require **patch summary** (S1+), preferably a git diff.
- Outputs are **anytime packets**: `@CTRL` first and early; everything else optional.

## What this is (and is not)
- This is an operator-friendly router and a set of protocols to stretch value out of 1 “turn” that contains many reads/writes.
- This is not a fully autonomous system; the human gearbox and MetaLLM are first-class controllers.

## Added in v0.19
- 26_capability_handshake.md
- 27_global_hot_promotion_table.md
- 28_ws_compaction_policy.md
- 29_broadcast_ops_guidance.md
- 30_local_structured_output_integration.md
