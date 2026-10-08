Rev1000 note: the project now distinguishes release infrastructure from current evidence and corrects stale product language that still called the editor a future prototype. The next work is a product-reality cycle, not another speculative subsystem.

# LLM start here (rev1000)

## Heart of the project

Micromax is a calm, scriptable editor for understandable least-authority
end-user automation. Its small concatenative language and replayable VM are the
configuration, macro, and plugin substrate. The editor is the demanding host
that makes semantics, authority, provenance, recovery, and resource limits
matter.

> Build an editor people choose to inhabit, with explicit effects, visible
> provenance, recoverable failure, bounded host work, and headless truth.

Trust comes first, taste second, flow third. Tiny and inspectable are means. The
headless editor model is product truth; curses is one reference renderer.
Capabilities are in-process application policy unless a smaller operating-system
boundary is explicitly proved.

## Current landing

Rev1000 is a trajectory correction.

The incoming rev0999 tree was technically strong but imbalanced: 995 docs, 278
test-tree files, a 34,506-line `editor.py`, 1,382 direct `Editor` methods, and a
partial stale full-suite manifest. Since rev0873 warned about coordinator gravity
and evidence becoming a second product, `editor.py` grew about 36 percent, direct
methods about 26 percent, and docs about 23 percent. Meanwhile package metadata,
CLI help, the line-UI greeting, package/class docstrings, and the tutorial still
described the editor as a future prototype.

Rev1000 lands three bounded corrections:

1. `tools/mxaudit.py` reports each full-suite manifest's presence, current
   source/test inventory, internal consistency, completeness, pass state, test
   and batch counts, source digest, and issues. A partial checkpoint stays useful
   but cannot imply a current release receipt.
2. First-contact code and documentation describe the current editor and put a
   runnable product loop ahead of revision archaeology.
3. The roadmap pivots to five sustained product sessions, first-run/help
   clarity, executed publication evidence, and coordinator extraction only when
   there is a second consumer plus net deletion.

Read `docs/958-mission-product-reality-and-evidence-honesty-audit.md` and
`REV1000_AUDIT.md` first. Use `docs/revision-index.json` to find exact historical
technical evidence instead of loading every revision note into working context.

## Working invariants

1. Ordinary safe defaults form a usable editor; security machinery that breaks the normal loop has failed.
2. Headless behavior is product truth; renderers consume shared models.
3. Startup failure leaves a live inspectable model and an honest nonzero machine result.
4. Creation never silently replaces live text; delayed state follows exact identity, generation, and authority.
5. Physical input cannot launder plugin authority through bindings, prompts, callbacks, macros, timers, or later acceptance.
6. Every effect names authority, input, preflight, finite owner, limits/deadlines, teardown, and post-failure state.
7. Predictable geometry is denied before allocation; opaque work gets a killable or limited owner only from evidence.
8. Multi-location edits share one immutable source coordinate space and one user-visible undo boundary.
9. History retains exact inverse data at the narrowest witnessed mutation boundary; grouped replay validates every changed target before one commit.
10. Delayed query-replace owns exact source-generation truth, a compact immutable plan, and sparse accepted history; it never rematches replacement-created text.
11. Recovery is text plus authority. History uses the current save baseline and never resurrects a retired journal record.
12. Rendering performs no filesystem discovery; external truth refreshes at explicit lifecycle boundaries.
13. Rollback claims stay narrow; disk, process, network, native, memory, wall-clock, and crash effects are not called atomic without a smaller proof.
14. Release evidence is multidimensional: presence, currency, consistency, completeness, pass state, platform, and consumer verification are separate facts.
15. Linked revisions preserve immutable handoff evidence; divergent work advances the revision.
16. Refactors must reduce demonstrated coordinator gravity. A wrapper, file move, or registry without net deletion is not simplification.
17. A public extension boundary must be smaller than internal Python surfaces before process or Wasm isolation.
18. Taste and flow need real transcripts and journeys, not only feature inventories.
19. “Micromax” remains an internal codename until naming/search/legal review supports a distinct public identity.
20. Proof machinery protects the editor loop; it does not replace it.

## Where to work

- Product loop and first contact: `README.md`, `docs/70-tutorial.md`,
  `src/micromax_editor/__main__.py`, `startup.py`, shared screen/help models,
  default keybindings, and complete editor journeys.
- Editor semantics: `src/micromax_editor/editor.py`, `buffer.py`, `undo.py`,
  `simultaneous_edits.py`, `query_replace.py`, `actions_default.py`, and
  `command_dispatcher.py`.
- Trust/effects: `capabilities.py`, `effect_contracts.py`, policy modules,
  `plugin_runtime.py`, `plugins.py`, `hostcall_boundary.py`, worker/process
  owners, and `docs/security-boundaries.md`.
- Release/evidence: `tools/mxrelease.py`, `mxrepro.py`, `mxaudit.py`,
  `mxcontext.py`, `mxeffects.py`, `mkrevzip.py`, the reproducible-release
  workflow, and `.artifacts/` manifests.
- Portable contract: `src/micromax/`, `portability/kernel_cases.json`, compact
  screen/effect schemas, and the future small extension world.
- Historical evidence: `docs/revision-index.json` and only the exact indexed
  audit files relevant to the owner under change.

## Known pressure

- Internal correctness evidence is much stronger than sustained-user, taste,
  flow, adoption, and preference evidence.
- `Editor` remains a 32,000-line class. Extract only a coherent owner with a
  second real consumer, narrower authority, preserved journeys, and net deletion.
- Documentation, tests, audit predicates, release tools, and revision ritual can
  become a second product. Add one durable contract and machine row where
  possible; do not create essays by default.
- The hosted exact-byte lane is configured but not yet executed and
  consumer-verified for this source. Windows/macOS receipts and public release
  claims remain absent.
- The carried short-window full-suite checkpoint is intentionally partial. Its
  current state must remain visible and must not be promoted by wording.
- Grapheme-cluster editing and terminal-cell width semantics are open. One code
  point is not a universal user character or display cell.
- The filesystem/power-loss support matrix is narrower than the depth of the
  save/recovery implementation suggests.
- Synchronous save has no asynchronous/re-entrant generation claim. A future
  async writer needs an explicit payload/generation lease.
- The stable public extension contract is smaller than internal Python but still
  not compact enough for clean process/Wasm isolation.
- “Micromax” collides with active technology brands and is a discoverability and
  release-identity risk.

## Recommended next move

Run one five-session dogfood ledger before another long trust-hardening sequence:

1. clean environment to first edit/save/help;
2. ordinary multi-file project work;
3. restricted startup and plugin inspection;
4. forced-interruption recovery and resumed save; and
5. one session by a non-author of the subsystem.

Record task, friction, workaround, trust/taste/flow category, headless
reproduction, and the smallest correction. Ship no more than three product
changes from the evidence. Then execute and consumer-verify the hosted release
lane. Only after those two loops should the project choose one coordinator
extraction or compact extension-world design.

## Validation commands

```bash
make timely
python tools/mxaudit.py --json --check
python tools/mxcontext.py --check
python tools/mxeffects.py --check
python -m pytest -q tests/test_mxaudit.py tests/test_editor_main_cli.py
python tools/mxrelease.py --manifest .artifacts/mxrelease-full-suite.json --summary
```

A green timely lane is bounded health evidence, not a complete-suite, hosted,
cross-platform, or public-release claim.
