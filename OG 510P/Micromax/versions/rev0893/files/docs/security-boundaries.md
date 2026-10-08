# Micromax security boundaries

This is the living security contract and threat model for the current in-process editor host.  It
must stay tied to executable behavior.  Do not use it to imply an OS sandbox,
process isolation, or safety for adversarial native/Python code.
This contract is part of the curated installed-help corpus as of rev0873 and reflects rev0893 retired-macro refusal and timer pending-work budget, rev0892 active-interaction generation cleanup, rev0891 retired-callback refusal, rev0890 wordlist tombstones, rev0889 dictionary/provenance rollback coupling, rev0888 scoped live-callback rollback, rev0887 cleanup diagnostics, opt-in durable cleanup failure receipts, narrow group/generation cleanup restore, and touched command/action/keymap/timer/hook/mark/delayed-row/singleton-help/recovery/interaction plus generation macro rollback behavior.

## Assets

- User files opened, saved, listed, or remembered by the editor.
- User configuration and init files.
- Plugin source, metadata, runtime registrations, timers, hooks, commands,
  keybindings, active interactions, saved macro slots, and palette MRU rows.
- Editor state that can reveal user work: buffers, marks, recent files, prompt
  history, clipboard rows, search state, messages, and undo/navigation stacks.
- Trust decisions: startup trust state, restricted plugin-load grants, grant
  revocation state, and provenance shown to the user.
- Release evidence: tests, context snapshot, audit metrics, revision index, and package archive.

## Actors

- **User/trusted operator:** intentionally opens files, types commands, loads
  plugins, and approves source execution.
- **Workspace-controlled code:** repository plugins, local Micromax files, and
  documents that can influence editor behavior if evaluated.
- **Script/plugin context:** code already running inside the Micromax VM under
  editor script authority.
- **Broken extension:** non-malicious plugin code that fails during load, reload,
  lifecycle hooks, or cleanup.
- **Hostile local process:** another process or user account changing files while
  Micromax is running.  Current mitigations are best effort, not a complete
  defense.

## Trust states

### Trusted

Trusted is the compatibility default.  Startup may load bundled or configured
plugins and user init automatically.  Manual plugin load/reload follows the
ordinary recovery path.

### Restricted

Restricted is for browsing an unfamiliar workspace without silently evaluating
workspace-controlled code.

- Startup scans plugin metadata and entry containment but does not evaluate
  plugin source.
- Startup skips user init automatic evaluation.
- `plugin load NAME` is the explicit user transition from scanned candidate to
  evaluated source.
- `plugin reload NAME` only reloads an already loaded plugin and requires an
  active grant.
- Grants are session-local and can be revoked.
- Grants are stale if the plugin name, root, entry, or package digest no longer
  matches disk.
- Loaded restricted plugin callbacks get package-local source-load authority only
  while the loaded generation still matches its package digest and the matching
  session grant is still active.
- Failed live plugin callbacks restore plugin-owned runtime group/generation
  state through scoped snapshots when the callback still resolves to a loaded
  plugin; source/lifecycle/deinit registrations still use the broader plugin
  transaction snapshot. VM dictionary topology and dictionary-keyed word
  provenance now restore together on every dictionary rollback path.
- `plugin unload NAME` removes a loaded plugin through the plugin-manager cleanup
  path and revokes the matching restricted session grant only after required
  runtime-group cleanup succeeds.
- Failed runtime-group cleanup or staged-retag commit sweeps abort unload/reload
  rather than reporting false clean success.
- Cleanup/retag commit guards restore partial group-sweep mutations with a
  narrow runtime-group snapshot rather than the broad plugin transaction
  snapshot.  Command, action, keybinding, timer, hook, mark, recent-file, palette-MRU, prompt-history, saved-cursor, clipboard, active-search, and help-history state inside that guard now restore from touched runtime state instead of full surface copies.
