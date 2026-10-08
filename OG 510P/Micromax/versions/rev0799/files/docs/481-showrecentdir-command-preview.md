# Rev539 - showrecentdir command preview

Rev539 tightens one remaining recent-inspection seam in the command bar: plain `showrecentdir` used to keep the ordinary exact-command doc row, but it did not preview any actual recent-directory truth before Enter.

That gap was small but real. Micromax already knew the newest visible recent slot, already let `showrecentdir DIR|N|#N` inspect one exact bucket side-effect-free, and already reused that exact row when you typed a matching directory or `#N` token. The blind spot was only the command's own no-arg entry point.

The new `_prompt_showrecentdir_command_row(...)` keeps the fix local and headless-first by reusing `recent_dir_detail_row_by_index(1)`. When a recent bucket exists, the row now previews the newest visible bucket, its file count/open-state flags, and the same tiny sample-row truth the exact inspector already trusts. When no recent files exist, the row now says `no recent directories · expects DIR|N|#N`.

This is intentionally small. It does not change command execution, bucket grouping, or host boundaries. It only makes the last pre-submit row for the exact recent-directory inspector tell the same truth Micromax already knows.
