# Micromax security boundaries

This is the living security contract and threat model for the current in-process
editor host. It must stay tied to executable behavior. Do not use it to imply an
operating-system sandbox, process isolation, or safety for adversarial
native/Python code.

Rev0982 gives synchronous Popen construction a finite caller boundary and makes
true-wordwrap/search/replacement/multicursor coordinates sparse under exact leases.
Rev0981's multiprocessing start owner and rev0980's spawn-first context remain
current. Rev0979's complete framed worker result boundary
and visible large-buffer dirty policy, rev0978's capture-pipe ownership,
rev0977's finite browser child, rev0972's reduced plugin world, rev0973's
host-owned instruction fuel, rev0974's allocation preflight, rev0975's Linux
regex-child memory ceiling, and rev0976's checked i64 boundary remain in force.
This contract is included in installed help.
Historical narrow changes are indexed in `docs/revision-index.json`; current
generated high-risk effect facts are in `docs/33-effect-resource-contract.md`.

## Assets

- User files opened, saved, listed, or remembered by the editor.
- Private interrupted-save records containing exact unsaved editor text, commit fingerprints, target/parent authority, requested-path metadata, final permission intent, and save-lease evidence.
- Private checkpoint/document temporary files that may contain exact unsaved text after abrupt process death.
- User configuration and init files.
- Plugin source, metadata, runtime registrations, timers, hooks, commands,
  keybindings, active interactions, saved macro slots, and palette MRU rows, and help-history rows.
- Editor state that can reveal user work: buffers, marks, recent files, prompt
  history, clipboard rows, search state, help-history rows, messages, and undo/navigation stacks.
- Trust decisions: startup trust state, restricted plugin-load grants, grant
  revocation state, and provenance shown to the user.
- Release evidence: captured source rows, generated context, focused test logs,
  builder declaration, wheel bytes/verification records, installed-artifact
  probe, receipt, revision index, and package archive.

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

## Release source and build boundary

**Threats:** tests, wheels, and archives can observe different working-tree
states; symlinks or special files can redirect capture; source timestamps,
permissions, caller umask, home state, Python paths, or package indexes can
become undeclared build inputs; malformed wheels or receipts can create false
evidence; mutable action tags can retarget CI code.

**Current mitigation:** `tools/mxrepro.py` captures declared regular-file bytes
once, generates context once, and materializes independent phase trees. It
rejects live-byte/mode drift, normalizes source timestamps and 0644/0755 modes,
uses separate homes and a deterministic offline environment, builds and verifies
two byte-identical wheels, installs the exact candidate under isolated Python,
and seals the result in one bounded receipt. `tools/mkrevzip.py` recomputes the
source identity and requires two byte-identical archives. The CI workflow has
read-only contents permission, no persisted checkout credentials, and full-SHA
action pins.

**Residual boundary:** capture is file-by-file rather than an atomic hostile-
writer snapshot. Equality is for one declared toolchain/platform class. Builder
downloads are exact-version but not hash-locked/hermetic. Mode normalization
discards original permission intent. Receipt integrity is not signing,
authorship, transparency, SLSA, public CI execution, or a complete-suite claim.

## Input and delayed authority

A physical keypress starts outside script context, but it is not a blanket
privilege grant. Keybindings and active keymodes can outlive the code that
created them, so both carry origin metadata.

- The shipped product keymap is installed by the host before plugins. Its normal
  open, save, undo, clipboard, picker, and palette paths are interactive editor
  behavior and do not require script capabilities.
- `plugins/core/init.mx` is an exact readable mirror. Exact repeats are
  idempotent and cannot take ownership of already-installed trusted rows.
- A binding added by a plugin remains plugin-owned. A later user keypress runs
  it under the captured plugin root, generation, group, and script origin.
- A mode activated by a script remains a delayed authority object. A trusted
  binding selected through that mode runs under the mode's lower authority.
- Query-replace captures the exact target buffer object, observed text
  generation, and creating script authority. Later physical answers cannot
  retarget a recycled name, reuse stale coordinates, or elevate plugin-owned edits.
- A script-owned project picker captures only buffer/recent context already
  readable by that origin. If `cap.fs-open` or another delayed check denies the
  selected target, retaining the prompt preserves the same lower origin and
  immutable inventory; a later physical Enter cannot launder interactive
  authority or trigger an implicit rescan.
- Script-origin synthetic keypresses never borrow the target binding's trusted
  authority; even an allowed protected replay stays under the caller's script
  context.
- Trusted user init and interactive commands may intentionally rebind defaults.
- Restricted startup installs the host baseline without evaluating plugin or
  user-init source.

This distinction keeps the editor usable under safe defaults without laundering
extension code through user gestures.

## Plugin namespace and presentation boundary

**Threats:** load-order dependencies become ambient imports; an undeclared sibling
or transitive implementation word shadows an intended dependency; visibility of
a dependency permits definitions or deferred-behavior replacement; a plugin
probes exact statusline/prompt/screen snapshots and couples itself to trusted host
internals.

**Mitigations:** `plugin.json requires` defines one deterministic readable closure
for source, lifecycle, and delayed callbacks: self, direct dependencies in
manifest order, breadth-first transitive dependencies, then Forth. Only self is
writable. Namespace primitives preflight the active `WordlistAccessScope`,
`VM._add_word()` enforces final dictionary mutation, and owned deferred words
require the same write authority for `is` / `defer!`. Module/wordlist creation is
internal. Broad hook inventory is filtered to readable wordlists. Exact
presentation models are absent from plugin feature probes and denied before
call operands are consumed; trusted host/headless/TUI execution is unchanged.

**Residual boundary:** this is in-process application policy. Mutable values
explicitly returned by dependencies remain object capabilities, shared hook
registration remains an intentional extension point, and most hostcalls remain
experimental rather than denied. Rev0973 adds the distinct instruction-dispatch
boundary below; rev0974 separately owns predictable string-result amplification.
Syscalls, arbitrary native/blocking work, total heap, and process faults remain
outside both.

## Plugin instruction-liveness boundary

**Threats:** plugin source or lifecycle runs forever; a retained command, key,
timer, hook, prompt operation, or macro step monopolizes the UI thread; guest
code clears the apparent host limit with `-1 set-budget`; nested evaluation starts
with a fresh allowance; a hostile `deinit` prevents recovery by graceful unload.

