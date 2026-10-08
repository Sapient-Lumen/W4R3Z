# Rev0987 authority incidents

Validation found multiple unsealed rev0987 worktrees and build graphs left by
older orchestration. One deleted a build directory during a registry run; later
processes repeatedly launched compiler and sanitizer work against divergent
source trees. Those trees and every result derived from them were excluded.

The final authority was isolated under
`/home/oai/share/AnonSync-rev0987-seal-20260804T062447Z-17352` with protected
GCC and Clang build directories. Divergent source/build pairs were terminated
and removed, recovering roughly 5 GiB during the final pass and preventing
cross-branch binaries from entering release evidence.

The fresh Clang product lane was therefore accounted from the exact retained
251-edge graph through bounded immutable invocations. Every one of the 43
registered product tests has an explicit passing terminal line; long focused
proofs were also executed directly with ASan/UBSan and leak detection.
