# Archived vision through rev0951

This file preserves the complete living `docs/00-vision.md` body from rev0951 before rev0952 compacted the current product compass. Use `docs/revision-index.json` for the structured revision ledger.

---

# Vision

**Micromax** is a small, embeddable, concatenative language intended to be a *sane* plugin/config/macro system.

Rev0913 keeps the mission framing and routes editor open/revert/source/user-init reads plus prompt/palette path completion through existing fd-backed VM-tunable filesystem timeout seams, recorded in `docs/871-open-prompt-filesystem-timeout.md`. Rev0912 bounded `ed.fs-read` preflight plus final byte loading, rev0911 bounded `ed.fs-list` directory traversal, rev0910 bounded `ed.fs-stat` metadata observation, rev0908-rev0909 bounded shell and external clipboard processes, rev0905-rev0907 bounded source loading and prompt completion scans, and rev0902-rev0904 added read/query/scan budgets. The former revision preamble remains preserved in
`docs/history/00-vision-through-rev0448.md`.

## Mission

Micromax exists to make **end-user programmability powerful without quietly
handing every extension ambient authority**.

The product is a small concatenative language, a reference virtual machine, and
an editor host in which configuration, macros, and plugins all cross explicit,
inspectable boundaries. The terminal editor is the first proving ground, not the
whole purpose.

The shortest useful description is:

> a least-authority automation language with a recoverable editor host

Recovery must be honest about effect class. Declarations can be staged, selected
session state can be journaled, document edits can join undo transactions, and
external effects may be irreversible. Rev0876 applies that rule to group cleanup/retag sweeps; rev0877 applies it
to generation-scoped delayed-state cleanup; rev0878 makes retained cleanup
failures inspectable through plugin command and hostcall rows; rev0879 narrows
the command slice of runtime-group cleanup rollback to touched command groups,
rev0880 applies the same touched-group cut to actions, keybindings, and
pending timers, and rev0881 applies it to hooks and marks while fixing shallow
hook-handler evidence, rev0882 applies it to recent files, palette MRU,
prompt history, and saved cursors, rev0883 applies it to clipboard, active search, and help history, rev0884
applies it to recovery stacks and delayed interactions, rev0885 applies it to
non-macro generation cleanup rows/registers, rev0886 applies it to macro
saved slots and active recording state, rev0887 persists cleanup failure
receipts when explicitly enabled behind `cap.persist`, rev0888 moves failed
live plugin callbacks onto scoped group/generation rollback while keeping cursor
and option rollback, rev0889 makes word authority part of the VM dictionary
transaction so failed source/lifecycle/deinit definitions cannot leave orphan
provenance rows, rev0890 removes replaced/unloaded committed wordlists
from live VM lookup after recording compact tombstones, rev0891 refuses deferred callbacks from retired plugin generations before their bodies execute, rev0892 refuses and clears stale prompt/qreplace/open-url interaction responses, rev0893 refuses retired saved macro playback while bounding pending timers, rev0897 fixes shared tool timeout teardown for escaped descendant process groups, rev0898 adds shared VM-visible hostcall result budgets with argument-stack restoration on oversized results, rev0899 adds regex hostcall input preflight with argument-preserving boundary failures, rev0900 routes recognized risky regex patterns through a timeout worker, rev0901 preflights structured editor model dimensions before host-state traversal, rev0902 preflights `ed.fs-read` byte size before byte loading while preserving the final fd-bound read check, rev0903 preflights free-text query byte size before broad host-state scans and prompt-opening query side effects, rev0904 adds scan/row budgets before broad row-builder and filesystem-list materialization, rev0908-rev0909 bound script-visible and optional helper processes, rev0910 bounds `ed.fs-stat` wall-clock observation, rev0911 bounds `ed.fs-list` traversal, rev0912 bounds `ed.fs-read` preflight plus final fd-bound byte loading, and rev0913 bounds editor open/revert/source/user-init reads plus prompt/palette path completion.
Cleanup guards now restore the known surfaces they can mutate without claiming
to roll back arbitrary edits, external effects, or dictionary topology. No
single word such as “rollback” should blur those different guarantees.

## Key commitment

Micromax is not an afterthought bolted onto the editor. It is the editor's
**plugin, configuration, and macro system**, so namespace hygiene, explicit host
boundaries, execution budgets, provenance, and recovery are product requirements.

## The product hierarchy

When priorities conflict, protect these layers in order:

1. **Language semantics.** A small, teachable data model and deterministic VM.
2. **Authority boundaries.** Host effects are named, gated, attributable, and
   denied by default where practical.
3. **Recovery.** A broken script or extension should be diagnosable and should
   not casually destroy user state.
4. **Headless truth.** Important editor state is available as stable models and
   testable commands; curses is a view, not the source of truth.
5. **Taste, trust, and flow.** The interactive editor should feel calm, honest,
   and fast enough to remain useful while the deeper runtime matures.

The Python VM is the executable semantic oracle for future ports. Public host
effects and headless models must first become small, versioned contracts with
explicit lifecycle semantics. A future Rust, Wasm, or other implementation is successful only when it preserves the language
and host-boundary contracts, not merely when it runs faster.

## What “Forth-inspired” means here

Micromax keeps the parts that reward composition:

