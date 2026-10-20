# ADR 0026: A source-linked build must compile against canonical c-toxcore headers

**Status:** accepted and implemented in rev0007

## Context

IoTox deliberately retains a small built-in declaration set so an exact loadable ABI mock can
be compiled without installing c-toxcore. That fallback is useful for deterministic tests,
but it must never silently stand in for official declarations when building the standalone
product from pinned c-toxcore source.

## Decision

When `IOTOX_TOXCORE_SOURCE_DIR` enables the linked provider, compilation fails unless the
canonical c-toxcore public headers are visible and declare an API compatible with 0.2.23.
The linked provider continues to populate the same narrow function table used by runtime
loading. Startup also verifies the runtime version functions and every consumed numeric limit.

The standalone scripts pin c-toxcore 0.2.23 and libsodium 1.0.22 by immutable release archive
hash. The source-linked product is one executable; the dynamic provider remains available only
when an explicit path/environment override is supplied for diagnostics and integration.

## Consequences

A future networked CLI run will discover source/header/API mismatches at compile time instead
of accidentally validating only IoTox's fallback declarations. rev0007 has source-reviewed and
compiled the guard in runtime-provider builds, but this cloudtainer could not fetch the pinned
archives; the source-linked lane remains prepared rather than executed.
