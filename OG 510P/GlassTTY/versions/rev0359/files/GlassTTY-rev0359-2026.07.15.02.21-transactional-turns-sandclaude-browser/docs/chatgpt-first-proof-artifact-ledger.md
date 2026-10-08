# ChatGPT first-proof artifact ledger

The artifact ledger is the materiality audit for the first ChatGPT plain-chat checkpoint proof. It answers a simpler question than the evaluator: are the expected files present, parseable, nonempty where applicable, and tied to one shared attempt identity?

It does not decide whether the browser proof is semantically valid. After the ledger passes, the operator still runs JSON Schema validation, the bundle-audit evidence graph, the schema v20 evaluator, and human privacy/redaction review.

## Canonical artifact-slot registry

The registry lives in `scripts/chatgpt_first_proof_artifact_ledger.py` as `ARTIFACT_SLOTS`. It is intentionally the single machine-readable list for the 30 evidence-pack slots named in the runbook and live evidence README.

Print it with:

```bash
python scripts/chatgpt-first-proof-artifact-ledger.py registry --pretty
```

## Readiness levels

`capture-ready` requires the raw capture files, slots 1-25, to exist and be parseable when they are JSON files.

`evaluator-ready` additionally requires `bundle-manifest.json`, because the schema validator, bundle audit, and semantic evaluator consume the joined manifest rather than the loose per-file capture folder.

`review-ready` additionally expects the structural schema-validation report, bundle-audit report, and evaluator report.

`publication-review-ready` additionally expects `privacy-redaction-review.md`. This does not make anything public-citable; it only proves the human redaction decision file exists.

## Command

```bash
python scripts/chatgpt-first-proof-artifact-ledger.py audit \
  --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack \
  --output-dir validation/latest/chatgpt-first-proof-artifact-ledger \
  --readiness-level evaluator-ready \
  --pretty
```

Use `--require-ready` when a CI or operator checklist should fail closed.

## What the ledger catches

- missing files in the selected readiness level;
- empty required text/markdown/image placeholders;
- JSON parse failures;
- drift where one JSON artifact carries a different `attempt_id`, `run_id`, `bundle_id`, `proof_id`, `session_id`, or `capture_id` from the rest of the pack;
- accidental assumption that a loose evidence folder is evaluator-ready before `bundle-manifest.json` exists.

## What the ledger does not catch

- stale DOM nodes;
- wrong turn witnesses;
- aggregate parent wrappers;
- wrong tab or conversation semantics beyond visible attempt-id drift;
- publication safety;
- support-claim readiness.

Those remain the jobs of `scripts/chatgpt-first-proof-schema-validation.py`, `scripts/chatgpt-first-proof-bundle-audit.py`, `scripts/chatgpt-first-proof-evaluator.py`, and the downstream privacy/support/publication gates.