- a tiny vocabulary of named words;
- direct interaction and redefinition;
- data-stack composition;
- wordlists and explicit search order;
- a portability corpus that describes observable behavior.

It does not promise Forth-standard conformance. Quotations, combinators, source
spans, structured errors, execution budgets, and host capabilities are central
because this is an embedding language rather than a bare-metal environment.

## Security truth

The current implementation is an **application-level authority boundary**, not
an operating-system sandbox.

Capabilities are editor options that control advertised host features. Filesystem
roots, origin/provenance checks, transaction helpers, and step budgets materially
reduce accidental authority and make policy inspectable. They do not yet provide
hostile-code containment:

- grants are host/editor configured rather than cryptographically isolated per
  plugin;
- plugins and the VM execute in-process;
- instruction budgets do not bound memory, native blocking calls, or every
  hostcall's wall-clock time;
- a Python process compromise bypasses application policy;
- workspace trust now controls automatic plugin/user-init loading, but it is not
  process isolation or hostile-code containment.

Documentation and UI must say this plainly. “Capability-gated” must never be
used as a synonym for “safe to run adversarial code.”

## Stable contracts still required

Before Micromax should invite a broad third-party plugin ecosystem, it needs:

- a normative language/conformance document, versioned independently from the
  Python implementation;
- a versioned public hostcall and plugin lifecycle contract, distinct from
  internal editor helpers;
- an explicit threat model covering workspace code, config, plugins, persistence,
  external commands, network access, denial of service, restricted/manual-load
  transitions, and recovery;
- grant scope and provenance rules that can answer “which plugin received which
  authority, from whom, for how long?”;
- canonical schemas for headless models and hostcall rows so zero/empty/error
  cases cannot silently drift;
- reproducible development and release inputs, plus artifact provenance.

## Architectural rule

Prefer **small pure models plus thin side-effect coordinators**.

Extract a seam only when its behavior is already pinned by focused tests. Do not
replace one large coordinator with a speculative registry that merely moves the
complexity. Large surfaces such as `Editor`, the editor hostcall installer,
`docs_cues_model_from_parts()`, and the test-evidence runner should shrink by
coherent families, not by line-count theater.

External protocols should remain adapters:

- LSP is a sensible language-intelligence boundary when Micromax needs one;
- Tree-sitter is a sensible incremental parsing option for syntax-aware editing;
- Wasm Components/WIT are a promising future isolation and interface mechanism;
- none should become a dependency until the native host/plugin contract is small
  and versioned enough to express through them.

## Non-goals for the current phase

Micromax is not currently trying to be:

- a complete IDE or a drop-in replacement for mature editors;
- an arbitrary-Python plugin host;
- a claim of secure execution for malicious extensions;
- a bespoke replacement for every parser or language server;
- a revision-history database disguised as a landing page;
- a test-orchestration product whose complexity eclipses the runtime it proves.

## Definition of progress

A revision is high leverage when it does at least one of the following without
weakening another:

- makes semantics more portable and explicit;
- removes ambient or ambiguous authority;
- makes failure/recovery more truthful;
- reduces a broad coordinator behind a tested contract;
- lowers handoff, build, or evidence cost while preserving confidence;
- improves a real editing loop under the taste/trust/flow lens.

Raw feature count, documentation count, test count, and revision count are not
success metrics.

## Near-term sequence

1. Finish remaining resource-handle enumeration now that dictionary lookup, direct saved XTs, generated callbacks, active interactions, and saved macros are covered.
2. Split one broad source/lifecycle transaction by typed effect family while retaining the broad snapshot as a differential oracle.
3. Build the executable effect-class/lifecycle matrix from live code paths where it removes implementation risk.
4. Publish versioned stable/experimental/internal extension imports, exports, schemas, and feature negotiation.
5. Add host payload, output, prompt-row, buffer, timeout, cancellation, and remaining pending-work budgets.
6. Lock the development environment and add focused CI, package inspection, artifact digests, and build provenance.
7. Compact one-note-per-revision docs/evidence overhead and continue contract-backed monolith cuts.
8. Prototype process or Wasm isolation only after the interface boundary is stable enough to survive outside Python objects.

The current filesystem read preflight landing is `docs/860-fs-read-preflight-budget.md`; the structured model input-budget landing is `docs/859-structured-model-dimension-budget.md`; the current regex timeout landing is `docs/858-regex-timeout-worker.md`; the current regex input preflight landing is `docs/857-regex-hostcall-input-preflight.md`; the hostcall-result budget landing is `docs/856-hostcall-result-budget.md`; the current process-tree timeout and mission audit landing is `docs/855-cloudtainer-process-tree-timeout-audit.md`; the current testing-runway landing is `docs/854-testing-runway-ux.md`; the stale-macro/timer-budget landing is `docs/851-stale-macro-timer-budget.md`; the delayed-interaction landing is `docs/850-generation-interaction-cleanup.md`; the runtime-retention landing is `docs/848-retired-wordlist-tombstones-package-budgets.md`; the broader cloudtainer audit and staged recommendations live in
`docs/847-cloudtainer-heart-gap-waste-word-authority.md`. The detailed rev0856 audit lives in
`docs/814-cloudtainer-mission-context-threat-audit.md`. The first executable
trust-state step is documented in `docs/815-workspace-trust-restricted-startup.md`.
