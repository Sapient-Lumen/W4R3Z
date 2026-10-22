# Dependency gate corpus v0

## Purpose
This deterministic corpus settles Steward's first dependency-gate proof slice. It checks that dependency declarations, dependency condition checks, lifecycle dependency gates, and fallback/degraded-mode witnesses remain weak, scoped evidence rather than topology authority, start-order authority, readiness, serving, failure, operation execution, work completion, or effect success.

## Packet families
- `ST-DEPSPEC v0` — dependency declaration/specification witness.
- `ST-DEPCHECK v0` — dependency condition/check witness from one bounded vantage.
- `ST-DEPGATE v0` — lifecycle request dependency-gate decision witness.
- `ST-DEPFALLBACK v0` — fallback or degraded-mode witness selected because of dependency condition.

## Corpus
The generated corpus is `corpora/dependency-gate-corpus-v0.jsonl`.

## Executable checker
The checker is `../../tools/steward_dependency_gate_harness.py`.

## Required acceptances
- A hard `requires` dependency declaration can be recorded without becoming topology authority or start order.
- A soft dependency preference can be recorded without blocking lifecycle action.
- An available dependency check can be used as a bounded condition witness.
- A degraded dependency check can support an explicit degraded gate only when paired with a fallback witness.
- A dependency gate may allow, block, or degrade a request without executing the request.

## Required rejections
- Dependency declaration as topology authority.
- Dependency declaration as start order, readiness, serving, admission, work completion, or effect truth.
- Available dependency check as subject readiness or serving.
- Stale known dependency checks.
- Fallback activation as repair, rollback success, readiness, serving, work completion, or effect success.
- Dependency gate as operation execution.
- Allow gate citing unavailable or stale hard dependency checks.
- Degrade gate without a known active fallback witness.
- Gate/check/spec mismatch.
- Duplicate dependency-gate ids with different canonical bytes.
