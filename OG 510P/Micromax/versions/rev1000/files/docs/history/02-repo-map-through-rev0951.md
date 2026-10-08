# Archived repo map through rev0951

Preserved before the rev0952 living-document compaction.

---

# Repo map (rev0951)

## Product layers

- `src/micromax/` — parser/compiler/VM, core vocabulary, portability helpers,
  bounded bundled-stdlib resource loading, and bundled stdlib. This is the executable semantic oracle.
- `src/micromax_editor/` — headless editor state/models, command coordination,
  capability policy, generated effect/resource contracts, plugin lifecycle, timer resource ownership, resource discovery, and curses view.
- `plugins/` — bundled Micromax-language plugins and manifests.
- `portability/kernel_cases.json` — observable cross-implementation behavior.
- `docs/` — living contracts/help plus append-only revision/audit history.
- `tests/` — VM, policy, editor, package, CLI, and evidence-runner contracts.
- `tools/` — lint/context/audit/effect-contract generation and installed-help stale-check/doctor/timely/release/portability/package/aggregate-evidence CLIs; rev0951 makes timely summary evidence completion-honest for interrupted prefixes.

## Mission-critical boundaries

- `src/micromax/vm.py`, `stdlib_resource.py`, `core.py`, `host_limits.py`, and `host_regex.py`: language semantics, bounded stdlib package-resource startup, execution budgets, shared hostcall result budgets, regex hostcall input preflight, and risky-regex timeout-worker containment.
- `src/micromax_editor/effect_contracts.py`: first generated effect/resource contract slice and installed-help renderer, deriving high-risk host-effect rows from live registries, capability policy, default budgets, stdlib resource facts, regex facts, and audit evidence.
- `src/micromax_editor/capabilities.py`: host-advertised feature registry.
- `hostcall_boundary.py` / `hostcall_transactions.py`: current authority,
  filesystem-read byte/time, filesystem-list row/time, editor open/source-read time, query, scan-row, shell command/output/timeout, source-load, source-load-graph, source-eval-step, prompt path-completion scan/time, and model-dimension preflight, and transaction helpers around effects.
- `micromax_bridge.py`: VM-to-editor hostcall installation; currently too large.
- `host_process.py`: bounded editor shell execution with output caps and timeout/process-tree teardown.
- `workspace_trust.py` / `startup.py`: trusted versus restricted automatic
  code-loading policy.
- `plugin_grants.py` / `plugins.py`: grants, content freshness, lifecycle,
  staged reload, unload, cleanup orchestration, and runtime-group commit guards.
