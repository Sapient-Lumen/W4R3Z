# Decision-adapter law/model gates refactor — rev0325

Rev0325 targets the riskiest frontier left after final-disposition synthesis: the archive could say what should be blocked or defaulted, but it still treated live-law checks and quantitative/model work as generic unknowns. This revision converts those unknowns into checked adapter packets.

## What changed

Added `tools/resolve_decision_adapters.py` and `tools/audit_decision_adapters.py`. `tools/synthesize_disposition.py` now calls the adapter resolver, and `tools/answer_case.py` exposes a `resolve_current_law_jurisdiction_and_model_adapters` step.

Adapter types emitted:

- `current_law_refresh_adapter` — refresh volatile or implementation-sensitive source-currentness refs before final legal advice or implementation.
- `jurisdiction_scope_adapter` — resolve jurisdiction, effective date, authority level, and conflict rule before applying a disposition.
- `quantitative_model_adapter` — estimate incidence, revenue, distribution, behavior, take-up, enforcement error, and administrative cost where the route demands it.
- `floor_delivery_adapter` — verify take-up, no-rent fallback, accessibility, language, timing, and nonforfeiture before relying on a protected-floor remedy.
- `no_go_threshold_adapter` — verify noncompensable-harm or no-go thresholds before pricing, offsetting, permitting, or compensating.

## Runtime result

Decision-adapter runtime status: decision_adapter_requirements_resolved
Decision-adapter answer packets: 122
Adapter packets: 122/122
Complete adapter answers: 122/122
Adapter route instances: 610
Adapter check recall: 1724/1724
Current-law adapter recall: 295/295
Due-soon current-law adapter recall: 15/15
Jurisdiction adapter recall: 570/570
Quantitative adapter recall: 419/419
Floor-delivery adapter recall: 388/388
No-go-threshold adapter recall: 52/52
Adapter cannot-finalize recall: 445/445

Adapter type counts: current_law_refresh_adapter: 295, floor_delivery_adapter: 388, jurisdiction_scope_adapter: 570, no_go_threshold_adapter: 52, quantitative_model_adapter: 419
Current-law review-due states: due_soon: 15, not_due_yet: 280

## Audit/refactor target

This revision deliberately avoids adding route records, axes, or doctrine memos. The refactor is a runtime boundary:

`selected routes + source-currentness registry + disposition → adapter checks + adapter cannot-finalize markers`

The decision-adapter audit recomputes adapter obligations from selected route packets and the currentness registry. It does not read case contracts, expected routes, or expected answers.

## Corrective note

The old `unknowns` language said jurisdiction-specific current-law validation and model estimates were simply not emitted. Rev0325 replaces that with explicit adapter requirements. The archive still does not perform live legal research or modeling, but it now identifies which validations are required, which sources are due soon, and which implementation gates cannot be bypassed.

## Remaining frontier

The next risky layer is adapter execution: attaching real jurisdiction/current-law fetchers and quantitative model interfaces to these adapter packets, then recording validation results without turning the archive into a stale-law database.
