# Cloudtainer mission, stale-roadmap, and headless-contract audit (rev0958)

## Executive judgment

The heart of Micromax is **least-authority end-user automation embodied in a
calm editor**. One small language is meant to be configuration, macro, and
plugin substrate; the host is meant to make effects explicit, provenance
visible, failure recoverable, work finite, and behavior inspectable without a
terminal renderer.

The shortest useful product test remains:

> Can a person trust this editor enough to inhabit it, understand what automation
> did, and recover when it fails?

That is stronger than “small Forth,” “micro-like editor,” or “many passing
tests.” The archive contains unusually thoughtful trust engineering. It also
contains evidence that its supporting machinery and sparse model surfaces have
started competing with the product.

Rev0958 makes one immediate course correction: stale installed roadmap and
decision pages are replaced with current guidance and added to executable
freshness checks. It does not pretend that the larger architecture and product
gaps are solved.

## What is already strong

- A host-neutral replayable VM and 156-case portability corpus provide a real
  semantic oracle.
- Restricted startup, captured callback/keybinding authority, package-bound
  grants, scoped cleanup, and an explicit threat model keep the in-process claim
  unusually honest.
- Startup, destructive exit, buffer creation, project-file discovery, query
  replacement, and archive publication increasingly use exact witnesses rather
  than mutable labels.
- The generated `micromax.effect-resource-contract.v1` table gives 23 high-risk
  effects and retained owners a current machine-derived landing.
- The archive collects 2,595 tests, has bounded/resumable evidence lanes, and
  refuses internally inconsistent revision archives.

Those are foundations worth preserving. The next phase should make them serve
ordinary editing more directly rather than multiplying adjacent proof objects.

## Measured allocation in the received rev0957 archive

`mxaudit --json` and direct archive inspection reported:

| Area | Files | Lines | Bytes |
| --- | ---: | ---: | ---: |
| Documentation | 904 | 76,782 | 8,571,730 |
| Runtime source | 114 | 75,679 | 2,956,464 |
| Tests | 212 | 63,116 | 2,243,456 |
| Repository tools | 16 | 12,476 | 546,651 |

The central `Editor` class spans 28,220 lines inside a 29,695-line module, has
1,282 methods, initializes 100 state attributes, and exposes 112 lifecycle
helpers. The plugin runtime snapshot has 47 fields. Other single definitions
remain very large: `install_editor_hostcalls()` is 2,659 lines,
`docs_cues_model_from_parts()` is 1,928, and `install_core_words()` is 1,731.

These are measurements, not automatic refactoring instructions. They show that
coordination and ownership are still encoded through repetition and reviewer
memory.

## What is missing

### 1. Complete lived product journeys

The strongest tests are often narrow policy regressions. The archive itself
names the missing user-level contracts:

- failed save through retained dirty state, recovery persistence, restart,
  restore, dismissal, and feedback;
- restricted plugin scan through denial, provenance, explicit grant, reload,
  revocation, and cleanup;
- one designed highlight precedence across edit, selection, search, prompt,
  status, help, and diagnostics;
- observed repeated search/edit/selection/multicursor/macro loops.

A daily-driver editor is proved by coherent journeys, not by the number of
inspectable micro-surfaces.

### 2. A compact, versioned headless product contract

The current `--dump-screen 24 80` result for a blank scratch buffer was 214,604
bytes. `docs_cues` alone occupied about 115 KB. That object had 192 top-level
keys; each of 22 visible rows had 193 keys. A representative blank row contained
91 empty lists, 97 zero integers, and four empty strings.

The model is internally rich, but the command presented as headless inspection
serializes a sparse diagnostic cube. This creates four problems:

1. humans and small tools cannot easily see the actual screen;
2. every new cue can become a new public-looking field and regression burden;
3. compatibility is undefined because the row schemas are unversioned;
4. empty/default metadata consumes most of the artifact even when no docs cue is
   active.

Headless truth needs two layers: a compact stable product view and an opt-in
full diagnostic graph. The compact layer should have explicit byte and field
budgets plus a schema version.

### 3. One typed retained-resource owner graph

Micromax has spent many revisions finding one more survivor: marks, search,
prompt history, recent files, palette MRU, saved cursors, clipboard, help
history, recovery stacks, options, macros, timers, interactions, wordlists, and
query replacement. The fixes are often correct, but the recurring shape is the
signal.

