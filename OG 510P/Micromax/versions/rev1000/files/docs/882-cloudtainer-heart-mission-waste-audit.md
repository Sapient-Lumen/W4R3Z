# Rev0924 — cloudtainer heart, mission, gap, and waste audit

Date: 2026-07-08

This revision is a diagnosis and sequencing correction. It does not claim a new
sandbox, a new runtime boundary, or a code repair. It reads the rev0923 archive
as a product/architecture system, checks current external guidance, and names
what should change next in the cloudtainer.

## Executive judgment

The heart of Micromax is **a least-authority automation substrate**, not a small
terminal editor. The editor matters because it is the first hard host where the
same Micromax language must configure, script, macro, and extend real user work
without silently inheriting ambient authority. The calm editor goal is therefore
secondary but not decorative: taste, trust, and flow are the proof that explicit
authority can still feel usable.

The central promise is:

> powerful end-user programmability with explicit effects, visible provenance,
> recoverable failure, and headless truth.

The project is healthiest when it turns an invisible host effect into a named,
budgeted, attributable, testable seam. The recent filesystem/process/resource
work mostly serves that promise. The project is least healthy when it keeps
adding one more sidecar, snapshot field, revision note, or evidence runner knob
without shrinking the contract users and future implementors must understand.

## What is missing

### 1. One living host-effect/resource-budget contract

The repository now has many good local facts: command/action/key/hook/timer
ownership, stale-generation guards, shell and clipboard process budgets, regex
input/time budgets, filesystem read/list/stat/open/write/save budgets, docs scan
budgets, project-root marker batching, and help-doc read timeouts. The facts are
spread across revision notes, tests, `mxaudit` checks, hostcall boundary helpers,
and large coordinator code.

A single living contract should answer these questions for every host effect:

- What is the effect class: declaration, reversible session state, document edit,
  durable internal state, external/irreversible effect, observation/disclosure,
  or resource allocation?
- Which capability grants it?
- Which plugin/user/session owns it?
- Is it staged before load commit?
- What is the failure behavior?
- What is the unload/revoke behavior?
- Which byte/row/time/depth/count budgets apply?
- Which headless row proves the denial, timeout, stale reference, or cleanup
  receipt?

Do not start with another hand-maintained doctrine table. First retire or
explicitly classify the last visible direct filesystem/process survivors, then
generate the first slice from live code/test metadata.

### 2. A real owner graph for plugin-created resources

The deep rev0873 finding is still true. Micromax keeps discovering one more
plugin-created thing that can survive reload, failure, or grant revocation. The
recent narrow snapshots are much better than full global rollback, but the model
is still distributed across `Editor` state fields, authority sidecars,
`RuntimeRegistrationSnapshot`, cleanup helpers, plugin-manager paths, audit
predicates, and revision notes.

The next architecture step is not a rewrite. It is a typed owner graph for one
family at a time: declare the resource shape, owner identity, commit/abort hooks,
stale-reference behavior, and headless evidence row. Keep the broad snapshot as
a differential oracle until one family proves parity, then move that family out
of broad snapshot ownership.

### 3. A security story that is honest at the process boundary

The current security wording is mostly honest: this is application-level
authority control, not hostile-code containment. That must remain prominent.
Workspace-trust style controls help with automatic execution, but they are not a
malicious-extension sandbox. Current VS Code documentation makes the same kind
of distinction: restricted mode limits automatic code execution, but cannot make
a malicious extension safe merely by policy.

Longer term, a separate plugin process or Wasm/WASI component boundary is
plausible. It should not happen until Micromax has a small, versioned hostcall
contract. WASI is attractive because its own documentation frames applications
as starting with no ambient authority and receiving only explicit host grants;
that matches the Micromax mission. But pushing today’s implicit editor API into
Wasm would freeze the wrong boundary.

### 4. Release provenance and reproducibility

Local audit still reports zero lock files, zero CI workflows, zero aggregate
handoff manifests, and zero release-suite manifests in this archive. The package
version is still `0.0.8` while the archive revision is rev0923/rev0924. That can
be acceptable for a hand-evolved research repo only if the policy is explicit.
Without a lock, CI/package inspection, artifact digest, and package-version vs
archive-revision policy, the archive proves less than the code thinks it proves.