- Plugin-originated code cannot clear or change its loader-owned runtime group
  while registering commands, keys, timers, hooks, actions, or marks.
- Plugin-owned active keymodes, prompts, query-replace sessions, and pending URL
  confirmations are tagged with the same cleanup group and removed on unload.
- Plugin-owned saved macros are treated as delayed executable state and removed
  or restored by plugin lifecycle transactions.
- Plugin-owned saved-selection and jumplist rows are treated as delayed
  navigation/recovery state and removed or restored by plugin lifecycle
  transactions.
- Plugin-owned active-search registers are treated as delayed navigation state
  and removed or restored by plugin lifecycle transactions.
- Plugin-owned prompt-history rows, help-history rows, active-search registers, and clipboard registers are treated as delayed executable/replay/navigation state
  and removed or restored by plugin lifecycle transactions.
- Plugin-owned recent-file MRU and savecursor rows are treated as delayed
  file-navigation state and removed or restored by plugin lifecycle transactions.
- Plugin-owned command-palette MRU rows are treated as delayed command/action
  selection state and removed or restored by plugin lifecycle transactions.
- Plugin-owned internal clipboard contents are treated as delayed paste/export
  state and removed or restored by plugin lifecycle transactions.
- Scripts cannot self-approve restricted loads, revoke grants, or unload plugins.

Restricted does **not** prevent a user from manually evaluating code, and it does
not make approved code safe.

## Defended attacks

