# Rev0856 — cloudtainer mission, context diet, and threat-boundary audit

## Executive finding

Micromax's strongest idea is not “a small terminal editor.” It is **least-authority
end-user programmability**: one small language serving as config, macro, and
plugin substrate inside a host that makes effects visible, attributable, and
recoverable.

The project has real evidence for that idea. It also accumulated a second system
around it: hundreds of micro-revision notes, a giant “compact” context manifest,
and a sophisticated aggregate-test checkpoint runner. Those supports became large
enough to obscure the mission and tax every cloudtainer handoff.

Rev0856 makes one immediate correction: restore a small living context and vision
without deleting the full archive or weakening validation.

## Incoming measurements

The rev0855 archive contained roughly:

- 1,120 archive entries;
- 786 Markdown documentation files and 301 Python files;
- 7.3 MB of docs versus 2.2 MB of runtime source and 1.9 MB of tests;
- a 42,371-byte `mxcontext --json` payload listing 660 documentation paths;
- a 1,371-line context generator dominated by static path lists;
- a 269-line context test and a 162-line archive test dominated by individual
  path assertions;
- a 24,084-line `editor.py`, including an `Editor` class around 23,138 lines;
- multi-thousand-line hostcall, core-word, and docs-cues builders;
- 2,220 passing selected tests in the carried 64-chunk aggregate manifest, with
  about 740 seconds of accumulated chunk runtime.

These are audit measurements, not product goals.

## What had gone severely wrong

### 1. The compact handoff became a duplicate catalog

`tools/mxcontext.py` described itself as a short, stable context snapshot while
listing most of the documentation corpus. The full revision ledger already
existed in `docs/revision-index.json`; repeating it made every JSON handoff larger
and made each new note require more test churn.

Worse, the tests institutionalized the duplication by asserting hundreds of
individual historical paths. The anti-drift mechanism had become context drift
with a passing test suite.

Rev0856 replaces enumeration with:

- a small set of durable design and operation entrypoints;
- the newest 12 revision-index entries, derived automatically;
- explicit inventory counts for the omitted corpus;
- pointers to the revision and installed-help catalogs;
- size/count ceilings and invariants instead of historical-path assertions.

### 2. The living vision was front-loaded with archaeology

The actual vision began after 298 lines of old revision notes. That preserved
history but inverted the reading order. The old text is now archived under
`docs/history/`; `docs/00-vision.md` begins with the current mission, security
truth, non-goals, and decision rules.

### 3. Proof machinery risks becoming a second product

`tools/mxtest.py` is valuable: bounded, resumable evidence is much safer in a
cloudtainer than one monolithic pytest stream. Yet the evidence path now has its
own large command surface, checkpoints, dependency inference, doctor wrappers,
and extensive tests. The project should measure proof cost and keep a fast
semantic/conformance lane separate from packaging, subprocess, and CLI probes.

The target is not fewer tests. It is **a clearer confidence ladder**:

1. seconds: VM semantics, capability policy, pure editor models;
2. minutes: editor integration and plugin lifecycle;
3. explicit release lane: packaging, installed resources, subprocess/CLI, full
   aggregate evidence.

### 4. Capability language overstates the current containment model

The implementation is thoughtful but in-process. Capability bits are editor
options reflected into VM host features. The filesystem root is explicitly a
best-effort pragmatic boundary. Step budgets bound VM instructions, not Python
memory, native blocking, or all hostcall time.

This is useful least-authority engineering, but not a hostile-plugin sandbox.
The distinction must be visible at the product landing, not discoverable only in
source comments and historical revision notes.

## What's missing, in priority order

### A. A threat model and trust states

Define actors and assets: user config, workspace files, installed plugins,
workspace plugins, persisted state, secrets, files outside the project, shell,
network, clipboard, and editor integrity. Define what “trusted,” “restricted,”
and “denied” mean at startup and at each grant.

The most important near-term product state is a workspace/config restricted mode:
unfamiliar repositories should be browseable without automatically evaluating
workspace-controlled code.

### B. Per-extension grants and revocation

Current host-configured capability options are too coarse for a mature ecosystem.
A future grant record should include plugin identity, capability, scope/root,
issuer, duration, provenance, and revocation state. Same-process enforcement may
remain initially, but the data model should be ready for a separate extension
host.

### C. A versioned public extension contract

Separate public API from internal hostcalls. Version:

- lifecycle hooks and failure semantics;
- capability names and parameter schemas;
- model/row schemas;
- persistence ownership and migration;
- compatibility and deprecation rules.

A WIT-like contract discipline is useful even before Wasm is used.

### D. Normative language and conformance

`docs/21-language-spec-sketch.md` is explicitly non-normative. Promote a small
versioned core: parsing, literals, stacks, quotations, lookup/search order,
errors, budgets, and hostcall behavior. Keep the Python VM as reference oracle,
but make ports conform to observable cases rather than implementation structure.

