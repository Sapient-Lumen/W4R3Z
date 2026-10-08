# Query-replace all budget (rev0931)

Rev0931 returns from release hygiene to a runtime owner seam.  A single delayed
query-replace response could previously drive `qreplace all` across every
remaining match in the buffer in one foreground action.  That was not a plugin
registry problem; it was an unbounded host edit loop whose cost depended on the
current buffer, replacement size, and match count.

## External check

The online check used MITRE's current CWE entries as the guardrail vocabulary,
not as a claim that Micromax is an adversarial sandbox:

- CWE-400, Uncontrolled Resource Consumption, recommends limiting the resources
  an actor can cause a product to expend: <https://cwe.mitre.org/data/definitions/400.html>
- CWE-772, Missing Release of Resource after Effective Lifetime, frames why
  delayed/owned runtime state should not outlive the action or owner that needs
  it: <https://cwe.mitre.org/data/definitions/772.html>

For Micromax, the practical translation is simple: an interactive answer should
have a host-owned budget and a recovery path.  It should not silently become an
unbounded edit sweep just because the command is convenient.

## What changed

- Added the integer option `qreplace.max`, defaulting to `10000` replacements per
  `qreplace all` action.  `0` preserves the old unlimited behavior only as an
  explicit opt-in.
- Refactored `Editor.qreplace_all()` so it counts replacements in the current
  response, stops at the configured budget, leaves the query-replace session
  active at the next selected match, and reports a visible status message.
- Kept retry behavior boring: issuing `all` again continues from the active
  session in another bounded chunk.
- Added regressions for the budget stop/retry path and for explicit
  `qreplace.max=0` unlimited behavior.
- Extended `tools/mxaudit.py --check` with
  `qreplace_all_replacement_budget=True` and human output
  `qreplace-all-budget=True`.

## Audit/refactor value

This is deliberately not another registry or doctrine pass.  The refactor moves
one visible resource budget into the editor host itself, ties it to an existing
option owner, and makes the active-session recovery behavior testable.  The audit
predicate is a smoke alarm for the executable seam: option, helper, bounded loop,
visible stop message, and regressions must remain present together.

## Validation

Run from the repository root:

```sh
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q tests/test_editor_query_replace.py tests/test_editor_qreplace_interaction_boundary.py

PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q tests/test_mxaudit.py

PYTHONPATH=src python tools/mxaudit.py --check --limit 3
```

Observed in the rev0931 cloudtainer:

- `tests/test_editor_query_replace.py tests/test_editor_qreplace_interaction_boundary.py`:
  `22 passed`
- `tests/test_mxaudit.py`: `2 passed`
- `tools/mxaudit.py --check --limit 3`: clean check with
  `qreplace-all-budget=True`

## Remaining risk

- This is an in-process per-action edited-buffer budget, not OS containment, a
  hard wall-clock timeout, or a heap cap. Rev0975 separately bounds Linux regex
  worker address-space growth; applying accepted edits still belongs to the
  editor process.
- Very large replacements still allocate edited buffer content in the same
  Python process.
- Active interaction snapshot/restore still has raw field access in
  `plugin_runtime`; a future high-leverage slice should move one cleanup or
  snapshot path through typed owner methods rather than adding more policy prose.
