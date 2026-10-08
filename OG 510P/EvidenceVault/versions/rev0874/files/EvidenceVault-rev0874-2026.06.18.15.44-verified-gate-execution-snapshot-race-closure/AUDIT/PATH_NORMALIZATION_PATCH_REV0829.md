# PACT path normalization patch rev0829

Concrete normalization of PACT build-host absolute paths to shipped relative paths where the referenced target is present in the archive.

- Files changed: **3**
- References normalized: **3**
- All new relative targets exist after expansion: **true**

| File | Field | New relative value |
| --- | --- | --- |
| `sources/pact/PACT_workdir/eval_otel_to_pact_mcp5000/bundle_optin_signed/manifest.json` | `source.path` | `../otlp_synth_5000.json` |
| `sources/pact/PACT_workdir/eval_real_registry_admission_bundle/out_summary.json` | `receipt_path` | `out/registry_admission_bundle_receipt.json` |
| `sources/pact/PACT_workdir/eval_real_registry_surface_policy/out_summary.json` | `violations_sample_path` | `out/violations.json` |
