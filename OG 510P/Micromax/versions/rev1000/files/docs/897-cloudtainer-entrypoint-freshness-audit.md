# Cloudtainer mission and entrypoint freshness audit (rev0939)

Rev0939 is a deep-read and sequencing correction. It does not claim a new
sandbox, a new plugin boundary, or a broad architectural extraction. It records
the current heart/gap/waste diagnosis, refreshes stale curated handoff
entrypoints, and turns that exact drift into an audit-checked invariant.

## Heart of the mission

Micromax is trying to prove that end-user automation can be powerful without
quietly granting every extension ambient authority. The terminal editor is the
stress host, not the final thesis. Editing forces the language and host to handle
real mutable state: commands, macros, timers, hooks, prompts, search registers,
clipboard, filesystem reads/writes, subprocesses, package-local resources,
provenance, undo, rollback, and failure receipts.

The core mission is:

> least-authority end-user programmability with explicit effects, visible
> provenance, recoverable failure, bounded host work, and headless truth.

The codebase is healthiest when it makes an invisible effect into a named,
budgeted, attributable, tested owner seam. It is least healthy when it adds one
more revision note, raw snapshot field, audit predicate, or sidecar cleanup
helper without shrinking what a future maintainer must understand.

## What is missing

### 1. One executable effect/resource contract

The repository now contains many hard-won local boundaries: filesystem read/list
/stat/open timeouts, source-load budgets, regex input/time limits, shell and
external clipboard process caps, prompt/query/scan row limits, package resource
budgets, stale-generation guards, and editor-owned rollback seams for several
active interaction and delayed executable families.

Those facts remain spread across revision notes, tests, `mxaudit`, large editor
methods, plugin-runtime snapshot helpers, and capability policy. A future
contract should be generated from live owner methods, hostcall metadata, tests,
and audit seams. It should answer for each host effect:

- effect class;
- granting capability;
- owner identity;
- provenance key;
- byte, row, time, depth, process, and count budgets;
- staged/committed state;
- failure, unload, revoke, and stale-generation behavior;
- user/headless evidence rows.

The important constraint is not to write a big doctrine table first. The project
has already learned that hand-maintained lists become stale. Start by making the
next owner slice emit enough metadata that a first generated contract section is
possible.

### 2. A typed owner graph

The recent owner-method lane is directionally right. Prompt, query-replace,
keymode, pending open-url, callback interactions, clipboard, and macro state are
moving from raw runtime field juggling toward editor-owned snapshot/restore
seams. The missing abstraction is a small owner graph: each plugin-created or
script-created resource should name its owner, lifetime, stale-reference policy,
and evidence row.

Do not rewrite `Editor` first. Move one family at a time only when there is a
concrete stale lifetime, authority clobber, retention, or rollback failure to
remove. Keep the broad `RuntimeRegistrationSnapshot` as an oracle until each
family proves parity, then retire that family from broad ownership.

### 3. A versioned public extension surface

Micromax should not freeze the current implicit `Editor` object as its plugin
API. The stable surface should eventually look more like a small import/export
world: documented functions, typed handles, effect classes, versioning, and
migration rules. Declarative extensions should stay declarative; procedural code
should receive explicit handles and bounded operations rather than ambient
objects.

### 4. Release truth

The archive still reports no lock files, no CI workflow, and no external build
provenance. Rev0930 made the no-runtime-dependency/no-lock stance executable,
which is honest for the current research archive. It is not the same thing as a
published package supply-chain story. If Micromax starts publishing a package or
binary artifact, the sequence should be: lock consumption, CI/package
inspection, artifact digest, then signed provenance.

### 5. Handoff freshness as an audit invariant

This revision lands a small correction because the stale-entrypoint problem was
observable in the incoming archive: `docs/01-llm-start-here.md` still pointed at
rev0937 and `docs/43-worklist.md` still pointed at rev0934 while the archive was
rev0938. That is not a runtime vulnerability, but it is a cloudtainer waste
source. The curated entrypoints are supposed to reduce context load. If they lag,
future sessions waste time rediscovering which note is authoritative.

Rev0939 adds a `mxaudit --check` invariant for curated entrypoint revision
freshness, covering `README.md`, `TODO.md`, `docs/01-llm-start-here.md`,
`docs/02-repo-map.md`, and `docs/43-worklist.md`.

## What has gone wrong or wasteful

### Documentation became a second product

The docs are often useful. The waste is the storage model: hundreds of numbered
micro-notes compete with living contracts. This revision necessarily adds one
more note because the session asks for a deep read, but its main corrective move
is not more prose; it is an audit check that keeps curated entrypoints current.

### The survivor patch loop remains tempting

The project has successfully eliminated many direct filesystem/process/resource
survivors one at a time. That work was necessary. It is now risky as a default
rhythm: each new grep-driven survivor fix can make the system feel safer while
postponing the generated effect/resource contract.

