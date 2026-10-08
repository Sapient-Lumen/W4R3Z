# rev0796 build-graph boundary

The focused snapshot-seal proof requires 8 Ninja actions and 3 first-party
translation units: path security, the seal owner, and its test. Those units are
1,679 lines / 66,366 bytes. The integrated WAL-sidecar proof and the executable
core each require 52 actions and expose the 22-translation-unit, 49,119-line
core archive.

`sqlite_path_security.cpp` was removed from the monolithic core source list and
made an independently linked owner. CMake configuration guards prevent the path
and seal implementations, or their focused test, from acquiring a dependency
on `anonsync_core_lib`.
