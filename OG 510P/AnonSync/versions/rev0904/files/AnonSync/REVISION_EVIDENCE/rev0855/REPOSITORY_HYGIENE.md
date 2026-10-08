# Rev0855 repository hygiene

The release tree contains source, tests, tools, third-party source, and revision
evidence only. Build trees, VCS metadata, object files, executables, CMake cache
files, and Python bytecode are excluded from the package.

During patch-projection verification, importing audit helpers created five
`tools/__pycache__/*.pyc` files. The projection mismatch detected them before
packaging. They were removed, bytecode generation was disabled for subsequent
verification, and the replayed and current projections then matched at
**283/283** active files.

The active implementation delta is **14 files, 479 insertions, and 85
deletions**. No bundled third-party file changed.

The busy API inventory was also made less wasteful: it now removes `//` comments
before recognizing calls, so documentation no longer appears as executable C
API ownership.
