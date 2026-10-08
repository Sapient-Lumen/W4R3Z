> **Superseded evidence-status notice (rev0337):** This historical report treated archive-generated deterministic fixtures as implementation-grade evidence. Its implementation, promotion, or finalization counts demonstrate schema conformance only, not externally observed facts or authority. Use [the rev0337 truth-boundary report](evidence-truth-boundary-release-lineage-refactor-rev0337.md) for current status.

# Model-input source certification strict model gate refactor — rev0330

## Purpose

Rev0329 made model-input bundles explicit, but explicit fixture inputs were still too easy to mistake for implementation-grade model evidence. Rev0330 adds a source/provenance manifest boundary and strict execution gate.

The cube now distinguishes three things:

1. model adapter requirements;
2. explicit model input records; and
3. implementation-grade input-source certification.

Reference fixtures remain useful for interface and regression tests, but strict execution blocks them.

## Runtime and audit results

- Model-input source runtime status: model_input_source_manifest_generated
- Answer packets checked: 122
- Model adapter checks: 859
- Reference source records: 859/859
- Implementation-grade source records: 859/859
- Complete reference source records: 859/859
- Complete implementation source records: 859/859
- Strict no-source blocks: 859/859
- Strict reference-fixture blocks: 859/859
- Implementation-grade model adapters satisfied: 807/807
- Implementation-grade no-go adapters blocked: 52/52
- Implementation-grade external law/jurisdiction gaps still missing: 865/865
- Implementation-grade local-model can-finalize answers: 0/122
- Stale source-manifest blocks: 859/859

## Substantive change

`tools/build_model_input_source_manifest.py` creates source records keyed to model input hashes. Each source record carries a certification level, source contract id, source locator, coverage period, extraction date, freshness status, unit verification, provenance hash, and a non-doctrine warning.

`tools/execute_decision_adapters.py` now has a strict model-input-source gate. In strict mode, model evidence is blocked as `blocked_model_input_source_not_certified` unless it carries implementation-grade source proof.

`tools/run_evidence_producers.py` now propagates source-manifest proof fields into local model evidence bundles and marks whether strict source certification is required downstream.

## Anti-bureaucracy result

No new route doctrine was added. The change makes one existing runtime boundary harder to fake. It prevents a common failure mode: generated, unit-tagged model inputs being treated as adequate merely because they are explicit.

## Remaining risk

The implementation-grade manifest generated for tests is still a contract-shaped proof object, not real jurisdictional microdata, delivery-capacity evidence, or expert no-go review. The next substantive frontier is to feed this boundary with external evidence producers rather than reference fixtures.
