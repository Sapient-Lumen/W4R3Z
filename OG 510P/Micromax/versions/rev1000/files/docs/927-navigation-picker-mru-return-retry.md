# Rev0971 — navigation picker MRU return, captured project context, and retryable failure

## Outcome

Micromax's navigation pickers now treat an empty query as a request to *return somewhere useful*, not as a request to accept the first alphabetic row or reopen the active target.

- The buffer picker selects the most-recent other readable buffer when it is visible.
- The recent-file and recent-directory pickers select the previous open file's visible recent entry and avoid the active file when another candidate exists.
- The bounded project picker places a captured `Open and recent` section first, with the previous open project file Enter-ready.
- A failed Enter keeps the same picker open, preserving its query, selected row, project inventory, metadata, script origin, and prompt mode.
- A selected recent row is accepted only while it is still present in the authority-filtered recent register.

The common two-file project loop is now:

```text
edit second.py
Ctrl-O
Enter            -> first.py
Ctrl-O
Enter            -> second.py
```

No project index, watcher, database, results pane, background job, new option, persistent navigation registry, or additional keybinding was added.

## The recurring failures

### 1. Project inventory erased working-set context

Before rev0971, an empty project picker sorted root files first and then top-level directories. With `src/model.py` active and `src/view.py` previously used, the selected row could be an unrelated `pyproject.toml`. The active file was buried under `src` and merely labeled `open`; the previous file had no special position or cue. Reopening the picker repeated the same friction.

The problem was not weak fuzzy search. The finite scanner had already done the expensive and security-sensitive work, but presentation discarded the editor's own MRU and recent knowledge.

### 2. Buffer and recent pickers defaulted to a no-op

The buffer and recent row providers already exposed useful alternatives, but prompt refresh always reset selection to row zero. In common MRU order, row zero was the active file. Opening the picker and pressing Enter therefore appeared successful while changing nothing.

Reordering every provider would have mixed query ranking, grouping, and navigation policy. Rev0971 instead adds one small prompt-layer initial-selection rule: try caller-supplied preferred candidates, otherwise choose the first non-avoided visible candidate, and fall back to row zero only when every row is honestly unavoidable.

### 3. Failed acceptance destroyed useful state

`submit_prompt()` detached a prompt before executing its target, which is correct on success: the old picker must not remain above the newly selected buffer. The same lifecycle also ran on failure. A disappeared project file, closed buffer, removed recent entry, or delayed script denial discarded the query and selected row. Retrying another row required reopening—and for project files, rescanning—the same scope.

Rev0971 extracts the navigation submit bodies and applies one narrow completion rule. Success leaves the prompt closed. Failure restores the exact prompt object only when no submission path deliberately installed a replacement prompt. The user can edit the query, move to another row, or retry; all ordinary validation runs again.

### 4. A stale recent selection outlived its grant

Recent rows are a presentation of `visible_recent_files()`, which is filtered by current authority and provenance. The old selected-row path could be submitted after that register changed because selection resolution trusted the captured suggestion string. Rev0971 requires the selected string to remain an exact member of the current visible register. There is still no raw-path fallback in recent pickers.

## Product judgment

The mission is a calm editor, not a maximal file browser. Movement among the last few files is a daily loop and deserves less friction than first-time project exploration. Failure should preserve recoverable user work rather than erase it. The smallest useful correction is therefore:

1. keep one finite project membership snapshot;
2. capture a small authorized working-set projection for empty browsing;
3. leave typed fuzzy search over the complete snapshot;
4. select a useful other target in existing buffer/recent rows without rewriting their rankers; and
5. retain picker state when acceptance fails.

Official editor documentation supports the separation between broad inventory and recent/open navigation:

- GNU Emacs documents an empty buffer-switch request as choosing the most recently selected buffer other than the current one: <https://www.gnu.org/software/emacs/manual/html_node/emacs/Select-Buffer.html>.
- Visual Studio Code documents repeated Quick Open as a way to cycle recently opened files, and separately documents `Ctrl-Tab` over open editors: <https://code.visualstudio.com/docs/editing/tips-and-tricks> and <https://code.visualstudio.com/docs/editing/editingevolved>.
- Zed's Tab Switcher is sorted by recent usage and explicitly aims to return to prior work: <https://zed.dev/docs/tab-switcher> and <https://zed.dev/docs/finding-navigating>.
- Helix exposes a last-accessed/alternate-file motion plus distinct file, buffer, jumplist, and changed-file pickers: <https://docs.helix-editor.com/keymap.html>.
- Python distinguishes lexical path manipulation such as `abspath`, `normpath`, and `commonpath` from filesystem-observing existence and resolution operations: <https://docs.python.org/3/library/os.path.html> and <https://docs.python.org/3/library/pathlib.html>.

The failed-acceptance lifecycle also has direct current precedent:

- VS Code's `QuickInput` API says an acceptance gesture does not automatically hide the UI; the owner decides whether the input is acceptable and whether to call `hide()`. Its input validation contract separately says an `Error` prevents acceptance: <https://code.visualstudio.com/api/references/vscode-api#QuickInput> and <https://code.visualstudio.com/api/references/vscode-api#InputBoxValidationSeverity>.
- The WAI-ARIA Authoring Practices listbox pattern keeps focus on the selected option when a listbox regains focus and defines arrow/type-ahead movement over that explicit focused row: <https://www.w3.org/WAI/ARIA/apg/patterns/listbox/>.
- Helix assigns `Enter` to opening the selected picker row and `Escape`/`Ctrl-C` to closing the picker; it even provides `Alt-Enter` for opening without closing. Acceptance, background action, and dismissal are distinct gestures: <https://docs.helix-editor.com/keymap.html#picker>.

Micromax borrows the interaction distinction, not another editor's architecture. Research was checked on 2026-07-18.

## Architecture

### One project membership authority

`project_files.py` still produces one bounded, symlink-averse, immutable relative-path inventory. MRU and recent state may only reorder or decorate exact members of that inventory. A buffer or recent path outside the snapshot cannot enter suggestions and cannot be submitted.

### One captured project context generation

When the file prompt opens, `Editor._project_file_picker_context()`:

1. validates the scanner's relative inventory strings into an in-memory membership set;
2. reads only buffers permitted by current runtime authority;
3. maps those buffer paths lexically to project-relative candidates without resolving every inventory member;
4. marks the active snapshot member without promoting it;
5. places the most-recent readable other open member first;
6. appends other readable open members in MRU order;
7. fills remaining slots from authority-filtered recent files;
8. caps promoted context at 12 paths; and
9. stores plain lists/dictionaries in `Prompt.picker_meta`.

The lexical mapping uses normalized absolute path strings only to propose a relative name. Exact inventory intersection is mandatory, and the later open performs real containment, symlink, kind, and existence checks. This avoids turning presentation into a second filesystem scan.

Prompt lifecycle snapshots deep-copy the metadata. Later project-query keystrokes filter the captured generation and do not rescan buffers, recent state, or filesystem paths.

### Pure project row planning

`project_picker.py` owns deterministic presentation:

- one normalization pass over the captured inventory per refresh;
- exact context membership normalization and capping through that set;
- snapshot-member-only status normalization through that set;
- empty-query context-first ordering;
- historical project-root/top-directory ordering for the remainder;
- complete-inventory fuzzy ranking for non-empty queries;
- duplicate elimination; and
- shared section labels for status, section jumps, and TUI headers.

`Editor` remains the authority-aware coordinator. The extracted module is a pure plan, not a second owner framework.

### Shared initial selection, not shared ranking

`prompt_refresh.prompt_suggestion_index()` receives the provider's already-built candidate list plus optional preferred and avoided candidate strings. It never changes row order or match inclusion.

For an empty buffer prompt, the preferred candidate is `previous_buffer_name()` and the active name is avoided. For recent pickers, the previous and active buffer paths are mapped to their visible recent spellings. For a project prompt, `previous` and `active` are read from captured status metadata. Once the query is non-empty, each provider's existing ranker owns row zero again.