### Coordinator gravity is still severe

Current audit metrics report `src/micromax_editor/editor.py` as the largest file
and `Editor` as the dominant mutable-state owner. This is not merely aesthetic.
It makes authority review expensive. The right correction is contract-backed
owner extraction, not a blind rewrite.

### Evidence tooling can consume the oxygen

The timely/release/mxtest tooling is valuable because the cloudtainer is
constrained and handoffs are frequent. It becomes waste when evidence runners and
revision ledgers absorb more design attention than product loops. Treat deletion,
compaction, and generated evidence as real progress when they preserve truth and
reduce reading load.

## Online research implications

The current external guidance supports the Micromax direction:

- OWASP API4:2023 says unrestricted resource consumption includes missing or
  inappropriate execution timeouts, memory limits, file/process limits, upload
  size, operation count, record count, and spending limits:
  https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- MITRE CWE-770 frames allocation without limits/throttling as a base weakness
  and explicitly calls for minimum/maximum capability expectations and graceful
  failure under limits: https://cwe.mitre.org/data/definitions/770.html
- Python's `subprocess.run(..., timeout=...)` kills and waits for a child after a
  timeout, but process creation itself may not be interruptible; `Popen.communicate()`
  does not kill the child on timeout and buffers output in memory, so Micromax is
  right to pair timeouts with output budgets and teardown logic:
  https://docs.python.org/3/library/subprocess.html
- Python `Future.cancel()` can fail once work is running; Python 3.14 adds
  `ProcessPoolExecutor.terminate_workers()` and `kill_workers()`, reinforcing
  that cancellation and worker lifetime are separate resources:
  https://docs.python.org/3/library/concurrent.futures.html
- VS Code Workspace Trust is a useful comparison for restricted automatic
  execution, but its own documentation warns that Workspace Trust cannot prevent
  a malicious extension from executing code. Micromax should keep making the same
  distinction between application-level policy and hostile-code containment:
  https://code.visualstudio.com/docs/editing/workspaces/workspace-trust
- Starlark remains the closest language-design neighbor: small, embedded,
  deterministic, hermetic by default, and tooling-friendly. Micromax differs by
  being concatenative and editor-hosted, but the lesson is the same: a scripting
  language becomes safe only when host effects are explicit:
  https://starlark-lang.org/
- WIT in the WebAssembly Component Model defines contracts between components
  rather than behavior. That is a good shape for a future Micromax plugin API,
  but only after the native host-effect contract is already small and explicit:
  https://component-model.bytecodealliance.org/design/wit.html
- SLSA describes supply-chain controls for tamper resistance and artifact
  integrity. Micromax should not pretend local zip provenance is signed release
  provenance; it should add SLSA-like steps only when a real release lane exists:
  https://slsa.dev/

## Speculation

The strongest future shape is a small automation kernel with three surfaces:

1. **a portable VM/reference oracle** for deterministic language semantics;
2. **a generated host-effect contract** for capabilities, budgets, provenance,
   ownership, and evidence;
3. **one or more hosts** that prove the contract under real work, with the editor
   remaining the first and harshest host.

The editor can stay modest. The durable product is not a clone of Emacs, Vim,
Nano, or Micro. It is the contract that lets a user ask, “What did this extension
receive authority to do, what did it actually do, what can be rolled back, what
cannot, and what resource ceilings protect my session?”

## What changed in rev0939

- Added this deep cloudtainer mission/gap/waste audit.
- Refreshed `docs/01-llm-start-here.md`, `docs/02-repo-map.md`, and
  `docs/43-worklist.md` to the current revision.
- Added curated entrypoint revision metrics to `tools/mxaudit.py`.
- Made `mxaudit --check` fail if `README.md`, `TODO.md`, `docs/01-llm-start-here.md`,
  `docs/02-repo-map.md`, or `docs/43-worklist.md` point at a stale revision.
- Added focused `tests/test_mxaudit.py` coverage for the JSON and human audit
  output.

## What should change next

1. Generate the first effect/resource-contract slice from live owner facts,
   starting with active-search or another small remaining singleton only if a
   concrete authority/lifetime route test justifies it.
2. Keep moving raw runtime snapshot fields behind typed owners one family at a
   time; count removal from `RuntimeRegistrationSnapshot` as progress only after
   parity tests pass.
3. Promote the resource/effect/security contract into installed help rather than
   installing every revision note.
4. Add release locks/CI/provenance only when there is an actual published package
   or binary lane to protect.
5. Treat documentation compaction and audit-generated living contracts as
   product work, not janitorial work.

## Validation target

```sh
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q tests/test_mxaudit.py tests/test_revision_index.py

PYTHONPATH=src python tools/mxaudit.py --json --check
PYTHONPATH=src python tools/mxcontext.py --check
PYTHONPATH=src python tools/mxlint.py
```