**Mitigations:** script base/nested budgets and embedding-owned host frames are
separate VM state. Every dispatched step decrements every active host frame.
Plugin source/lifecycle and recognized retained callbacks enter one fresh finite
host budget, then restore prior script-budget state. Exhaustion uses the existing
error/rollback path; an uncommitted candidate stays uncommitted, failed delayed
state is restored, a failed graceful deinit leaves the live generation present,
and force unload/revoke remain recovery lanes. Guest code cannot clear or enlarge
the host frame through language words.

**Residual boundary:** fuel counts Micromax instruction dispatch. It does not
interrupt a blocking/expensive Python or native primitive after dispatch enters
that call, cap memory, isolate syscalls, survive interpreter corruption, or
contain process crashes. Tokenization/parsing before execution is also outside
the step counter. Those risks need measured per-resource owners, not a stronger
claim for fuel.

## External browser-launch boundary

**Threats:** an allowed `ed.open-url` call enters Python's platform browser controller after one Micromax dispatch. A Unix text-mode browser can make that controller wait until browser exit, monopolizing the editor/plugin thread beyond the reach of VM fuel. Malformed or non-finite deadline tuning can also erase an apparently finite process/worker owner.

**Mitigations:** URL validation and `cap.open-url` run before the effect. The product default launches an absolute `open_url_child.py` through `python -I -S` and the bounded argv process owner. The child alone imports `webbrowser`; the parent applies a six-second deadline, 16 KiB combined diagnostic ceiling, fresh process group where supported, and terminate/kill teardown. A POSIX end-to-end hostcall test observes the blocking browser PID, proves it is gone after timeout, and executes more code in the same VM. Shared subprocess capture and multiprocessing teardown remove duplicate policy; boolean, malformed, `NaN`, and infinite deadlines fall back to finite defaults while declared finite non-positive/`None` direct modes stay explicit.

**Residual boundary:** one platform constructor that never returns can retain one daemon starter and the single-pending gate, although this and later callers remain finite. Starter creation and late cleanup callbacks are not independently preemptible. POSIX descendant cleanup is stronger than the current Windows direct-child fallback. Successfully detached browsers intentionally survive. This boundary does not sandbox browser code, filter syscalls, cap total memory, survive interpreter corruption, contain arbitrary native crashes, or grant URL authority.

## Captured subprocess and filesystem-worker completion

**Threats:** a bounded shell/argv leader exits successfully after starting a descendant that retains stdout, stderr, or stdin. The pipe never reaches EOF, daemon capture threads remain live, and ancestry cleanup can miss a descendant that creates a new session and is reparented. Separately, a one-shot worker can fill a Queue feeder before parent reap or can leave a valid length prefix plus incomplete body; CPython's Queue timeout polls readiness once and then enters a blocking full-frame receive.

**Mitigations:** the shared process owner names its capture threads, records POSIX anonymous-pipe identity, and joins all I/O against one absolute drain deadline. If a thread still lacks EOF after the leader stops, Linux exceptional cleanup scans `/proc/*/fd` for the exact pipe objects, prefers pidfd-stable process identity, and applies TERM then forceful teardown; the confirmed process group is the other-POSIX fallback. A child with all standard descriptors redirected owns no capture resource and survives. All affected one-shot filesystem, save, plugin, docs, project, and compatibility-regex multiprocessing results use a private magic/length socket frame; the nonblocking parent consumes header and body under one absolute deadline, checks declared size before payload growth, decodes one trusted pickle, and closes every process/endpoint path. Their Process constructor/start is deferred into one temporary starter. Gate wait and start share one absolute startup deadline, at most one unresolved starter exists, and a timed-out starter retains sole late child/channel/operation cleanup ownership. Importable workers prefer spawn because the observed forkserver acquired native threads; forkserver remains fallback and explicit fork is rejected.

**Residual boundary:** exact capture-holder discovery is Linux procfs-specific and permission-dependent. Pidfds are used only when both Python and the kernel support them; the older-Linux start-time/numeric-PID fallback is best effort, not atomic. Windows has direct-child cleanup, not tested Job Object ownership; framed sockets and starter handoff are tested here only on Linux. A permanently blocked platform start can retain one daemon starter and its gate even though callers and retries remain finite. Starter-thread creation, synchronous late-cleanup callbacks, child-side serialization, and Windows whole-tree ownership are not fully bounded. Regex/browser/general process Popen construction now uses the separate rev0982 single-pending owner and shares an absolute lease with readiness or execution. Correctly detached effects intentionally outlive Micromax. Private-worker pickle is not a hostile-sender boundary. This does not sandbox subprocess code, filter syscalls, cap total host memory, or contain arbitrary native crashes.

## Sparse editor-coordinate boundary

**Threats:** a huge logical line or dense match/edit set retains one Python object per wrap boundary, line start, span endpoint, or rich replace row; repaint/debug paths accidentally rematerialize the complete geometry; stale cached geometry addresses changed text.

**Mitigations:** true wordwrap stores bounded native checkpoints and resumes exact decisions locally; the visual-row index retains only four exact line layouts and evicts changed lines. Search owns native line/span arrays and bounded representations. Replacement keeps compact apply edits and materializes rich rows only for compatibility/samples. Simultaneous edits reuse a caller-owned compact line index. Every cache is tied to exact text identity/version/configuration or discarded.

**Residual boundary:** first scans remain proportional to source length; source/replacement text, undo snapshots, compatibility APIs requesting all rows, RSS/native allocations, and arbitrary plugin values are not capped by coordinate packing. `array('Q')` assumes editor coordinates fit unsigned 64-bit cells, which is far beyond Python's practical string address space but remains an explicit representation choice.

## Predictable string-allocation boundary

**Threats:** a plugin enters one string hostcall that projects far more output
than the configured result ceiling; the Python allocator fails before the generic
postcondition; a repeated-reference list makes a defensive preflight rescan or
copy caller data; core value rendering expands a modest object graph during one
VM instruction.

**Mitigations:** concatenate, split, join, and replace compute prospective bytes
and cells before allocation while retaining all operands. Join validates in
place, uses a fixed-size alias cache, and stops on the first proven overrun.
`to-str`, `.`, `.s`, and `s-format %s` share an incremental renderer under a
separate finite ceiling. UTF-8 counting does not materialize a second byte copy;
malformed tuning fails to defaults. The generic post-hostcall check remains
defense in depth.

