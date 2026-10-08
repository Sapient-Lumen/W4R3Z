# Cloudtainer heart, missing contract, waste audit, and word-authority repair (rev0889)

## Executive finding

The heart of Micromax is **not a terminal editor**.  It is an attempt to make
end-user automation small enough to understand and powerful enough to matter,
while forcing authority, provenance, failure, and recovery to remain visible.
The editor is the proving host.  The strategically valuable product is a
**least-authority automation kernel with a recoverable, inspectable host**.

That mission is unusually coherent across the language, VM, capability registry,
restricted startup, plugin package grants, headless models, rollback machinery,
and security documentation.  The repository is strongest when it makes one
boundary executable and testable.  It is weakest when it substitutes another
revision note, another broad snapshot field, or another sidecar-specific cleanup
helper for a single effect contract.

Rev0889 fixes one concrete instance of that weakness: failed plugin source and
lifecycle transactions restored VM dictionary topology but could leave stale
`Editor._word_authority` provenance rows for words that no longer existed.
Dictionary state and dictionary-keyed provenance now snapshot and restore as one
unit.

## What the project is really trying to prove

Micromax is exploring whether an automation language can offer all of these at
once:

1. a compact, portable semantic core;
2. explicit host effects rather than ambient Python authority;
3. user-visible provenance and trust transitions;
4. recoverable extension failure;
5. deterministic, headless behavioral truth;
6. enough editor ergonomics to test the design under real interaction pressure.

The editor matters because editing exposes nearly every difficult class of
state: reversible registrations, document mutations, delayed callbacks,
navigation history, clipboard/search state, persistent preferences, filesystem
access, subprocesses, and external effects.  If Micromax can classify those
honestly, it can become more than an editor plugin system: it can become a small
explainable automation substrate.

## What is missing

### 1. One executable effect-lifecycle contract

The repository has capabilities, provenance sidecars, cleanup groups,
generation tokens, runtime snapshots, and many preservation tests.  It does not
yet have one machine-readable table that says, for every public hostcall and
delayed state family:

- effect class;
- required capability;
- authority/provenance key;
- whether the effect is staged;
- commit, abort, reload, unload, revoke, and crash behavior;
- persistence and migration behavior;
- reversibility or irreversibility;
- schema/API version and stability tier.

Without that table, lifecycle correctness is discovered sidecar by sidecar.  The
word-authority leak fixed here is direct evidence: dictionary topology and its
provenance had separate rollback ownership, so source/lifecycle failures could
restore one and strand the other.

### 2. A versioned extension contract

The current host surface is large and mostly implicit.  The audit sees 251
editor hostcall implementations, roughly 140 advertised host features, and 41
capability entries.  Plugins can target behavior, but they cannot yet target a
small declared interface version with compatibility, feature negotiation,
deprecation, and persistence migration rules.

A useful future contract should resemble an explicit import/export world rather
than “whatever the Editor object currently exposes.”  Declarative extensions
should remain declarative.  Procedural extensions should receive typed handles
and bounded interfaces.

### 3. Bounded runtime resource ownership

Successful plugin reload and unload deliberately retain committed wordlists in
`vm.wordlists` for historical/provenance inspection.  This keeps executable
`Word` objects, not compact historical facts.  A local benchmark in this
revision loaded a 300-definition plugin and reloaded it 80 times:

- 82 wordlists remained;
- 24,593 words remained;
- traced live-memory growth was about 20.23 MiB;
- every future dictionary snapshot had more dictionaries and word objects to
  traverse.

This is an unbounded retention policy disguised as provenance.  Historical
inspection should use bounded tombstone records containing generation, digest,
word names, source locations, and unload reason.  Retired executable wordlists
should be released once no live callback/XT/resource handle can reference them.
That change needs reference-liveness and stale-callback tests; it should not be
an eager `del vm.wordlists[wid]` patch.

### 4. Release truth

The archive has no standards-based dependency lock, repository CI workflow,
hosted build provenance, or complete aggregate evidence manifest.  Package
version `0.0.8` and archive revision `0889` describe different axes, but their
relationship is not documented as policy.  A green local test suite is useful
evidence, not a reproducible release chain.

### 5. Contract-backed architecture cuts