- `plugin_runtime.py`: broad registration/state snapshot and rollback glue plus
  narrow `RuntimeGroupStateSnapshot` and `RuntimeGenerationStateSnapshot`
  boundaries for cleanup/retag and delayed generation cleanup;
  `RuntimeRegistrationSnapshot` currently has 46 fields, cleanup/retag/generation
  sweeps return structured operation reports, failed commit sweeps raise
  `RuntimeGroupOperationError` through the plugin manager, rev0878 exposes
  retained failed-surface rows through plugin diagnostics, rev0879 adds
  touched command-group state inside the group snapshot, rev0880 extends
  touched group state to actions, keybindings, and pending timers, and rev0881
  extends touched state to hooks and marks while cloning mutable hook handlers, rev0882 extends touched state to recent files, palette MRU, prompt history, and saved cursors, rev0883 extends touched state to clipboard, active search, and help history,
  rev0884 extends touched state to recovery stacks and delayed interactions, rev0885 scopes non-macro generation cleanup by plugin root/generation, rev0886 scopes macro generation cleanup saved slots/live recording by plugin root/generation, rev0887 adds opt-in durable cleanup failure receipts behind `cap.persist`, rev0888 scopes failed live plugin callback rollback by loaded plugin group/root/generation while preserving cursor/option rollback, rev0889 couples dictionary-keyed word provenance to `VmDictionarySnapshot`, rev0890 retires replaced/unloaded plugin wordlists into compact tombstones with package fingerprint budgets, rev0891 rejects deferred callbacks from retired plugin generations through the shared callback runner, rev0892 scopes active delayed interactions by plugin generation, and rev0893 refuses retired saved macro playback while routing `ed.after` through a pending-work budget, and rev0928 makes canceled timers release live callback task rows immediately with bounded stale heap-id drift, rev0929 makes handoff zips self-verifying against embedded member provenance, rev0930 records executable package-input policy, rev0931 bounds `qreplace all` responses with a host-owned replacement budget, rev0932 routes pending open-url snapshot/restore through editor-owned owner methods, rev0933 routes query-replace snapshot/restore through editor-owned session+cursor owner methods, rev0934 routes prompt snapshot/restore through editor-owned owner methods, rev0935 routes keymode snapshot/restore through editor-owned owner methods, rev0936 routes broad failed-callback interaction snapshot/restore through one editor-owned aggregate owner, rev0937 routes clipboard group/generation/broad registration snapshot/restore through editor-owned clipboard owner methods, rev0938 routes macro generation snapshot/restore through editor-owned macro owner methods, rev0939 makes curated entrypoint freshness an audit-checked handoff invariant, rev0940 generates a checked high-risk effect/resource contract slice, rev0941 routes active-search rollback through editor-owned owner methods while exposing a generated active-search owner row, rev0942 routes prompt-history rollback through editor-owned owner methods while exposing a generated prompt-history owner row, rev0943 routes recent-files rollback through editor-owned owner methods while exposing a generated recent-files owner row, rev0944 routes saved-cursor rollback through editor-owned owner methods while exposing a generated saved-cursor owner row, rev0945 routes command-palette recent rollback through editor-owned owner methods while exposing a generated palette-recent owner row, rev0946 routes help-history rollback through editor-owned owner methods while exposing a generated help-history owner row, rev0947 routes recovery rollback through editor-owned owner methods while exposing a generated recovery owner row, rev0948 renders the generated contract into installed help with audit-enforced freshness, rev0949 routes option-state rollback through public editor-owned owner methods while exposing a generated option-state owner row, rev0950 routes mark rollback through public editor-owned owner methods while exposing a generated mark owner row, and rev0951 makes the timely handoff summary v3 completion-honest for outer-stopped prefixes.
- `editor.py`: orchestration and most mutable state; current audit metrics should
  be treated as the source of truth for line/method counts.
- `docs_cues.py`: headless markdown/docs model; the primary builder remains a
  major extraction candidate.
- `prompt_refresh.py` / `prompt_suggestions.py`: examples of narrow pure-model
  extraction behind existing behavior.

## Missing effect-lifecycle boundary

Rev0951 adds completion-honest cloudtainer evidence: mxtimely summary v3 carries planned/pending step fields and marks interrupted prefixes partial. Rev0950 adds the retained named-mark navigation row, `ed.mark-register`, for group and broad mark rollback through public editor-owned methods, and removes a redundant recent-files group restore call. Rev0949 adds the configuration/capability option row, `ed.option-state-register`, for failed plugin source/lifecycle and scoped callback option rollback through public editor-owned methods. Rev0948 renders the generated effect/resource contract into `docs/33-effect-resource-contract.md`, an installed help topic checked by `mxeffects --check-help-doc` and `mxaudit --check`. Rev0947 added the retained cursor/selection recovery row, `ed.recovery-register`. Rev0946 added the retained help-navigation row, `ed.help-history-register`. Rev0945 added the command-palette recent row, `ed.palette-recent-register`. Rev0944 added the saved-cursor retained path+position row, `ed.saved-cursor-register`. Rev0943 added the recent-file retained path owner row, `ed.recent-files-register`. Rev0942 added the retained prompt-history owner row, `ed.prompt-history-register`. Rev0941 added the first owner row, `ed.active-search-register`, for active-search query/provenance rollback. Rev0940 started turning scattered effect/resource facts into an executable contract by generating rows for the highest-risk host effects from live registries, capability options, default budgets, stdlib resource facts, regex facts, and audit evidence. The remaining runtime gaps are broad owner rows and delayed resource families that should move only when they have concrete stale/lifetime or authority failures.

