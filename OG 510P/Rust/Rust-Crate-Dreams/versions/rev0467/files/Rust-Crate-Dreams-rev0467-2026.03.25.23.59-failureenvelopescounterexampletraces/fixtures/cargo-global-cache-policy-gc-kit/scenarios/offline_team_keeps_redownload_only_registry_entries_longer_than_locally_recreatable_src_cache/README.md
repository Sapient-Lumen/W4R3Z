# Scenario: offline-heavy teams keep redownload-only registry data longer than locally recreatable source cache

This scenario exists so **P-0480** does not flatten “space reclaimed” into one fake cleanup win.

The key claim is that a cleanup policy may legitimately treat:

- unpacked `registry/src` trees as more locally recreatable,
- but `.crate` archives and registry index/git data as more costly to lose for an offline-heavy workflow.

The sharper move is to keep the **recovery obligation** explicit.
