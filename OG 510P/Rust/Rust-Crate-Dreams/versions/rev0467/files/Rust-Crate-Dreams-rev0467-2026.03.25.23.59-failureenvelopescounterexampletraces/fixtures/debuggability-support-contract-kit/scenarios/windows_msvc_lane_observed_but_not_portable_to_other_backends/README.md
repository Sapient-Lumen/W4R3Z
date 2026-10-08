# windows_msvc_lane_observed_but_not_portable_to_other_backends

Scenario intent:
A Windows MSVC release can have a `pdb`, embedded NatVis, and one observed Visual Studio debugging lane while still lacking an honest portable claim for LLDB, async inspection, or Rust expression evaluation.

The point is to keep **broad posture**, **exact backend observation**, and **portable claim ceiling** separate.
