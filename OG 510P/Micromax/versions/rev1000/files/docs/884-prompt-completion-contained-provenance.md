# Rev0926 — prompt completion contained listing and archive-member provenance

## What changed

This revision converts the prompt-completion standalone directory branch from a
bare `Path.exists()` / `Path.is_dir()` / `Path.iterdir()` / child `is_dir()` path
into the same contained directory-list seam used by editor prompt completion and
script-visible filesystem listing.

`src/micromax_editor/prompt_completion.py::path_completion_candidates()` now
always calls `list_dir_contained_bounded()` for directory observation. A positive
`timeout_seconds` still gives editor callers the killable filesystem-list worker;
`None` now means "run the contained fd-backed list synchronously" instead of
"fall back to ambient pathlib probes." Direct library callers also get a bounded
page by default: when no `scan_limit` is supplied, the function limits the
contained list to the same maximum page size it can return.

This is deliberately smaller than a new effect registry. It removes an actual
survivor that rev0925 named as the next risky branch, keeps the existing render
policy intact, and avoids multiplying worker processes for standalone tests.

The revision also lands one concrete release-provenance repair in
`tools/mkrevzip.py`. The generated `MICROMAX-CONTEXT.json` manifest inside each
revision zip now includes `archive.provenance`, a SHA-256 member manifest with:

- schema: `micromax.mkrevzip.archive-provenance.v1`;
- digest over every packaged source member path, byte count, and SHA-256;
- total file count and byte count;
- per-member `path`, `bytes`, and `sha256` entries.

The generated manifest itself is excluded from the provenance digest to avoid a
recursive hash. This does not replace signatures or supply-chain attestation, but
it makes the offline handoff archive materially easier to verify and compare
without opening every file by hand.

## Why this was next

Rev0925 left one prompt-completion survivor: standalone completion used direct
pathlib observation while editor/script paths used bounded filesystem seams. That
was safe enough only as long as every capability-sensitive path was carefully
kept out of the standalone branch. The risk was not a known exploit; it was an
architecture footgun. A future caller could reuse the pure helper and accidentally
get different authority/resource behavior than the editor path.

The safer invariant is simpler:

> prompt path completion observes directories through one contained list helper;
> the caller chooses worker timeout and containment policy, not a separate ambient
> implementation.

The archive-provenance repair addresses another recurring handoff risk. The
project has good test/evidence manifests, but the zip itself was still mostly a
named bundle. Adding member digests to the embedded context manifest turns the
archive into something a later cloudtainer can sanity-check by content, not only
by filename convention.

## Online research used

Current Python `pathlib` documentation describes `Path.exists()`, `Path.is_file()`,
and `Path.is_dir()` as high-level boolean observations where false can conflate
missing, invalid, inaccessible, and wrong-kind states; it also notes that these
helpers normally follow symlinks unless told otherwise. That reinforces keeping
policy-relevant path observation behind Micromax's contained stat/list/read
seams instead of rebuilding truth from bare booleans. Source:
https://docs.python.org/3/library/pathlib.html

Python's `subprocess` timeout documentation still says `run(..., timeout=...)`
kills and waits for the child after `communicate()` times out, while warning that
initial process creation may not be interruptible on many platform APIs. This
continues to support narrow worker usage and avoiding one worker per completion
row. Source: https://docs.python.org/3/library/subprocess.html

Python's `concurrent.futures` documentation for 3.14 documents result timeouts
as wait limits and separately exposes `ProcessPoolExecutor.terminate_workers()` /
`kill_workers()`. The design lesson is still that timeout observation and
execution teardown are different concepts; Micromax should keep blocking
filesystem work in a process-owned seam when it claims a killable timeout.
Source: https://docs.python.org/3/library/concurrent.futures.html

OWASP API4:2023 frames unrestricted resource consumption as missing limits over
execution time, memory, files, processes, payload size, and operation count. The
prompt-completion change is an editor-local case of the same concern: a common
interactive helper should not be able to walk or classify an arbitrarily large
user-controlled directory via an unbounded alternate branch. Source:
https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/

WASI's public capability guidance remains the best long-term north star: programs
start without ambient I/O and receive explicit capabilities. Micromax is not a
WASI host today, but the local invariant is the same shape: no separate ambient
filesystem path just because the caller is "standalone." Sources:
https://wasi.dev/ and https://github.com/WebAssembly/WASI/blob/main/docs/Capabilities.md

## Audit/refactor notes

The direct branch removal changed the audit contract. `tools/mxaudit.py` now
expects `prompt_path_completion_scan_budget` to prove all of these facts:

- the helper still accepts `scan_limit`;
- it derives `contained_limit` from the scan cap or return page size;
- it calls `list_dir_contained_bounded()`;
- the prompt-completion module no longer contains the old direct `Path.iterdir`,
  `base.exists()`, or `child.is_dir()` branch; and
- editor callers still pass the VM scan budget and timeout into path completion.

The release-hygiene audit now also reports and checks
`mkrevzip_provenance_present`, backed by code and tests for archive member rows,
provenance digest generation, and embedding in the archive manifest.

This is a small audit refactor, but it is intentionally code-adjacent: the audit
predicate changed because the implementation boundary changed, not because a new
prose doctrine was added.

## Tests and audit

Focused prompt-completion validation:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_prompt_completion.py
```

Result: 17 passed.

Focused script-context completion validation:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_script_context_fs_caps.py::test_script_created_command_prompt_later_tab_needs_fs_list_cap tests/test_editor_script_context_fs_caps.py::test_script_command_prompt_path_completion_uses_vm_scan_budget tests/test_editor_script_context_fs_caps.py::test_script_command_prompt_path_completion_refuses_symlink_escape
```

Result: 3 passed.

Archive provenance validation:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mkrevzip.py
```

Result: 7 passed.

Audit validation:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxaudit.py
PYTHONPATH=src python tools/mxaudit.py --check
```

Result: 2 passed, and `mxaudit --check` passed with
`path-completion-scan-budget=True` and `mkrevzip provenance present=True` in the
human output.

A combined prompt/script/mkrevzip/mxaudit pytest command was also attempted in
one shell. It emitted progress dots through the selected tests but hit the outer
cloudtainer command timeout before printing the final pytest summary. The same
selected tests passed when split into the focused commands above; this note is
kept to avoid overstating the combined command as a completed run.

## Remaining risk

This is still an in-process application-level capability boundary, not hostile
plugin containment. `path_completion_candidates()` now uses the contained list
helper everywhere, but standalone callers without a positive timeout still run
that helper synchronously. That is acceptable for local pure/helper tests and
simple non-hostcall use; editor callers remain responsible for passing the VM
filesystem-list timeout and any containment root.

The next best runtime work is not another broad table. Classify trusted bundled
stdlib resource loading separately from workspace/plugin authority, then choose
one plugin-owned family—timers, prompt/history rows, or macro slots—and move it
toward a typed owner with commit/abort, stale-reference, unload/revoke, and
headless evidence behavior.

The new archive-member provenance is content integrity metadata, not a signature,
lockfile, SBOM, CI attestation, or package-version policy. It makes future
revision zips easier to audit; it does not prove where the zip came from.
