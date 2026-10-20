# ADR 0013: One product executable

**Status:** accepted and implemented in rev0005  
**Supersedes:** the two-product-binary consequence recorded by ADR 0010

## Context

The agent and its local controller were separate executables in rev0004. The product is
conceptually one thing, and users should not need to remember which binary owns the network
and which one speaks to it.

## Decision

Install one product executable named `iotox`.

`iotox run` starts the foreground agent. Other subcommands use the same binary as a local
client. Internal libraries, mocks, tests, fuzzers, and optional incubator tools remain
separate build targets when useful.

## Consequences

Packaging, documentation, service units, and user memory become simpler. Process tests must
exercise one binary in both roles. No stale `iotoxd` artifact may enter a revision package.
