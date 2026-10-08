# Rev0923 — help doc read timeout

## What changed

Help-doc navigation now reads actual markdown pages through the bounded contained filesystem read seam instead of direct `Path.read_text()` calls.

`src/micromax_editor/editor.py` adds:

- `_docs_containment_root()`
- `_read_help_doc_text()`

The following paths now use bounded filesystem observation:

- opening a help document into a protected help buffer,
- resolving explicit docs-root markdown paths,
- following relative markdown help links, and
- reading target-document heading metadata for help-link search.

The read path uses `read_file_bytes_contained_bounded()` with the docs-root containment policy, the docs per-file byte budget, and the existing VM-tunable filesystem read timeout.  Explicit CLI help paths can still opt out of docs-root containment with `allow_outside_root=True`, but they still use the bounded read helper and byte budget.

## Why this was next

Rev0921 bounded the docs catalog scan, but cataloging is only the first half of help navigation.  Opening a selected doc still did a full direct `Path.read_text()`, and link-search metadata could read a target doc the same way.  That left a surprising gap: the picker could be bounded while the apparently ordinary act of opening or searching a help link still performed an ambient filesystem read.

This is a real hot-path risk rather than a registry gap.  `help`, `helpfollow`, `helplinkpick`, and target-heading search all run inside the editor's interactive surface.  A slow remote docs path or oversized markdown file should degrade as a bounded help failure, not monopolize the session.

## Online research used

- Python's `subprocess` documentation says timeout handling kills and waits for the child process, while process creation itself may not be interruptible on all platforms.  That still supports process-owned timeout seams for blocking filesystem work.
- Python's `concurrent.futures` documentation warns about deadlocks with `ThreadPoolExecutor` tasks that wait on each other, reinforcing that running thread work is not the containment story for a wedged filesystem read.
- OWASP API4:2023 treats missing execution timeouts and missing operation/record limits as unrestricted resource-consumption risk.  Help navigation is not an HTTP API, but a user-triggered markdown read with no time or byte boundary has the same failure shape.
- CWE-400 describes uncontrolled resource consumption as failing to restrict the size or amount of resources an actor can influence; this revision narrows that exact read/metadata surface.

Sources: <https://docs.python.org/3/library/subprocess.html>, <https://docs.python.org/3/library/concurrent.futures.html>, <https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/>, <https://cwe.mitre.org/data/definitions/400.html>.

## Tests and audit

New focused regressions in `tests/test_editor_help_docs_boundary.py` cover:

- opening help docs without using `Path.read_text()`,
- explicit docs paths and relative help-follow path resolution without direct `Path.is_file()`, and
- target-heading metadata reads without direct `Path.read_text()`.

`tools/mxaudit.py --check` now hard-checks `help_doc_read_timeout_boundary`, including the bounded read helper, docs-root containment helper, bounded explicit-path stat, and the absence of the old direct help-doc read patterns.

Focused validation run for this revision:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_help_docs_boundary.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_help_docs_navigation.py tests/test_editor_helplinkpick.py tests/test_editor_help_picker_browse_budget.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxaudit.py::test_mxaudit_json_reports_repeatable_structural_signals tests/test_mxaudit.py::test_mxaudit_human_output_names_major_pressure_surfaces
PYTHONPATH=src python tools/mxaudit.py --check
PYTHONPATH=src python tools/mxcontext.py --check
PYTHONPATH=src python tools/mxlint.py
```

## Remaining risk

The docs catalog still reads only a prefix for title/summary extraction, while opening a doc reads up to the per-doc byte budget.  Very large help pages now fail boundedly rather than loading silently.  Process creation itself can still take nonzero time, matching Python's documented subprocess timeout caveat.

The next useful pass should keep retiring concrete survivors.  Candidate seams are small but still visible: optional plugin metadata existence, installed resource-root directory selection, and fallback/private markdown helpers.  Touch them only where they are hot, delayed, or capability-sensitive; avoid another broad doctrine table until the obvious host-effect survivors are gone.
