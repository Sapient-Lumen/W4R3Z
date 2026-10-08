# Mixed Rust/C++ sanitized build needs explicit external compiler-runtime routing

This scenario keeps one mixed-language truth visible:
a successful build may still depend on an explicit runtime-linkage route outside Rust's default compiler runtime.

The receipt should say that `external-clangrt` or an equivalent route was needed because instrumented C++ participated in the run.