Each retained object needs the same small facts: identity, origin, authority,
lifetime, cleanup trigger, rollback scope, disclosure policy, and resource
budget. A typed owner record or effect journal should make those facts explicit.
The first implementation should replace one narrow owner family and reduce code;
it should not become a universal framework before proving that result.

### 4. Ordinary release truth

The archive has no CI workflow, dependency lock, complete carried release
manifest, or reproducible-build attestation. Two wheel builds from the same tree
produced different SHA-256 digests; their file contents matched, while six
`dist-info` member timestamps differed. The Python package remains `0.0.8`, the
host API reports `0.1`, and the archive is rev0957, with no public rule connecting
those identities.

The current archive verifier is valuable internal-consistency evidence. It is
not a public release provenance or reproducible-build claim.

### 5. A process model that matches current Python

The bounded doctor passed, but Python 3.13 emitted repeated warnings that
`fork()` from a multithreaded process can deadlock. Current project-file workers
already prefer isolated contexts; legacy short filesystem workers do not.
Migration is now compatibility work, not speculative hardening.

### 6. Current installed navigation

The received installed `docs/40-roadmap.md` still described rev1-rev10, carried a
“Rev58 checkpoint,” and said terminal UI implementation was “later.” The
installed `docs/41-decisions-log.md` stopped around rev299-rev302. The product is
rev0957 and has a working curses TUI.

This was severe because both files are packaged as help and listed in curated
context. A future operator could follow passing handoff checks and still read a
false product sequence. The prior freshness audit checked five living entrypoints
but omitted these two installed guidance pages.

## What has gone severely wrong or wasteful

### Installed archaeology masqueraded as current direction

History preservation is good; history in the current roadmap is not. The old
pages are now archived verbatim under `docs/history/`, while current pages state
outcomes, durable decisions, open decisions, and non-goals.

### “Headless truth” accumulated into sparse schema debt

The docs-cue model began as a way to move renderer knowledge into inspectable
state. Hundreds of narrowly additive fields later, a blank screen pays the full
schema cost. The mistake is not making cues inspectable. It is treating every
internal diagnostic facet as if it belonged in one always-expanded product
payload.

### The survivor audit became a development rhythm

One-owner-at-a-time fixes repaired real authority and cleanup defects. Repeating
that rhythm indefinitely will keep enlarging `Editor`, plugin snapshots, audit
heuristics, revision notes, and focused tests. The next corrective unit is one
owner abstraction that demonstrably deletes repetition.

### Evidence and documentation became a parallel product

The docs are often good and the runners solve real cloudtainer constraints. The
waste is the storage and change model: 904 documentation files, 881 numbered root
docs, 12,476 lines of repository tools, and one revision note for many tiny
metadata additions. The project can preserve forensic history while bundling
related changes into outcome revisions and keeping installed help small.

### Internal correctness outpaced external product reality

The archive proves many invariants but contains no equivalent evidence that a
person used the editor for sustained daily work, that common loops became faster,
or that the screen hierarchy is pleasant. This is an inference from the archive,
not a claim that no such use occurred. Future product decisions should carry a
small transcript, scenario, or measured interaction cost when practical.

## What should change, in order

### Now

1. Finish the save/recovery journey.
2. Specify a compact screen schema with an explicit version and budgets; retain
   the full model under an explicit diagnostic mode.
3. Complete the restricted-plugin journey.
4. Remove remaining multithreaded-fork warnings through isolated workers.
5. Establish one restrained reference highlight precedence.

### Architecture next

1. Choose one retained resource family and replace its bespoke
   snapshot/restore/retag/remove set with a typed owner/journal seam.
2. Measure whether code, snapshot breadth, and audit heuristics shrink.
3. Classify hostcalls, lifecycle rows, and models as stable, experimental, or
   internal.
4. Extract coordinator policy only behind already-pinned behavior.

### Release next

1. Add CI by reusing current context, audit, lint, portability, focused journey,
   wheel, and archive-verification commands.
2. Set a declared build epoch/environment and make two wheels bit-identical.
3. Emit a small provenance statement containing source and artifact digests,
   builder identity, command, and environment.
4. Decide how package, host API, and archive versions relate.

### Stop doing

- Do not add another top-level screen field for every inspectable distinction.
- Do not solve each new retained resource only with a larger global snapshot.
- Do not call a local focused manifest “release” evidence.
- Do not leave historical prose in installed current-guidance slots.
- Do not begin process/Wasm isolation before the extension boundary is smaller
  and versioned.

