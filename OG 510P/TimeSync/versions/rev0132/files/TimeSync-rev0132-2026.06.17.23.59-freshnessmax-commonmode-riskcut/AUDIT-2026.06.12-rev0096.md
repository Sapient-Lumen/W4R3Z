# TimeSync rev0096 audit — transport envelope temporal boundary and semantic-vector runner

## Finding 1 — envelope `sent_at` was only policy text

The adapter catalog already said transport freshness comes from the semantic payload and that fixture/API/relay transport timestamps must not become TimeState freshness. That was correct, but incomplete: a transport envelope could still carry a payload whose semantic event timestamp was after the envelope `sent_at`. The payload might pass its own schema and semantic checks, while the carrier artifact implied it had been sent before the facts it contained existed.

rev0096 adds `tools/transport_envelope_temporal.py` and wires it into `check_transport_envelope`. The helper checks only event/observation/publication timestamps such as `assessment_time`, `checked_at`, `evaluated_at`, `observed_at`, `responded_at`, `generated_at`, `issued_at`, `exported_at`, `record_created_at`, `last_discipline`, and `last_correction`. It intentionally ignores window bounds such as `not_after`, `current_use_not_after`, and `expires_at`, because those may legitimately point into the future.

## Finding 2 — transport sent time must not become freshness

The fix is deliberately narrow. Passing the new helper does not make `sent_at` provenance, freshness, actionability, profile evidence, or profile-binding material. It only says the envelope did not claim to be sent before semantic events already present in the payload.

## Finding 3 — semantic-vector execution was validator plumbing

`tools/validate_archive.py` still contains too many semantic families, but vector execution mechanics were especially removable: duplicate vector IDs, fixture coverage, JSON-load failure expectations, schema/semantic pass/fail accounting, and expected-error matching do not need to live beside profile and evidence logic.

rev0096 adds `tools/semantic_vectors.py` and moves that runner logic behind callbacks. The validator now supplies `load_json`, `schema_validate`, `semantic_validate`, catalog index, and adapter index. This reduces validator line count even though rev0096 adds a new transport-envelope semantic check family and three new negative vectors.

## New negative fixtures

```text
examples/negative/transport-discovery-result-freshness-after-sent-invalid.json
examples/negative/transport-local-assessment-after-sent-invalid.json
examples/negative/transport-retained-export-after-sent-invalid.json
```

All three are derivation-checked in `tests/fixture-derivations.yaml`.

## Remaining risk

FT-0090 should stay open, but it should now bias toward small executable extractions and fixture-family derivations. The next risky area is not a new conceptual registry; it is accidental drift between copied fixtures, validation branches, and transport/integrity wording.
