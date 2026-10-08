# External backend route

This scenario keeps the crate honest about a common support reality: some debugger families should be modeled as explicit external/manual lanes instead of fake embedded parity.

This is where LLDB-family support should usually land first: official LLDB formatter docs describe summaries, filters, synthetic children, and Python-backed formatters as external formatter substrate rather than a Rust-embedded visualizer lane.

