# Environment capability contract — rev0085

The current cloudtainer can execute source, model, patch-composition, and
headless upstream-unit checks. It cannot complete the remaining native product
validation.

The machine-readable probe covers PyGObject, GTK3, GTK4, Gio, Xvfb, D-Bus
session tooling, `msgfmt`, and native Win32 execution. Capability presence is
only a prerequisite; it is never counted as a completed UI scenario.

The following packets remain explicitly bounded:

```text
SEARCH-AGAIN-EPOCH-01A  native GTK3/GTK4 page-state validation
SEARCH-AGAIN-EPOCH-01B  native GTK3/GTK4 action visibility and keyboard/accessibility validation
SEARCH-AGAIN-EPOCH-01C  native GTK3/GTK4, Gio desktop-shell, and Win32 notification validation
WISHLIST-CAP-01          native GTK3/GTK4 long-lived inbox lifecycle validation
```

All four packets retain `selected_patch: null`. The exact public-head execution
completed in rev0085 removes a source-intake qualifier, but it does not remove
these native boundaries.