**Residual boundary:** existing inputs already occupy memory. Counting and native
string operations still consume CPU in one dispatch; upper/lower case conversion
retains a bounded-factor allocate-then-check path; child memory, arbitrary native
work, crashes, syscalls, and process compromise are not contained.

## Checked integer-domain boundary

**Threat:** script/plugin code grows arbitrary Python integers inside one VM primitive; fuel cannot interrupt the multiplication, late allocator failure can erase operands, and booleans or host-mutated bytecode can re-enter through weak `isinstance(int)` checks.

**Mitigations:** `micromax.vm` owns one non-boolean signed-64-bit predicate, bounded decimal parser, and bytecode ingress/export/dispatch validation. `micromax.core` inspects integer operands before mutation and commits only after range/zero checks. Source, `to-int`, JSON integer text, version/constants/operands/spans, compiled code, and plugin callbacks reuse the same rule; negative constant indexes are rejected instead of inheriting Python list semantics.

**Residual boundary:** strings, collections, cells, quotations, map keys, generic equality, and opaque host values may still retain memory or invoke host behavior. Linear scanning of already-admitted input still costs CPU. Native blocking/crash/syscall paths and interpreter compromise remain outside this language boundary.

## Recoverable startup and destructive exit

**Threats:** a failed first open can leave no active buffer and turn a normal
render into a traceback; a front end can bypass dirty-buffer policy by breaking
its own loop; and a sticky repeat-to-confirm bit can authorize discarding edits,
new targets, or replacement buffers that were never named by the warning.

**Mitigations:** CLI and TUI call `startup.open_initial_buffer()`, whose typed
result distinguishes requested-open success from a guaranteed live fallback.
Headless screen dump emits the fallback model but returns nonzero on requested
open failure. The headless REPL routes `:q`, `:q!`, and EOF through normal editor
quit policy; dirty exhausted non-interactive EOF returns status 2, while terminal
EOF returns to the prompt without retaining confirmation. `quit`, `close`,
`closeall`, and `only` share one weak-identity witness over operation scope,
buffer object, mutation version, dirty bit, path, and retained `only` context.
Only an unchanged second request confirms; relevant changes replace the witness
and refresh the warning. Force forms remain explicit.

**Residual risk:** the witness relies on supported buffer mutation paths keeping
`Buffer.version` monotonic. A fallback buffer is usability recovery, not success
for the requested open. The interactive TUI continues after recoverable failure
rather than returning the headless dump status. In-process native/Python code can
bypass application policy.

## Buffer creation and retained identity

**Threats:** a duplicate display name can silently replace a live dictionary
entry, orphan dirty text without close/discard policy, retarget name-keyed marks
or authority metadata, or let a script allocate unbounded retained editor state.

**Mitigations:** `Editor.new_buffer()` is strict and raises before cursor
allocation or any editor mutation when the exact name is live. The pure bounded
`unique_buffer_name()` owner supplies deterministic `<N>` / `*name-N*` labels to
`new_buffer_unique()`. File/help opens first reuse normalized path identity and
otherwise preserve pathless same-name buffers under a disambiguated label. The
human `new [NAME]` command and `NewBuffer` action share
`create_untitled_buffer()`. Script context is denied. Rollback clears and updates
the existing public `buffers` and `marks` mappings instead of replacing them, so
retained embedder/inspector references remain live. The structural audit parses
guard ordering and inventories buffer insertion, deletion, rename removal, bulk
restore, whole-registry assignment, and mark-registry restore owners.

**Residual risk:** buffer names remain lookup keys across several sidecars; the
no-clobber rule prevents accidental replacement but is not an immutable-ID
architecture. There is no `cap.buffer-create`: a future script surface must bound
live count, initial bytes, provenance, visibility, unload, close/save, and
rollback. In-process Python/native code can still mutate dictionaries directly.

## Project-file discovery and delayed open

**Threats:** recursive discovery can consume unbounded CPU/memory/time, block on
unusual filesystems, expose hidden/generated paths, follow symlinks outside a
workspace, retain a stale path after disk changes, or let a plugin-created picker
borrow the authority of a later user Enter. Process workers can also deadlock if
a parent joins before draining a full queue, or inherit inconsistent lock state
when a multithreaded editor forks.

**Mitigations:** one picker open creates one deterministic immutable snapshot.
Host defaults cap files, directories, depth, observed entries, relative-path
bytes, and wall time. Hidden entries are off by default; VCS/cache/build
directories remain excluded. POSIX traversal uses fd-relative opens and
`O_NOFOLLOW` where available. Submission accepts only a captured clean relative
path, strictly re-resolves it, proves containment, rejects symlink traversal or
type changes, performs a bounded stat, and then opens. Script creation requires
`cap.fs-list`; script submission requires `cap.fs-open`; prompt origin survives
physical navigation. New recursive workers prefer `spawn`/`forkserver`, receive
one complete private framed result before reap, and release every process/socket
path on success and failure.

**Residual risk:** filesystem containment is best-effort application policy, not
an OS sandbox. The portable path fallback cannot offer every POSIX fd guarantee;
remote/kernel filesystems may still behave unexpectedly; snapshots can become
stale and therefore fail; built-in exclusions are not `.gitignore` semantics.
Legacy short filesystem workers still prefer `fork` for compatibility and should
be migrated. A hostile native/Python extension in-process can bypass this model.

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
  snapshot.  Command, action, keybinding, timer, hook, mark, recent-file, palette-MRU, prompt-history, saved-cursor, clipboard, active-search, help-history, and recovery state inside that guard now restore from touched runtime state instead of full surface copies.
- Plugin-originated code cannot clear or change its loader-owned runtime group
  while registering commands, keys, timers, hooks, actions, or marks.
- Plugin-owned active keymodes, prompts, query-replace sessions, and pending URL
  confirmations are tagged with the same cleanup group and removed on unload.
- Plugin-owned saved macros are treated as delayed executable state and removed
  or restored by plugin lifecycle transactions.
- Plugin-owned saved-selection and jumplist rows are treated as delayed
  navigation/recovery state and removed or restored by plugin lifecycle
  transactions through an editor-owned recovery register.
- Plugin-owned active-search registers are treated as delayed navigation state
  and removed or restored by plugin lifecycle transactions.