Rev0873 identifies the central architecture gap. Rev0874 made cleanup evidence
visible and fixed live-buffer option rollback. Rev0875 uses that evidence for
commit policy on unload/reload. Rev0876 narrows the cleanup/retag rollback
boundary to group-sweep surfaces. Rev0877 narrows generation-scoped delayed-state
cleanup and restores both group and generation snapshots when unload/reload-old
cleanup fails after partial mutation. Rev0878 makes retained cleanup failures
visible through command, hostcall, completion, and audit seams. Rev0879 migrates
command cleanup/retag rollback to touched command-group state; rev0880 migrates
actions, keybindings, and pending timers to touched group state, and rev0881
migrates hooks and marks while fixing shallow hook-handler snapshot evidence, rev0882 migrates four delayed-state sidecars to touched authority-row snapshots, rev0883 migrates clipboard, active search, and help history to touched authority-state snapshots, rev0884 migrates recovery stacks and delayed interactions away from full cursor/prompt snapshots, rev0885 migrates non-macro generation cleanup away from broad delayed-state snapshots, rev0886 migrates macro generation cleanup away from broad macro-registry snapshots, rev0887 persists failed cleanup diagnostics as bounded JSONL receipts when explicitly enabled, rev0888 migrates failed live plugin callback rollback away from the broad registration snapshot when loaded plugin identity is available, rev0889 closes an orphan word-provenance leak by making `_word_authority` part of dictionary snapshot/restore, rev0890 removes the largest measured old-wordlist retention path by tombstoning retired committed wordlists, rev0891 routes stale generated callbacks to one live-generation guard, rev0892 adds generation-scoped cleanup and stale-response clearing for prompt/qreplace/open-url/keymode interactions, rev0893 prunes retired saved macro slots plus bounds pending timers, rev0894 adds a timely Python handoff lane, rev0895 adds a resumable selected-file-batch full-suite release lane, rev0896 makes the test/release runway timed, shared, and next-action-guided without changing runtime semantics, rev0897 reaps escaped descendant process groups in shared timeout teardown after a deep cloudtainer mission audit, and rev0898 adds shared VM-visible hostcall result byte/cell budgets with stack restoration on violation, rev0899 adds regex hostcall input preflight with argument-preserving boundary failures, rev0900 routes recognized risky regex patterns through a timeout worker, rev0901 preflights structured editor model dimensions before row-builder traversal, rev0902 preflights `ed.fs-read` byte size before byte loading while retaining the final fd-bound read check, and rev0903 preflights free-text query byte size before broad docs/help/prompt/palette scans while hard-checking the query and fs-read audit seams, rev0904 adds scan/row budgets, rev0905 adds executable source-size/eval-step budgets, rev0906 adds cumulative source-load graph depth/byte budgets, rev0907 applies the shared scan budget to command-prompt path completion before directory iteration/sort, rev0908 bounds `ed.shell` command input, output capture, and timeout/process-tree teardown before the VM result budget runs, and rev0909 routes external clipboard helper processes through bounded argv input/output and timeout teardown, rev0910 runs `ed.fs-stat` metadata observation through a VM-tunable timeout worker while preserving fd-bound containment, rev0911 runs `ed.fs-list` directory traversal through the same VM-tunable worker pattern while preserving row budgets, rev0912 moves `ed.fs-read` preflight plus final fd-bound byte loading into a VM-tunable timeout worker while preserving byte and containment checks, rev0913 routes editor open/revert/source/user-init reads plus prompt/palette path completion through the existing bounded filesystem seams, rev0914 bounds atomic editor/persistence writes with worker-temp cleanup, rev0915 bounds save preflight directory-kind checks, freshness/hash capture, and mkparents parent creation, rev0921 bounds docs/help catalog scanning, rev0922 batches project-root marker observation for hot recent/buffer grouping, rev0923 bounds help-doc opening, explicit docs path resolution, relative help-link following, and target-heading metadata reads, rev0924 re-centers the cloudtainer mission/gap/waste diagnosis with a concrete next survivor recommendation, rev0925 routes optional plugin metadata existence through contained plugin I/O while failing closed on escaping metadata, moves the docs-index private fallback to contained prefix reads, and makes timely summary evidence incremental to prevent stale handoff artifacts after outer termination, rev0926 removes the standalone ambient prompt-completion directory branch while adding archive-member provenance to revision zips, rev0927 gives bundled stdlib startup an explicit package-resource byte/provenance contract, and rev0928 gives timer cancellation a concrete owner/lifetime boundary, and rev0929 consumes embedded archive-member provenance with a budgeted zip verifier. The broader gap remains: effects are
capability-checked, but their lifecycle semantics are not defined in one
contract. Revs 0863-0872 repeatedly added authority sidecars, remove/retag
helpers, snapshot fields, and rollback tests for newly discovered state
survivors.

