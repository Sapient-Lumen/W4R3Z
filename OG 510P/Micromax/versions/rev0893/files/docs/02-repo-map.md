# Repo map (rev0893)

## Product layers

- `src/micromax/` — parser/compiler/VM, core vocabulary, portability helpers,
  and bundled stdlib. This is the executable semantic oracle.
- `src/micromax_editor/` — headless editor state/models, command coordination,
  capability policy, plugin lifecycle, resource discovery, and curses view.
- `plugins/` — bundled Micromax-language plugins and manifests.
- `portability/kernel_cases.json` — observable cross-implementation behavior.
- `docs/` — living contracts/help plus append-only revision/audit history.
- `tests/` — VM, policy, editor, package, CLI, and evidence-runner contracts.
- `tools/` — lint/context/audit/doctor/portability/package/aggregate-evidence CLIs.

## Mission-critical boundaries

- `src/micromax/vm.py` and `core.py`: language semantics and execution budgets.
- `src/micromax_editor/capabilities.py`: host-advertised feature registry.
- `hostcall_boundary.py` / `hostcall_transactions.py`: current authority and
  transaction helpers around effects.
- `micromax_bridge.py`: VM-to-editor hostcall installation; currently too large.
- `workspace_trust.py` / `startup.py`: trusted versus restricted automatic
  code-loading policy.
- `plugin_grants.py` / `plugins.py`: grants, content freshness, lifecycle,
  staged reload, unload, cleanup orchestration, and runtime-group commit guards.
- `plugin_runtime.py`: broad registration/state snapshot and rollback glue plus
  narrow `RuntimeGroupStateSnapshot` and `RuntimeGenerationStateSnapshot`
  boundaries for cleanup/retag and delayed generation cleanup;
  `RuntimeRegistrationSnapshot` currently has 40 fields, cleanup/retag/generation
  sweeps return structured operation reports, failed commit sweeps raise
  `RuntimeGroupOperationError` through the plugin manager, rev0878 exposes
  retained failed-surface rows through plugin diagnostics, rev0879 adds
  touched command-group state inside the group snapshot, rev0880 extends
  touched group state to actions, keybindings, and pending timers, and rev0881
  extends touched state to hooks and marks while cloning mutable hook handlers, rev0882 extends touched state to recent files, palette MRU, prompt history, and saved cursors, rev0883 extends touched state to clipboard, active search, and help history,
  rev0884 extends touched state to recovery stacks and delayed interactions, rev0885 scopes non-macro generation cleanup by plugin root/generation, rev0886 scopes macro generation cleanup saved slots/live recording by plugin root/generation, rev0887 adds opt-in durable cleanup failure receipts behind `cap.persist`, rev0888 scopes failed live plugin callback rollback by loaded plugin group/root/generation while preserving cursor/option rollback, rev0889 couples dictionary-keyed word provenance to `VmDictionarySnapshot`, rev0890 retires replaced/unloaded plugin wordlists into compact tombstones with package fingerprint budgets, rev0891 rejects deferred callbacks from retired plugin generations through the shared callback runner, rev0892 scopes active delayed interactions by plugin generation, and rev0893 refuses retired saved macro playback while routing `ed.after` through a pending-work budget.
- `editor.py`: orchestration and most mutable state; current audit metrics should
  be treated as the source of truth for line/method counts.
- `docs_cues.py`: headless markdown/docs model; the primary builder remains a
  major extraction candidate.
- `prompt_refresh.py` / `prompt_suggestions.py`: examples of narrow pure-model
  extraction behind existing behavior.

## Missing effect-lifecycle boundary

