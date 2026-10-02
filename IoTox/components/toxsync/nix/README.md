# Nix environment

`flake.nix` exposes the `toxsync` package and a C++20 development shell for
x86-64 and AArch64 Linux. The reviewed `flake.lock` is committed beside it so package and
development-shell evaluation use the same pinned nixpkgs revision.

Useful commands:

```sh
nix develop
cmake --preset gcc-debug
cmake --build --preset gcc-debug
ctest --preset gcc-debug
nix build
nix flake check
```

When testing uncommitted component changes from this directory, use `nix build path:.#toxsync`; the
ordinary Git-backed flake source intentionally excludes untracked files.

The upstream hsynz reference snapshot is not a toxsync build dependency.
