# compile_time_deps_vs_full_build

A tool-facing `--compile-time-deps` or editor-like run is compared against a later full build.

This scenario exists to prove that the rebuild kit can **reference** tool-surface drift without swallowing the `P-0494` lane whole.
The bundle may say that a tool invocation drifted from the fuller build and that this likely affected reuse or expectations, but it must not claim that the tool-only run was equivalent to a real build.
