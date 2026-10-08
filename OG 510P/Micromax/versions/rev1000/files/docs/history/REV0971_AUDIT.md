# Revision 0971 audit

## Priority judgment

Rev0970 named the repeated buffer/recent/project navigation loop as the next product risk. The first reproduction showed four failures in one daily path: project browsing discarded the editor's working set, buffer/recent browsing selected the active file and made Enter a no-op, a failed Enter destroyed the user's picker state, and a selected recent row could outlive the recent register that originally authorized it. These were flow and trust defects, not a missing search framework.

## Severe or wasteful findings

| Finding | Consequence | Correction |
|---|---|---|
| Empty project picker prioritized unrelated alphabetic root files | A common two-file loop repeatedly required typing or row movement | Bounded open/recent project context precedes ordinary project groups |
| Empty buffer/recent pickers selected the active file | Enter appeared to work but produced no navigation | Prefer the MRU other destination and avoid the active target when another visible row exists |
| Active and previous project files were both generic `open` | The useful alternate was visually ambiguous | Explicit `active` and `previous` cues, including dirty combinations |
| Failed buffer/file/recent acceptance closed the prompt | Query, selected row, and bounded filesystem evidence were lost precisely when correction was needed | Restore the exact prompt object and keymode on failure unless another prompt replaced it |
| A recent picker trusted its captured selected string after the recent register changed | Stale presentation could bypass the current visible-recent membership check | Revalidate selected rows against `visible_recent_files()` at submit |
| Project open truth was rebuilt on every keypress | Repeated authority checks and path resolution over an unchanged inventory | Capture plain context/status metadata once |
| Context construction canonicalized each snapshot member in the earlier draft | A bounded scan could still be followed by thousands of foreground filesystem resolutions | Validate inventory strings in memory; map only candidate buffer/recent paths lexically; intersect exactly |
| Recent return-target planning read the authority-filtered register once per path | Opening one recent picker repeated normalization and authority checks over the same register | Capture one visible register view and map preferred/active paths together |
| The extracted planner rebuilt the same inventory set for context and status filtering | Every query keystroke paid redundant full-snapshot passes | Normalize the inventory once and route both projections through that set |
| Row logic lived inside the 32k-line coordinator | Ordering, dedupe, labels, and query behavior were difficult to test independently | Small pure `project_picker.py` planner |
| Living docs still claimed editor regex ran synchronously and navigation capture was pending | Handoffs could send work back toward already-fixed risks | Correct current entrypoints and generated effect-contract evidence |
| `mxcontext` recognized only the historical words `Latest tiny landing` | Renaming the current handoff to honestly say `substantive` made release currentness fail even when all revision numbers agreed | Accept the two explicit historical/current labels while retaining strict revision and orphan checks |
| Recent revision metadata expanded the compact handoff to 68 docs and 65 code paths | The datacube violated its own 64-item budget and `mxcontext --check` failed at release time | Move the oldest evidence triplets to the history lane and list only actually touched rev0971 code |

## Trust review

The project scan remains the sole membership grant. Context cannot add a path. Submission still resolves under the captured root, refuses absolute and dot-dot paths, requires exact containment and no post-scan symlink traversal, observes a regular file through the bounded stat boundary, and opens only with the delayed prompt authority.

Project context calls `_buffer_read_allowed()` for buffers and `visible_recent_files()` for recent entries. In script context, the ambient active buffer follows existing policy while unrelated user buffers and recent rows remain hidden absent capability or matching provenance. Lexical path comparison is presentation-only: exact snapshot membership must still succeed, and submit performs the filesystem checks.

Retry restoration does not broaden authority. The same prompt object, captured origin, inventory, and metadata are retained. A later retry reruns the normal submit checks. If the failed submission intentionally installs a replacement prompt, that replacement wins and the old picker is not resurrected.

## Waste removed

- no per-keystroke iteration over all buffers for the project picker;
- no per-keystroke path expansion/resolution/relative conversion for project rows;
- no canonicalization of every member after the bounded scanner has already produced relative inventory;
- no duplicate recent-register read or duplicate project-inventory normalization on one refresh;
- no repeated typing merely to return to the previous file;
- no discarded query/snapshot followed by a redundant project rescan after a stale target;
- no duplicate context and ordinary rows;
- no new picker, keybinding, option, watcher, persistent cache, navigation registry, schema, or background service;
- no unbounded accumulation of old revision evidence in the generated handoff; history remains catalogued without being inlined;
- no release dependence on one adjective in the TODO handoff while revision-number mismatch and orphan detection remain strict;
- no new structural-audit registry entry where focused behavioral tests already prove the contract.

## Remaining risk

Project decorations are deliberately stale until that prompt is reopened. Buffer and recent pickers remain live views rather than immutable inventories. A failed stale row stays visible until the user edits, moves, or reopens the picker; pressing Enter again honestly repeats the failure. Promoted project context is capped at 12, while status metadata can still reflect the finite open-buffer set. Path identity is lexical/nominal rather than inode or hard-link identity. No complete repository-suite claim is made.
