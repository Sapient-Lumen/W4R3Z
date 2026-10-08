# Rev0942 — prompt-history owner contract row

## What changed

Rev0942 moves prompt-history rollback from raw runtime dictionary surgery into an
editor-owned replay-history owner seam and makes that seam visible in the
generated effect/resource contract.

`PromptHistoryRegisterEntry` and `PromptHistoryRegisterSnapshot` are now the
editor-owned value objects for authority-stamped prompt-history rows.
`Editor.snapshot_prompt_history_group_state()` /
`restore_prompt_history_group_state()` and
`Editor.snapshot_prompt_history_generation_state()` /
`restore_prompt_history_generation_state()` capture, clear, and restore replayable
prompt-history rows while preserving unrelated trusted/user rows. `plugin_runtime.py`
uses those owner methods for runtime-group cleanup, generation cleanup, and broad
registration restore before falling back to the legacy raw `history` /
`history_authority` path for alternate embedders.

The generated effect/resource contract now includes
`ed.prompt-history-register` as an `editor-owner` row with `cap.history-clear`
and `cap.persist` as the authority-bearing capabilities. `mxaudit --check`
reports and enforces `prompt_history_owner_snapshot_present`, and
`tools/mxeffects.py --json --check` validates the owner method facts alongside
`ed.active-search-register` and the host-effect rows.

## Why this was next

The highest-risk unfinished seam after rev0941 was not another static registry.
It was a retained replay surface. Prompt history can hold command, search, or
other prompt text after the callback or plugin generation that created it has
returned. If cleanup/reload/unload snapshots keep poking the raw history
containers directly, policy lives in two places: the editor protects replay and
clear semantics, while the runtime still knows how to rewrite the private
sidecar.

This change makes prompt history look like the rest of the owner-migration
sequence: the runtime asks the editor owner to snapshot and restore a concrete
resource family, and the generated contract row exists only because live owner
methods, audit evidence, and focused route tests exist.

## Online research used

CWE-772 treats unreleased resources after their effective lifetime as a distinct
class of failure. The Micromax analogue here is retained replay authority: a row
can outlive the plugin generation that authored it unless the lifecycle owner
knows how to identify and release it:
https://cwe.mitre.org/data/definitions/772.html

OWASP logging guidance is a useful comparator because logs and prompt history
share a trap: both can retain sensitive, replayable, or attacker-controlled text.
The practical lesson is to keep retention, access, and cleanup rules explicit
rather than treating stored text as harmless inert state:
https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
https://owasp.org/Top10/2025/A09_2025-Security_Logging_and_Alerting_Failures/

Python's `importlib.resources.as_file()` is a small but useful lifetime pattern:
resources that need a temporary filesystem realization are scoped to a context
manager and cleaned up on exit. Prompt history is not a file resource, but the
same shape applies: the effective lifetime must be owned by the component that
understands the resource:
https://docs.python.org/3/library/importlib.resources.html

The WebAssembly Component Model/WIT resource model continues to be the strongest
north-star shape for future host boundaries: resources have owned and borrowed
handles, and ownership transfer/drop semantics are explicit. Micromax is still an
in-process Python host, but the owner row should name the host owner, capability
side, and cleanup/recovery side now:
https://github.com/WebAssembly/component-model/blob/main/design/mvp/WIT.md
https://component-model.bytecodealliance.org/design/wit.html

## Audit/refactor notes

This was deliberately implemented as a runtime refactor plus generated evidence,
not just a new doctrine note:

- The editor now owns prompt-history row capture/restore for both runtime groups
  and plugin generations.
- Runtime group rollback, generation rollback, and broad registration restore
  call the owner seam first.
- The legacy raw dictionary path remains as fallback for alternate embedders, but
  the in-tree primary path is owner-routed.
- Focused regressions monkeypatch the editor owner methods to prove the runtime
  routes through them.
- `mxaudit` checks the editor value objects, owner methods, runtime routing,
  broad fallback routing, human output, and focused tests.
- `effect_contracts.py` introspects the live editor methods and capability
  registry to generate `ed.prompt-history-register`.

## Tests and audit

Focused validation for the owner route and generated contract:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_plugin_runtime_group_policy.py tests/test_effect_contracts.py tests/test_mxaudit.py
```

Result: passed.

Contract and audit validation:

```bash
PYTHONPATH=src python tools/mxeffects.py --json --check
PYTHONPATH=src python tools/mxaudit.py --json --check
```

Result: both passed; the generated contract now reports 16 rows, including
`ed.prompt-history-register` and `ed.active-search-register`, with no validation
errors.

## Remaining risk

The generated owner contract now covers two retained/delayed resource families,
but it is still not a complete effect/lifecycle graph. Recent files, palette MRU,
saved cursors, marks, recovery stacks, help history, document edits, durable
external effects, crash behavior, and hostile-code containment remain outside a
unified owner contract. The next migration should stay behavior-backed: choose
the next survivor only if a route test can demonstrate stale lifetime, authority
clobber, retention, or rollback failure.
