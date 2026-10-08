# Rev1000 — mission, product reality, and evidence-honesty audit

Date: 2026-08-01

This audit reads the rev0999 datacube as a whole rather than treating its latest
optimization as the project. It combines repository measurements, living and
historical design notes, source and test structure, release artifacts, current
first-contact surfaces, and external research. Speculation is labeled. No legal,
security-sandbox, cross-platform, public-release, or user-adoption claim follows
from this document.

## Executive judgment

The heart of Micromax is:

> **a calm, inhabitable editor whose automation is understandable,
> least-authority, attributable, bounded, recoverable, and inspectable without a
> terminal renderer**

The language and replayable VM are not separate products competing for priority.
They are the editor's configuration, macro, and extension substrate. The editor
is not merely a demo for the VM either. It is the pressure test that forces the
host boundary to become honest.

The project has become unusually strong at **trust engineering**. It can describe
who owns a delayed effect, which generation is authoritative, what work is
bounded, how failure is surfaced, what is reversible, and which evidence supports
which claim. That is rare and valuable.

The severe problem is trajectory, not one catastrophic defect. Micromax has
built an exceptional trust laboratory faster than it has built proof that the
editor is pleasant to adopt, easy to learn, preferred for real work, or even
coherently presented on first contact. The proof system, revision ritual, and
32,000-line coordinator now risk becoming the product that receives the most
care. The editor can remain locally correct while the mission fails globally.

Rev1000 therefore should be read as a pivot marker:

1. preserve the hard-won trust model;
2. make evidence state honest instead of equating a configured lane with a
   current receipt;
3. repair first-contact product truth;
4. move the next sequence toward sustained use, taste, and flow;
5. simplify only where a narrow owner, second consumer, and net deletion are
   demonstrated; and
6. defer a Wasm/process extension host until a compact public contract exists.

## What was read and measured

The incoming archive contained 1,539 files. The executable structural audit and
additional repository scans reported:

- 995 documentation files, 91,471 text lines, and 9.69 MB;
- 136 source files, 96,989 text lines, and 3.74 MB;
- 278 test-tree files, 86,568 text lines, and 3.04 MB;
- 36 tool files, 23,277 text lines, and 0.95 MB;
- 925 Markdown files directly under `docs/`, including 924 numbered notes and
  856 whose numeric prefix is 100 or greater;
- 248 machine-indexed revision entries;
- 273 `tests/test_*.py` files, about 3,296 test functions, and 19,445 Python
  `assert` statements;
- `src/micromax_editor/editor.py` at 34,506 lines;
- the `Editor` class at 32,796 lines, 1,382 direct methods, and 112
  `self` attributes initialized in `__init__`; and
- `RuntimeRegistrationSnapshot` at 47 fields.

The most useful longitudinal comparison is rev0873's own structural audit. At
that point `editor.py` was 25,363 lines, `Editor` had 1,100 methods and 99
initialized attributes, and the docs tree had 810 files. By rev0999:

- `editor.py` grew by 9,143 lines, about 36.0 percent;
- direct `Editor` methods grew by 282, about 25.6 percent;
- initialized state attributes grew by 13, about 13.1 percent; and
- documentation files grew by 185, about 22.8 percent.

That earlier audit already said coordinator gravity and documentation/evidence
maintenance were dangerous. The warning was accurate, but the repository did
not convert it into an enforceable change in trajectory.

The carried `.artifacts/mxrelease-full-suite.json` provided another important
signal. Before rev1000 it was a partial rev0991-era checkpoint: 1 of 65 batches
had passed, 4 of 260 files had run, and 12 tests had passed. Its test inventory
and source digest no longer matched the repository, which now has 273 test
files. `mxrelease --verify` could report that drift, but normal `mxaudit` output
said only that one manifest and a full-suite runway were present. A human could
therefore see infrastructure presence without seeing evidence currency,
completeness, or pass state.

First-contact text was similarly split between present reality and archaeology:

- the README opened with a dense rev0999 transport optimization and did not reach
  a runnable command until line 151;
