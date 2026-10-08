# Validation artifact inventory

`validation/latest/` is now large enough that future operators can lose time just orienting themselves inside it.

`python scripts/validation-artifact-inventory.py --pretty` generates a compact bucketed inventory of that tree.

## Current bucket taxonomy

The inventory groups files into stable operator-facing buckets instead of one long undifferentiated file list:

- `capture_bundles`
- `manual_and_forensics`
- `checks_and_tests`
- `fixture_samples_and_indexes`
- `status_and_reports`
- `other`

The goal is not archival purity. The goal is a quick answer to:

- where the frozen truth bundles live,
- where manual forensic evidence lives,
- where test/check logs live,
- and how much validation/latest sprawl exists before another bundle is added or a handoff is packed.

## Capture path

```bash
python scripts/validation-artifact-inventory.py capture --output-dir validation/latest/validation-artifact-inventory
```
