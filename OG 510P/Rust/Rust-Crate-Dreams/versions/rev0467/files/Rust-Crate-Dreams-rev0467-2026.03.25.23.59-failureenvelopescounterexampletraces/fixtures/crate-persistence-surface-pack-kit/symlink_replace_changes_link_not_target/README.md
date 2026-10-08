# Symlink replace changes link, not target

Simulates a crate that says it “updates the config file pointed to by a symlink”, but its save helper actually replaces the symlink path itself.

Why this matters:
- `atomic-write-file` documents that if the destination path is a symlink, the symlink is replaced and the original target is left untouched.
- A persistence-surface crate should therefore make **publication target** explicit instead of assuming that a path-like save updated the canonical target.

What this scenario should force:
- a `publication-target.report` that can say `symlink_replaced_target_untouched`
- a summary that distinguishes replacing a path entry from mutating the file the symlink previously pointed to
- a doctor warning such as `symlink_replace_presented_as_target_update`