- package metadata called the project a “micro-esque editor prototype”;
- the command-line help used the same prototype language;
- the line REPL greeted users as a prototype;
- the package docstring said the project was not a full editor yet;
- the `Editor` docstring said the goal was to “steadily steal” features from
  Micro; and
- `docs/70-tutorial.md` was still a draft claiming the repository focused on the
  language/VM first and that the editor was not a full TUI.

Those statements were once reasonable. In rev0999 they were false product
positioning.

## The heart of the mission

Micromax has three nested missions. They should not be confused.

### Product mission

Build a calm editor people can trust and choose to inhabit. “Calm” means the
ordinary loop is legible: start, open, move, search, edit, save, recover, extend,
and quit. It does not mean sparse features or silent failure. It means visible
hierarchy, bounded surprise, and recovery without drama.

### Automation mission

Let people configure and automate the editor without granting every script or
extension ambient authority. Effects should be named, policy-controlled,
provenance-carrying, resource-bounded, and inspectable. A later physical keypress
must not launder the authority of the plugin that registered the action.

### Systems mission

Provide a small replayable semantic oracle and compact public contracts from
which other hosts or implementations can be built. Python is an implementation
and research vehicle, not the definition of the portable product.

The order still matters:

1. **Trust** makes normal work safe, predictable, and recoverable.
2. **Taste** makes the editor coherent and worth returning to.
3. **Flow** makes repeated work fast enough that users stay in the instrument.

The project has repeatedly stated this order. Its actual allocation of attention
has over-optimized the first item and under-measured the latter two.

## What is genuinely strong

### Headless truth is a real differentiator

The compact screen contract, status/prompt models, exact journey tests, and
renderer-independent editor semantics are not mere test conveniences. They make
behavior observable without terminal scraping and reduce the chance that the TUI
becomes a second source of truth. This can support accessibility tooling,
alternative renderers, remote control, deterministic demos, and future ports.

### Authority follows delayed work

The repository takes provenance seriously across commands, actions, keymaps,
hooks, timers, prompts, query-replace, recovery, plugin generations, and cleanup.
This directly serves the end-user automation mission. Many extension systems
make registration easy and lifecycle truth implicit; Micromax does the opposite.

### Failure and resource ownership are unusually explicit

Process construction, target readiness, operation deadlines, result framing,
teardown, exact source generations, recovery records, regex workers, and
allocation-amplifying hostcalls have named owners and bounded failure behavior.
The project generally refuses to call external effects atomic or an in-process
capability policy a hostile-code sandbox.

### The repository preserves dissenting evidence

Recent audits often record what remains unproved: page-cache charge, child
materialization, filesystem assumptions, incomplete hosted evidence, pointer
vectors, cross-platform gaps, or non-atomic external effects. That discipline is
worth keeping. The correction is to make it cheaper and more product-directed,
not to abandon it.

## What is missing

### 1. Product proof

There is extensive proof that individual semantics are exact and bounded. There
is little durable proof that a person can adopt the editor and complete useful
work comfortably over repeated sessions.

Missing evidence includes:

- a first-run transcript from installation to first saved edit;
- five or more sustained dogfood sessions with tasks, friction, workarounds, and
  return behavior recorded;
- a measured “time to first successful edit/save/help” journey;
- a coherent default workspace and discoverable help loop;
- evidence that users understand restricted versus trusted startup;
- taste review across terminal sizes and common color capabilities;
- flow measurements for open/switch/find/replace/repeat/edit loops; and
- an external user or second maintainer who can succeed without repository
  archaeology.

This is the largest mission gap. A full test suite cannot substitute for it.

### 2. A coherent first-contact story

The repository knows its mission, but the initial surfaces did not. A user should
not have to read a transport-memory benchmark before learning how to launch the
editor. The editor, language, headless contract, and capability model need one
short current narrative.

Rev1000 corrects the most misleading labels, but the next product revision should
also test the actual blank-start experience. A clean screen can still be
undiscoverable. The smallest likely improvement is a restrained, dismissible
first-buffer hint or a clearly visible help affordance driven by the shared
headless model—not a tutorial framework or telemetry system.

### 3. Taste and flow criteria

The repository has many feature contracts but no compact product scorecard. A
useful scorecard could stay tiny:

