# Rev0873 — mission, effect-lifecycle, and cloudtainer audit

Date: 2026-06-18

This is a diagnosis and sequencing correction. It does not claim a new sandbox or
complete plugin atomicity. The incoming rev0872 archive contains strong local
security work, but the pattern of that work now reveals a missing abstraction:
Micromax has no explicit lifecycle contract for host effects.

## Executive judgment

The heart of Micromax is **not** “a small terminal editor.” It is a small,
inspectable, least-authority automation substrate in which configuration,
macros, and extensions use one portable language; effects are explicit;
provenance is visible; failures are recoverable; and headless models are the
source of truth. The editor is the first demanding host and test fixture for
that substrate.

The project is strongest where it makes invisible authority visible. Restricted
startup, content-bound grants, callback freshness, group ownership, rollback,
and headless evidence all serve the same mission: let a person automate real
work without silently handing every extension the whole process.

The main danger is now architectural rather than conceptual. Micromax is
reconstructing effect ownership one mutable field at a time inside an enormous
coordinator. That approach can keep fixing individual leaks while never making
plugin lifecycle semantics complete, cheap, or understandable.

## Incoming rev0872 measurements

These measurements were taken from the unpacked archive. Rev0873 adds
`tools/mxaudit.py` so future audits can reproduce the structural subset with
`make audit-metrics` instead of rebuilding it manually.

- 1,152 archive entries and about 12.2 MB uncompressed.
- 810 files under `docs/`, 105 under `src/`, and 196 under `tests/`.
- 797 root Markdown files under `docs/`; 729 numbered root docs have a numeric
  prefix of 100 or greater.
- Three duplicate numeric prefixes remain: 32, 735, and 752.
- `src/micromax_editor/editor.py` is 25,363 lines.
- The `Editor` class spans about 24,400 lines, contains 1,100 direct methods,
  and initializes 99 state attributes.
- Fourteen `Editor.__init__` attributes are explicit authority sidecars.
- Fifty-five direct `Editor` helpers match the current snapshot/restore,
  remove/retag, group/plugin/state lifecycle pattern.
- `RuntimeRegistrationSnapshot` carries 40 fields.
- Other large seams include `install_editor_hostcalls()` at roughly 2,582
  lines, `docs_cues_model_from_parts()` at roughly 1,928 lines,
  `install_core_words()` at roughly 1,714 lines, and
  `install_default_actions()` at roughly 1,345 lines.
- Pytest collected 2,284 tests. A direct `make test` attempt did not fail, but
  it reached only about 31 percent before an external 240-second command limit.
- No current aggregate `.artifacts/mxtest-all*.json` manifest was present in the
  incoming archive.
- No repository CI workflow or dependency lock file was present.
- `scripts/typecheck.sh` targets `src/micromax` and `tests`, omits the much
  larger `src/micromax_editor` package, and reports success-by-skip when mypy is
  unavailable.
- The internal revision is rev0872 while package metadata remains version
  `0.0.8`; the relationship between archive revisions and package versions is
  not documented as a release policy.

These are not all defects. They are pressure indicators. The important signal
is how they reinforce one another: a huge stateful coordinator, a large
snapshot, slow proof, and hundreds of notes make every additional mutable
surface expensive to reason about.

## What has gone severely wrong

### 1. The survivor audit became a patch loop

Revs 0863 through 0872 repeatedly find one more plugin-created state survivor:
interactions, macros, recovery stacks, search, prompt history, file navigation,
palette MRU, clipboard, help history, and options. Each fix is locally sensible
and often security-positive. Ten consecutive revisions with the same shape,
however, are evidence that the host lacks a first-class model of effects and
lifecycle.

The current pattern is:

1. add or discover mutable editor state;
2. add an authority sidecar;
3. add remove/retag methods;
4. expand `RuntimeRegistrationSnapshot`;
5. copy the state before plugin work;
6. restore it on selected failure paths;
7. write another narrow test and revision note;
8. repeat when the next survivor appears.

This is whack-a-mole correctness. It distributes the ownership registry across
parallel lists, maps, fields, plugin-manager cleanup, snapshot code, docs, and
tests. The implementation can still miss a surface even while every existing
focused test passes.

### 2. Snapshot cost grows with global editor state