| Attack | Current mitigation |
| --- | --- |
| Workspace plugin runs at startup while browsing unfamiliar code. | `--trust restricted` scans metadata only and skips source evaluation. |
| User init runs automatically in restricted startup. | Restricted startup skips user init and reports that decision. |
| `plugin reload NAME` hides a first-time load. | Restricted reload refuses available-but-unloaded candidates and points to `plugin load NAME`. |
| Script approves its own plugin load. | Restricted `plugin load NAME` is denied in script context. |
| Script revokes, unloads, or inventories grants/plugins silently. | `plugin revoke` and `plugin unload` are denied in script context; `plugin grants` is hidden without `cap.plugin-read`. |
| Metadata or entry path changes after approval. | Restricted reload re-reads disk and treats the grant as stale. |
| Same-path source/helper bytes change after approval. | Rev0859 package digests make the grant stale. |
| Changed helper is lazy-loaded later by an old plugin callback. | Rev0860 withholds callback package-local source-load authority until a fresh approved reload lands. |
| Revoked grant still allows future callback helper loads. | Rev0861 requires an active matching grant before restricted callbacks regain package-local source-load authority. |
| Failed live plugin callback still needs the broad 40-field runtime snapshot. | Rev0888 passes loaded plugin group/root/generation identity into callback rollback and uses scoped group plus generation snapshots, while preserving cursor, option, execution, and message rollback. Legacy/no-identity callbacks, plugin source loading, lifecycle hooks, and deinit rollback still use the broad fallback. |
| Failed plugin source/lifecycle rollback removes transient words but leaves their word-authority rows behind. | Rev0889 stores editor word provenance in `VmDictionarySnapshot`, restores dictionary topology first, then filters/restores provenance against live words. Failed source, staged lifecycle, deinit, and callback rollback share this invariant. |
| Successful plugin reload/unload leaves old committed wordlists and executable `Word` objects live indefinitely. | Rev0890 records bounded `PluginWordlistTombstone` metadata, removes retired wordlists from live VM lookup/search order, scrubs word authority rows for the retired wid, and marks direct saved XTs so stale invocation fails clearly. |
| Captured keybindings, hooks, or timers from a retired plugin generation continue to run later under ambient authority. | Rev0891 makes generated plugin callbacks pass through `Editor.run_script_origin_callback()` and refuse execution when their captured plugin generation is no longer loaded; hook handlers and timers now share this runner. Legacy rows without generation still lose private package-root authority and fall back to ordinary filesystem capability checks. |
| Restricted manual plugin grant fingerprinting can walk or hash an unexpectedly large package tree. | Rev0890 adds file-count and total-byte package fingerprint budgets before a grant can be accepted. |
| User cannot remove a loaded plugin surface without restarting. | Rev0861 adds interactive `plugin unload NAME`, backed by the existing cleanup transaction and blocked in script context. |
| Plugin unload or reload cleanup partially fails but the manager still reports the plugin as cleanly removed or replaced. | Rev0875 makes unload old-group cleanup and reload old-cleanup/staged-retag commit-critical. Rev0876 restores partially swept group surfaces with a narrow snapshot. Rev0877 also guards generation-scoped delayed-state cleanup and restores both group and generation snapshots when unload/reload-old cleanup fails after partial mutation. Rev0878 exposes retained failed surfaces through `plugin cleanup [NAME]` and `ed.plugin-cleanup-failure-rows`; rev0879 narrows command rollback inside group sweeps to touched command groups; rev0880 applies the same touched-group rule to actions, keybindings, and pending timers; rev0881 applies it to hooks and marks and fixes mutable hook-handler snapshot evidence; rev0882 applies touched authority-row rollback to recent files, palette MRU, prompt history, and saved cursors; rev0883 applies touched authority-state rollback to clipboard, active search, and help history; rev0884 applies touched rollback to recovery stacks and delayed interactions and preserves trusted named `qreplace`/`openurl` keymodes during plugin-owned interaction cleanup; rev0885 scopes non-macro generation cleanup rows/registers; rev0886 scopes macro generation cleanup slots/recording; rev0887 can persist failed cleanup-surface receipts as opt-in JSONL behind `cap.persist` and `plugin.cleanup-log.persist`, so `plugin cleanup` can still show diagnostic rows after restart. |
| Plugin clears or changes its runtime group so callbacks survive unload cleanup. | Rev0862 locks loader-owned plugin editor/hook groups during plugin-originated execution and denies group escape attempts. |
| Plugin leaves delayed interaction state behind after unload. | Rev0863 stamps active keymodes/prompts with the plugin group and removes matching keymodes, prompts, query-replace sessions, and pending URL confirmations during plugin cleanup. |
| A stale prompt, query-replace session, or URL confirmation is reinserted after its plugin generation is retired. | Rev0892 rejects the response with a `stale plugin ...` denial, refuses the submit/edit/open effect, and clears the retired interaction object. |
| A saved macro slot from a retired plugin generation is reinserted or survives outside ordinary cleanup. | Rev0893 rejects playback with `macro play: stale plugin macro ...`, clears the retired slot, and prunes it before raw macro read/list/detail exposure. |
| Plugin queues unbounded delayed timer callbacks through `ed.after`. | Rev0893 routes `ed.after` through `Editor.schedule_timer_checked()` and refuses new delayed callbacks once `max_pending_timers` is full. |
| Plugin leaves a saved macro that later replays after unload. | Rev0864 treats saved macros as delayed executable state: unload removes macro slots owned by the plugin generation, and failed plugin lifecycle transactions restore the prior macro registry. Rev0886 narrows generation-cleanup rollback to plugin-owned saved slots/`last` only when owned, without rewinding unrelated trusted/user macro slots. Rev0893 adds a stale-generation guard for reinserted saved macro slots. |
| Plugin reload cannot replace its own same-named macro without losing the old macro on failure. | Rev0864 temporarily prunes old-generation macros under a transaction snapshot so staged reload can replace them and failed staged reload restores them. Rev0886 restores only selected generation-owned macro slots and any generation-owned active recording when generation cleanup later fails. |
| Plugin leaves saved-selection or jumplist recovery rows behind after unload. | Rev0865 removes selection-stack and jumplist rows owned by the unloaded plugin group/generation. |
| Plugin reload recreates the same jumplist snapshot but deduplication suppresses the new row before old cleanup. | Rev0865 prunes old-generation recovery rows under the transaction snapshot before staged evaluation, then retags staged rows or restores old rows on failure. |
| Plugin leaves an active search query that later drives find-next/find-prev after unload. | Rev0866 removes active-search registers owned by the unloaded plugin group/generation and restores them on failed staged reload. |
| Plugin reload should replace or drop its old active search without leaving stale query state. | Rev0866 prunes old-generation active search under the transaction snapshot, retags staged search on success, and restores old search on failure. |
| Plugin leaves command/find prompt-history text that can be replayed after unload. | Rev0867 removes prompt-history rows owned by the unloaded plugin group/generation and restores them on failed staged reload. |
| Plugin-authored command history was persisted before unload. | Rev0867 best-effort saves prompt-history pruning when history persistence is enabled, so stale plugin command text is not reintroduced from the configured history file. |
| Plugin leaves recent-file MRU or savecursor navigation rows after unload. | Rev0868 removes recent-file and savecursor rows owned by the unloaded plugin group/generation and restores them on failed staged reload. |
| Plugin-authored file-navigation rows were persisted before unload. | Rev0868 best-effort saves recent-file/savecursor pruning when those persistence stores are enabled, so stale plugin navigation rows are not immediately reloaded from disk. |
| Plugin leaves command-palette MRU rows that keep stale command/action choices near the top of later palette prompts. | Rev0869 removes palette MRU rows owned by the unloaded plugin group/generation and restores them on failed staged reload. |
| Plugin leaves internal clipboard contents that later feed paste or clipboard export after unload. | Rev0870 removes clipboard state owned by the unloaded plugin group/generation and restores it on failed staged reload. |
| Plugin leaves helpback/helpforward/helpresume navigation rows after unload or reload. | Rev0871 removes help-history rows owned by the unloaded plugin group/generation, retags staged replacement rows, and restores old rows on failed staged reload. |
| Plugin reload pre-prunes old help-session rows while the old help buffer is still visible, accidentally turning the old plugin target into trusted history. | Rev0871 falls back to active help-buffer authority when session rows were intentionally pruned, so staged reload cannot launder old plugin-opened docs targets into ambient trusted help history. |
| Failed plugin source, reload, deinit, or callback leaves ordinary option changes behind even though the plugin transaction rolled back. | Rev0872 snapshots global and buffer-local option state in plugin runtime transactions and restores it on failure or discarded deinit mutations; rev0874 binds new buffer-local snapshots to live buffer identity rather than mutable names. |
| Failed runtime-group cleanup report is visible but has no consequence for commit paths. | Rev0875 uses reports as policy for unload/reload commit sweeps, while still preserving the primary plugin error when cleanup evidence is collected during an already-failing source/lifecycle path. |
| Broad “plugin transaction” wording implies that all effects are atomic. | Rev0873 documents the missing effect-lifecycle contract: arbitrary document edits, new buffers, file opens, durable writes, external I/O, and process effects are not covered by the current state snapshot unless a narrower contract explicitly says so. |
| Runtime group cleanup or retag partially fails but looks clean. | Rev0874 returns structured cleanup/retag operation reports and retains bounded plugin-manager evidence, while preserving best-effort sweeping. |
| Generation-scoped delayed-state cleanup fails after group cleanup has already removed registrations. | Rev0877 reports generation-cleanup failures, restores delayed-state surfaces from `RuntimeGenerationStateSnapshot`, and restores group state too in unload/reload-old cleanup commit guards. Rev0885 makes non-macro generation rows/registers root/generation scoped; rev0886 makes macro generation rollback root/generation scoped too. |
| User cannot inspect which cleanup surface failed after unload/reload aborts. | Rev0878 adds `plugin cleanup [NAME]`, `ed.plugin-cleanup-failure-rows`, prompt-completion visibility, and audit checks for retained cleanup/retag/generation failure rows. Rev0879 points failed unload/reload feedback to `plugin cleanup NAME` when retained rows exist; rev0880 keeps those diagnostics while narrowing more registry rollback state; rev0881 keeps them while narrowing hooks and marks; rev0882 keeps them while narrowing delayed recent/palette/prompt/saved-cursor rows; rev0883 keeps them while narrowing clipboard/search/help-history state; rev0884 keeps them while narrowing recovery/interaction state; rev0885 keeps them while narrowing non-macro generation rows; rev0886 keeps them while narrowing macro generation state; rev0887 can persist them across restart when cleanup-log persistence is explicitly enabled. |
| Broken plugin reload leaks staged registrations. | Plugin reload uses staged groups, snapshots, rollback, and cleanup. |
| Plugin reads source outside its package through relative include/require. | Plugin execution context grants only package-local loads unless separate script filesystem capability is present. |
| Script reads/writes arbitrary files through editor hostcalls. | Capability roots and explicit `cap.fs-*` options gate script file operations. |

