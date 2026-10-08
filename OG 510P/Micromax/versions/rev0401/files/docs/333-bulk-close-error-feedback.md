# Bulk close error feedback

This revision tightens one tiny trust-first seam in buffer cleanup.

Micromax already had the important *behavior* for bulk closing:

- `only` keeps the current buffer and safely closes the rest
- `closeall` can wipe the session back to `*scratch*`
- both commands guard dirty buffers unless forced
- successful runs already reported the landed active buffer

But the unexpected failure path still lagged behind the newer typed command
dialect.

Before this revision, if the shared close helper raised unexpectedly, the user
saw messages like:

- `only error: boom`
- `closeall error: boom`

Those lines were understandable, but they were slightly out of step with the
rest of the command bar, which had been moving toward explicit
`surface: error: details` feedback.

Now the same failures read as:

- `only: error: boom`
- `closeall: error: boom`

That change is small, but it helps in exactly the moments when the editor most
needs to be inspectable:

- message logs stay easier to grep
- test expectations stay structurally consistent
- future plugin or scripting bugs keep the failing surface visible
- bulk buffer cleanup no longer switches dialects when the fault is unexpected

The implementation is deliberately tiny: only the two command-local exception
messages change, and focused tests force the shared close helper to raise so the
behavior stays pinned down.
