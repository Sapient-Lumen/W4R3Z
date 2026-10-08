# Rev0897 — cloudtainer mission audit and escaped timeout cleanup

Date: 2026-07-07

## Executive finding

The heart of Micromax remains **least-authority end-user automation with an
honest, recoverable host**.  The editor is not the destination; it is the stress
fixture.  Editing forces the system to confront exactly the state classes that a
small automation substrate must classify: declarations, reversible session
state, document edits, delayed work, durable state, filesystem effects,
subprocesses, and irreversible observations.

The project is strongest when it turns a boundary into executable behavior.  It
is weakest when the cloudtainer keeps adding prose, snapshots, and handoff
machinery faster than it deletes or consolidates them.  Rev0897 fixes one
cloudtainer-specific instance of that weakness: timeout tooling could kill the
direct tool child but leave nested pytest grandchildren alive when an inner tool
created its own process groups.

## What is missing

### One executable effect-lifecycle matrix

The repository already has capabilities, plugin grants, group/generation
snapshots, stale-generation guards, cleanup diagnostics, and release manifests.
It still lacks one generated table that says, for each public hostcall and owned
resource family:

- effect class;
- capability and trust precondition;
- provenance key;
- staged/committed/persistent status;
- load, callback, reload, unload, revoke, timeout, crash, and restart behavior;
- reversible versus irreversible consequence;
- public stability tier and schema version.

Without that table, correctness is still found by survivor audit.  The prior
word-authority leak and this revision's timeout-grandchild leak are the same
class of failure: an operation name sounded complete, but the implementation did
not own every object that operation could create.

### A versioned extension surface

Micromax should not freeze the current `Editor` object as the public extension
API.  The near-term target should be three tiers: stable tiny hostcalls,
experimental hostcalls that can change with revision notes, and internal helpers
that plugins cannot import.  The effect matrix should generate the stable and
experimental surface list.

### Bounded ownership beyond plugin state

Runtime plugin survivors have received the most attention.  The next budgets
should be host-owned limits for output capture, hostcall argument/result payloads,
prompt rows, buffer creation, subprocess/cancellation surfaces, and release-tool
process trees.  These are not glamorous, but they make in-process execution less
fragile before any Wasm or out-of-process extension host exists.

### Release provenance

Rev0895 and rev0896 improved local release evidence.  Remaining release truth is
more ordinary: lock dependencies, run a small hosted CI lane, inspect packages,
record artifact digests, and state how archive revisions relate to package
versions.

## What went severely wrong or wasteful

### The cloudtainer optimized the evidence lane until it became a product

The repository has hundreds of revision documents, a large release/test runner,
and a sophisticated short-window lane.  Those tools are useful, but their cost is
now visible in audit metrics: docs and evidence machinery compete with the small
language/editor host for attention.  Future revisions should count deletion,
compaction, and contract generation as progress.

### Timeout ownership was incomplete

`tools/mxtoolrun.py` used a separate process group for its direct child and killed
that group on timeout.  That was not enough for nested handoff tools.  `mxdoctor`
can create its own subprocess groups for pytest children; once those pytest
processes are in new groups, killing only the outer `mxdoctor` group does not
necessarily reap them.  In a constrained cloudtainer, that can leave CPU-heavy
pytest grandchildren running after the supervising tool has already reported or
been interrupted.

The bug mirrors the main product's security lesson: **authority is not owned
because an outer wrapper says it is owned**.  It is owned only when the concrete
resource handles are enumerated and tested.

## Rev0897 repair

`mxtoolrun.terminate_process()` now performs best-effort POSIX descendant cleanup
before signaling the direct child group.  On Linux it snapshots `/proc`, finds
current descendants of the supervised child, signals descendant process groups
that escaped the direct group, deduplicates groups, avoids the runner's own
process group, then signals the direct child/group.  The KILL path repeats the
same process-tree cleanup if TERM does not finish the direct child.

The regression test creates a child that forks a grandchild into a new session,
then proves that `run_captured()` timeout returns `124` and the detached
grandchild no longer remains alive.

## Online research implications

VS Code's extension architecture is a useful comparison but not a destination:
it documents multiple extension hosts, including local, web, and remote hosts,
and says the extension host is responsible for running extensions while keeping
misbehaving extensions from hurting startup/UI responsiveness.  Its Workspace
Trust model also explicitly treats unfamiliar code as risky and disables or
limits automatic execution in Restricted Mode, while warning that this is not a
complete defense against malicious extensions.

