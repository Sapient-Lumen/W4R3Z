# ADR 0014: Source-linked and runtime-loaded toxcore providers share one seam

**Status:** accepted and implemented as architecture in rev0005

## Context

Runtime loading provides an exact ABI test point but asking owners to install a matching
shared toxcore weakens the standalone product. Directly scattering linked toxcore calls
would sacrifice the test seam.

## Decision

Both providers populate the same `toxcore::abi::Api` table. A source-linked build selects
the linked provider by default. An explicit library path selects the dynamic provider.
Research builds without source integration use the dynamic provider.

The source-linked path targets pinned c-toxcore 0.2.23 and its official `toxcore_static`
target. Runtime version and numeric constant checks remain.

## Consequences

One owner-thread implementation serves production and tests. The standalone binary can
contain toxcore, while the loadable mock continues to exercise the actual ABI boundary.
The official source-linked build remains an evidence gate until run externally.
