# Precedence resolution and decision-order refactor — rev0323

Rev0323 targets the next risky edge after rev0322. The archive could emit source-backed claim packets, but candidate-score order could still masquerade as final decision order. That is dangerous in composite cases: no-go harm, protected-floor relief, actor accountability, source currentness, record contestability, enforcement, revenue, and proceeds rules do not have equal procedural priority.

## Substantive change

Added `tools/resolve_precedence.py`, a compact runtime resolver that consumes selected route/profile packets and emits a decision order. `tools/answer_case.py` now calls that resolver and exposes `precedence_resolution`, `precedence_order`, and a `resolve_precedence_before_disposition` answer step.

Candidate score still answers relevance. Precedence band answers what must be settled first. The resolver orders selected routes through these bands:

1. no-go or noncompensable harm before pricing or compensation;
2. release-integrity/source-currentness gates before downstream use;
3. protected floor, due process, access, and cure before collection;
4. real actor, controller, beneficiary, and burden-bearer assignment before liability;
5. record, contestability, measurement, and correction before finality;
6. penalty/liability/enforcement after floor and actor checks;
7. ordinary revenue, fee, rent, and benefit-nexus classification after gates;
8. proceeds, prefunding, public upside, and anti-supplantation after classification.

## Audit/refactor

Added `tools/audit_precedence_resolution.py`. It invokes `answer_case.py` across all active golden cases, recalculates expected precedence from the generated route-profile index, and fails release if answer packets omit the precedence step, carry stale inline labels, lose selected-route coverage, drift from the resolver, or allow lower-priority collection/pricing moves to precede higher-priority no-go/floor/actor gates.

The answer emitter no longer owns the precedence heuristic. It imports a single resolver module, so precedence is now a checked runtime layer rather than scattered answer-label prose.

## Machine result

- Precedence runtime status: precedence_resolver_invoked
- Precedence answer packets: 122
- Precedence route instances: 610
- Precedence ordered cases: 122/122
- Precedence sorted cases: 122/122
- Precedence changed candidate order: 44
- Precedence triggered-rule cases: 97
- Precedence triggered rules: 279
- Currentness gate cases: 68
- No-go gate cases: 39
- Precedence band counts: 10: 52, 15: 25, 20: 451, 30: 71, 40: 11

Triggered-rule counts:
- `actor_assignment_before_liability_collection_or_compensation`: 76
- `contest_record_and_measurement_before_finality_or_penalty`: 58
- `currentness_and_release_integrity_before_final_answer`: 7
- `floor_before_collection_fee_penalty_or_forfeiture`: 56
- `no_go_before_pricing_or_compensation`: 29
- `ordinary_revenue_classification_after_no_go_floor_and_actor_checks`: 53

## What this deliberately does not do

Rev0323 does not add routes, sources, or axes. It also does not pretend to produce final jurisdiction-specific legal advice or quantitative fiscal modeling. It closes a more immediate failure mode: confusing candidate ranking with decision priority. Final advice still needs current-law refresh, quantitative estimates where relevant, and human conflict review.

## Next riskiest frontier

The next high-value pass should move from ordered packets toward minimal final-answer synthesis: a deterministic text/JSON disposition that says which move is blocked, which move is default, what facts remain unknown, and what current-law or quantitative model check must happen before action.
