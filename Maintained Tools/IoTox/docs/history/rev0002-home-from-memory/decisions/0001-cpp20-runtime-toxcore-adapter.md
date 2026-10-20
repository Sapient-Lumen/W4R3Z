# ADR 0001: C++20 core with a runtime c-toxcore adapter

**Status:** accepted for rev0001

## Context

IoTox should be written in C++ where possible, while Tox’s maintained implementation is a C library. The first container has GCC, Clang, CMake, and Ninja, but no c-toxcore development package.

## Decision

All IoTox-owned source is C++20. c-toxcore is treated as an external runtime dependency loaded through a narrow symbol table. No business-logic source includes toxcore headers.

## Consequences

- The project and tests build without toxcore installed.
- A deterministic C++ shared-library mock can exercise the boundary.
- Missing or incompatible symbols fail at startup with diagnostics.
- A future CI job must compile against the official headers to detect declaration drift.
- Runtime loading does not remove c-toxcore licensing obligations.
