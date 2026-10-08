# Evidence-producer execution and model-runner refactor — rev0328

Active revision: rev0328. Codename: `evidence-producer-execution-model-runner-refactor`. Generated: 2026-06-18T15:37:00Z.

## What changed

Rev0327 registered evidence-producer contracts and planned one evidence request per adapter. Rev0328 makes that boundary executable.

Added:

- `tools/run_evidence_producers.py` — a registered producer runner that emits adapter evidence bundles.
- `tools/audit_evidence_producer_execution.py` — an audit that validates fixture execution, local model execution, stale-evidence blocking, and jurisdiction-scope blocking.

Refactored:

- `tools/execute_decision_adapters.py` now blocks stale evidence under each producer contract's freshness policy.
- `tools/execute_decision_adapters.py` now blocks jurisdiction-scope evidence when implementation status, preemption/treaty conflict, or conflict resolution remains unresolved.
- The model producer contracts now permit local reference model execution while keeping output retention external-bundle-only.
- The no-go producer contract now permits a local threshold screen, but that screen returns `uncertain` and therefore blocks finalization rather than clearing no-go gates.

## Runtime chain

`facts -> candidate routes -> selected profiles -> claim packets -> precedence order -> final disposition -> decision adapters -> adapter execution evidence validation -> registered evidence-producer request gates -> evidence-producer runner`

## Runtime guarantees

Evidence-producer runner runtime status: evidence_producer_runner_invoked
Answer packets checked: 122
Adapter checks: 1724
Interface-fixture evidence produced: 1724/1724
Interface-fixture satisfied adapters: 1724/1724
Local-model evidence produced: 859/859
Local-model external adapters skipped: 865/865
Local-model satisfied adapters: 807/807
Local-model missing external adapters: 865/865
Local-model no-go blocks: 52/52
Local-model can-finalize answers: 0/122
Stale-evidence blocked adapters: 1724/1724
Jurisdiction uncertain-scope block count: 5

Local model evidence produced by adapter type:

- `quantitative_model_adapter`: 419
- `floor_delivery_adapter`: 388
- `no_go_threshold_adapter`: 52

Local model evidence deliberately skipped by adapter type:

- `current_law_refresh_adapter`: 295
- `jurisdiction_scope_adapter`: 570

## Substantive correction

The risky failure mode after rev0327 was that registered producers existed, but the archive still lacked a reusable execution boundary. The audit itself could fabricate synthetic evidence, and the executor did not yet enforce freshness or unresolved jurisdiction-scope blocking.

Rev0328 closes that gap. The producer runner can emit evidence bundles; the executor checks those bundles; the audit proves that local quantitative/floor model output can satisfy model-style adapters, while current-law and jurisdiction adapters remain blocked without external authority evidence. No-go threshold screens are executable, but they block by default unless a registered external/human no-go review clears the threshold.

## Refactor/audit target

This pass does not add route records, sources, or axis values. It moves producer evidence generation out of audit-only helper functions and into a reusable runner. It also tightens the executor so evidence cannot satisfy adapters merely by being well-shaped, registered, and fresh-looking; freshness and jurisdiction scope are now semantic gates.

## Remaining risky frontier

The next frontier is replacing interface fixtures with real producer adapters: a current-law authority retriever that records locators and effective dates from external authority sources, and calibrated quantitative/floor/no-go model runners that accept case inputs, model inputs, assumptions, and uncertainty rather than generating reference outputs from adapter shape alone.