### E. Reproducible builds and release provenance

`requirements-dev.txt` and `pyproject.toml` currently use broad lower bounds, and
bootstrap installs can resolve different tool versions over time. Add a standard
lock file for supported environments, build in CI, record the source revision and
build inputs, and attach checksums/provenance to released archives.

The archive's context manifest is useful handoff metadata; it is not yet signed
build provenance.

### F. Stable schemas for headless truth

Rev0855 found a real empty-state schema drift in docs cues. Convert important
headless payloads from organically assembled dictionaries/lists into canonical
TypedDict/dataclass/JSON-schema-like contracts with explicit schema versions.
Test active, empty, denied, error, and compatibility cases from one source of
truth.

### G. Monolith reduction with budgets

The biggest coordinators should have explicit size/responsibility budgets:

- `Editor` owns orchestration, not every model and formatter;
- hostcalls install by coherent capability family;
- docs cues split into parsing, indexing, geometry, and aggregation only behind
  preservation fixtures;
- core words install from table-driven specifications where semantics permit;
- test evidence code exposes a small stable CLI and keeps internals modular.

Do not perform a broad rewrite. Each extraction needs a behavior-preserving test
and a measurable reduction in responsibility.

## Online research anchors and implications

External systems suggest useful boundaries, not templates to copy wholesale.
The pages below were checked on 2026-06-18.

- [VS Code Extension Host](https://code.visualstudio.com/api/advanced-topics/extension-host)
  separates extension execution from UI work to protect stability/performance.
  Micromax should eventually isolate untrusted or failure-prone extensions from
  the editor coordinator.
- [VS Code Workspace Trust](https://code.visualstudio.com/docs/editing/workspaces/workspace-trust)
  treats opening unfamiliar source as different from authorizing code execution.
  Micromax lacks this first-class trust state.
- [WIT worlds](https://component-model.bytecodealliance.org/design/worlds.html)
  describe imports and exports as a precise component contract. This maps well
  to capability-scoped plugin APIs once the native contract is stable.
- [WASI](https://wasi.dev/) is designed as a secure standard host interface for
  Wasm components. A future extension host could expose only Micromax-specific
  and selected WASI imports, but Wasm is not a substitute for defining policy.
- [SLSA Build Track](https://slsa.dev/spec/v1.2/build-track-basics) distinguishes
  “provenance exists” from signed and hardened build provenance. Micromax should
  first make builds reproducible and automatically record inputs.
- [PyPA `pylock.toml`](https://packaging.python.org/en/latest/specifications/pylock-toml/)
  standardizes dependency locks for reproducible Python installation.
- [Language Server Protocol](https://microsoft.github.io/language-server-protocol/)
  avoids reimplementing language intelligence in every editor. LSP should remain
  an optional process adapter rather than growing bespoke equivalents in `Editor`.
- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) provides incremental
  concrete syntax trees. It is a candidate for syntax-aware editing after the
  current markdown/docs-specific model boundary is clean.
- [Forth standard purpose](https://forth-standard.org/standard/intro) emphasizes
  observable portability. Micromax should borrow that discipline without
  claiming standards conformance.

## Staged correction

### Now

- Keep living docs short and catalog-backed.
- Publish the application-boundary-versus-sandbox distinction.
- Add context size/count budgets.
- Preserve the current aggregate manifest and focused regression lanes.

### Next

- Write `docs/security-boundaries.md` and a stable/experimental API matrix.
- Introduce schema versions for headless models.
- Add a lock file and minimal CI build/test/provenance workflow.
- Split a fast semantic suite from slow release integration.
- Extract one coherent hostcall family and one docs-cues sub-builder.

### Later

- Add restricted workspace mode and grant records.
- Move extension execution to a recoverable process boundary, or prototype a
  Wasm Component host with explicit imports.
- Add optional LSP/Tree-sitter adapters based on real editor needs.
- Publish a conformance suite usable by a second VM implementation.

## Product speculation

The plausible niche is “more programmable than a nano-like editor, much smaller
than an IDE, and more explicit about authority than arbitrary embedded Python or
Lua.” The editor itself can stay modest if the runtime, extension contract, and
headless model are unusually trustworthy.

The failure mode is feature-by-feature accretion: hundreds of tiny commands,
metadata rows, revision notes, and tests can create impressive local coverage
without producing a stable public product. Future revisions should report which
contract became clearer, which authority was reduced, or which user loop became
better—not merely which counter increased.

## Rev0856 evidence target

This revision intentionally avoids runtime behavior changes. Validation should
cover lint, context/revision/archive invariants, living-doc hygiene, package
resource behavior, and refreshed aggregate evidence for changed tooling/tests/docs.
