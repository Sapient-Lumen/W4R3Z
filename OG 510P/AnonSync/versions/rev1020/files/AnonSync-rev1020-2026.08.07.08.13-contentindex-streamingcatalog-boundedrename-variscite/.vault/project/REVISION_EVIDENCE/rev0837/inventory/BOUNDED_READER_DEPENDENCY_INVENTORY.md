# Bounded-reader dependency inventory

The production implementation is one standalone static-library leaf with no
first-party link dependency. Each focused executable contains exactly two
first-party translation units: its own test and
`src/sync_bounded_regular_file.cpp`. Neither focused target links
`anonsync_core_lib`.

The core links the leaf privately, while CMake excludes the leaf source from the
21-source core aggregation and contains configure-time guards against
reabsorption. The two production symbol consumers are `sync_domain.cpp` and
`sync_operator_cli.cpp`; the old hidden helper has zero current production
sites.

Raw Ninja target queries, command closures, the CMake Graphviz graph, and the
machine-readable inventory accompany this note.
