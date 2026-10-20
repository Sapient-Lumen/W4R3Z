# ADR 0419: Make standalone build generator tolerant

Status: accepted

Date: 2026-10-01

## Context

The source-linked standalone build is part of the release handoff: it produces
`dist/standalone/iotox`, licenses, `build-info.txt`, `verification.txt`, an
SPDX SBOM, and optional pinned source inputs. The script previously hardcoded
CMake's `Ninja` generator. That worked on hosts with Ninja installed, but it
made an otherwise capable release host fail before compilation.

## Decision

`tools/build-standalone.sh` now chooses its CMake generator as follows:

1. use `IOTOX_CMAKE_GENERATOR` when the operator sets it;
2. otherwise use `Ninja` when `ninja` or `ninja-build` is available;
3. otherwise fall back to `Unix Makefiles`.

If the default standalone build directory already contains a CMake cache from a
different generator, the script moves to a generator-specific build root instead
of requiring manual cleanup. If the operator explicitly set
`IOTOX_STANDALONE_BUILD_DIR`, the script fails with a clear instruction rather
than guessing.

The selected generator, static C++ runtime choice, and effective extra link
flags are recorded in `dist/standalone/build-info.txt`.
The script also fails early when no C or C++ compiler is visible and tells the
operator to set `CC`/`CXX` or run inside the project dev shell.

## Consequences

The standalone binary path is easier to run on small, bare-metal, or freshly
bootstrapped hosts while preserving exact source-commit provenance and the
existing verifier contract.
