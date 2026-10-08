# Test-lane isolation refactor — rev0072

## Finding

An exploratory combined runner placed the legacy behavior-witness harness and the upstream unit suite in one broader workflow. The later suite became order-dependent and stalled in the shares-test area, even though both source states passed when tested from pristine extractions.

That result was not accepted as either an upstream regression or a clean pass. The combined runner was removed from the canonical closure gate.

The likely risk boundary is shared mutable test state rather than the five patched production files: upstream unit fixtures write configuration, share databases, and temporary audio files, while the legacy witness tooling also exercises process and filesystem state. rev0072 does not claim a single proven root cause for the stall.

## Correction

`tools/probe_rev0072_upstream_unit_parity.py` now gives each state all of the following:

```text
fresh source extraction
private HOME
private XDG_CONFIG_HOME
private XDG_DATA_HOME
private XDG_CACHE_HOME
private TMPDIR
private working directory
disabled third-party pytest plugin autoload
disabled pytest cache provider
network tests not enabled
```

The unpatched and patched runs do not share a checkout or runtime directory. The patch stack is applied only to the patched checkout.

## Observed isolated result

```text
exact current 3.3.x ref: 98089ac233aa57786e8dbdc48123f6ac1c4767d8
patch files applied:       4 / 4
unpatched unit result:     58 passed, 1 skipped
patched unit result:       58 passed, 1 skipped
outcome parity:            pass
```

The gettext `msgfmt` binary is unavailable in this environment, so `test_i18n.py` is explicitly excluded in both states and recorded as an environment exclusion. The one reported skip is produced by the remaining upstream suite.

## Rule for future cube work

Do not append unrelated suites to a stateful historical harness and interpret the aggregate as one proof. Use a fresh extraction, fresh runtime namespace, explicit environment exclusions, and a process timeout for each test purpose. A timeout or order-dependent result is evidence about the harness until reproduced in an isolated lane.

## Canonical outputs

```text
tools/probe_rev0072_upstream_unit_parity.py
data/rev0072_upstream_unit_parity.csv
data/rev0072_upstream_unit_patch_apply.csv
data/rev0072_upstream_unit_parity_summary.json
evidence/rev0072-upstream-unit-parity-runtime/
```