- startup reaches editable state without unexplained noise;
- help is reachable and useful within one action;
- open/switch/search/save each have a direct default path;
- repeated search and file switching preserve context;
- errors name the failed operation and next action;
- 80x24 and a narrow terminal preserve hierarchy rather than merely fit; and
- a real task can be completed without opening repository documentation.

The purpose is not numerical vanity. It is to stop proof work from winning every
priority discussion merely because it is easier to formalize.

### 4. Current release evidence

The configured hosted lane is not an executed release. A partial manifest is not
complete-suite evidence. An attestation workflow is not a verified consumer
receipt. GitHub's own artifact-attestation documentation says consumers must
verify the attestation and evaluate their policy; attestations link artifacts to
source/build instructions but do not make artifacts secure by themselves.

The project already says this in prose. Rev1000 makes the state visible in the
normal structural audit. The remaining work is execution: produce retained
subjects, download them, verify identity and subject digests from a consumer
context, and publish only the claims that survive.

### 5. A compact public extension contract

Micromax has many internal hostcalls and lifecycle surfaces, but the stable
public “world” is not yet small enough to isolate cleanly. Process or Wasm
containment before interface reduction would fossilize `Editor` internals and
turn every internal shape into compatibility debt.

The missing artifact is a versioned, small contract of resources and effects:
for example buffer views, edit transactions, commands/actions, bounded prompts,
messages, timers, filesystem roots, process requests, and receipts. Each should
state ownership, authority, lifetime, limits, failure, and compatibility.

### 6. Platform semantics

Several product contracts remain underspecified:

- extended grapheme-cluster movement, deletion, selection, and cursor columns;
- terminal-cell width and ambiguous-width policy;
- filesystem and sudden-power-loss support matrix;
- Windows/macOS process-tree and release receipts;
- asynchronous save generation ownership, if asynchronous save is introduced;
  and
- a second renderer or consumer that proves which screen-contract fields are
  public rather than Python diagnostics.

Unicode UAX #29 describes grapheme clusters as user-perceived characters and
notes their relevance to cursor movement, selection, and backspace. UAX #11's
East Asian Width property is informative; actual glyph width also depends on
font and layout. Micromax should therefore adopt grapheme/cell semantics from a
concrete terminal plus second-consumer journey, not by pretending one code point
always equals one cell.

### 7. Public identity

“Micromax” is already the active name of Micromax Informatics and other
technology businesses. The official Micromax Informatics site was active in
2026. This audit makes no trademark conclusion, but the collision is a real
search, discoverability, package, and release-identity risk.

Treat “Micromax” as an internal codename until a basic naming and legal review is
complete. A public launch should use a distinct searchable name and preserve the
old name only as provenance if appropriate.

## Where something has gone severely wrong or wasteful

### 1. The coordinator warning was not converted into a constraint

Rev0873 correctly identified `Editor` as an enormous coordinator. Since then its
file grew about 36 percent and its direct methods about 26 percent. The failure
is not that a large file exists; it is that repeated audits did not alter the
rule by which new responsibility enters it.

A broad rewrite would be dangerous. Continued accretion is also dangerous. The
correct constraint is:

> Extract only a coherent owner that has a second real consumer, deletes more
> coordinator code than it adds, narrows authority, and leaves journey behavior
> unchanged.

A directory move, façade, owner registry, or new abstract base class does not
count as simplification. Net deletion and a smaller public contract do.

### 2. Evidence machinery became a second product

The repository has nearly as many test lines as source lines, more than seven
source-tree documentation files for every source file, 248 indexed revisions,
and a large family of context/audit/release/measurement tools. Much of this is
valuable. The waste arises when every correction produces another permanent
note, artifact, audit predicate, revision-index entry, living-doc rewrite, and
handoff ritual regardless of product significance.

This has three costs:

- maintainers spend time keeping evidence about evidence current;
- high-signal product contracts are buried in chronology; and
- the project can feel productive while mostly improving its ability to describe
  itself.

A healthier rule is “one durable contract plus one machine row,” not “one new
essay per seam forever.” Historical notes can remain immutable while the normal
working set is aggressively compacted.