- Plugin-owned prompt-history rows, help-history rows, recovery rows, active-search registers, and clipboard registers are treated as delayed executable/replay/navigation state
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
| Bundled default keys inherit plugin authority, so safe script capabilities disable ordinary user open/save/undo/clipboard/navigation. | Rev0952 installs one declarative keymap as trusted host policy before plugin load or restricted scanning. The bundled core Micromax rows are exact idempotent mirrors, parity tests prevent drift, and product-journey tests run physical keys with the script capabilities left off. |
| Failed initial path/help open leaves zero buffers, so a renderer or screen dump crashes instead of exposing a usable failure state. | Rev0954 routes CLI and TUI through `open_initial_buffer()`, guarantees a live active fallback, preserves a visible diagnostic, and makes a failed headless dump return valid JSON with nonzero status. |
| Document text, object names, paths, or I/O failures embed ANSI/C1, carriage-return, line-separator, or bidi controls that alter the terminal used to inspect a snapshot or error. | Rev0964 keeps raw v1 JSON intact but makes `micromax-screen` neutralize Unicode `Cc`, `Cf`, `Zl`, and `Zp` characters in text and stderr; programmatic consumers remain responsible for their own output context. |
| A front end treats `:q` or EOF as direct loop exit and bypasses dirty-buffer policy. | Rev0954 routes headless quit and EOF through editor commands; dirty terminal EOF returns to the prompt without retained consent, and dirty exhausted non-interactive EOF returns status 2. |
| Warning once, then edit/open/rename/replace, then repeat `quit`/`close`/`closeall`/`only` discards state that was never confirmed. | Rev0954 replaces sticky booleans with one exact weak-identity/version/path/dirty witness. Any relevant state or operation-scope change refreshes the warning; only an unchanged second request confirms. |
| Duplicate buffer creation silently orphans a dirty same-name buffer and makes marks/authority appear to target a replacement; rollback replaces public registry objects and strands retained references. | Rev0955 makes `new_buffer()` fail before any state mutation, routes human/file/help convenience through bounded deterministic unique labels, denies script untitled creation, restores buffer/mark registries in place, and AST-audits single-key plus whole-registry writers. |
| Query-replace follows a mutable buffer name, so navigation loses accepted-edit undo, rename strands selection, cleanup touches an unrelated active buffer, or close/name reuse retargets delayed edits. | Rev0957 captures a weak exact-buffer witness, centralizes target selection/session/undo disposal, marks mutations under captured authority, finalizes on navigation, follows rename by object identity, and drops before close/name reuse. |
| An unrelated supported edit consumes query-replace's selected match and leaves stale offsets live, so a delayed confirmation edits different text or merges undo chronology. | Rev0966 adds the exact `Buffer.version` to the witness, validates every delayed response, closes before other mutating actions, splits post-hoc recorded edits at their pre-edit snapshot, and refuses unsafe grouped undo after raw drift. |
| Failed plugin cleanup finalizes query-replace into undo and then restores the live session, leaving both a provisional committed edit record and an active interaction. | Rev0957 snapshots undo membership only when query-replace is in the group/generation cleanup scope. Successful cleanup commits one entry; failed cleanup restores the session and rewinds only cleanup-created undo membership. |
| A handoff filename claims a new revision while its manifest, context, living source breadcrumbs, and revision-index head still describe an older tree. | Rev0957 makes `mkrevzip --rev` an assertion over six agreeing repository breadcrumbs; archive verification cross-checks canonical filename, manifest, context, archived sources, timezone, raw member paths, provenance, digests, CRC, duplicates, and budgets before atomic publication. |
| Focused tests, wheel builds, and archives reread a changing source tree and therefore certify different generations. | Rev0965 captures declared regular-file bytes once, generates context once, materializes separate phase copies, rechecks the live tree before publication, and binds the receipt/archive to the same recomputed source identity. |
| Identical source bytes extracted under a restrictive umask produce a different wheel through member permission metadata. | Rev0965 normalizes materialized files/directories to 0644/0755 independent of source mode and caller umask, then rejects phase-time mode drift on POSIX. |
| A malformed or internally inconsistent wheel is byte-compared but still treated as releasable. | Rev0965 independently checks safe unique members, CRC, complete `RECORD` hashes/sizes, normalized timestamps, PEP 639 metadata/license placement, resources, plugins, docs, and entry points, then installs and probes the exact selected wheel. |
| A CI action tag moves or checkout credentials grant unnecessary write-capable state. | The rev0965 workflow has `contents: read`, disables persisted checkout credentials, and pins checkout/setup actions to full release commit SHAs. |
| `plugin reload NAME` hides a first-time load. | Restricted reload refuses available-but-unloaded candidates and points to `plugin load NAME`. |
| Script approves its own plugin load. | Restricted `plugin load NAME` is denied in script context. |
| Script revokes, unloads, or inventories grants/plugins silently. | `plugin revoke` and `plugin unload` are denied in script context; `plugin grants` is hidden without `cap.plugin-read`. |
| Metadata, entry, or helper bytes change after approval and later evaluation reopens a different file state. | Rev0961 captures a bounded immutable package snapshot, validates metadata/entry against it, and uses it for initial, lifecycle, reload, and package-local lazy source. Restricted reload separately reports live drift. |
| Changed helper is lazy-loaded later by an old plugin callback. | The callback reads the committed snapshot, so disk drift cannot retarget it. Approving a replacement does not change or disable the old generation; explicit reload commits the new snapshot. |
| Revoked grant still leaves registered plugin commands, timers, hooks, bindings, delayed rows, or wordlists executable. | Interactive `plugin revoke` performs host-owned transactional cleanup without running `deinit`, then marks the grant revoked. Cleanup failure leaves runtime and grant unchanged and visible. |
| Failed live plugin callback still needs the broad 40-field runtime snapshot. | Rev0888 passes loaded plugin group/root/generation identity into callback rollback and uses scoped group plus generation snapshots, while preserving cursor, option, execution, and message rollback. Legacy/no-identity callbacks, plugin source loading, lifecycle hooks, and deinit rollback still use the broad fallback. |
| Failed plugin source/lifecycle rollback removes transient words but leaves their word-authority rows behind. | Rev0889 stores editor word provenance in `VmDictionarySnapshot`, restores dictionary topology first, then filters/restores provenance against live words. Failed source, staged lifecycle, deinit, and callback rollback share this invariant. |
| Successful plugin reload/unload leaves old committed wordlists and executable `Word` objects live indefinitely. | Rev0890 records bounded `PluginWordlistTombstone` metadata, removes retired wordlists from live VM lookup/search order, scrubs word authority rows for the retired wid, and marks direct saved XTs so stale invocation fails clearly. |
| Captured keybindings, hooks, or timers from a retired plugin generation continue to run later under ambient authority. | Rev0891 makes generated plugin callbacks pass through `Editor.run_script_origin_callback()` and refuse execution when their captured plugin generation is no longer loaded; hook handlers and timers now share this runner. Legacy rows without generation still lose private package-root authority and fall back to ordinary filesystem capability checks. |
| Restricted manual plugin approval can walk, materialize, retain, or return an unexpectedly large package. | File-count, per-package byte, aggregate retained-snapshot byte, worker-time, and result teardown limits apply before a grant is recorded. Rev0961 also drains large queue results before joining the child. |
| User cannot remove a loaded plugin surface without restarting or must trust plugin cleanup code during authority withdrawal. | `plugin unload` is the graceful lifecycle path. `plugin revoke` is the host-owned no-`deinit` path; both are denied in script context. |
| Plugin unload or reload cleanup partially fails but the manager still reports the plugin as cleanly removed or replaced. | Rev0875 makes unload old-group cleanup and reload old-cleanup/staged-retag commit-critical. Rev0876 restores partially swept group surfaces with a narrow snapshot. Rev0877 also guards generation-scoped delayed-state cleanup and restores both group and generation snapshots when unload/reload-old cleanup fails after partial mutation. Rev0878 exposes retained failed surfaces through `plugin cleanup [NAME]` and `ed.plugin-cleanup-failure-rows`; rev0879 narrows command rollback inside group sweeps to touched command groups; rev0880 applies the same touched-group rule to actions, keybindings, and pending timers; rev0881 applies it to hooks and marks and fixes mutable hook-handler snapshot evidence; rev0950 routes mark rollback through an editor-owned owner register and generated `ed.mark-register` contract row; rev0882 applies touched authority-row rollback to recent files, palette MRU, prompt history, and saved cursors; rev0883 applies touched authority-state rollback to clipboard, active search, and help history; rev0884 applies touched rollback to recovery stacks and delayed interactions and preserves trusted named `qreplace`/`openurl` keymodes during plugin-owned interaction cleanup; rev0947 routes recovery stack rollback through an editor-owned owner register and generated `ed.recovery-register` contract row; rev0885 scopes non-macro generation cleanup rows/registers; rev0886 scopes macro generation cleanup slots/recording; rev0887 can persist failed cleanup-surface receipts as opt-in JSONL behind `cap.persist` and `plugin.cleanup-log.persist`, so `plugin cleanup` can still show diagnostic rows after restart. |
| Plugin clears or changes its runtime group so callbacks survive unload cleanup. | Rev0862 locks loader-owned plugin editor/hook groups during plugin-originated execution and denies group escape attempts. |
| Plugin leaves delayed interaction state behind after unload. | Rev0863 stamps active keymodes/prompts with the plugin group and removes matching keymodes, prompts, query-replace sessions, and pending URL confirmations during plugin cleanup. |
| A stale prompt, query-replace session, or URL confirmation is reinserted after its plugin generation is retired. | Rev0892 rejects the response with a `stale plugin ...` denial, refuses the submit/edit/open effect, and clears the retired interaction object. |
| One delayed `qreplace all` response performs an unexpectedly huge foreground replacement sweep. | Rev0931 adds `qreplace.max` (default `10000`, `0` = explicit unlimited) and stops with the query-replace session active at the next match when the per-response replacement budget is reached. |
| A saved macro slot from a retired plugin generation is reinserted or survives outside ordinary cleanup. | Rev0893 rejects playback with `macro play: stale plugin macro ...`, clears the retired slot, and prunes it before raw macro read/list/detail exposure. |
| Plugin queues unbounded delayed timer callbacks through `ed.after`. | Rev0893 routes `ed.after` through `Editor.schedule_timer_checked()` and refuses new delayed callbacks once `max_pending_timers` is full. Rev0928 also removes canceled timer task rows immediately and compacts stale heap ids so schedule/cancel loops do not retain callback payloads or grow an unbounded raw heap. |
| Allowed hostcall returns an oversized VM-visible result payload. | Rev0898 gives the VM shared `hostcall_result_max_bytes` and `hostcall_result_max_cells` limits. The core `hostcall` word estimates the changed stack suffix after an allowlisted host function returns, restores the argument stack, and raises `hostcall result budget exceeded` when the result is too large. |
| Plugin-callable string construction allocates a much larger result before the post-hostcall budget can run, or repeated aliases make the preflight itself wasteful. | Rev0974 preflights exact concatenate/split/join/replace bytes and cells before allocation, preserves complete requests, removes the join list copy, caches aliases in a fixed table, stops at a proven overrun, and incrementally bounds formatter/core value rendering. Existing inputs, arbitrary native CPU, total heap, crashes, and syscalls remain outside the claim. |
| Allowed regex hostcall receives oversized or malformed caller-controlled inputs before result-budget checks can fire. | Rev0899 gives `re.search`, `re.findall`, `re.sub`, `re.subn`, and `re.escape` preflight byte budgets and argument-shape validation before entering Python's regex engine or replacement compiler. Direct hostcall failures keep caller arguments visible for inspection. |
| Caller-authored regex parsing or matching wedges the editor/VM foreground, including shapes the old heuristic misses or deeply nested patterns that fail during `re.compile()`. | Rev0970 routes every non-literal editor scan and every finite positive-timeout VM regex request through one one-shot `python -I -S` child. The child owns compilation, matching, capture expansion, bounded result construction, and stable parser-recursion classification; startup/request clocks are separate, timeout kills/reaps the child, direct VM operands remain inspectable, and candidate editor search does not replace prior replay state. |
| A caller regex completes before its deadline while CPython native repeat/backtracking state consumes unbounded child memory. | Rev0975 (preserved in rev0976) adds one central 144 MiB post-request headroom default. On Linux the isolated child lowers soft and hard `RLIMIT_AS` after request decode and before compile/match; allocation failure is a stable `memory-limit` operation and a fresh child remains usable. The pure executor cannot alter the host process limit. This does not cover parent serialization, child JSON decode, other platforms, RSS/cgroups, syscalls, or crashes. |
| Structured editor model hostcalls accept runaway dimensions before row-builder traversal. | Rev0901 gives screen/docs/help/prompt model hostcalls VM-tunable line, column, width, and screen-area preflight budgets. Oversized calls fail before builders walk host-owned state and preserve direct operands. |
| Public CLI/REPL screen dumps accept runaway geometry or ambiguous JSON that consumes work or yields different downstream interpretations. | Rev0964 applies shared line/column/cell preflight before startup or model traversal and ships a strict bounded consumer that rejects duplicate names, non-standard/floating numbers, excessive bytes/depth, surrogates, unknown fields, and invalid row/cursor/cue relationships. |
| A destructive primary or secondary selection exists in editor state but is visually absent, or prompt cursor placement is recomputed from unrelated edit-window scroll state. | Rev0967 projects at most 4096 cursor sources and a 4096-character syntax prefix per visible logical line into shared viewport facts, emits compatible `syntax-*` / `selection-*` compact cues, paints selected logical newlines, and places the terminal cursor from the already-composed screen cursor. Character coordinates remain distinct from terminal-cell fidelity. |
| Script-visible `ed.fs-read` loads oversized file bytes before the shared result budget can run. | Rev0902 gives `ed.fs-read` a VM-tunable pre-read byte budget. The target is opened and checked for kind, size, and containment before byte loading, then checked again at the final fd-bound read seam so late growth or swaps still fail closed. |
| Script-visible docs/help/prompt/palette query hostcalls accept arbitrarily large query strings before broad scans. | Rev0903 adds a VM-tunable `editor_hostcall_query_max_bytes` preflight for free-text query hostcalls. Oversized queries fail before scan builders or prompt-opening side effects and preserve the caller operand. |
| Script-visible picker/list hostcalls can scan unbounded host rows before result budgets fire. | Rev0904 adds VM-tunable scan/row budgets for broad editor row builders, `ed.fs-list`, and path completion before materializing large candidate lists. |
| Capability-approved `ed.open-url` enters a text-mode browser controller that waits after plugin fuel has dispatched the hostcall. | Rev0977 moves the standard-library controller to one `python -I -S` child with a six-second deadline, 16 KiB diagnostics, process-group teardown where supported, and a real hostcall liveness test. URL validation/capability remain separate. Popen construction now shares the six-second lease through the rev0982 single-pending owner; a permanently blocked constructor, starter creation, Windows Job Objects, browser sandboxing, syscalls, total memory, and native crashes remain outside the claim. |
| A bounded argv/shell leader exits zero while a descendant retains Micromax capture pipes, or a one-shot worker blocks during start or behind an incomplete result frame. | Rev0978 follows exact Linux pipe ownership after one bounded drain. Rev0979 replaces affected Queue/Pipe terminal results with one private framed socket read under an absolute deadline and byte ceiling. Rev0980 prefers spawn after observing native forkserver threads. Rev0981 defers multiprocessing Process construction/start to one deadline-owned starter, caps unresolved starts at one, transfers late cleanup, and proves post-stall recovery. Rev0982 gives synchronous Popen construction the parallel one-pending late-cleanup owner and shares its deadline with execution/readiness. Other POSIX hosts use capture-group fallback; permanent late-starter reclamation, starter creation, cleanup liveness, Windows Job Objects, child serialization memory, and hostile-worker pickle remain outside the claim. |
| Exact dirty tracking hashes a large logical document after every mutation, making the trust mechanism itself a typing-latency cliff. | Rev0979 installs visible reversible buffer-local `fastdirty=true` at a 1 MiB saved baseline, keeps smaller buffers exact, and encodes large exact signatures in bounded chunks after native joining. Sticky-until-save semantics are explicit; other whole-buffer costs and total-memory limits remain open. |
| Unchanged search repaint/status or softwrap movement repeatedly scans the complete document, and dense match/edit or true-wordwrap geometry retains one Python object per coordinate. | Rev0980 reuses one exact search snapshot and compact visual-row prefix index. Rev0982 adds bounded sparse true-wordwrap checkpoints and a four-line exact LRU, packed line/span arrays, compact replacement edits, and reused simultaneous-edit line indexes. Cold first scans, source/replacement/undo text, explicit compatibility projections, RSS/native memory, and public mutable `Buffer.lines` remain residuals; unknown mutation forces rebuild. |
| Script-visible filesystem observation can block after capability and containment preflight. | Rev0910 runs `ed.fs-stat` through a VM-tunable timeout worker, rev0911 runs `ed.fs-list` through the same worker pattern, rev0912 runs `ed.fs-read` size/kind preflight plus fd-bound byte loading through a VM-tunable timeout worker, rev0913 routes editor open/revert/source/user-init reads plus prompt/palette path completion through bounded filesystem seams while preserving containment, row/byte/source budgets, and normal failure behavior, rev0914 runs atomic editor/persistence writes through a VM-tunable killable worker with best-effort worker-temp cleanup, and rev0915 bounds save-time directory-kind checks, freshness/hash capture, and mkparents parent creation. Direct/non-atomic writes and hot status disk-state probes are still not killable. |
| An explicit save fails or the process restarts, leaving the only edited text in memory; recovery may overwrite a changed target, retire before permission completion, or delete a live process's private temp. | Rev0960 checkpoints exact editor text before commit, opens recovery as a dirty review buffer with disk unchanged, requires explicit force/save-as after conflict, and uses bounded startup/inventory work. Rev0962 adds real process-death evidence, private-from-birth document temps, and separate file/directory sync witnesses. Rev0963 pins exact final-mode and parent authority before checkpoint publication; retains matching-byte records until explicit fd-bound mode/file/directory completion; and makes payload-blind private-temp cleanup explicit, bounded, lease-bound, PID-namespace-aware, process-instance-verified, and fail closed. Sudden-power-loss, hostile-peer, cross-namespace cleanup, and unpublished-document-temp correlation remain outside the claim. |
| Executable source loads can read or evaluate oversized files one at a time. | Rev0905 adds VM-tunable per-file source-load byte and nested eval-step budgets for `ed.require` and script-context core `include` / `require` / `reload`. |
| A tiny approved source file can recursively include many individually small files. | Rev0906 adds VM-tunable source-load graph depth and cumulative-byte budgets shared by direct `ed.require` and nested script-context core loader words. |
| Plugin leaves a saved macro that later replays after unload. | Rev0864 treats saved macros as delayed executable state: unload removes macro slots owned by the plugin generation, and failed plugin lifecycle transactions restore the prior macro registry. Rev0886 narrows generation-cleanup rollback to plugin-owned saved slots/`last` only when owned, without rewinding unrelated trusted/user macro slots. Rev0893 adds a stale-generation guard for reinserted saved macro slots. |
| Plugin reload cannot replace its own same-named macro without losing the old macro on failure. | Rev0864 temporarily prunes old-generation macros under a transaction snapshot so staged reload can replace them and failed staged reload restores them. Rev0886 restores only selected generation-owned macro slots and any generation-owned active recording when generation cleanup later fails. |
| Plugin leaves saved-selection or jumplist recovery rows behind after unload. | Rev0865 removes selection-stack and jumplist rows owned by the unloaded plugin group/generation. |
| Plugin reload recreates the same jumplist snapshot but deduplication suppresses the new row before old cleanup. | Rev0865 prunes old-generation recovery rows under the transaction snapshot before staged evaluation, then retags staged rows or restores old rows on failure. |
| Plugin leaves an active search query that later drives find-next/find-prev after unload. | Rev0866 removes active-search registers owned by the unloaded plugin group/generation and restores them on failed staged reload. |
| Plugin reload should replace or drop its old active search without leaving stale query state. | Rev0866 prunes old-generation active search under the transaction snapshot, retags staged search on success, and restores old search on failure. |
| Plugin leaves command/find prompt-history text that can be replayed after unload. | Rev0867 removes prompt-history rows owned by the unloaded plugin group/generation and restores them on failed staged reload. |
| Plugin-authored command history was persisted before unload. | Rev0867 best-effort saves prompt-history pruning when history persistence is enabled, so stale plugin command text is not reintroduced from the configured history file. |
| Plugin leaves recent-file MRU or savecursor navigation rows after unload. | Rev0868 removes recent-file and savecursor rows owned by the unloaded plugin group/generation and restores them on failed staged reload. Rev0943 routes recent-file rollback through editor-owned owner methods and a generated `ed.recent-files-register` row; rev0944 routes saved-cursor rollback through editor-owned owner methods and a generated `ed.saved-cursor-register` row. |
| Plugin-authored file-navigation rows were persisted before unload. | Rev0868 best-effort saves recent-file/savecursor pruning when those persistence stores are enabled, so stale plugin navigation rows are not immediately reloaded from disk. |
| Plugin leaves command-palette MRU rows that keep stale command/action choices near the top of later palette prompts. | Rev0869 removes palette MRU rows owned by the unloaded plugin group/generation and restores them on failed staged reload. Rev0945 routes palette-recent rollback through editor-owned owner methods and a generated `ed.palette-recent-register` row. |
| Plugin leaves internal clipboard contents that later feed paste or clipboard export after unload. | Rev0870 removes clipboard state owned by the unloaded plugin group/generation and restores it on failed staged reload. |
| Plugin leaves helpback/helpforward/helpresume navigation rows after unload or reload. | Rev0871 removes help-history rows owned by the unloaded plugin group/generation, retags staged replacement rows, and restores old rows on failed staged reload. |
| Plugin reload pre-prunes old help-session rows while the old help buffer is still visible, accidentally turning the old plugin target into trusted history. | Rev0871 falls back to active help-buffer authority when session rows were intentionally pruned, so staged reload cannot launder old plugin-opened docs targets into ambient trusted help history. |
| Failed plugin source, reload, deinit, or callback leaves ordinary option changes behind even though the plugin transaction rolled back. | Rev0872 snapshots global and buffer-local option state in plugin runtime transactions and restores it on failure or discarded deinit mutations; rev0874 binds new buffer-local snapshots to live buffer identity rather than mutable names; rev0949 routes broad failed source/lifecycle restore and scoped callback option rollback through public editor-owned option methods and a generated `ed.option-state-register` row. |
| Failed runtime-group cleanup report is visible but has no consequence for commit paths. | Rev0875 uses reports as policy for unload/reload commit sweeps, while still preserving the primary plugin error when cleanup evidence is collected during an already-failing source/lifecycle path. |
| Broad “plugin transaction” wording implies that all effects are atomic. | Rev0873 documents the missing effect-lifecycle contract: arbitrary document edits, new buffers, file opens, durable writes, external I/O, and process effects are not covered by the current state snapshot unless a narrower contract explicitly says so. |
| Runtime group cleanup or retag partially fails but looks clean. | Rev0874 returns structured cleanup/retag operation reports and retains bounded plugin-manager evidence, while preserving best-effort sweeping. |
| Generation-scoped delayed-state cleanup fails after group cleanup has already removed registrations. | Rev0877 reports generation-cleanup failures, restores delayed-state surfaces from `RuntimeGenerationStateSnapshot`, and restores group state too in unload/reload-old cleanup commit guards. Rev0885 makes non-macro generation rows/registers root/generation scoped; rev0886 makes macro generation rollback root/generation scoped too. |
| User cannot inspect which cleanup surface failed after unload/reload aborts. | Rev0878 adds `plugin cleanup [NAME]`, `ed.plugin-cleanup-failure-rows`, prompt-completion visibility, and audit checks for retained cleanup/retag/generation failure rows. Rev0879 points failed unload/reload feedback to `plugin cleanup NAME` when retained rows exist; rev0880 keeps those diagnostics while narrowing more registry rollback state; rev0881 keeps them while narrowing hooks and marks; rev0882 keeps them while narrowing delayed recent/palette/prompt/saved-cursor rows; rev0883 keeps them while narrowing clipboard/search/help-history state; rev0884 keeps them while narrowing recovery/interaction state; rev0885 keeps them while narrowing non-macro generation rows; rev0886 keeps them while narrowing macro generation state; rev0887 can persist them across restart when cleanup-log persistence is explicitly enabled. |
| Broken plugin reload leaks staged registrations. | Plugin reload uses staged groups, snapshots, rollback, and cleanup. |
| Plugin source/lifecycle/callback code resolves an undeclared sibling or inherits a trusted ambient search order. | Rev0972 installs one exact search order of self, declared dependency closure, and Forth for every plugin execution path. |
| A plugin switches into a dependency wordlist or rebinds a visible dependency deferred word. | Rev0972 permits writes only to the executing plugin dictionary, enforces definitions at `VM._add_word()`, and requires owner write authority for `is` / `defer!`. |
| A plugin probes or calls exact renderer/status/prompt/screen models that should remain host implementation details. | Rev0972 hides internal models from plugin feature probes and denies exact plugin calls before consuming stack evidence, while preserving trusted host access. |
| Plugin reads source outside its package through relative include/require. | Plugin execution context grants only package-local loads unless separate script filesystem capability is present. |
| Script reads/writes arbitrary files through editor hostcalls. | Capability roots and explicit `cap.fs-*` options gate script file operations. |

