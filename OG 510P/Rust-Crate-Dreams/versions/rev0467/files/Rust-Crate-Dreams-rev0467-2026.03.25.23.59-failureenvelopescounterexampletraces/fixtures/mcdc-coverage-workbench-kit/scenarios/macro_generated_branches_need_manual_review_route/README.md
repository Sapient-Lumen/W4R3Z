# Scenario — macro-generated branches need a manual-review route

This scenario protects against silently ignoring branch forms introduced by macro expansion.

If the current toolchain discards spans that are not directly visible, the crate should emit a manual-review-required drift or caveat state instead of claiming full support.
