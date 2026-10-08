# Rev0943 — recent-files owner contract row

## What changed

Rev0943 moves recent-files rollback from raw runtime list/authority sidecar
rewrites into an editor-owned retained-path owner seam and makes that seam visible
in the generated effect/resource contract.

`RecentFilesRegisterEntry` and `RecentFilesRegisterSnapshot` are now the
editor-owned value objects for authority-stamped recent-file MRU rows.
`Editor.snapshot_recent_files_group_state()` /
`restore_recent_files_group_state()` and
`Editor.snapshot_recent_files_generation_state()` /
`restore_recent_files_generation_state()` capture, clear, and restore retained
path rows while preserving unrelated trusted/user rows. `plugin_runtime.py` uses
those owner methods for runtime-group cleanup, generation cleanup, and broad
registration restore before falling back to the legacy raw `recent_files` /
`recent_files_authority` path for alternate embedders.

The generated effect/resource contract now includes `ed.recent-files-register`
as an `editor-owner` row with `cap.recent-read`, `cap.history-clear`, and
`cap.persist` as the authority-bearing capabilities. `mxaudit --check` reports
and enforces `recent_files_owner_snapshot_present`, and `tools/mxeffects.py
--json --check` validates the owner method facts alongside the active-search,
prompt-history, and high-risk host-effect rows.

## Why this was next

Recent files looked like a boring MRU list, but it was the next concrete
survivor after active search and prompt history. It retains filesystem paths,
carries a per-row authority sidecar, may be persisted, and can later steer UI
file selection or disclosure. That makes it a retained path-history resource,
not a cosmetic list.

Before this change, runtime cleanup and broad registration restore still knew how
to snapshot and rewrite `recent_files` and `recent_files_authority` directly.
That split policy between the editor, which understands MRU limits, persistence,
and recent-file capabilities, and the runtime, which should only know that a
resource family has an owner seam. Rev0943 removes that primary-path duplicate
knowledge and leaves raw sidecar handling only as a defensive fallback for
alternate editor hosts or old snapshots.

## Online research used

OWASP API4:2023 treats resource limits as a host boundary problem across CPU,
memory, storage, network, operation counts, and provider costs. The Micromax
lesson remains that retained host-visible effects should have bounded, named
owners and cleanup/recovery behavior instead of living as ambient mutable state:
https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/

CWE-200 and CWE-359 are useful framing for recent-file paths: path MRU rows can
expose sensitive information or private personal/environment information even
when no file bytes are read. The owner row therefore names this as retained path
history authority rather than treating it as harmless UI state:
https://cwe.mitre.org/data/definitions/200.html
https://cwe.mitre.org/data/definitions/359.html

The WebAssembly Component Model/WIT resource model remains the best comparator
for future Micromax host boundaries: resources are explicit handles with owner
semantics, not anonymous pieces of shared process memory. Micromax is still an
in-process Python editor host, but generated owner rows should keep moving toward
that handle/owner/drop shape one concrete family at a time:
https://component-model.bytecodealliance.org/using-wit-resources.html
https://github.com/WebAssembly/component-model/blob/main/design/mvp/WIT.md

## Audit/refactor notes

This landing was intentionally code-backed:

- The editor now owns recent-file row capture/restore for runtime groups and
  plugin generations.
- Runtime group rollback, generation rollback, and broad registration restore
  call the owner seam first.
- The legacy raw list/authority path remains for alternate embedders and old
  snapshots, but the in-tree primary route is owner-routed.
- Focused regressions monkeypatch the editor owner methods to prove the runtime
  calls them for group, generation, and broad registration restore.
- `mxaudit` checks the editor value objects, owner methods, runtime routing,
  broad restore route, human output, focused tests, and generated contract row.
- `effect_contracts.py` introspects the live editor methods and capability
  registry to generate `ed.recent-files-register`.

The main waste corrected here was duplicate lifecycle policy: broad cleanup could
still rewind retained path rows by hand even though the editor already held the
state and authority model.

## Tests and audit

Focused validation for the owner route and generated contract:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_plugin_runtime_group_policy.py tests/test_effect_contracts.py tests/test_mxaudit.py
```

Contract and audit validation:

```bash
PYTHONPATH=src python tools/mxeffects.py --json --check
PYTHONPATH=src python tools/mxaudit.py --json --check
```

Full short-window validation for the archive also used `mxlint`, `mxcontext
--check`, and `make timely`.

## Remaining risk

The generated owner contract now covers recent files, active search, and prompt
history, but it is still not a complete effect/lifecycle graph. Palette MRU,
saved cursors, marks, recovery stacks, help history, document edits, durable
external effects, crash behavior, memory pressure, native code, and hostile-code
containment remain outside a unified owner contract. The next migration should
stay behavior-backed: choose the next survivor only if a route test can prove a
stale lifetime, authority clobber, retained disclosure, or rollback failure.