At this revision, `src/micromax_editor/editor.py` is 25,628 lines and the
`Editor` class has 1,109 direct methods.  It owns 99 initialized state
attributes, including 14 authority-related sidecars.  `RuntimeRegistrationSnapshot`
has 40 fields.  These numbers are not merely aesthetic: they make it expensive
to prove that an effect is complete, scoped, and correctly rolled back.

A rewrite would destroy hard-won semantics.  The correct cut is contract-first:
extract one typed effect coordinator or plugin-host adapter behind preservation
tests, then reduce the original coordinator measurably.

## Places where the cloudtainer has gone wasteful

### Documentation became a second product

The rev0888 baseline contains 826 documentation files and 65,678 documentation
lines, versus 111 source files and 64,366 source lines.  There are 813 root
Markdown documents, 812 with numeric prefixes, and 745 numbered 100 or higher.
The revision index contains only 138 entries despite archive revision 888, and
recent work repeatedly appends a narrow lifecycle note.

The documentation is often good.  The waste is its storage model: one note per
micro-revision, repeated living-document preambles, and a curated installed-help
set that points into a much larger source-only history.  The result taxes search,
handoff, packaging truth, and future editing.

Corrective direction:

- keep a small set of living contracts;
- keep a machine revision ledger;
- bundle historical notes by epoch or subsystem;
- enforce a documentation-growth budget in `mxaudit`;
- stop using a new root document as the default proof that a small code change
  happened.

This file is retained because the user requested a deep datacube audit; its own
recommendation is that future sessions update this living audit or a bundled
ledger rather than continuing the one-note-per-revision pattern.

### Evidence orchestration is overgrown

`tools/mxtest.py` is more than 4,500 lines.  The project has sophisticated local
chunking and checkpoint machinery but no ordinary hosted CI lane.  This is a
cloudtainer optimization that has begun to compete with the product.  Keep the
resumable runner for constrained environments, but establish a small canonical
confidence ladder first: semantic/policy conformance, package/install, CLI and
subprocess, then aggregate release evidence.

### Snapshot breadth hides ownership mistakes

The 40-field broad registration snapshot has preserved correctness during
migration, but it also makes missing sidecars likely and snapshot cost grow with
unrelated state.  It should remain an oracle/fallback while each effect family
moves to typed capture/commit/abort behavior.  Deleting it before the effect
matrix exists would trade visible debt for silent regressions.

## Concrete defect repaired in rev0889

### Failure mode

`PluginManager._build_plugin()` snapshots `VmDictionarySnapshot` and
`RuntimeRegistrationSnapshot`.  VM definitions call
`Editor._stamp_vm_word_authority()`, which writes provenance into
`Editor._word_authority` keyed by `(wid, word-name)`.

Before rev0889, failed source or lifecycle rollback restored wordlists, modules,
search order, IDs, and runtime registrations, but not `_word_authority`.  A
failing plugin such as:

```text
: leaked-name 1 ;
unknownword
```

left no live `leaked-name` word, yet retained a provenance row for its transient
wordlist ID.  Repeating failures with fresh names grew the sidecar indefinitely.
Callback paths had separate explicit word-authority snapshots, which masked the
gap there but did not establish a dictionary invariant.

### Repair

`VmDictionarySnapshot` now carries optional `word_authority` state.
`snapshot_vm_dictionary_state()` obtains it from the editor owner, and
`restore_vm_dictionary_state()` restores it only after dictionary topology is
back in place, allowing `_restore_word_authority()` to filter against live words.
The duplicated callback-only restoration was removed; callbacks, source loads,
lifecycle hooks, failed reloads, and discarded deinit mutations now share the
same dictionary-plus-provenance boundary.

Regression tests assert exact word-authority equality across:

- failed initial plugin source evaluation;
- failed staged reload lifecycle evaluation;
- failed unload `deinit` after transient word definitions.

`mxaudit --check` now fails if dictionary snapshots stop carrying/restoring word
provenance.

## What should change next, in order

1. **Implement bounded retired-wordlist metadata.**  First add observability and
   liveness accounting; then replace retained executable wordlists with bounded
   tombstones after unload/reload.
