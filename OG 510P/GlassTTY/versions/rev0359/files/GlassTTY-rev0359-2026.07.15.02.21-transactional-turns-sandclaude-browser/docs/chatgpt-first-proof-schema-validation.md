# ChatGPT first-proof schema validation

`schemas/chatgpt-first-proof-bundle.schema.json` is the structural contract for `bundle-manifest.json`. It is deliberately stricter than a free-form capture folder, but it is still only a structural precheck. Semantic proof acceptance remains in the schema v20 evaluator.

Run it after the artifact ledger says the evidence pack is evaluator-ready:

```bash
python scripts/chatgpt-first-proof-schema-validation.py validate \
  --input validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/bundle-manifest.json \
  --output-dir validation/latest/chatgpt-first-proof-schema-validation \
  --pretty
```

Use `--require-ok` when a CI or operator checklist should fail closed.

The generated `bundle-schema-validation.json` records the input hash, schema hash, validator, error count, and compact JSON-path diagnostics. A passing schema report is required before bundle audit and evaluator review, but it never widens support claims.