## Residual risks

- Everything still runs inside one Python process.
- A loaded plugin can consume memory, block, exploit Python/native bugs, or abuse
  any stable or experimental hostcall it is allowed to reach; rev0972 removes ambient sibling namespaces and exact host-owned models, while rev0898 bounds the VM-visible result payload after an allowed hostcall returns, and rev0970 contains every positive-timeout VM/direct-editor caller regex compile and execution in a one-shot child, and rev0975 gives that Linux child finite post-request address-space headroom, and rev0901 preflights structured model dimensions before row-builder traversal, and rev0902 preflights `ed.fs-read` byte size before file-byte loading, and rev0912 moves the accepted `ed.fs-read` preflight/final read into a timeout worker, and rev0913 applies the same reference-host timeout pattern to editor open/revert/source/user-init reads and prompt/palette completion, rev0914 applies it to atomic write commits with temp cleanup, and rev0915 applies it to save preflight freshness/hash and mkparents parent creation, but this is not a general CPU, temporary-allocation, direct-write, hot status-probe, or side-effect rollback guarantee.
- Step budgets do not bound all wall-clock time, memory, subprocesses, terminal
  behavior, or native library behavior.
- Immutable package snapshots, package capture/retention budgets, grant checks, runtime-group locks, delayed-interaction cleanup, saved-macro cleanup/refusal, recovery-stack cleanup, active-search cleanup, prompt-history cleanup, file-navigation cleanup, saved-cursor owner rollback, palette-recent owner rollback, clipboard cleanup, help-history cleanup, option-state owner rollback, mark owner rollback, generation cleanup guards, touched command/action/keymap/timer/hook/mark/delayed-row/singleton-help/recovery/interaction/macro cleanup restore, retired-wordlist tombstones, retired deferred-callback guards, retired interaction guards, timer pending-work budgets, `ed.fs-read` preflight byte budgets and timeout workers, editor open/source-resolution/source/user-init-read timeout workers, prompt/palette path-completion scan/time budgets, atomic write timeout workers, save freshness/mkparents timeout workers, query-replace all replacement budgets, structured model dimension budgets, regex timeout workers, regex hostcall input budgets, VM hostcall result budgets, scoped live-callback rollback, and option rollback are stale-grant,
  stale-callback, and cleanup-consistency checks, not signed provenance or atomic
  filesystem attestation.
