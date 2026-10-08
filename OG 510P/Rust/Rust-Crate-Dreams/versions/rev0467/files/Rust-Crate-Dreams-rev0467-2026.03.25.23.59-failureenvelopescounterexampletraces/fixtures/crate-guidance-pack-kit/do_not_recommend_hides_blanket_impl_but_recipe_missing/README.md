# Scenario — do_not_recommend hides blanket impl but recipe missing

A trait-heavy crate correctly uses `#[diagnostic::do_not_recommend]` to suppress a misleading blanket-impl hint, but never supplies the smallest working adapter or implementation path.

Why it matters:
- the user is spared a bad recommendation,
- but the official recovery path is still under-specified,
- so the crate should emit a doctor warning instead of pretending guidance is complete.