Deferred plugin callbacks take a broad runtime snapshot even when a callback
will touch only one small surface. The option addition deep-copies global
options and every live buffer's local option map. Future survivor patches will
keep increasing the cost and failure surface unless the model changes.

Whole-state snapshots are useful as a recovery backstop, but they should not be
the permanent ownership architecture. A callback should not need to copy
unrelated navigation, clipboard, macro, prompt, help, and option state merely to
register one command.

### 3. “Rollback” is broader in wording than in semantics

Micromax correctly documents that arbitrary buffer edits, new buffers, file
opens, external I/O, blocking hostcalls, and process effects are not generally
undone. Nevertheless, the code and revision language increasingly use one
transaction vocabulary for very different classes of effects.

A plugin registration is naturally staged. A local option write is reversible.
A user document edit belongs in undo history. A file save, shell command, URL
open, system clipboard export, or network call may be irreversible. Treating
all of them as “plugin transaction state” obscures the real contract.

A narrow rev0872 follow-up risk illustrates the issue: buffer-local options are
snapshotted by buffer name and critical restore blocks swallow exceptions. A
buffer renamed during an uncommitted path or a failed restore can therefore be
hard to diagnose. That does not invalidate rev0872, but it shows why field-level
snapshotting cannot be the final semantic boundary.

### 4. Coordinator gravity is consuming the design

A 25,363-line `editor.py` with 1,100 methods is not merely a style problem. It
makes authority, UI state, persistence, plugin lifecycle, command semantics,
headless models, and recovery share one mutation namespace. The danger is not
that the file is aesthetically large; it is that no reviewer can cheaply prove
which state a plugin operation can touch.

The same gravity exists in giant installer/model functions. A broad rewrite
would be dangerous, but indefinitely adding one more helper to the same object
is also dangerous. The correct response is contract-first extraction behind
behavior-preserving tests.

### 5. Documentation and evidence have become a maintenance product

The revision trail is valuable, but 810 docs and 729 high-numbered root notes
create search noise, duplicate numbering, packaging choices, context curation,
and stale-handoff risk. The repository has already had living docs tell an old
story after the implementation moved on.

`tools/mxtest.py` is itself 4,512 lines, and one test module is 6,640 lines. The
proof machinery is powerful, but it can absorb engineering attention that
should go to the language, authority contract, and host architecture.

Historical notes should remain available, but the normal working set should be
a small set of living contracts plus a machine-readable ledger. New revision
notes should not be mistaken for product progress.

### 6. The security contract was absent from installed help

`docs/security-boundaries.md` is explicitly the living security contract and is
second in the README reading order. Rev0872's installed-help manifest and
`pyproject.toml` omitted it, so an installed-wheel user could read the vision
and recent cleanup notes without the central threat model.

Rev0873 corrects that omission and adds an installed-layout regression test.
This was a release-facing truth failure, not just a docs preference.

## What is missing

### 1. A host-effect lifecycle contract

Before another general survivor patch, define every host effect along two axes:
its effect class and its lifecycle behavior.

| Effect class | Examples | Load/callback behavior | Failure behavior | Unload/revoke behavior |
| --- | --- | --- | --- | --- |
| Declaration/registration | command, action, key, hook, timer | stage under a generation | discard staged records | host drops owned handles |
| Reversible session state | prompt row, search register, palette MRU, local option | journal old/new value or use typed owner-aware adapter | restore journal | explicit retain, remove, or revert policy |
| User document edit | insert/delete/replace | join an editor undo transaction | abort transaction when promised atomic | normally retained as user-visible history |
| Durable internal state | recent files, cursor persistence, history file | stage durable write or record compensating update | no partial durable commit | prune owned rows and persist once |
| External/irreversible effect | save, shell, URL, network, system clipboard export | require explicit capability and commit boundary | cannot promise rollback; return a receipt | no fictional cleanup claim |
| Observation/disclosure | read buffer, list files, read option/history | scoped read capability | no mutation to restore | grant revocation blocks future reads |

The contract must separately state semantics for discovery, approval, load,
load commit, callback, staged reload, reload commit, deinit, unload, grant
revocation, callback crash, and host crash.

Minimum invariants:

- uncommitted declarations are invisible outside the staging generation;
- every delayed executable or navigation resource has one owner and one cleanup
  route;
