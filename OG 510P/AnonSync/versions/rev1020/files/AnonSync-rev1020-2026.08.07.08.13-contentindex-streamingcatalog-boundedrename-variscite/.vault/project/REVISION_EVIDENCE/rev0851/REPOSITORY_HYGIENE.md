# Rev0851 repository hygiene

The release projection contains **276 active files / 17,601,745 bytes**. The
source delta is confined to **13 active files**: two new production files, one
new focused test, and ten modified build, implementation, test, audit, and
release-verifier files. Bundled third-party source is unchanged.

No symlink, object, archive, executable, CMake build tree, VCS directory, or
Python bytecode is included. A generated `tools/__pycache__` entry created while
running audits was detected during patch replay, removed, and excluded before
projection and manifest sealing.

The exact active patch applies to the sealed rev0850 parent and reproduces all
**276/276** active paths, byte counts, and SHA-256 digests. The package verifier
recomputes the active projection and requires the new owned-policy files only
for rev0851 and later.

The repository still carries substantial structural debt. `src/sync_domain.cpp`
is 15,287 lines and CMakeLists.txt is approximately 2,700 lines. Historical
`REVISION_EVIDENCE` dominates package size, and many Python audits inspect
source spelling. Those checks are valuable where they preserve unique primitive
ownership—as the raw-fork finding demonstrated—but they should be retired when
a typed boundary or executable semantic oracle makes them redundant.