The incoming `.artifacts/mxtimely-summary.json` also contained a stale context
note (`Rev: 922`) while the tree breadcrumbs were rev0923. That is not a runtime
bug, but it is exactly the kind of handoff drift that the filename discipline and
context manifest are supposed to prevent.

### 5. A smaller current documentation surface

The docs are valuable, but the shape is wasteful. This archive has 861 docs
files, about 8.0 MB of docs, 848 root Markdown docs, and 780 numbered root docs
with prefixes >=100. Source has about 2.7 MB. The revision trail is now a product
of its own. The normal working set should be a small set of living contracts plus
a machine-readable ledger; append-only history should be preserved but not force
every agent to reread hundreds of micro-notes.

`docs/01-llm-start-here.md` and `docs/43-worklist.md` have also lagged the
current revision trail. That is a warning sign: curated living docs must be
trusted entrypoints, not nostalgic entrypoints.

## What has gone severely wrong or wasteful

### 1. The survivor patch loop is still the dominant rhythm

The project has been successfully killing ambient filesystem/process/resource
surfaces one by one. That is good work. But the repetition is now a structural
smell: every revision can find one more survivor because the effect inventory is
still inferred from grep, focused tests, and reviewer memory. The next phase
needs a generated or at least code-adjacent inventory, not merely more prose.

### 2. Coordinator gravity remains severe

`mxaudit` measures `src/micromax_editor/editor.py` at 26,472 lines, `Editor` at
1,142 methods, and 102 `__init__` state attributes. `RuntimeRegistrationSnapshot`
has 40 fields. This is not primarily a style failure. It is an authority proof
failure: too many unrelated mutation namespaces live in the same coordinator, so
reviewers cannot cheaply prove what a plugin operation can touch.

### 3. Proof machinery can eclipse product progress

`tools/mxtest.py` is 4,512 lines and one prompt-completion hostcall test module
is 6,640 lines. The evidence runner is helpful in a constrained cloudtainer, but
it is also becoming a subsystem whose complexity competes with the runtime. This
session saw `make timely` complete context/audit/lint/portable and then get
externally terminated during doctor; running `make doctor` separately passed.
That supports the existing resumable-evidence direction, but also argues for
fewer nested aggregators and clearer “what does this artifact prove?” summaries.

### 4. Resource hardening repeats research instead of centralizing it

The current online guidance continues to support Micromax’s direction: Python’s
`subprocess.run(..., timeout=...)` kills and waits for the child, but process
creation itself may not be interruptible; `Popen.communicate(timeout=...)` does
not kill the child by itself and buffers output in memory; futures cannot cancel
a call once it is running; Python 3.14 added explicit `ProcessPoolExecutor`
`terminate_workers()` and `kill_workers()` methods. OWASP guidance similarly
emphasizes input size, request size, resource-allocation, timeout, and cost
limits. These facts should be captured once in a living resource-budget contract,
not restated in every narrow revision note.

### 5. The installed/current help split is under-specified

Installed help is curated, which is good. But if the latest resource/security
truth lives only in source-checkout revision notes, installed users can miss the
current boundary story. The durable fix is not to install every micro-note; it is
to promote the resource/effect-budget contract and security boundary into the
installed help set.

## What should change next

### Next tiny code landing

Patch the smallest real survivor first: `src/micromax_editor/plugin_meta.py` uses
`meta_path.exists()` to decide whether optional `plugin.json` exists even though
`plugin_file_exists()` is already imported and used for `entry` checks. Replace
that direct existence probe with the contained plugin I/O seam, preserve the
optional metadata semantics, and add a focused regression plus an `mxaudit`
predicate. This is a good rev0925 candidate because it is small, capability
sensitive, and in the plugin-loading path.

Secondary candidates, in priority order:

1. `src/micromax_editor/resource_roots.py` implicit installed docs/plugins root
   selection still uses direct `cand.is_dir()`. It is one-shot startup work, so
   patch only if the next contract wants all runtime resource discovery to share
   the same bounded stat seam.
2. `src/micromax_editor/docs_index.py::_scan_doc_file()` still has a private
   direct `Path.read_text()` compatibility fallback. Either route it through the
   bounded docs seam or mark it explicitly as deprecated/test-only.