- Recoverable startup guarantees a live editor model, not that the requested path
  or help target opened. Headless callers must honor the typed result or process
  status rather than treating fallback JSON as success.
- State-bound discard confirmation relies on supported mutation paths updating
  `Buffer.version`; direct internal mutation is outside the extension contract.
- Buffer labels remain name-keyed rather than immutable-ID references. Add a
  stable ID layer only when persisted marks/recovery, rename, multi-view, or
  extension handles justify the migration.
- Query-replace witnesses exact live object and supported content generation; raw private-storage mutation can bypass both application policy and the counter.
  Unsupported out-of-band mutation during a live session can invalidate match
  coordinates or become part of the grouped edit; add version isolation only for
  a demonstrated supported mutation path.
- The single-source lane proves internal consistency and same-declared-builder
  wheel/archive equality. It does not prove cryptographic authorship, release
  signing, hostile-writer atomic capture, hermetic dependencies, hosted CI
  execution, universal cross-platform reproducibility, or a complete suite.
- Script-owned buffer creation remains unavailable until a finite retained-state
  and lifecycle contract exists; do not turn `new` into an ambient hostcall.
- A hostile local process can still mutate a multi-file package during capture; the resulting grant binds exactly the captured mixture, but capture is not an atomic directory snapshot.
- There is no durable per-plugin permission store, signed plugin identity,
  separate extension host, Wasm boundary, or seccomp/container policy.
