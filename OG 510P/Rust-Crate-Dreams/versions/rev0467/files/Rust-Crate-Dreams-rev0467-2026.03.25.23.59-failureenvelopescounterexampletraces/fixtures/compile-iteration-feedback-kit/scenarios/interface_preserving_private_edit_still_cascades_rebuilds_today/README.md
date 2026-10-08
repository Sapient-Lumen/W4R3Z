# Interface-preserving private edit still cascades rebuilds today

This scenario exists to force **P-0537** to separate current Cargo/rustc behavior from the stronger future shape users actually want.

The current Relink don’t Rebuild goal explicitly says implementation-only and comment-level edits still rebuild reverse dependencies today.
A worthy compile-iteration crate should record that such an edit is interface-preserving even when the current strongest route is still broader rebuild work than users expect.
