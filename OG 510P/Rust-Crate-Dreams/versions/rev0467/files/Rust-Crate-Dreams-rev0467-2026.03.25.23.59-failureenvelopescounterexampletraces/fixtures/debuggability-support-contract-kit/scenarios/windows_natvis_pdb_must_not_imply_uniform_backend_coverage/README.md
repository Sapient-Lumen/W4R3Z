# windows_natvis_pdb_must_not_imply_uniform_backend_coverage

Scenario intent:
A Windows MSVC release can legitimately ship a `pdb` plus embedded NatVis while still lacking a broad claim about LLDB, async inspection, or expression evaluation.

The point is to keep **artifact posture**, **visualizer asset presence**, and **backend-family coverage** separate.
