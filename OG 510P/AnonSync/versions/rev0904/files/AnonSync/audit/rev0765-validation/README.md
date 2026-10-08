# Rev0765 validation index

Raw revision evidence is centralized at `../../../../.revision-evidence/rev0765/` to avoid duplicating build logs inside the active C++ tree.

- `validation/`: fresh configure, build, complete CTest, focused retention, domain, lifecycle, warning, and static-source evidence.
- `sanitizer/`: honest partial ASan+UBSan evidence; changed production objects compiled, complete graph/runtime not claimed.
- `provenance/`: rev0764-to-rev0765 source patch and inventories.
- `release/`: gate, toolchain, binary provenance, summary, and validator result.
