# Rev0912 — cloudtainer heart audit and filesystem read timeout worker

Date: 2026-07-08

## Executive finding

The heart of Micromax is **least-authority end-user automation with a host that
can explain, bound, and recover from effects**.  The terminal editor is the
stress fixture, not the final product category.  Editing is valuable because it
forces the system to confront declarations, reversible session state, user text
edits, delayed executable work, durable state, filesystem observation, process
launches, and irreversible external effects in one small host.

The strongest thread in the repository is that it keeps turning vague safety
claims into executable seams: capability gates, restricted startup, package
fingerprints, generation-scoped stale-callback refusal, tombstoned retired
wordlists, row/byte budgets, and worker timeouts.  The weakest thread is that
those seams are still discovered one at a time instead of generated from one
host-effect lifecycle contract.

Rev0912 corrects one concrete remaining filesystem stall path.  `ed.fs-read`
already had capability/root checks, an fd-bound final read, and a VM-tunable byte
budget.  It still performed accepted file open/fstat/read work in the editor
process.  A slow special file, remote filesystem, or wedged read could freeze the
host before the byte budget or VM result budget could help.  This revision routes
`ed.fs-read` through a VM-tunable killable worker while preserving the existing
byte and containment checks.

## What is missing

### 1. One executable effect-lifecycle matrix

The repository needs a generated table, backed by code metadata and audit checks,
for every public hostcall and every owned resource family.  Each row should name:

- effect class;
- capability and trust precondition;
- provenance key and ownership handle;
- argument, output, row, byte, time, and process budgets;
- staged, committed, persistent, reversible, or irreversible status;
- load, callback, reload, unload, revoke, timeout, crash, and restart behavior;
- public stability tier and schema version.

Without this matrix, every new helper risks becoming another sidecar-specific
patch.  The cloudtainer has been good at fixing survivors, but the repeated
shape of the fixes proves the architecture is still missing an owner map.

### 2. A small versioned extension surface

Micromax should not freeze the current `Editor` object as its plugin API.  The
right next shape is a tiny stable hostcall tier, a visible experimental tier, and
internal helpers that plugins cannot depend on.  The host-effect matrix should be
the source that generates plugin-facing reference docs, audit coverage, and later
process/Wasm adapter interfaces.

### 3. Contract-backed extraction from `Editor`

`Editor` remains the gravity well: thousands of lines, hundreds of methods, and
many authority sidecars in one mutation namespace.  A rewrite would likely lose
hard-won behavior.  The safer path is to extract one effect owner only after the
matrix states its handles, lifecycle rules, failure modes, and tests.  Each
extraction should reduce measured `Editor` responsibility rather than create a
forwarding facade.

### 4. Ordinary release provenance

The repo has strong local handoff runners and a short-window release lane.  It
still lacks the boring release guarantees that make evidence portable: dependency
locks, small hosted CI, package inspection, archive digests, and an explicit
policy connecting archive revision numbers with package versions.

### 5. Documentation compaction as real progress

The docs are not bad; the storage model is wasteful.  `mxaudit` now reports 849
doc files, 68,133 documentation lines, 835 numbered root docs, and 768 numbered
root docs at 100 or higher.  The working set should become living contracts plus
a machine revision ledger.  Historical micro-notes should eventually be bundled
by epoch or subsystem.

## Online research implications

OWASP API4:2023 treats missing or inappropriate resource limits as a vulnerability
and explicitly lists execution timeouts, memory, file descriptors, process count,
upload size, operation count, record count, and provider spending limits.  That
maps well to Micromax: capability checks decide whether a script may ask, but
resource budgets decide how much host work the request may consume.  Source:
https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/

CWE-400 frames uncontrolled resource consumption as failing to control allocation
and maintenance of limited resources; common impacts include CPU, memory, and
other denial-of-service forms.  The filesystem-read timeout is therefore not a
feature flourish.  It is a resource-ownership repair.  Source:
https://cwe.mitre.org/data/definitions/400.html

VS Code is the useful comparison, not the template.  Its Extension Host is
explicitly responsible for running extensions, can exist in local/web/remote
locations, and is designed so misbehaving extensions do not slow UI operations or
startup.  Its Workspace Trust model disables or limits extensions in Restricted
Mode when they have not opted into that trust state.  Micromax is much smaller,
but the lesson is the same: trust state, host location, activation, and effect
capability must be product concepts.  Sources:
https://code.visualstudio.com/api/advanced-topics/extension-host and
https://code.visualstudio.com/docs/editing/workspaces/workspace-trust

Starlark remains the language-design warning sign.  It is a small embeddable
configuration/scripting language whose public pitch emphasizes deterministic,
hermetic, tooling-friendly execution.  Micromax can stay concatenative, but it
should keep the same discipline: small semantics, host-owned effects, and tooling
as a first-class contract.  Source: https://starlark-lang.org/

The WebAssembly Component Model and WASI are relevant later, not first.  WIT
worlds describe a component contract in terms of imports and exports, and the
WASI repository now identifies Preview 2 as WIT-based and Preview 3 as the
current async-oriented preview.  That is a strong future isolation/adaptation
shape, but only after Micromax knows what effects its host world exposes.  Sources:
https://component-model.bytecodealliance.org/design/wit.html and
https://github.com/WebAssembly/WASI

