# Pending open URL owner snapshot (rev0932)

Rev0932 tackles the active-interaction owner gap named by rev0931 without
starting a broad registry pass.  The chosen slice is intentionally narrow: the
pending external-URL confirmation row used by help/cursor/command link opening.
Before this revision, runtime cleanup and rollback code in `plugin_runtime.py`
read and rewrote `_pending_open_url`, `_pending_open_url_source`, and
`_pending_open_url_authority` directly while also managing keymode/prompt/query
state nearby.  That made the URL row look like three unrelated fields instead
of one delayed-authority object.

## External check

The online check reused resource-lifetime and consumption guidance as the
practical vocabulary for this slice:

- MITRE CWE-772, Missing Release of Resource after Effective Lifetime:
  <https://cwe.mitre.org/data/definitions/772.html>
- OWASP API4:2023, Unrestricted Resource Consumption:
  <https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/>

For Micromax, the translation is not “add a bigger policy registry.”  A delayed
interaction row should have a single owner that captures, clears, and restores
all of its live state together.  If cleanup code restores only the URL but not
the source/authority, or clears authority without clearing the URL, stale
interaction prompts can survive beyond their effective lifetime.

## What changed

- Added `PendingOpenUrlInteractionSnapshot` in `editor.py` as the editor-owned
  value object for pending external-URL confirmation state.
- Added editor owner methods for group and generation snapshot/restore:
  `snapshot_pending_open_url_group_state()`,
  `restore_pending_open_url_group_state()`,
  `snapshot_pending_open_url_generation_state()`, and
  `restore_pending_open_url_generation_state()`.
- Refactored active-interaction group/generation snapshot and restore in
  `plugin_runtime.py` to call those owner methods instead of directly reading
  or writing the pending URL row.
- Reused the owner clear helper in `remove_interaction_group()` and
  `remove_plugin_interaction_generation()` so ordinary cleanup and rollback
  share the same URL/source/authority reset semantics.
- Added focused regressions that monkeypatch the editor owner methods and prove
  runtime group/generation snapshot+restore actually route through the owner.
- Extended `tools/mxaudit.py --check` with
  `pending_open_url_owner_snapshot_present=True` and human output
  `open-url-owner=True`.

## Audit/refactor value

This removes one direct field family from the riskiest active-interaction
snapshot/restore paths.  Prompt and query-replace still need the same treatment
later, but this slice proves the pattern: keep the runtime wrapper narrow, let
the editor own its delayed row semantics, and require tests plus an audit
predicate before calling the boundary real.

## Validation

Run from the repository root:

```sh
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q tests/test_plugin_runtime_group_policy.py tests/test_mxaudit.py

PYTHONPATH=src python tools/mxaudit.py --check --limit 3
```

Observed in the rev0932 cloudtainer:

- `tests/test_plugin_runtime_group_policy.py tests/test_mxaudit.py`: `41 passed, 13 warnings`
- revision-index/docs/context/audit focused selector (`tests/test_revision_index.py tests/test_docs_living_hygiene.py tests/test_mxcontext.py tests/test_plugin_runtime_group_policy.py tests/test_mxaudit.py`): `50 passed, 13 warnings`
- `tools/mxaudit.py --check --limit 3`: clean check with
  `open-url-owner=True`
- `tools/mxlint.py`: `mxlint: ok`
- `tools/mxcontext.py --check`: clean context check for rev0932

## Remaining risk

- This is one delayed interaction row, not a full interaction-owner extraction.
- Prompt and query-replace group/generation snapshots still reach through direct
  editor fields and should be next candidates only if the slice stays small.
- Broad failed-callback interaction snapshot still directly stores the whole
  prompt/qreplace/keymode/open-url/input scratch state for compatibility.
- This remains an in-process application boundary, not OS sandboxing, memory
  isolation, or a malicious-plugin containment claim.
