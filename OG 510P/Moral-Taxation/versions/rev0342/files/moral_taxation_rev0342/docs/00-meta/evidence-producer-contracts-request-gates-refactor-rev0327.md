# Evidence-producer contracts and request gates refactor — rev0327

Active revision: rev0327. Codename: `evidence-producer-contracts-request-gates-refactor`. Generated: 2026-06-18T14:56:00Z.

## What changed

Rev0326 made adapter execution depend on external evidence. Rev0327 makes that boundary harder to fake: evidence now has to identify a registered producer contract, and every adapter check can be converted into a producer-specific evidence request.

This deliberately avoids turning the archive into a stale-law database or a repository of old model outputs. The archive stores the producer contract and request shape. Perishable legal lookups, jurisdiction determinations, floor-delivery checks, no-go reviews, and quantitative model outputs remain external evidence bundles validated at runtime.

## New/refactored tools

- `tools/plan_adapter_evidence_requests.py` converts answer-packet adapter checks into external evidence request packets.
- `tools/audit_evidence_producer_contracts.py` audits producer contracts, request coverage, registered-producer satisfaction, and invalid-producer blocking.
- `tools/execute_decision_adapters.py` now requires producer metadata and a registered producer contract before supplied evidence can satisfy an adapter.

## Runtime chain

`facts -> candidate routes -> selected profiles -> claim packets -> precedence order -> final disposition -> decision adapters -> adapter execution evidence validation -> registered evidence-producer request gates`

## Runtime guarantees

Evidence-producer runtime status: evidence_producer_contracts_checked
Evidence-producer contracts: 5
Adapter types covered: 5/5
Evidence requests planned: 1724/1724
Evidence requests with producer coverage: 1724/1724
Evidence requests with lookup keys: 1724/1724
Evidence requests external-only: 1724/1724
Registered-producer synthetic evidence satisfied adapters: 1724/1724
Invalid-producer evidence blocked adapters: 1724/1724
Invalid-producer can-finalize answers: 0/122
Adapter-execution registered producer results: 1724/1724

Producer coverage by adapter type:

- `current_law_refresh_adapter`: current-law authority retrieval, 295 requests.
- `jurisdiction_scope_adapter`: jurisdiction/effective-date/conflict resolution, 570 requests.
- `quantitative_model_adapter`: fiscal, incidence, distribution, enforcement-error, and cost modeling, 419 requests.
- `floor_delivery_adapter`: take-up, accessibility, fallback, and nonforfeiture delivery checks, 388 requests.
- `no_go_threshold_adapter`: nonpricing/noncompensable-harm threshold review, 52 requests.

## Substantive correction

The risky failure mode after rev0326 was that any sufficiently shaped JSON could appear to satisfy the adapter executor. That would invite fabricated or stale evidence. Rev0327 closes that gap: the executor requires `producer_id`, `producer_contract_version`, `evidence_kind`, `created_at`, and `producer_mode`; it checks those fields against `docs/00-meta/evidence-producer-contracts.json`; and it blocks unregistered producers across all 1724 adapter checks.

## Refactor/audit target

This pass does not add route records, sources, or axis values. It refactors the implementation frontier into a checked producer/request boundary:

`adapter_checks -> evidence_request_plan -> external producer bundle -> registered-producer executor validation`

That is the substantive anti-bureaucracy move: more runtime enforceability, not more doctrine.

## Remaining risky frontier

The next frontier is real producer execution: implementing at least one current-law retriever and one quantitative model runner that emit evidence bundles with locators, dates, input hashes, assumptions, uncertainty, and explicit block/satisfy statuses, while keeping those outputs outside the archive's durable doctrine.
