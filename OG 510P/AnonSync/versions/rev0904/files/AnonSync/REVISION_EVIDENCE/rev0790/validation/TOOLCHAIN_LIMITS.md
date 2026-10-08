# rev0790 toolchain and validation limits

- The fresh GCC 14 Debug/`-Werror` build completed. The complete suite passed
  46/46 both with four-way CTest execution (13.17 seconds) and in the final
  serial inventory (26.79 seconds). These cloudtainer durations are environment
  observations, not benchmarks.
- The fresh Clang 17 lane compiled the full first-party core and focused tests
  with project warnings plus `-Werror`. The extracted exact-value and projection
  boundaries also passed `-Wconversion -Wsign-conversion -Werror` five times.
- The required GCC ASan/UBSan lane instruments the extracted first-party exact
  scalar and projection code. The pinned SQLite amalgamation is not
  instrumented by default and remains an unpassed optional gate.
- A full sanitizer core build was resumed across four command windows and
  remained in `src/sync_domain.cpp`. This is an incomplete optional experiment,
  not a pass and not a sanitizer finding. The focused boundary lane passed 5/5.
- The installed Swift-derived Clang 17 libFuzzer runtime emits an
  `.eh_frame_hdr` linker warning and requires `-print_funcs=0` in this
  cloudtainer. The validated campaign uses libFuzzer+UBSan. No combined
  libFuzzer+ASan claim is made.
- Exact storage-class validation does not bound resource consumption. Most text
  readers retain the unlimited default, and the untrusted snapshot profile does
  not yet set every connection/file/VM/heap limit. No denial-of-service
  containment claim is made.
- Source audits are deterministic regression fences, not substitutes for
  semantic review, compiler analysis, dynamic tests, mutation, or formal proof.
- Build-action and source-exposure figures are dependency measurements from
  fresh Ninja dry-runs, not production performance benchmarks.