Rev0873 identifies the central architecture gap. Rev0874 made cleanup evidence
visible and fixed live-buffer option rollback. Rev0875 uses that evidence for
commit policy on unload/reload. Rev0876 narrows the cleanup/retag rollback
boundary to group-sweep surfaces. Rev0877 narrows generation-scoped delayed-state
cleanup and restores both group and generation snapshots when unload/reload-old
cleanup fails after partial mutation. Rev0878 makes retained cleanup failures
visible through command, hostcall, completion, and audit seams. Rev0879 migrates
command cleanup/retag rollback to touched command-group state; rev0880 migrates
actions, keybindings, and pending timers to touched group state, and rev0881
migrates hooks and marks while fixing shallow hook-handler snapshot evidence, rev0882 migrates four delayed-state sidecars to touched authority-row snapshots, rev0883 migrates clipboard, active search, and help history to touched authority-state snapshots, rev0884 migrates recovery stacks and delayed interactions away from full cursor/prompt snapshots, rev0885 migrates non-macro generation cleanup away from broad delayed-state snapshots, rev0886 migrates macro generation cleanup away from broad macro-registry snapshots, rev0887 persists failed cleanup diagnostics as bounded JSONL receipts when explicitly enabled, rev0888 migrates failed live plugin callback rollback away from the broad registration snapshot when loaded plugin identity is available, rev0889 closes an orphan word-provenance leak by making `_word_authority` part of dictionary snapshot/restore, rev0890 removes the largest measured old-wordlist retention path by tombstoning retired committed wordlists, rev0891 routes stale generated callbacks to one live-generation guard, rev0892 adds generation-scoped cleanup and stale-response clearing for prompt/qreplace/open-url/keymode interactions, and rev0893 prunes retired saved macro slots plus bounds pending timers. The broader gap remains: effects are
capability-checked, but their lifecycle semantics are not defined in one
contract. Revs 0863-0872 repeatedly added authority sidecars, remove/retag
helpers, snapshot fields, and rollback tests for newly discovered state
survivors.

The next contract must classify declarations, reversible session state, document
edits, durable internal state, irreversible external effects, and observations;
then state load/callback/reload/deinit/unload/revoke/crash behavior for each.
See `docs/831-cloudtainer-mission-effect-lifecycle-audit.md`.

## Security boundary

Capabilities are editor-level options mirrored into VM host features. Filesystem
roots and origin checks are best-effort policy. `--trust restricted` prevents
automatic plugin and user-init evaluation; explicit restricted loads use
content-bound session grants. Plugin unload removes the currently enumerated
plugin-owned registrations and delayed state. Failed unload/reload cleanup or
retag now aborts rather than reporting false clean success, rev0876 restores partial cleanup/retag sweeps with a narrow group-surface
snapshot, rev0877 restores generation-scoped delayed-state cleanup with a
narrow generation snapshot, rev0878 exposes retained cleanup failure rows, and
rev0879 scopes command rollback to touched cleanup/retag groups, rev0880 does the same for actions, keybindings, and pending timers, and
rev0881 does the same for hooks and marks, rev0882 does the same for recent files, palette MRU, prompt history, and saved cursors, rev0883 does the same for clipboard, active search, and help history, rev0884 does the same for recovery stacks and delayed interactions, rev0885 does the same for non-macro generation cleanup rows/registers, rev0886 does the same for macro generation cleanup slots/recording, rev0887 preserves failed cleanup-surface diagnostics across restart when `plugin.cleanup-log.persist` is enabled behind `cap.persist`, rev0888 scopes failed live plugin callbacks to plugin group/generation snapshots while leaving source/lifecycle registrations on the broad fallback, rev0889 restores dictionary-keyed word provenance with dictionary topology for source/lifecycle/deinit rollback, rev0890 removes retired old wordlists from live VM lookup while keeping compact tombstones, rev0891 refuses stale generated callback bodies once their plugin generation is gone, rev0892 refuses and clears stale prompt/qreplace/open-url interaction responses, and rev0893 refuses retired saved macro playback while bounding pending timers.

Scripts/plugins remain in-process. Arbitrary document edits, new buffers, file
opens, external I/O, blocking hostcalls, memory exhaustion, native code, and
process compromise are not generally rolled back or contained. The executable
truth is `docs/security-boundaries.md`, which is included in installed help.

## Structural audit lane