### Retryable navigation submission

`submit_prompt()` still detaches the prompt before execution. Buffer submission is extracted to `_submit_buffer_prompt()`, and buffer/file/recent/recentdir results pass through `_finish_navigation_picker_submit()`.

- On success, nothing is restored.
- On failure with no replacement prompt, the exact original prompt is restored and prompt keymode is pushed once.
- On failure after another prompt was deliberately installed, the replacement remains authoritative.
- Captured script origin and project metadata remain attached to the same prompt object.

A retry is not a continuation grant. It calls the normal switch/open path again and must pass current membership, authority, existence, type, containment, and symlink checks.

## Audit and waste removed

The former project row path rebuilt open/modified truth on every refresh. Each keypress iterated buffers, checked authority, expanded paths, resolved paths, and recomputed relative names before ranking the same immutable file list. An early rev0971 draft improved capture but still canonicalized every inventory member after the scanner. A 4,099-member regression now replaces the old normalization hook with a failure and proves context construction only handles the few candidate paths. A separate regression proves preferred/avoided recent-target planning reads the authority-filtered recent register once.

The failure lifecycle audit found that the same detach-on-submit pattern lost state across four navigation prompts. One helper now owns the success/failure distinction rather than four slightly different repairs.

The audit also proves:

- the active project path is never duplicated in the promoted section;
- duplicate buffer names, path aliases, or recent paths cannot duplicate a project row;
- malformed and out-of-snapshot context/status metadata is ignored;
- script code without buffer/recent read authority cannot infer a user's previous buffer through the project picker;
- typed project queries rank the complete captured inventory with the historical shared row metadata, while context cannot admit an out-of-snapshot path;
- section headers, section jumps, headless status, and TUI display consume the same labeler;
- recent selection is revalidated against current visible membership;
- failed project acceptance retains the exact snapshot and performs no second scan;
- failed script acceptance retains its original script identity rather than borrowing interactive authority;
- prompt keymode is restored once, not stacked repeatedly; and
- submit-time project containment, regular-file, disappearance, and symlink-swap checks remain unchanged.

## Visible examples

An empty project query can render:

```text
Open and recent
> first.py       previous
  notes.md       modified
  closed.md      recent

Project root
  pyproject.toml file

src
  second.py      active
```

A typed query removes the special grouping and ranks matching snapshot members under `Matches`. The shared ranker still considers path, kind, status, and parent metadata as it did before extraction; regardless of which field matches, every result must remain an exact snapshot member.

An empty recent picker may retain its existing project-grouped row order while selecting row 2, the previous file, rather than row 1, the active file. Status and TUI position summaries therefore report the selected row honestly instead of pretending that selection and row order are the same concept.

After a stale project file is selected:

```text
filepick: file disappeared since scan: stale.txt
```

The picker remains open with `stale.txt` in the query and the original inventory intact. Selecting `survivor.txt` can succeed without another scan.

## Boundaries and remaining risks

- Project context is intentionally stale for the lifetime of one prompt. Reopen it to capture newer MRU, dirty, recent, or authority state.
- Buffer and recent pickers are live provider views, not immutable project-style inventories.
- Promotion is capped at 12. A very large open-buffer set still belongs in the dedicated buffer picker or a typed project query.
- A failed stale row remains visible until the user edits, moves, or reopens. Repeated Enter repeats the same honest error.
- Lexical path identity is not inode, hard-link, mount, or universal case identity. It is only a candidate mapping before exact inventory intersection and submit-time filesystem validation.
- The project scan remains eager and finite rather than indexed. Large-workspace latency should be measured before introducing caches, watchers, or background indexing.
- This revision does not merge recent-file and buffer registries or create a universal navigation history.

## Highest-value next work

The recurring navigation defect is closed. The next risky architecture item is the extension boundary: identify actual plugin consumers, classify imports/hostcalls/lifecycle models as stable or internal, and delete or narrow accidental surface before process or WebAssembly isolation. Do not turn that work into a label registry; require at least one real surface reduction and preserved plugin journeys.