### 3. The survivor-patch loop remained structurally attractive

Many revisions discovered one more mutable surface, sidecar, rollback path,
transport copy, generation witness, or finite deadline. These fixes were often
correct. The repeated shape rewarded local patching because it produced a crisp
reproduction, test, metric, and revision. Product friction is messier and was
therefore easier to defer.

The correction is sequencing, not contempt for hardening. For the next product
cycle, a new trust mechanism should need either a severe reproduced failure or a
release blocker. Otherwise the default work should be onboarding, dogfood,
taste, flow, and interface reduction.

### 4. First-contact truth was allowed to rot

Calling the editor a future prototype after hundreds of editor revisions is not
humility; it is stale documentation. It obscures what exists, discourages users,
and lets the project avoid judging the current product as a product.

Rev1000 removes the worst contradictions from package metadata, CLI help, the
headless greeting, package/class docstrings, and the tutorial. The README and
tutorial now include the missing checkout-install step and use the installed
product entry points. Living guidance must keep runnable product truth ahead of
revision detail.

### 5. Infrastructure presence was too easy to mistake for evidence

The release runway existed, and an old partial manifest existed. Normal audit
output surfaced those facts but not the manifest's stale source/test inventory.
That is an evidence-integrity smell: not falsification, but a presentation that
makes the reassuring fact easier to see than the disqualifying fact.

Rev1000 adds separate fields for presence, current source/test inventory,
internal consistency, completeness, pass state, and issues. Partial checkpoints
remain useful. They simply cannot silently inherit the authority of current
release evidence.

### 6. Optimization detail dominated the public narrative

The rev0999 work was technically substantial, but a 16.8-million-character regex
transport witness is not the first thing a prospective user needs to know. The
README's ordering revealed an internal incentive problem: the latest proof was
more visible than the enduring product loop.

Release notes should remain available, but the top-level narrative should answer:
what is this, why would I use it, how do I start, what can I trust, and what is
not yet supported?

## External comparison and what it suggests

### Micro: immediate usability is part of the product contract

Micro's official site describes it as a modern, intuitive terminal editor and
puts features and built-in help close to first contact. Its official about page
states that help is available from the command bar and directly through
`Ctrl-G`.

Micromax already has `Ctrl-G`, searchable help, common keybindings, and a single
Python entry point. The gap is not necessarily feature count. It is that those
facts were buried beneath implementation history. The lesson is to make
“usable now” an explicit, tested product claim.

### Helix: differentiated flow can be concrete

Helix documents syntax-aware motions that move selections according to the
syntax tree. Micromax need not copy Helix or add tree-sitter immediately. The
useful comparison is strategic: a serious editor eventually needs a few clear
flow advantages that users feel, not only internal safety advantages maintainers
can prove.

Micromax's candidate differentiator is trustworthy automation: macros and
extensions whose effects and provenance can be inspected. That must become as
visible and easy to demonstrate as a syntax-aware motion is in Helix.

### Zed and the WebAssembly Component Model: reduce the contract before isolation

Zed's official extension documentation uses Rust extensions compiled for
`wasm32-wasip2`. The WebAssembly Component Model documentation describes WIT as
an interface language for contracts, not behavior; worlds declare imports and
exports; interfaces are single-focus composable contracts; components interact
through interfaces rather than shared memory.

The relevant lesson is not “switch to Wasm now.” It is “define a small world.”
Micromax should first stabilize a compact set of versioned editor resources and
effects. Once the contract survives a second consumer, procedural extensions can
be evaluated in a Wasm component or isolated process without exporting the
entire Python object graph.

### GitHub attestations: configured provenance is not consumed provenance

GitHub's official documentation emphasizes verification by consumers and warns
that attestations are not a guarantee that an artifact is secure. Micromax's
release design is directionally strong because it binds source, builder inputs,
wheel probes, receipts, and archives. Its remaining gap is exactly the one the
external model implies: run it, retain subjects, verify signer/identity and
subject digests, and apply an explicit consumer policy.

### Unicode: editing units and display cells are separate contracts

