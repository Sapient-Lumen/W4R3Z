# Validation guide

`tools/llmpoetry_validate.py` checks package health, not artistic success.

It verifies:

- required root files exist;
- JSON files parse;
- manifest entries match file hashes where applicable;
- original seed docs are present;
- specimen registry marks every Fable specimen quarantined;
- no poem is admitted without records;
- required schemas and registries exist.

Run:

```bash
make validate
```

A validation pass means the office can be resumed. It does not mean any poem is good.