The next contract expansion must classify declarations, reversible session state, document
edits, durable internal state, irreversible external effects, and observations;
then state load/callback/reload/deinit/unload/revoke/crash behavior for each.
See `docs/831-cloudtainer-mission-effect-lifecycle-audit.md`,
`docs/898-generated-effect-resource-contract.md`,
`docs/899-active-search-owner-contract.md`, and
`docs/909-timely-summary-completion-honesty.md`, `docs/908-mark-owner-contract.md`, `docs/907-option-state-owner-contract.md`, `docs/906-effect-contract-installed-help.md`, `docs/33-effect-resource-contract.md`, `docs/905-recovery-owner-contract.md`, `docs/904-help-history-owner-contract.md`, `docs/903-palette-recent-owner-contract.md`, `docs/902-saved-cursor-owner-contract.md`, `docs/901-recent-files-owner-contract.md`, and `docs/900-prompt-history-owner-contract.md`.

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
rev0881 does the same for hooks and marks, rev0882 does the same for recent files, palette MRU, prompt history, and saved cursors, rev0883 does the same for clipboard, active search, and help history, rev0884 does the same for recovery stacks and delayed interactions, rev0885 does the same for non-macro generation cleanup rows/registers, rev0886 does the same for macro generation cleanup slots/recording, rev0887 preserves failed cleanup-surface diagnostics across restart when `plugin.cleanup-log.persist` is enabled behind `cap.persist`, rev0888 scopes failed live plugin callbacks to plugin group/generation snapshots while leaving source/lifecycle registrations on the broad fallback, rev0889 restores dictionary-keyed word provenance with dictionary topology for source/lifecycle/deinit rollback, rev0890 removes retired old wordlists from live VM lookup while keeping compact tombstones, rev0891 refuses stale generated callback bodies once their plugin generation is gone, rev0892 refuses and clears stale prompt/qreplace/open-url interaction responses, rev0893 refuses retired saved macro playback while bounding pending timers, rev0908 bounds the enabled shell hostcall output/time surface, rev0909 bounds the optional external clipboard process surface, rev0910 bounds the `ed.fs-stat` metadata/open/fstat wall-clock surface, rev0911 bounds the `ed.fs-list` directory traversal wall-clock surface, rev0912 bounds the `ed.fs-read` preflight/final-read wall-clock surface, rev0913 bounds editor open/revert/source/user-init-read and prompt/palette path-completion filesystem observation surfaces, rev0914 bounds atomic write commits, rev0915 bounds save preflight freshness/hash and mkparents work, rev0921 bounds docs/help catalog scanning, rev0922 batches project-root marker observation for recent/buffer grouping, rev0923 bounds help-doc open/read and link-target heading metadata, rev0924 records the next resource/effect contract correction path, rev0925 bounds optional plugin metadata existence through the contained plugin-file seam, closes the docs-index private fallback read survivor, and prevents stale mxtimely summary evidence after interrupted handoff runs, rev0926 routes standalone prompt path completion through contained listing while adding archive-member provenance to revision zips, rev0927 gives bundled stdlib startup an explicit package-resource byte/provenance contract, rev0928 makes timer cancellation release callback task rows immediately while routing timer rollback through owner methods, rev0929 verifies handoff zips against embedded member provenance before treating them as intact datacubes, rev0931 bounds qreplace-all responses, rev0932 routes pending open-url rollback through owner methods, rev0933 routes query-replace rollback through owner methods, rev0934 routes prompt rollback through owner methods, rev0935 routes keymode rollback through owner methods, rev0936 routes broad failed-callback interaction rollback through an editor-owned aggregate owner, rev0937 routes clipboard rollback through editor-owned clipboard owner methods, rev0938 routes macro generation rollback through editor-owned macro owner methods, rev0939 audit-checks curated entrypoint freshness, rev0940 makes the first generated high-risk effect/resource contract slice executable, rev0941 routes active-search rollback through editor-owned owner methods with a generated owner-contract row, rev0942 routes prompt-history rollback through editor-owned owner methods with a generated retained-history owner-contract row, rev0943 routes recent-files rollback through editor-owned owner methods with a generated retained-path-history owner-contract row, rev0944 routes saved-cursor rollback through editor-owned owner methods with a generated retained-path+position owner-contract row, rev0945 routes palette-recent rollback through editor-owned owner methods with a generated retained command/action launch owner-contract row, rev0946 routes help-history rollback through editor-owned owner methods with a generated retained help-navigation owner-contract row, rev0947 routes recovery rollback through editor-owned owner methods with a generated retained cursor/selection recovery owner-contract row, rev0948 renders the generated effect/resource contract as installed help with audit-enforced freshness, rev0949 routes option rollback through public editor-owned methods with a generated configuration/capability option owner-contract row, rev0950 routes mark rollback through public editor-owned methods with a generated retained buffer+position mark owner-contract row, and rev0951 marks incomplete timely prefixes partial in summary evidence.

