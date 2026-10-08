# Dioxus RSX and asset reload are not Rust hotpatch

This scenario exists to force **P-0537** to keep Dioxus route families separate.

Dioxus documents:
- RSX hot reload that can sidestep recompiling Rust code for UI-structure edits,
- asset hot reload for CSS/images/static files,
- and a distinct experimental `--hotpatch` lane for Rust logic.

A serious compile-iteration crate should therefore not flatten “Dioxus hot reload exists” into one generic runtime-patch claim.
