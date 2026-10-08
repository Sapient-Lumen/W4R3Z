# rev0789 toolchain and validation limits

- The full final GCC Debug build completed and 44/44 tests passed. Its first
  clean build required more than one foreground command window because the
  monolithic core remains expensive; completed objects were retained and the
  resumed build finished normally.
- A separate clean optimized CMake experiment compiled both small first-party
  profile objects, then spent the remaining command window compiling the
  bundled SQLite amalgamation. The passing optimized gate therefore compiles
  and runs the three first-party boundaries directly with GCC 14 `-O3
  -DNDEBUG -Werror`; it is not described as a clean optimized rebuild of the
  third-party amalgamation.
- The default GCC ASan/UBSan lane instruments AnonSync C++ boundary code but not
  `third_party/sqlite-3.53.3/sqlite3.c`. A dedicated slower option exists via
  `ANONSYNC_SANITIZE_BUNDLED_SQLITE=ON` and remains an unpassed optional gate.
- The installed Swift Clang 17 libFuzzer archive emits an `.eh_frame_hdr`
  linker warning. Its function-symbolization path crashes unless
  `-print_funcs=0`, and combining its libFuzzer runtime with ASan fails during
  startup in this cloudtainer. The validated campaign therefore uses
  libFuzzer+UBSan; independent GCC ASan/UBSan runs cover the C++ boundary.
- No result in this revision is presented as a production performance
  benchmark. Build-action and source-exposure figures come from fresh Ninja
  dry-run dependency graphs.