Scripts/plugins remain in-process. Arbitrary document edits, new buffers, file
opens, external I/O, blocking hostcalls, memory exhaustion, native code, and
process compromise are not generally rolled back or contained. The executable
truth is `docs/security-boundaries.md`, which is included in installed help.

## Structural audit lane

`tools/mxaudit.py` is a small measurement command, not another test orchestrator.
It reports inventory, top Python files/definitions, `Editor` state/method counts,
plugin snapshot fields, narrow runtime-group and generation cleanup commit guards, touched registry/hook/mark/delayed-row/singleton/recovery/interaction snapshot seams, prompt/open-url/query-replace/keymode/callback-interaction/clipboard/active-search/help-history/prompt-history/recent-files/saved-cursor/palette-recent owner evidence, scoped callback rollback seams, dictionary/provenance coupling, retired-wordlist tombstones, retired deferred-callback guards, retired macro guards, timer pending-work budgets, VM hostcall result budgets, source-load graph budgets, contained prompt path-completion scan budgets, filesystem read/list/stat timeout workers, docs catalog timeouts including the private docs fallback prefix-read seam, project-root marker batching, help-doc read timeouts, package fingerprint budgets, plugin metadata contained-existence checks, cleanup diagnostics seams, recent lifecycle-revision
pressure, numbered-doc collisions, installed-help consistency, typecheck
coverage, lock files, CI workflows, aggregate manifests, the timely cloudtainer runway, incremental timely summary evidence, mkrevzip archive-member provenance, the mkrevzip archive verifier, generated effect/resource contract health, generated effect-contract installed-help freshness, bundled stdlib resource-contract evidence, timer cancellation release evidence, and the full-suite release runway.

```bash
make audit-metrics
python tools/mxaudit.py --json --check
```

