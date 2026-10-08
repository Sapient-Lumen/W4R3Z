# Rev0948 — effect contract installed help

## Why this was riskier than another owner row

The generated effect/resource contract was already executable, but it still lived
mostly in tools and revision notes.  That left the product surface stale: a user
could open installed help and inspect capabilities or security boundaries, yet
not see the generated rows that define high-risk host effects, owner methods,
budgets, and audit flags.  That is a drift risk and a session-waste risk because
every handoff had to keep restating contract truth in prose.

Current references kept the direction narrow.  MITRE [CWE-404](https://cwe.mitre.org/data/definitions/404.html) frames insufficient
resource tracking/release as a cause of resource exhaustion and confidentiality
problems.  VS Code's [Workspace Trust extension guide](https://code.visualstudio.com/api/extension-guides/workspace-trust) treats trust-sensitive
extension features as something to disable or limit until trust is granted.  The
Python [dataclasses documentation](https://docs.python.org/3/library/dataclasses.html) remains the current primary reference for the
small immutable value-object helpers used by the generated contract machinery.

## Landed change

- Added `EFFECT_CONTRACT_HELP_DOC` and
  `effect_contract_help_markdown(payload)` in
  `src/micromax_editor/effect_contracts.py`.
- Extended `tools/mxeffects.py` with `--markdown`, `--write-help-doc`, and
  `--check-help-doc` so the installed help page is generated from the same live
  payload as `mxeffects --json --check`.
- Added `docs/33-effect-resource-contract.md` to the installed help manifest and
  package data, then generated it from live registries, capability rows, owner
  methods, budgets, and audit flags.
- Extended `tools/mxaudit.py --check` so a missing, uninstalled, or stale
  generated help page fails audit integrity.
- Extended installed-runtime tests to open the generated help topic from a
  fake pip-target layout, proving the contract is visible outside a source
  checkout.

## Audit/refactor note

This is deliberately not a new static registry.  The new help page is a rendered
view of the generated payload, and the audit path compares the checked-in doc to
fresh generation.  The correction turns revision-note doctrine into a product
inspection surface while keeping the source of truth in code-backed contract
rows.

## Validation

- `python tools/mxeffects.py --markdown --check-help-doc --check`
- `python tools/mxeffects.py --json --check --check-help-doc`
- `python tools/mxaudit.py --json --check --limit 5`
- `pytest tests/test_effect_contracts.py tests/test_installed_runtime_resources.py tests/test_mxaudit.py tests/test_docs_living_hygiene.py`
- `python tools/mxlint.py`
- `python tools/mxcontext.py --check`
- `make timely`
