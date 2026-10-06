# Static convenience binary distribution — rev0034

## Included target

`bin/linux-x86_64/` contains:

- `bzip4_codec`
- `bzip4_cube_preflight`
- `bzip4_release_audit`
- `bzip4_activation_probe`

They are built in this cloudtainer with Clang 17.0.0, CMake Release mode,
`BZIP4_ENABLE_IPO=OFF`, and `-static`. `file` reports statically linked x86-64
ELF executables, `ldd` reports no dynamic executable, and program headers contain
no `PT_INTERP` segment.

The complete 23-group suite passes against the static build. A second independent
build directory produces byte-identical unstripped and stripped tools on this
host. Source and manifest remain canonical.

## Why Clang, not GCC IPO

The matched rev0034 matrix showed Clang `-O3` 10.18% faster for bzip4 encode and
14.77% faster for decode than GCC `-O3` on the current witness. GCC IPO was
slightly slower than GCC `-O3` in that matrix. Upstream bzip3 and libsais both
identify compiler sensitivity, and libsais recommends Clang for performance.

This is a host-specific release policy, not a portability guarantee. GCC remains
a mandatory independent validation compiler, and IPO remains an opt-in CMake
experiment.

## Rebuild command

```sh
CC=clang CXX=clang++ cmake -S . -B /tmp/bzip4-static -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON \
  -DBZIP4_ENABLE_IPO=OFF \
  -DCMAKE_EXE_LINKER_FLAGS=-static
cmake --build /tmp/bzip4-static -j2
ctest --test-dir /tmp/bzip4-static --output-on-failure
```

## Frame boundary

`bzip4_codec` emits and accepts the count-bearing BZ3v1 envelope used by the
upstream high-level C API. It does not guess the distinct EOF-terminated stream
emitted by the upstream CLI, because both use the same magic and heuristic
auto-detection would weaken admission. Equal-partition block records remain
identical.

Named profile commands are the recommended operational path. The profile name
is external metadata and must be authenticated by Datacube.

## Compatibility boundary

The tools target the observed GNU/Linux x86-64 environment. They may not run on
another architecture, old kernel, or policy environment. They are convenience
artifacts, not a replacement for source review, a broad portability promise, or
Datacube codec admission.