- every promise of atomicity names exactly which effect classes it covers;
- irreversible effects are never described as rolled back;
- cleanup failure is observable rather than swallowed;
- deinit cannot mutate arbitrary host state under a misleading cleanup label;
- user edits use undo semantics instead of being mixed with registration
  rollback;
- grants are explicit values/handles, not ambient truth inferred only from
  global options;
- the headless model can explain origin, grant, generation, and last transition.

### 2. A small public extension contract

Micromax has many hostcalls but no compact stable/experimental/internal matrix,
version negotiation, compatibility rules, or canonical interface definition.
That blocks both trustworthy third-party plugins and safe process/Wasm
isolation.

The next contract should define a minimal `PluginHost` surface with versioned
request/response schemas. Internal `Editor` methods must not become the public
API by accident. A WIT-like interface description is a useful model even if
Python remains the implementation language initially.

### 3. Typed resource handles and an effect journal

Do not replace parallel sidecars with one universal untyped registry. Instead,
use small typed adapters:

- `Authority` or `Grant` is an immutable value containing origin, generation,
  scope, and revocation identity;
- registrations return `ResourceHandle`s owned by the host;
- reversible state writes append typed journal entries;
- commit seals the journal and promotes staged handles;
- abort replays only touched entries in reverse order;
- unload asks each typed adapter to drop or retain its owned resources according
  to the declared policy.

This changes rollback complexity from “copy most editor state before every
callback” toward “record the effects this operation actually performs.” A broad
snapshot can remain temporarily as an assertion oracle during migration.

### 4. Explicit atomic blocks rather than universal callback atomicity

Not every callback should pretend to be a database transaction. Offer a small
explicit operation such as `ed.atomic` for effect classes that can really be
rolled back: registrations, selected session state, and document undo edits.
Crossing an irreversible boundary should either commit the current atomic block
or be rejected from it.

This makes failure behavior legible to plugin authors and users. It also lets
simple callbacks avoid paying to snapshot the whole editor.

### 5. Isolation and resource budgets after the contract

Moving plugins into another process or WebAssembly is valuable only after the
imports/exports and effect semantics are small. Otherwise Micromax will merely
serialize the current giant internal API.

A future isolated host needs, at minimum:

- explicit imported capabilities;
- memory/table/instance limits;
- deterministic fuel or instruction budgeting;
- wall-clock interruption;
- bounded message sizes and queue depth;
- cancellation and crash recovery;
- versioned schemas;
- durable grant policy separated from plugin identity and package freshness.

Wasm is not a magic safety switch. Host functions remain authority, and a
resource limiter does not automatically bound every host allocation or external
operation.

### 6. Reproducible release truth

Add a standards-based dependency lock, a focused CI lane, artifact build checks,
and build provenance. Explain how `rev####` relates to package semantic
versions. The archive context is useful, but it is not a substitute for a
repeatable environment and hosted evidence.

### 7. One canonical schema authority

Headless models are part of the product mission, yet many remain ad hoc Python
dictionaries and lists. Define versioned schemas for active, empty, denied,
stale, error, and partial states. Use the same schema definitions for runtime
validation, docs examples, fixtures, and any future cross-process interface.

## What should change, in order

1. **Freeze broad survivor expansion for one revision.** Continue only fixes
   that close an immediately demonstrated leak; first write the lifecycle
   matrix and inventory every existing effect surface.
2. **Define the public/internal extension matrix.** Mark every hostcall and
   model stable, experimental, or internal; assign schema versions.
3. **Introduce a typed effect journal beside the snapshot.** Migrate one family
   such as options or registrations and compare journal abort against the old
   snapshot in tests.
4. **Make cleanup failure visible.** Replace blanket exception swallowing in
   critical rollback paths with structured cleanup results and diagnostics.
5. **Extract a narrow `PluginHost` coordinator.** Move policy and lifecycle
   orchestration, not arbitrary editor behavior. Keep `Editor` as an adapter
   during migration.
6. **Separate proof lanes.** Fast VM/policy/schema conformance should run on
   every change; package/subprocess/full aggregate evidence should be an
   explicit release lane with regenerated manifests.
7. **Lock and automate the build.** Add `pylock.toml` or an equivalent standard
   lock, focused CI, wheel/sdist inspection, and provenance records.
8. **Prototype isolation last.** Use the versioned interface to test a process
   or Wasm extension host with fuel, wall-clock, memory, and message limits.