UAX #29 makes extended grapheme clusters the relevant default unit for many user
interactions. UAX #11 explains a width property useful for East Asian text but
also makes clear that display width is not simply storage size or code-point
count. Micromax's current code-point/terminal assumptions should be documented as
limited until a grapheme and cell policy is implemented and exercised across the
headless contract and at least two renderers/consumers.

## Speculation: the strongest future shape

This section is intentionally speculative.

Micromax could occupy a useful space between a small immediately usable editor
and a general extension platform:

> **the trustworthy programmable instrument** — simple enough to edit now,
> powerful enough to automate deeply, and explicit enough that users can see
> what an extension may do and why a delayed action still has authority.

A sensible architecture sequence is:

1. **Tiny semantic VM.** Keep the language deterministic, replayable, and
   host-neutral.
2. **Headless editor oracle.** Keep complete product behavior observable without
   curses.
3. **Compact public product contract.** Version the smallest screen, command,
   buffer, edit, prompt, message, and effect schemas that real consumers need.
4. **Typed resource/effect handles.** Represent authority and lifetime through
   narrow resources rather than raw `Editor` internals.
5. **Reference TUI.** Let curses remain one product renderer and interaction
   client.
6. **Optional isolated procedural host.** Only after the contract stabilizes,
   evaluate Wasm components or isolated processes for untrusted or crash-prone
   extensions.

The existing Micromax language should remain the default configuration and macro
surface. A future Wasm/process layer would be for procedural extension code that
needs isolation or another implementation language, not a replacement for the
small inspectable language.

A second speculative opportunity is evidence as an end-user feature. The same
provenance machinery used internally could power an “explain this action” view:
which binding won, who registered it, what capability it has, what resource and
time limits apply, and what effect receipt resulted. That would turn the trust
laboratory into a visible product advantage. It should be prototyped only after
the basic onboarding loop is clean.

## What should change now

### Phase 0 — evidence honesty and current product language

Rev1000 lands this phase:

- `mxaudit` reports release-manifest presence, current source/test inventory,
  internal consistency, completeness, pass state, counts, digest, and issues;
- focused tests protect the report;
- package metadata and CLI help describe the current editor mission;
- the line REPL no longer calls itself a prototype;
- editor/package docstrings state that headless behavior is product truth;
- README/tutorial first contact includes installation and real console entry
  points; and
- the tutorial starts with the editor and then teaches the language as its
  automation substrate.

### Phase 1 — one product-reality cycle

Before another long sequence of internal hardening revisions, run a five-session
dogfood program. Each session should record:

- the real task attempted;
- start/end state and files involved;
- actions used repeatedly;
- confusion, delay, workaround, or abandonment;
- trust concern versus taste concern versus flow concern;
- whether the issue is reproducible in the headless model; and
- the smallest product correction.

At least one session should begin from a clean environment and installation
instructions. At least one should use restricted startup. At least one should
exercise recovery after a forced interruption. At least one should be performed
by someone who did not author the relevant subsystem.

The output should be one compact ledger and no more than three product changes.
The goal is to learn, not to create a new test bureaucracy.

### Phase 2 — first-run and help loop

Use the dogfood evidence to choose the smallest onboarding improvement. Likely
candidates are a restrained scratch-buffer hint, a one-action help path, and a
short “first five commands” page. Keep the hint in the shared headless model so
TUI and external consumers agree. It must disappear predictably and never mask
failure or recovery attention.

### Phase 3 — coordinator reduction under a deletion budget

Choose one narrow seam only after the product cycle. A candidate extraction must:

- have a second real consumer or independently testable owner;
- remove responsibility from `Editor`, not merely proxy it;
- reduce direct methods or state attributes;
- preserve public behavior and authority witnesses; and
- delete more coordinator code than the new seam adds.

Track the same structural metrics rev0873 introduced. A refactor that leaves
`Editor` larger and adds another registry has failed this phase.

### Phase 4 — execute release evidence

Run the hosted exact-byte lane for the exact source, retain/download subjects,
verify attestations from a consumer context, and preserve the receipt. Refresh or
complete the short-window full-suite manifest. Add Windows/macOS claims only from
executed receipts.

