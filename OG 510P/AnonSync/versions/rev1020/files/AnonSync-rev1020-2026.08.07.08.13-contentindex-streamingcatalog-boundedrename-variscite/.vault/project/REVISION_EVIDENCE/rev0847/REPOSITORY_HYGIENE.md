# Rev0847 repository hygiene

## Packaged tree

The release root contains source, tests, tools, fuzz entry points, bundled
third-party source, revision notes, and evidence. Build trees remain outside the
package. Before manifest generation the tree is scanned for symlinks, VCS
metadata, object files, libraries, executables, CMake build products, core dumps,
coverage files, and Python caches.

The final package verifier recomputes the exact active projection, requires the
full production/header/test surface, checks every manifest member and digest,
and verifies the ZIP root, path safety, duplicate names, symlink absence, and CRC.
Rev0847 additionally makes the verification-budget focused test and architecture
audit mandatory package members.

## Build isolation incident

Several abandoned work/build roots from earlier attempts retained queued shell
commands. Those commands periodically launched compilers and Python audits,
starving complete CTest attempts even though no test had failed. The abandoned
roots and processes were removed, the active build cache was checked to point
only at the verified fresh source root, and the final registry was rerun under
direct observation. The retained final run is one uninterrupted 143/143 pass.

This was an environment hygiene failure, not a product-test failure. The
incident reinforces three operational rules:

- give every attempt a unique source and build root;
- terminate process groups, not merely the front shell, when abandoning work;
- record a process/build-root inventory before interpreting timeouts as code
  failures.

No abandoned root or build artifact is included in the package.

## Change amplifiers retained

Measured final-source debt:

- `src/sync_domain.cpp`: 15,287 lines;
- `src/sync_domain_selftests.cpp`: 9,348 lines;
- `src/sqlite_replay_ledger.cpp`: 4,527 lines;
- `src/reporting_selftests.cpp`: 4,992 lines;
- `CMakeLists.txt`: 2,530 lines;
- source audit tools: 42;
- historical `REVISION_EVIDENCE` before rev0847: 25,781,657 bytes;
- active first-party implementation/test/tool/fuzz files excluding bundled
  third-party source: 7,053,241 bytes.

The evidence corpus is therefore several times larger than the active
first-party cube, and the largest production/test units remain substantial
change amplifiers. Future refactors should move invariants into small typed
owners and semantic model tests, then retire superseded spelling audits instead
of adding permanent parallel proof systems.
