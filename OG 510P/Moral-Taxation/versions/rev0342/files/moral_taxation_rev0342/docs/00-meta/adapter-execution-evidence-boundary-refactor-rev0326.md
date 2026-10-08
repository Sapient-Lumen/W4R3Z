# Adapter-execution evidence boundary refactor — rev0326

Active revision: rev0326. Codename: `adapter-execution-evidence-boundary-refactor`. Generated: 2026-06-18T14:14:00Z.

## What changed

Rev0325 could name the implementation adapters required before action. Rev0326 adds the next checked boundary: `tools/execute_decision_adapters.py` validates an external evidence bundle against those adapter packets and blocks finalization when evidence is missing, incomplete, or affirmatively changes the result.

This is deliberately not a live-law database and not a fiscal model runner. The archive now distinguishes three states that had been easy to blur:

1. the cube requires a current-law, jurisdiction, model, floor-delivery, or no-go check;
2. an outside system or human has supplied evidence for that check;
3. the evidence validates the adapter or blocks finalization.

## Runtime chain

`facts -> candidate routes -> selected profiles -> claim packets -> precedence order -> final disposition -> decision adapters -> adapter execution evidence validation`

## New tools

- `tools/execute_decision_adapters.py` validates adapter evidence bundles keyed by adapter ID or adapter-specific lookup keys.
- `tools/audit_adapter_execution.py` proves the execution boundary across all active golden cases.

## Runtime guarantees

Adapter-execution runtime status: decision_adapter_execution_evidence_checked
Adapter-execution answer packets: 122
Adapter-execution adapter checks: 1724
Empty-evidence missing adapters: 1724/1724
Empty-evidence blocked adapters: 1724/1724
Empty-evidence can-finalize answers: 0/122
Empty-evidence cannot-finalize markers: 1724/1724
Synthetic-evidence satisfied adapters: 1724/1724
Synthetic-evidence can-finalize answers: 122/122
Adapter-execution type counts: current_law_refresh_adapter: 295, floor_delivery_adapter: 388, jurisdiction_scope_adapter: 570, no_go_threshold_adapter: 52, quantitative_model_adapter: 419
Empty-evidence status counts: blocked_missing_external_evidence: 1724
Synthetic-evidence status counts: executed_evidence_satisfies_adapter: 1724

## Substantive correction

The risky failure mode was subtle: once the cube could emit adapter requirements, a downstream reader might treat those requirements as if they had already been executed. Rev0326 makes that impossible in the runtime surface. With no evidence bundle, every adapter returns `blocked_missing_external_evidence`; finalization remains blocked.

When evidence is provided, the executor checks required fields and required outputs by adapter type. Current-law evidence must include source, retrieval method, authority locator, jurisdiction, effective date, result status, reviewer/system, and whether the claim is supported. Quantitative, delivery, and no-go evidence must include model identity, version, input hash, assumptions, run time, uncertainty method, and every required output named by the adapter.

## Refactor/audit target

This pass does not add route records, sources, or axis values. It refactors the adapter layer by separating requirement generation from evidence execution. `tools/synthesize_disposition.py` now marks adapter execution as required and names `tools/execute_decision_adapters.py` as the execution tool. `tools/run_semantic_audits.py` and `Makefile` include the adapter-execution audit in the package path.

## Remaining risky frontier

The next frontier is to attach real evidence producers without embedding stale outputs: current-law fetch adapters should produce evidence bundles with locators and dates, and model adapters should produce reproducible output bundles with assumptions, uncertainty, and input hashes. The archive should keep validating those bundles rather than storing perishable answers as doctrine.