### Phase 5 — public contract, Unicode, and name

After the product loop and release lane are real:

- write the compact extension “world” and compatibility policy;
- use a second renderer/consumer to settle grapheme/cell semantics;
- state the filesystem/power-loss support matrix;
- decide package/API/revision version relationships; and
- select a distinct public project name after search and legal review.

## Repository policy corrections

The following rules would prevent the same waste from returning:

1. **Product before proof expansion.** Every new mechanism names the user journey
   it protects. A new audit predicate alone is not a product outcome.
2. **One durable contract, not one permanent essay per seam.** Revision notes may
   be immutable evidence, but current context points to compact contracts and a
   machine ledger.
3. **Evidence state is multi-dimensional.** Presence, currency, consistency,
   completeness, pass state, platform, and consumer verification are separate
   facts.
4. **Refactors have a deletion budget.** New owners must reduce coordinator
   gravity and public surface.
5. **No isolation before interface reduction.** Wasm/process work starts only
   after a compact contract and second consumer exist.
6. **No public launch under an ambiguous identity.** Naming review is a release
   gate, not a later marketing task.
7. **Trust, taste, and flow all receive evidence.** The project should be able to
   name current proof for each category, even when taste/flow proof is a short
   transcript rather than a formal model.

## Direct answers

### What is the heart of the mission?

A calm editor for understandable least-authority automation. The language, VM,
headless models, capabilities, provenance, recovery, and bounded workers all
exist to make a programmable editor trustworthy and inhabitable.

### What is missing?

Product adoption evidence, first-run clarity, sustained dogfood, taste/flow
criteria, a compact stable extension world, executed release/consumer receipts,
Unicode cell/grapheme semantics, named platform/filesystem support, and a
distinct public identity.

### What should change?

Keep the trust model, but pivot the next sequence toward product reality. Make
first contact truthful, run real tasks, prioritize the few highest-friction
corrections, execute the release evidence, and reduce the coordinator only under
net-deletion and second-consumer constraints.

### Has something gone severely wrong?

No single catastrophic correctness failure was found in the reviewed core. The
severe failure is cumulative: warnings about coordinator and evidence-product
growth were repeatedly documented while both continued growing; stale prototype
language survived after the product existed; and infrastructure presence was
more visible than evidence currency. Those are correctable trajectory failures.

### Where is work wasteful?

Revision archaeology, duplicated living-doc rewrites, audit predicates about
other audit lanes, survivor-by-survivor patches, and optimization detail that
displaces onboarding are the largest waste sources. They should be compacted and
made subordinate to a five-session product loop.

## Validation and limits

The incoming tree passed context, structural audit, effect-contract generation,
compile, lint, portability, and fast doctor lanes. The focused rev1000 audit,
CLI identity, living-doc, and entry-point tests pass. This document does not claim
a completed full suite, executed hosted release, platform parity, user preference,
or hostile-code sandbox. Rev1000 refreshes the carried full-suite checkpoint
against current source before packaging, but keeps its partial state explicit.

## Sources retrieved 2026-08-01

Primary or official sources used for comparison:

- Micro home: https://micro-editor.github.io/
- Micro about/help: https://micro-editor.github.io/about.html
- WebAssembly Component Model, WIT: https://component-model.bytecodealliance.org/design/wit.html
- WebAssembly Component Model, worlds: https://component-model.bytecodealliance.org/design/worlds.html
- WebAssembly Component Model, interfaces: https://component-model.bytecodealliance.org/design/interfaces.html
- WebAssembly Component Model, components: https://component-model.bytecodealliance.org/design/components.html
- Zed extension development: https://zed.dev/docs/extensions/developing-extensions.html
- Helix syntax-aware motions: https://docs.helix-editor.com/syntax-aware-motions.html
- GitHub artifact attestations: https://docs.github.com/en/actions/concepts/security/artifact-attestations
- GitHub build-provenance verification: https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds
- Unicode UAX #29, Text Segmentation: https://www.unicode.org/reports/tr29/
- Unicode UAX #11, East Asian Width: https://www.unicode.org/reports/tr11/
- Micromax Informatics official site: https://micromaxinfo.com/
