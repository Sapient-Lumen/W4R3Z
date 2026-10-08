# rev0072 current supported-branch closure

## One-command replay

From the cube root:

```bash
python tools/probe_rev0072_current_branch_closure.py \
  --source-zip auto \
  --write-data
```

Expected high-level result:

```text
status: pass
exact_current_ref_match: true
current_unpatched_fixed_regression_expected_failures_observed: 7
current_patched_fixed_regression_pass: 7
patch_apply_pass: 4
packets_current_applicable: 7
active_legacy_alias_hits: 0
```

## Filing interpretation

The exact current supported branch still lacks each proposed fixed behavior, and each exported patch/regression pair still replays. Treat the seven packets as current-applicable candidates. Do not infer severity solely from this gate; review each claim and public overlap before filing.

## Source handling

The upstream source bundle is external. `auto` accepts it only when both its SHA-256 and complete lane set match the pinned contract. Set `NICOTINE_SOURCE_ZIP` to override discovery without changing cube files.

## Isolated upstream unit parity

Run separately from the stateful historical witness harness:

```bash
python tools/probe_rev0072_upstream_unit_parity.py \
  --source-zip auto \
  --write-data
```

Expected outcome in the recorded environment is `58 passed, 1 skipped` in both the unpatched and patched states. `test_i18n.py` is excluded only when the external `msgfmt` program is absent, and that exclusion is recorded.