## What went wrong or wasteful

### The survivor audit became a loop

Recent history keeps finding one more retained or blocking object: old wordlists,
stale callbacks, active interactions, saved macros, pending timers, regex work,
shell output, external clipboard helpers, filesystem stat, filesystem list, and
now filesystem read.  Each fix is good.  The repeated discovery process is the
smell.  The project needs the effect matrix to stop relying on memory and grep as
its ownership oracle.

### Evidence tooling competes with the product

`tools/mxtest.py`, `tools/mxrelease.py`, `tools/mxtimely.py`, and audit/context
machinery are useful for cloudtainer handoff.  They should not become the main
thing.  Future sessions should count deletion, consolidation, and generated
contracts as progress when they reduce cognitive load without losing evidence.

### Resource limits were spread by hostcall family

The repo has rows, bytes, subprocess output, regex timeouts, stat/list timeouts,
source-load depth, and result budgets.  They are not yet one declared policy
surface.  Rev0912 intentionally follows the existing family pattern, but the next
step should be to generate an effect-budget inventory instead of hand-checking
one more string in `mxaudit.py` every time.

## Rev0912 landing

- `src/micromax_editor/file_access.py` adds
  `read_file_bytes_contained_bounded()`, which runs size/kind preflight and the
  final fd-bound byte read inside one short-lived worker when the timeout is
  positive.
- `src/micromax_editor/hostcall_boundary.py` adds
  `DEFAULT_FS_READ_TIMEOUT_SECONDS` and `effective_fs_read_timeout_seconds()`.
- `src/micromax_editor/micromax_bridge.py` installs
  `editor_hostcall_fs_read_timeout_seconds` on editor-owned VMs and passes the
  effective value into `ed.fs-read`.
- `src/micromax_editor/fs_hostcalls.py` routes `ed.fs-read` through the bounded
  helper while preserving the `{ok text err}` tuple shape.
- `tools/mxaudit.py` hard-checks `fs_read_timeout_worker` alongside the existing
  fs-read byte budget, fs-stat timeout, and fs-list timeout seams.
- `tests/test_editor_fs_read.py` adds a timeout regression and adapts
  containment/growth tests to prove worker-side mutation is still observed
  through filesystem state rather than parent-process local variables.

## Guarantees

- `ed.fs-read` remains disabled unless `cap.fs-read` is enabled.
- `cap.fs-root` and nominal path preflight still happen before the worker.
- The worker still performs the existing kind/size preflight and the final
  fd-bound read, so oversized files, late growth, and symlink/root swaps continue
  to fail closed.
- A timed-out read returns `ok=0`, empty text, and a diagnostic error string
  instead of freezing the editor process.
- `editor_hostcall_fs_read_timeout_seconds` is VM-tunable; non-positive values
  intentionally disable the reference worker boundary for hosts with stronger
  filesystem containment.

## Risks left

- Command-driven open/save and prompt-completion filesystem paths still need the
  same wall-clock treatment once their exact ownership boundaries are proven.
- The multiprocessing worker is a reference-host recovery seam, not a hostile-code
  sandbox or hostile-filesystem sandbox.
- Large allowed read payloads still cross a Python worker result channel.  The
  byte budget keeps this bounded, but a future external filesystem adapter should
  stream through an explicit result budget instead of relying on the reference
  queue transport.
- The effect contract is still prose-plus-audit checks, not the generated matrix
  the project needs.

## What should change next

1. **Finish filesystem wall-clock coverage for open/save and prompt completion.**
   Keep fd-bound containment and row/byte caps; do not replace them with path-only
   workers.
2. **Create the first generated effect-matrix slice.**  Start with filesystem
   observation because it now has capability, root, byte/row, timeout, and tuple
   behavior to model.
3. **Turn `mxaudit` resource checks into data.**  The check should read declared
   effect rows instead of searching for more ad-hoc strings.
4. **Define stable/experimental/internal hostcall tiers.**  Use a WIT-like
   import/export world as inspiration, even while Python remains the reference
   host.
5. **Compact docs by subsystem.**  Keep this revision note in the short term, but
   the long-term win is a living resource-boundary contract and a historical
   bundle, not another hundred single-revision files.
6. **Add release provenance.**  Lock dependencies, add small hosted CI/package
   inspection, record archive digests, and state archive-revision versus package
   version policy.

## Validation

Focused validation run during the rev0912 landing:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_fs_read.py tests/test_editor_fs_list.py tests/test_editor_fs_stat.py tests/test_mxaudit.py tests/test_mxcontext.py tests/test_revision_index.py
```

Result: 32 passed, 26 fork-worker warnings.

Handoff validation also passed:

```bash
PYTHONPATH=src python tools/mxaudit.py --json --check
PYTHONPATH=src python tools/mxlint.py
PYTHONPATH=src python tools/mxcontext.py --check
PYTHONPATH=src python tools/mxportable.py --quiet
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python tools/mxtimely.py --skip-tests --skip-doctor --summary-json .artifacts/mxtimely-summary.json
```

Results: audit ok for rev0912, `mxlint: ok`, context check ok, 156/156 portability cases passed, and the short timely lane passed context/audit/lint/portable.