- There is no polished per-plugin capability grant UI. Plugin-created bindings
  therefore remain capability-scoped even when the user presses them; a gesture
  does not temporarily elevate the callback.
- The full trusted default keymap is a product-startup choice. A bare embed keeps
  only internal modal bindings and must explicitly install the product defaults
  if it wants the same interactive open/save/undo behavior.
- The extension contract now has a small stable slice, experimental-by-default
  hostcalls, exact declared imports, and internal presentation models. It is still
  not broad third-party compatibility, a complete plugin owner graph, or a
  process/component ABI.
- Mutable lists, maps, cells, and other values deliberately returned by a
  dependency are object capabilities; there is no recursive object membrane.
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
- Keep host/user defaults usable without turning arbitrary plugin bindings or
  script-created modes into trusted code.
- Treat physical input as an event, not a capability transfer.
- Prefer immutable approved bytes, explicit pending replacement, transactional host-owned revoke, scoped failed-callback rollback, denied plugin group change, or removed plugin-owned delayed interaction/macro/recovery/search/history/file-navigation/palette/clipboard/help state over executing or retaining surfaces the user did not approve or still authorize.
- Keep restricted mode about automatic code loading and explicit manual approval;
  do not claim it contains malicious code.
- Do not add a universal untyped registry where one typed effect adapter, resource handle, or journal record would suffice.
- Runtime behavior, command messages, prompt completion, generated effect-contract rows, docs, and revision index
  must agree on each boundary.

Rev0972 note: restricted plugin generations still bind approval to exact captured bytes; executable plugin imports/writes and internal models are now constrained too. These remain in-process application policies, with no hostile-code sandbox, recursive object membrane, or atomic multi-file capture claim.