## Online research implications

The following current primary sources reinforce, rather than replace, the local
measurements:

- Python's multiprocessing documentation says POSIX defaults changed to
  `forkserver` in Python 3.14 and notes the multithreaded-`fork` deprecation:
  <https://docs.python.org/3/library/multiprocessing.html>. The project's warning
  is therefore a forward-compatibility signal, not cosmetic noise.
- VS Code separates extensions into extension-host processes for stability, but
  its runtime-security documentation says an extension host has the editor's
  permissions; Workspace Trust limits automatic execution but cannot make a
  malicious installed extension obey restricted mode:
  <https://code.visualstudio.com/api/advanced-topics/extension-host>,
  <https://code.visualstudio.com/docs/configure/extensions/extension-runtime-security>,
  and <https://code.visualstudio.com/docs/editing/workspaces/workspace-trust>.
  Micromax is right to distinguish application policy from hostile-code
  containment.
- WebAssembly Component Model WIT defines explicit interfaces, worlds, and
  resources: <https://component-model.bytecodealliance.org/design/wit.html>.
  It is a useful model for a future extension boundary only after Micromax's
  current imports/exports and resource ownership are made smaller and versioned.
- JSON Schema Draft 2020-12 provides a standard vocabulary for validating JSON
  contracts: <https://json-schema.org/draft/2020-12>. A schema should validate
  the compact headless contract; it should not canonize the current 193-field
  sparse row.
- Reproducible Builds defines a reproducible build as one whose outputs are
  bit-for-bit identical given the same source, environment, and instructions:
  <https://reproducible-builds.org/docs/definition/>. SLSA defines provenance as
  verifiable information about where, when, and how an artifact was produced:
  <https://slsa.dev/spec/v1.2/provenance>. Both are stronger and more useful
  public release claims than an internally consistent filename alone.
- OWASP API4:2023 treats unrestricted resource consumption as a security risk:
  <https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/>.
  Micromax's budget work is well aligned; the remaining opportunity is to make
  budget ownership declarative rather than family-by-family.
- Capability-security literature frames least authority as granting only the
  authority needed for a task. A useful historical anchor is Miller et al.,
  “Paradigm Regained”: <http://erights.org/talks/asian03/paradigm-revised.pdf>.
  The project should keep this principle visible without overstating what an
  in-process Python host can enforce.

## Speculation: the strongest future shape

The strongest product is not a miniature clone of a larger editor. It is a calm,
inspectable instrument with a small automation language and a host that can
answer, for every delayed effect:

- who created it;
- what authority it retained;
- what resource it owns;
- what bounds apply;
- how it is observed, revoked, and cleaned up;
- what recovery remains after failure.

A plausible long-term architecture is:

1. a tiny VM semantic core;
2. a headless editor model oracle;
3. a compact versioned host “world” of effects and resource handles;
4. one reference curses renderer;
5. optional extension isolation in another process or a Wasm component.

The distinctive advantage would be understandable automation, not extension
count. The immediate path to that future is subtraction: compact the public
model, unify one owner family, finish the ordinary journeys, and let visual taste
catch up with the trust machinery.

## Validation in this cloudtainer

- Living-doc, revision-index, context, and generated-effect-contract tests: 16
  passed.
- Structural-audit tests: 2 passed; installed-resource tests: 2 passed.
- Archive-lineage and corruption-policy tests: 30 passed.
- `mxcontext --check`, `mxaudit --check`, `mxlint`, and all 156 portability
  cases passed.
- The four-step skip-doctor timely lane completed with current rev0958 evidence.
- Doctor's bounded groups passed 19, 9, and 3 tests. Python 3.13 still emitted
  the multithreaded-`fork` warnings recorded above.

No full-suite claim is made. The full 2,595-test corpus was collected during the
audit, not completed after this revision.

## Rev0958 correction

- Archived the received roadmap and decisions pages through rev0957.
- Replaced both installed pages with current outcome and durable-decision views.
- Added both pages to the structural current-revision audit.
- Added living-doc size/history/stale-phrase regressions.
- Refreshed the handoff, revision index, generated effect contract, and context.

This revision changes guidance and evidence freshness, not runtime editor
behavior. No full-suite or hostile-code-isolation claim is made.
