# Focused build graph

The exact SQLite scalar proof is an independently linked C++ boundary. A fresh Ninja dry-run reports **6** actions and **2** first-party translation units (523 lines), versus **45** actions and **35** first-party translation units (53,355 lines) for `anonsync_core`.

This is a 7.5x action and 102.02x first-party line exposure difference. The CMake dependency guards fail configuration if the focused boundary or test acquires a dependency on `anonsync_core_lib`.
