# Scenario — rust-lldb wrapper is the formatter origin for the LLDB lane

This scenario models a project that ships NatVis and GDB embedded assets for their documented lanes, but relies on the toolchain-provided `rust-lldb` launcher for LLDB-family formatting support.

The point of the receipt is to avoid pretending that the crate’s own embedded assets prove the LLDB lane.