## Residual risks

- Everything still runs inside one Python process.
- A loaded plugin can consume memory, block, exploit Python/native bugs, or abuse
  any hostcall it is allowed to reach.
- Step budgets do not bound all wall-clock time, memory, subprocesses, terminal
  behavior, or native library behavior.
- Package digests, package fingerprint budgets, grant checks, runtime-group locks, delayed-interaction cleanup, saved-macro cleanup/refusal, recovery-stack cleanup, active-search cleanup, prompt-history cleanup, file-navigation cleanup, palette MRU cleanup, clipboard cleanup, help-history cleanup, generation cleanup guards, touched command/action/keymap/timer/hook/mark/delayed-row/singleton-help/recovery/interaction/macro cleanup restore, retired-wordlist tombstones, retired deferred-callback guards, retired interaction guards, timer pending-work budgets, scoped live-callback rollback, and option rollback are stale-grant,
  stale-callback, and cleanup-consistency checks, not signed provenance or atomic
  filesystem attestation.
- A hostile local process can still race file changes around non-atomic checks.
- There is no durable per-plugin permission store, signed plugin identity,
  separate extension host, Wasm boundary, or seccomp/container policy.
- The public extension contract is not yet stable enough to promise broad
  third-party plugin compatibility.
- Plugin rollback/cleanup semantics are distributed across authority sidecars,
  remove/retag helpers, and a 40-field snapshot rather than one executable
  effect-class/lifecycle contract. Rev0889 couples word provenance to dictionary
  rollback, rev0890 tombstones retired wordlists, rev0891 refuses retired generated callbacks, rev0892 generation-scopes active delayed interactions, and rev0893 refuses retired saved macro playback, but other ownership mistakes remain possible until the matrix exists.
- Retired wordlists are removed from dictionary lookup after unload/reload, direct saved XTs fail clearly, and saved macro rows now prune when stale; other resource references still need explicit stale-reference observability.
- Some restore paths still contain best-effort exception swallowing. Runtime-group
  cleanup/retag and generation-cleanup failures are now surfaced as structured
  reports on the guarded plugin-manager paths, and command/action/keymap/timer rows are the first
  touched-group rollback slice, but arbitrary host effects still do not have one
  uniform journal.

## Decision rules

- Prefer a visible denial over silent evaluation.
- Prefer a stale/revoked grant, withheld callback include root, scoped failed-callback rollback, denied plugin group change, or removed plugin-owned delayed interaction/macro/recovery/search/history/file-navigation/palette/clipboard/help state, scoped failed generation cleanup restore, or restored failed plugin option mutations over executing or retaining surfaces the user did not re-approve or still authorize.
- Keep restricted mode about automatic code loading and explicit manual approval;
  do not claim it contains malicious code.
- Do not add a universal untyped registry where one typed effect adapter, resource handle, or journal record would suffice.
- Runtime behavior, command messages, prompt completion, docs, and revision index
  must agree on each boundary.