`tools/mxaudit.py` is a small measurement command, not another test orchestrator.
It reports inventory, top Python files/definitions, `Editor` state/method counts,
plugin snapshot fields, narrow runtime-group and generation cleanup commit guards, touched registry/hook/mark/delayed-row/singleton/recovery/interaction snapshot seams, scoped callback rollback seams, dictionary/provenance coupling, retired-wordlist tombstones, retired deferred-callback guards, retired macro guards, timer pending-work budgets, package fingerprint budgets, cleanup diagnostics seams, recent lifecycle-revision
pressure, numbered-doc collisions, installed-help consistency, typecheck
coverage, lock files, CI workflows, and aggregate manifests.

```bash
make audit-metrics
python tools/mxaudit.py --json --check
```

`--check` fails only on audit-integrity errors such as an installed-help mismatch,
a missing installed security contract, unparseable Python, an unknown current
revision, or regression of the runtime-group cleanup/retag or generation-cleanup commit guards, their narrow snapshot boundaries, touched command/action/keymap/timer/hook/mark/delayed/singleton/recovery/interaction rollback, scoped live-callback rollback, dictionary-keyed word-provenance restore, retired-wordlist tombstones, retired deferred-callback guards, retired macro guards, timer pending-work budgets, package fingerprint budgets, mutable hook-handler clone evidence, or cleanup diagnostics visibility.
Large-file and missing-CI observations remain measurements rather than arbitrary
hard thresholds.

## Context and docs

`tools/mxcontext.py` is a curated handoff, not a file manifest. It contains:

- durable product/design/operation entrypoints;
- docs from the newest 12 revision-index entries;
- selected code entrypoints and commands;
- full docs/source/test inventory counts;
- catalog pointers.

Use `docs/revision-index.json` for the full history and
`docs/installed-help-manifest.txt` for runtime-help membership.

## Aggregate evidence lane

Makefile defaults are the handoff contract:

```text
CHUNKS=64
MAX_NEW_TESTS=120
MAX_NEW_FILES=8
TEST_BATCH_SIZE=0
FILE_TIMEOUT=180
MAX_RUNTIME_SECONDS=25
TEST_MANIFEST=.artifacts/mxtest-all-64.json
```

Run bounded resumable progress:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --run-chunks 64 \
  --strategy segment \
  --isolate-files \
  --resume \
  --checkpoint-tests \
  --max-new-tests 120 \
  --max-new-files 8 \
  --test-batch-size 0 \
  --file-timeout 180 \
  --max-runtime-seconds 25 \
  --json .artifacts/mxtest-all-64.json \
  --durations 0
```

Verify combined source/environment evidence:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --verify-current .artifacts/mxtest-all-64.json
```

The shorter aliases are `make test-all-chunks` and `make test-verify-current`.
The current archive does not carry a fresh complete aggregate manifest unless a
run explicitly regenerates and verifies `.artifacts/mxtest-all-64.json`; do not
infer a full-suite claim from focused evidence.

## Current structural and release risks

- `Editor`, `install_editor_hostcalls()`, `docs_cues_model_from_parts()`,
  `install_core_words()`, and `install_default_actions()` mix too many concerns.
- Broad source/lifecycle registration snapshots grow as new mutable state is discovered; remaining plugin-owned resource handles still need enumeration beyond words, callbacks, interactions, and macros.
- The public plugin API is not cleanly versioned apart from internal helpers.
- Headless dictionary/list payloads lack one canonical schema authority.
- Development dependencies are lower-bounded rather than locked.
- There is no repository CI workflow or hosted build provenance.
- `scripts/typecheck.sh` covers `src/micromax_editor`, but still skips when mypy is absent.
- Archive revision and package version policy is unexplained.
- Documentation and evidence tooling impose increasing maintenance cost.

## Safe next cuts

1. Enumerate remaining plugin-owned resource handles outside words, callbacks, interactions, and macros.
2. One typed source/lifecycle effect migration checked against the broad snapshot oracle.
3. Stable/experimental/internal extension imports/exports and schema versions.
4. Host payload/output/prompt/buffer/timeout/cancellation budgets beyond the initial timer cap.
5. Dependency lock, focused CI, package inspection, artifact digests, and provenance records.
6. Documentation/evidence compaction plus one contract-backed `PluginHost` or hostcall-family extraction with a measured reduction in the original coordinator.