`--check` fails only on audit-integrity errors such as an installed-help mismatch,
a missing installed security contract, unparseable Python, an unknown current
revision, a stale generated effect/resource contract or installed effect-contract help page, or regression of the runtime-group cleanup/retag or generation-cleanup commit guards, their narrow snapshot boundaries, touched command/action/keymap/timer/hook/mark/delayed/singleton/recovery/interaction rollback, prompt/open-url/query-replace/keymode/callback-interaction/clipboard/active-search/help-history/prompt-history/recent-files/saved-cursor/palette-recent owner evidence, scoped live-callback rollback, dictionary-keyed word-provenance restore, retired-wordlist tombstones, retired deferred-callback guards, retired macro guards, timer pending-work budgets, VM hostcall result budgets, bundled stdlib resource-contract evidence, timer cancellation release evidence, source-load graph budgets, contained prompt path-completion scan budgets, filesystem read/list/stat timeout workers, docs catalog timeouts including the private docs fallback prefix-read seam, project-root marker batching, help-doc read timeouts, package fingerprint budgets, plugin metadata contained-existence checks, incremental timely summary evidence, mkrevzip archive-member provenance, mkrevzip verifier evidence, mutable hook-handler clone evidence, or cleanup diagnostics visibility.
Large-file and missing-CI observations remain measurements rather than arbitrary
hard thresholds.

## Context and docs

`tools/mxcontext.py` is a curated handoff, not a file manifest. It contains:

- durable product/design/operation entrypoints;
- docs from the newest 12 revision-index entries;
- selected code entrypoints and commands;
- full docs/source/test inventory counts;
- catalog pointers.

Use `docs/revision-index.json` for the full history,
`docs/installed-help-manifest.txt` for runtime-help membership, and
`python tools/mxeffects.py --json --check` for the current generated high-risk
effect/resource slice.

## Timely cloudtainer lane

`make timely` runs the compact short-window handoff lane: context, audit, lint, quiet portability, and fast doctor checks. `tools/mxtimely.py` writes `.artifacts/mxtimely-summary.json` after every completed child as well as at normal completion, so a tooltimer kill during doctor or a later optional test slice does not leave the previous revision's summary in place. `make timely-tests` adds a tiny optional resumable `mxtest` checkpoint without stacking doctor on top of the test slice. These commands are health checks, not full-suite release evidence; use `make release-verify` for the current per-file release claim.

## Aggregate evidence lane

Makefile defaults are the handoff contract:

```text
CHUNKS=64
MAX_NEW_TESTS=60
MAX_NEW_FILES=4
TEST_BATCH_SIZE=10
FILE_TIMEOUT=45
MAX_RUNTIME_SECONDS=18
TEST_MANIFEST=.artifacts/mxtest-all-64.json
TIMELY_MANIFEST=.artifacts/mxtimely-mxtest.json
RELEASE_MANIFEST=.artifacts/mxrelease-full-suite.json
RELEASE_MAX_RUNTIME_SECONDS=8
RELEASE_BATCH_TIMEOUT=20
RELEASE_BATCH_SIZE=12
RELEASE_MAX_NEW_BATCHES=0
TIMELY_TIMEOUT_SCALE=1
```

Run bounded resumable progress:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --run-chunks 64 \
  --strategy segment \
  --isolate-files \
  --resume \
  --checkpoint-tests \
  --max-new-tests 60 \
  --max-new-files 4 \
  --test-batch-size 10 \
  --file-timeout 45 \
  --max-runtime-seconds 18 \
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

## Short-window full-suite release lane

The current release lane avoids whole-suite collection and accumulates per-file
pytest evidence in fresh child processes:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make release-suite
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make release-next
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make release-verify
python tools/mxrelease.py --manifest .artifacts/mxrelease-full-suite.json --summary
```

`make release-suite` is intentionally resumable and may stop after a clean
partial checkpoint. `make release-next` prints the manifest's copy/pasteable
next action for weaker handoff agents: continue, inspect a failed/timed-out
batch, or verify. `make release-verify` is the complete/current full-suite
claim and fails if `.artifacts/mxrelease-full-suite.json` is incomplete, failed,
timed out, or stale relative to the source digest.

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
