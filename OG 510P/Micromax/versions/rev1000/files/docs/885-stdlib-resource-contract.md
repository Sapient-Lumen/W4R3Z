# Rev0927 — bounded bundled-stdlib resource contract

## What changed

This revision classifies Micromax's boot stdlib as a trusted bundled package
resource with an explicit resource contract instead of leaving it as a direct
`VM._load_stdlib()` implementation detail.

`src/micromax/stdlib_resource.py` now owns the stdlib package-resource seam:

- resource identity: `micromax/stdlib/core.mx`;
- trust class: `bundled-package-resource`;
- authority note: package-local, not workspace/plugin filesystem authority;
- startup byte ceiling: 64 KiB;
- reader: `importlib.resources.files(...).joinpath(...).open("rb")`;
- read shape: at most `max_bytes + 1` before UTF-8 decode/eval;
- provenance: byte count and SHA-256 for the actual shipped bytes.

`src/micromax/vm.py` now imports that seam, keeps a `stdlib_resource` health row,
and reports the contract through `stdlib_health()` / `startup_health()`. Missing
resources still degrade by default and fail closed under `strict_stdlib=True`.
Oversized resources are reported as `stdlib-resource-limit`, with the static
contract attached to startup diagnostics.

This is a refactor, not a new sandbox. It removes package-resource reading from
the VM's broad startup method and makes the trusted/local boundary inspectable
from tests, tooling, and future hosts.

## Why this was next

Rev0926 named stdlib resource loading as the remaining apparent filesystem
survivor that should be classified before another broad effect table. The old
code used `importlib.resources.files("micromax").joinpath("stdlib/core.mx").read_text(...)`
inside `VM._load_stdlib()`. That was mostly correct authority-wise because the
source is bundled package data, but it was ambiguous in audits: it looked like a
bare read, had no byte budget, and did not record the bytes actually evaluated at
startup.

The corrected invariant is sharper:

> bundled stdlib startup is trusted package I/O with a small explicit byte
> budget and provenance row; workspace/plugin source loading remains governed by
> the existing host load policy and contained source-read seams.

This avoids wasting future cloudtainer turns rediscovering the same path as a
bug while still admitting that package resources are real bytes and should have a
resource budget.

## Online research used

Current Python `importlib.resources` documentation says package resources can be
opened/read in binary or text mode, that `files(anchor)` returns a `Traversable`
container, and that `open_binary()` is effectively
`files(anchor).joinpath(...).open('rb')`. It also warns that passing untrusted
inputs to the module is unsafe and that `as_file()` is only needed when a real
filesystem path is required. Source:
https://docs.python.org/3/library/importlib.resources.html

Python's resource ABC documentation describes package resources as binary
artifacts shipped within a package and emphasizes that resource access should be
abstract across filesystem-versus-zip storage. That supports treating the boot
stdlib as package data, not workspace path authority. Source:
https://docs.python.org/3/library/importlib.resources.abc.html

OWASP API4:2023 continues to frame unrestricted resource consumption around
missing or inappropriate limits on execution time, memory, file descriptors,
processes, upload/file sizes, operation counts, and records per page. The lesson
for this local startup seam is simple: even trusted package data should have a
small declared byte ceiling rather than being read as unbounded text. Source:
https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/

## Audit/refactor notes

The refactor deliberately separates concerns:

- `VM` decides whether stdlib loading is enabled, records degraded startup, and
evaluates the decoded source under the stable `<stdlib/core.mx>` pseudo-filename.
- `stdlib_resource` owns how the bundled resource is found, bounded, decoded, and
fingerprinted.
- `tools/mxaudit.py` now hard-checks `stdlib_resource_contract_present`, including
that the reader uses a binary `open("rb")`, reads only `max_bytes + 1`, records a
SHA-256, exposes `resource_contract`, avoids direct `importlib_resources.files`
inside `vm.py`, and has oversize-budget regression coverage.

This is one of the few times adding a small module is less bureaucratic than
leaving code in the main VM: it makes the authority category visible where the
bytes are loaded instead of burying it in a 1,800+ line file.

## Tests and audit

Focused stdlib startup/resource validation:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_stdlib_startup.py
```

Result: 6 passed.

Packaging validation:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_packaging_stdlib.py
```

Result: 1 passed.

Audit validation:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxaudit.py
PYTHONPATH=src python tools/mxaudit.py --check
```

Result: 2 passed, and `mxaudit --check` passed with
`stdlib-resource-contract=True` in the human output.

Revision-index/docs hygiene validation:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_revision_index.py tests/test_docs_living_hygiene.py
```

Result: 4 passed.

Two broader combined pytest commands were also attempted before the commands were
split. Each emitted progress dots, then hit the outer cloudtainer command timeout
before a final pytest summary. The split focused commands above are the completed
validation evidence for this archive.

## Remaining risk

The boot stdlib is still evaluated in-process during VM startup; the new contract
bounds and fingerprints the package bytes but does not sandbox stdlib code.
Because stdlib is project-owned package data, that is acceptable for the current
reference VM, but future third-party package/resource loading should not inherit
this trust class by default.

The next high-leverage runtime work is still to move one plugin-owned resource
family into a typed owner. Timers are the strongest candidate because they
combine deferred execution, unload/revoke behavior, stale-reference risk, and
resource budgeting. The success criterion should be a single owner with
commit/abort semantics and headless/audit evidence, not another registry essay.

Release provenance also remains unfinished beyond archive member hashes. The next
small repair there is a verifier or package-inspection lane that consumes the
rev0926 provenance instead of merely embedding it.