3. `src/micromax_editor/prompt_completion.py` preserves direct `Path.iterdir()`
   when `timeout_seconds is None`. Keep it for standalone callers only if all
   editor/hostcall paths prove they pass a timeout; otherwise split the helper so
   the unbounded path cannot be accidentally selected by a capability-sensitive
   caller.
4. `micromax.vm.VM._load_stdlib()` reads an importlib package resource directly.
   This is not the same risk as workspace/plugin filesystem access, but it should
   be classified as trusted package resource loading so the effect inventory does
   not keep reporting it as an unexplained survivor.

### Next documentation/evidence landing

Create `docs/resource-budget-contract.md` or a generated `docs/effect-budget-matrix.md`
that consolidates the current timeout/input/output/row/depth/count contract. It
should cite the source of truth in code and tests rather than repeating full
research in every future note.

### Next architecture landing

Pick one plugin-owned family and make it a typed owner module. Good candidates:
prompt/history rows, timers, or macro slots. The success condition is not fewer
lines in `Editor`; it is that one resource family has a single owner, a narrow
commit/abort journal, a stale-reference rule, and an audit row.

### Next release landing

Add a minimal lock/CI/provenance lane:

- freeze or record dev dependency inputs;
- run `make timely-tests` or an equivalent short evidence lane in CI;
- package an artifact digest and exact source/context manifest;
- document how `rev####` relates to `pyproject.toml` version.

## Online research notes

- Python 3.14.6 `subprocess` documentation: `subprocess.run(..., timeout=...)`
  passes the timeout to `Popen.communicate()` and kills/waits for the child on
  timeout; process creation itself may not be interruptible on many platform
  APIs. Source: https://docs.python.org/3/library/subprocess.html
- Python 3.14.6 `subprocess` documentation: `Popen.communicate(timeout=...)`
  raises `TimeoutExpired` without killing the child; callers must kill and then
  finish communication, and `communicate()` buffers captured data in memory.
  Source: https://docs.python.org/3/library/subprocess.html
- Python 3.14.6 `concurrent.futures` documentation: `Future.cancel()` returns
  false once the call is running, and Python 3.14 added
  `ProcessPoolExecutor.terminate_workers()` / `kill_workers()` for immediate
  worker teardown. Source: https://docs.python.org/3/library/concurrent.futures.html
- OWASP Denial of Service Cheat Sheet: limit session time/storage, upload size,
  total request size, input-based resource allocation, and input-driven function
  or threading intensity. Source:
  https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html
- OWASP API4:2023 Unrestricted Resource Consumption: define and enforce maximum
  sizes for parameters and payloads and use infrastructure that can limit memory,
  CPU, file descriptors, and process counts. Source:
  https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- VS Code Workspace Trust documentation: Restricted Mode prevents automatic code
  execution for unfamiliar workspaces, but cannot prevent malicious extensions
  from ignoring restricted mode. Source:
  https://code.visualstudio.com/docs/editing/workspaces/workspace-trust
- VS Code agent security documentation: modern editor/agent security is framed in
  terms of explicit trust boundaries for workspace, extension publisher, MCP
  server, and network domain. Source:
  https://code.visualstudio.com/docs/agents/security
- WASI.dev introduction: WASI applications run in a capability-based sandbox and
  start with no ambient authority except what the host grants. Source:
  https://wasi.dev/
- Bytecode Alliance WASI 0.2 note: WASI 0.2 is based on the Wasm component
  model, making it cross-language and virtualizable. Source:
  https://bytecodealliance.org/articles/WASI-0.2

## Validation performed in this cloudtainer

- `python tools/mxaudit.py --check` passed on the incoming rev0923 tree.
- `python tools/mxcontext.py --check` passed on the incoming rev0923 tree.
- `make doctor` passed its bounded preflight: 29 selected tests passed, with
  expected multiprocessing fork deprecation warnings on Python 3.13.
- `make timely` was externally terminated during the doctor step after
  context/audit/lint/portable had passed; this is recorded as cloudtainer runway
  evidence, not as a runtime failure.

## Recommended next handoff

Do rev0925 as a tiny code repair: bounded optional plugin metadata existence.
Keep the filename discipline. Do not start a broad extraction or effect-table
rewrite until that survivor and any other hot/capability-sensitive direct
filesystem probes are either patched or explicitly classified.
