# Rev825 hostcall and core primitive registry refactor

Rev825 takes the registration seam that was called out after rev824 and makes it concrete without rewriting handler behavior.

## What changed

- Added `src/micromax_editor/editor_hostcall_registry.py`.
- Moved editor hostcall names and handler bindings out of the bottom of `micromax_bridge.py` into an auditable table.
- Added `STATIC_EDITOR_HOST_FEATURES` so always-present editor feature advertisement is no longer hidden inside the bridge body.
- Added `src/micromax/core_registry.py`.
- Moved core primitive names, docs, and stack effects out of the tail of `core.py` into an auditable table.
- Added focused registry tests for hostcall uniqueness, static feature policy, core primitive uniqueness, and preservation of the effective `see` documentation.

The implementation bodies still live where they were. The refactor is table extraction, not behavioral redesign.

## Audit findings fixed

The bridge previously advertised three capability-controlled features statically:

```text
ed.hook-read
ed.hook-fire
ed.keymode-read
```

Those features are unsafe/optional surfaces controlled by `cap.hook-read`, `cap.hook-fire`, and `cap.keymode-read`. Rev825 removes them from static advertisement and reconciles capability-controlled feature strings through `refresh_vm_features(...)` after the hostcall registry is installed. They now report unavailable through `host.feature?` until the matching option is enabled.

The core primitive tail also registered `see` twice. The second registration was the one that actually survived in the VM dictionary. Rev825 removes the duplicate by deduplicating the table to the effective registration and preserves the final doc string:

```text
( -- ) parse next name; print definition
```

## Why this matters

Before this pass, reviewing the editor hostcall surface meant scanning thousands of lines of bridge handler bodies and then separately checking static feature strings. Before this pass, reviewing core primitive names meant reading the tail of `core.py` and noticing duplicate overwrites manually.

Now these surfaces have small tables that can be tested directly:

```text
EDITOR_HOSTCALL_REGISTRY
STATIC_EDITOR_HOST_FEATURES
CORE_PRIMITIVE_REGISTRY
```

That should make future porting and authority audits cheaper, while leaving the behavior-heavy implementation code in place.

## Validation in rev825

```bash
python tools/mxlint.py
# mxlint: ok
```

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q \
  tests/test_core_registry.py \
  tests/test_features.py \
  tests/test_editor_hostcall_registry.py \
  tests/test_editor_capabilities_registry.py \
  tests/test_editor_hook_authority.py \
  tests/test_editor_keybinding_authority.py \
  --durations=10
# 42 passed
```

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q \
  tests/test_editor_main_cli.py \
  tests/test_installed_runtime_resources.py \
  tests/test_mxcontext.py \
  tests/test_revision_index.py \
  tests/test_docs_living_hygiene.py \
  --durations=10
# 29 passed
```

A broader `tests/test_portability_suite.py` run was attempted separately. It passed the early/default corpus tests but exceeded the cloudtainer command window around the reverse-user metadata CLI test, so rev825 does not claim a complete portability-suite pass.

## Remaining risk

The hostcall and primitive tables are extracted, but the handler bodies are still large closures. The next safe step is to split handler families only when the surrounding tests identify a coherent behavior cluster. For editor work, the command-dispatcher body remains the highest-value registration-adjacent seam.