2. **Create the executable effect matrix.**  Generate documentation and audit
   coverage from it; do not hand-maintain another prose-only inventory.
3. **Make extension interfaces explicit and versioned.**  Stable,
   experimental, and internal tiers; typed imports/exports; schema versions;
   feature negotiation.
4. **Split source/lifecycle transactions by typed effect family.**  Keep the
   broad snapshot as a differential oracle until parity tests pass.
5. **Add resource budgets.**  Bound guest-to-host payload size, output capture,
   pending callbacks/timers, document/buffer creation, and wall-clock host
   operations.  Instruction budgets alone do not bound blocking hostcalls.
6. **Establish release reproducibility.**  Add `pylock.toml` or another
   standards-based lock, focused hosted CI, package inspection, artifact
   digests, and build provenance.
7. **Compact documentation and evidence machinery.**  Measure deletion and
   consolidation as progress.
8. **Extract one contract-backed plugin/effect coordinator.**  Require a measured
   reduction in `Editor`, not merely a forwarding wrapper that leaves ownership
   unchanged.

## Online research and design implications

Research checked on 2026-06-18:

- VS Code runs extensions in dedicated local, web, or remote extension hosts and
  uses lazy activation to protect UI stability/performance.  Its Workspace Trust
  documentation also states plainly that Restricted Mode cannot stop a
  malicious installed extension that ignores it.  Micromax is correct to avoid
  calling its in-process policy a sandbox; a future extension host is a separate
  architectural boundary, not another capability flag.
- Zed extension manifests include `schema_version`, and procedural extension
  code is compiled to WebAssembly.  This supports separating declarative
  contribution data from procedural code and versioning the contract before
  isolation work.
- WebAssembly Interface Types describe component “worlds” as explicit imports
  and exports and model resources as owned or borrowed handles.  That is a good
  conceptual fit for Micromax buffers, documents, prompts, timers, and plugin
  generations: authority should travel with a typed handle rather than be
  rediscovered through ambient editor state.
- Wasmtime exposes fuel/epoch interruption and per-hostcall transfer fuel, but
  explicitly notes that guest fuel does not solve a blocking hostcall.  A future
  Wasm boundary would still require async host operations, timeouts, memory and
  payload limits, and cancellation policy.
- PyPA now specifies `pylock.toml` for reproducible Python installation.  SLSA
  provenance models an attestation tying artifact digests to a build definition
  and builder.  These are concrete standards for the missing release-truth lane.

Primary references:

- https://code.visualstudio.com/api/advanced-topics/extension-host
- https://code.visualstudio.com/docs/editing/workspaces/workspace-trust
- https://zed.dev/docs/extensions/developing-extensions
- https://component-model.bytecodealliance.org/design/wit.html
- https://docs.wasmtime.dev/api/wasmtime/struct.Store.html
- https://docs.wasmtime.dev/api/wasmtime/struct.Config.html
- https://packaging.python.org/en/latest/specifications/pylock-toml/
- https://slsa.dev/spec/v1.2/build-provenance

## Speculation: the strongest future shape

The strongest plausible Micromax is a **capability-first personal automation
kernel** with several hosts, not one ever-growing editor object.  The language
and VM remain small.  Hosts publish versioned effect worlds.  Extensions declare
capabilities and schemas before activation.  Declarative contributions require
no procedural runtime.  Procedural code receives typed, revocable resource
handles.  Effects produce compact journal records.  Historical provenance is
metadata, not retained executable state.  Headless models are generated from the
same schemas used by plugins and tests.

The weaker future is an editor whose correctness depends on remembering every
new mutable field in a broad snapshot and every new provenance sidecar in four
cleanup functions.  Rev0889 removes one symptom.  The next work should remove
the conditions that make the symptom recur.

## Evidence and non-claims

The untouched rev0888 archive passed 2,331 tests before modification.  Focused
rev0889 dictionary/provenance and audit tests pass.  A fresh full-suite result is
recorded in the revision handoff after all documentation/context changes.

This revision does not garbage-collect old committed wordlists, add process or
Wasm isolation, bound blocking hostcalls, create a dependency lock or CI system,
or make all plugin effects atomic.  It repairs one real rollback leak and records
the higher-leverage path.
