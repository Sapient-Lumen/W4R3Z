# Convenience binaries

`linux-x86_64/` contains stripped, fully static GNU/Linux x86-64 tools built
from this exact source tree with Clang 17.0.0, CMake Release mode,
`BZIP4_ENABLE_IPO=OFF`, and `-static`.

They have no dynamic-loader dependency or `PT_INTERP`. Two independent build
directories produced byte-identical unstripped and stripped tools on this host,
and the static build passes all 23 strict test groups.

Source and the release manifest are canonical. These binaries are convenience
artifacts, not a portability guarantee or Datacube codec admission. Build and
validation details are in `docs/BINARY_DISTRIBUTION.md`.
