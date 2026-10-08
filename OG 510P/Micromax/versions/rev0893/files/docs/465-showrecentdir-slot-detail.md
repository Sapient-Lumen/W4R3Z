# showrecentdir slot detail

Rev523 tightens one small trust/flow/headless-first seam in the recent-file loop: exact recent-directory inspection no longer forces callers to translate a visible recent-file slot back into a parent directory path first.

## Why

By rev522, Micromax already had a coherent visible recent-slot dialect for exact recent-file inspection and reopen paths:

- `recent` showed MRU files as numbered slots
- `showrecent N|#N` let humans inspect one recent file by visible slot
- `recent-slot-detail` / `ed.recent-slot-detail-row` let scripts inspect that same exact row headlessly
- picker rows and feedback already printed the chosen recent file as `#N`

But the adjacent exact recent-directory surface still made one extra translation step visible:

- `showrecentdir DIR` could inspect one parent-directory bucket exactly
- `recent-dir-detail` / `ed.recent-dir-detail-row` could do the same for scripts
- yet callers who started from the visible file slot still had to resolve `#N -> path -> parent dir` themselves before asking the next obvious question: what does that file's recent-directory bucket look like?

That mismatch was small, but it made one honest row dialect less useful exactly where humans and future LLMs naturally branch from "this recent file" to "its surrounding directory bucket".

## What changed

Rev523 keeps the fix deliberately small and aligned with the existing recent-slot work:

- `showrecentdir DIR|N|#N` now accepts a visible recent-file slot as well as a raw directory label
- new hostcall `ed.recent-slot-dir-detail-row ( n|"#n" -- row|0 )` exposes that same exact recent-directory bucket headlessly
- new convenience word `recent-slot-dir-detail ( n|"#n" -- row|0 )` mirrors the hostcall inside Micromax scripts
- command-bar completion for `showrecentdir` now offers `#N` rows when the typed prefix starts with `#`, reusing the existing exact recent-directory row metadata instead of leaving the slot form blind

The row shape itself stays unchanged:

- `[query directory count active_count open_count dirty_count readonly_count sample_path sample_detail sample_menu sample_info]`

Only the addressing surface grows: callers can now reach the same exact directory bucket by visible recent-file slot when that is the most natural handle they already have.

## Trust and flow effect

This is intentionally a small follow-up, but it removes one needless mental hop:

- visible recent rows already say `#N`
- exact recent-file inspection already understands `#N`
- exact recent-directory inspection now understands the same token too

So the archive keeps one consistent story: if Micromax already shows a recent file as `#N`, the next adjacent exact inspection surface should understand that same visible handle instead of asking callers to reverse-engineer a directory label first.