9. **Compact history.** Keep the revision index, but move old narrow notes into
   periodic history bundles or generated catalogs so root docs remain a working
   set rather than an append-only event stream.

## Online comparison and implications

These comparisons are design inputs, not claims that Micromax should copy a
larger editor wholesale.

- VS Code uses one or more extension-host runtimes and explicitly frames that
  separation around editor stability, startup, and UI performance. Its
  Workspace Trust documentation also warns that Restricted Mode cannot contain
  a malicious extension. Micromax's restricted-startup honesty is therefore on
  the right track, while its same-process extension execution remains a known
  ceiling.
  - <https://code.visualstudio.com/api/advanced-topics/extension-host>
  - <https://code.visualstudio.com/docs/editing/workspaces/workspace-trust>
- The WebAssembly Component Model's WIT “world” describes exact imports and
  exports and intentionally defines a component surface rather than internal
  behavior. That is the useful lesson for Micromax: define the contract before
  changing the runtime.
  - <https://component-model.bytecodealliance.org/design/worlds.html>
  - <https://component-model.bytecodealliance.org/design/wit.html>
- Wasmtime exposes fuel, epoch interruption, and resource limiters as separate
  controls. Micromax would need a layered budget rather than assuming one VM
  step counter or one Wasm boundary solves CPU, wall-clock, memory, and hostcall
  risk.
  - <https://docs.wasmtime.dev/api/wasmtime/struct.Config.html>
  - <https://docs.wasmtime.dev/api/wasmtime/struct.Store.html>
- Zed compiles procedural extension code to WebAssembly and gives its extension
  manifest an explicit schema version. Extism makes WASI opt-in and emphasizes
  selective host functions. Both reinforce the order “small interface, explicit
  imports, then isolation.”
  - <https://zed.dev/docs/extensions/developing-extensions>
  - <https://extism.org/docs/concepts/configuration/>
  - <https://extism.org/docs/questions/>
- PyPA now specifies `pylock.toml` for reproducible installation. SLSA v1.2
  treats provenance as a staged supply-chain control, with higher levels adding
  hosted and signed evidence. Micromax can adopt the modest first step without
  pretending to have a hardened release pipeline immediately.
  - <https://packaging.python.org/en/latest/specifications/pylock-toml/>
  - <https://slsa.dev/spec/v1.2/>
  - <https://slsa.dev/spec/v1.2/build-provenance>

## Speculation: the strongest product direction

Micromax may be more valuable as an **undoable, explainable personal automation
kernel** than as another editor. The editor supplies realistic state,
interaction, and trust pressure, but the reusable product is the contract:
small scripts can request narrow effects, the host can show why they were
allowed, and failure can be explained or reversed where reversal is real.

That direction suggests three extension tiers:

1. **Declarative contributions** — commands, keys, menus, docs, schemas; cheap to
   validate and unload.
2. **Pure computations** — deterministic functions with no host imports; easy to
   cache, test, and eventually run in Wasm.
3. **Effectful automations** — explicit grant objects, effect journal, receipts,
   and commit boundaries.

It also suggests that provenance should be user-facing, not only internal
metadata. A command palette row, saved macro, search register, or document edit
could explain: “created by plugin X, generation Y, under grant Z, during
transaction T; retained/removed because policy P.” That would turn Micromax's
current sidecar work into a visible trust feature rather than hidden cleanup
machinery.

A further possibility is to treat the Python implementation as an executable
semantic oracle while a smaller Rust/Wasm host evolves around versioned WIT-like
interfaces. The oracle remains valuable only if behavior is specified in
portable cases rather than trapped in `Editor` methods.

## Rev0873 changes

- Added this mission/effect-lifecycle audit and made it the sequencing basis for
  the next worklist.
- Added `tools/mxaudit.py` and `make audit-metrics` for repeatable inventory,
  hotspot, lifecycle-snapshot, docs, typecheck, and release-hygiene metrics.
- Added focused tests for the audit schema and output.
- Added `docs/security-boundaries.md` to the installed-help manifest and
  `pyproject.toml` data files.
- Added an installed-layout test that opens the security contract outside the
  source checkout.

## Evidence boundary for this revision

This revision changes docs, packaging declarations, tests, and an audit tool. It
does not change runtime plugin behavior. Focused tests, lint, context checks,
and package-resource probes should pass before packaging. A fresh complete
aggregate manifest is still required before making a full-suite release claim.
