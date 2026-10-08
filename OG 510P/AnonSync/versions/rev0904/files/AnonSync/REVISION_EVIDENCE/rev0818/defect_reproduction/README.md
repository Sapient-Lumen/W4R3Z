# Sealed-parent intermediate-symlink differential

`intermediate_symlink_same_harness.cpp` is compiled unchanged with C++20,
`-Wall -Wextra -Wpedantic -Werror` against the exact rev0817 source and against
rev0818. It requests publication to `root/link/subdirectory/report.json`, where
`link` is an intermediate directory symlink to `root/real`.

Rev0817 reports success and creates the file in the symlink target. Rev0818
reports a typed prepublication failure, rejects the intermediate symlink, and
creates no redirected target. The JSON files are the direct machine-readable
outputs. Executable harness binaries are intentionally excluded from the
release package.