The relevant lesson for Micromax is not "copy VS Code."  It is: trust state,
extension location, and extension capabilities need to be explicit product
concepts, not implicit side effects of the editor object.

WASI and the WebAssembly Component Model are relevant later, after Micromax knows
which effects it is trying to host.  The Component Model frames components as
running against well-defined APIs supplied by a platform; WASI Preview 2 is a
stable WIT-defined API set, and WASI Preview 3 work is moving toward async and
stream support.  That suggests a future isolation path, but only after the
Micromax hostcall/effect contract exists.

Starlark is the closest language-design warning sign: it is small, embeddable,
deterministic, hermetic by default, and intentionally limits Python-like features
that complicate analysis.  Micromax can remain concatenative, but it should keep
Starlark's discipline: small semantics, host-controlled effects, and tooling as a
first-class design goal.

Recent VS Code extension-ecosystem research reinforces the risk: large extension
ecosystems routinely expose users to suspicious behavior, data exposure, and
cross-extension risks.  Micromax's least-authority premise is therefore still
worth pursuing, but the project should resist claiming safety from in-process
policy alone.

Research sources reviewed in this audit:

- VS Code Extension Host documentation: https://code.visualstudio.com/api/advanced-topics/extension-host
- VS Code Workspace Trust documentation: https://code.visualstudio.com/docs/editing/workspaces/workspace-trust
- WebAssembly Component Model introduction: https://component-model.bytecodealliance.org/
- WASI repository status notes: https://github.com/WebAssembly/WASI
- Starlark overview/specification: https://starlark-lang.org/ and https://bazel.build/rules/language
- arXiv 2411.07479, VS Code extension ecosystem analysis: https://arxiv.org/abs/2411.07479
- arXiv 2412.00707, VS Code extension data exposure analysis: https://arxiv.org/abs/2412.00707

## What should change next

1. **Make timeout/process ownership a first-class evidence surface.** Add a small
   audit check that the shared runner still has descendant-process cleanup and
   keep nested-timeout tests in the short tool lane.
2. **Create the first generated effect-matrix slice.** Start with a small family,
   such as timers or prompt interactions, and generate docs plus audit coverage
   from live code metadata.
3. **Add one host-owned payload/output budget.** Output capture and hostcall
   result size are the best next candidates because they affect both plugins and
   cloudtainer tooling.
4. **Consolidate revision notes by subsystem.** Keep the revision index, but
   bundle old docs by epoch.  New prose should update living contracts unless a
   revision introduces a genuinely new boundary.
5. **Lock and verify the package path.** Add a dependency lock, small CI, package
   inspection, and artifact digests before expanding release-runner complexity.
6. **Extract one contract-backed host owner from `Editor`.** Only extract a
   surface after the effect matrix identifies its state, policy, and rollback
   behavior; do not create another forwarding facade.

## Speculation

The strongest future shape is a tiny automation kernel with a generated host
contract: Micromax code declares effects; host adapters decide which effects are
available; every reversible effect has an owner and journal; irreversible effects
are labeled honestly; and editor plugins become only one host profile.  A Wasm or
separate-process runtime could later enforce some boundaries, but it should be an
implementation of the matrix, not a substitute for the matrix.

## Evidence

- `PYTHONPATH=src python3 tools/mxlint.py` → pass.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxtoolrun.py tests/test_mxtimely.py tests/test_mxrelease.py::test_batch_timing_summary_reports_slowest_batches tests/test_mxrelease.py::test_next_action_for_partial_manifest_is_copy_pasteable tests/test_mxcontext.py tests/test_revision_index.py tests/test_docs_living_hygiene.py` → 23 passed.
- `PYTHONPATH=src python3 tools/mxcontext.py --check` → rev0897 context pass.
- `PYTHONPATH=src python3 tools/mxaudit.py --check` → pass.
- `PYTHONPATH=src python3 tools/mxportable.py --quiet` → 156/156 cases passed.
- `PYTHONPATH=tools:src python3 tools/mxtimely.py --skip-doctor --skip-tests --summary-json .artifacts/mxtimely-summary.json` → pass; summary records rev0897.
- Manual reproduction after the fix: `mxtoolrun.run_captured(... tools/mxdoctor.py ..., timeout_seconds=5)` returned timeout `124` and left no `mxdoctor`/`pytest` descendants alive.

This revision does not claim a full release verification, a new sandbox, or any
runtime plugin-security semantic change.
