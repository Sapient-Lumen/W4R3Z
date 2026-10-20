# ADR 0010: The ratox successor is the immediate northstar

**Status:** accepted; process-shape clause superseded by ADR 0013

## Context

rev0003 integrated the Milehigh Mutorr Small Circles research. The work is coherent and
worth preserving, but distributed namespace replication is not required to deliver the
core value the user presently needs: a dependable, scriptable, self-owned Tox device
agent with ratox's simplicity.

Allowing optional research to occupy the default build, status prose, executable, and
test path obscured the critical sequence: real toxcore, two peers, local Unix usability,
authorization, and durable command semantics.

## Decision

The immediate northstar is a modern ratox successor.

- `iotox` is the sole public product executable; `iotox run` is the agent role (ADR 0013).
- Default source and tests focus on Tox lifecycle, local IPC, state, peers, packets,
  bootstrap/relay operation, and later authorization/durability.
- Mutorr remains intact under `incubator/mutorr/` and requires explicit CMake options.
- The basic device path must never depend on Mutorr.
- Reintroducing Mutorr into active product scope requires a later decision based on a
  functioning ratox-successor foundation.

## Consequences

The default repository tells one clear story. Existing Mutorr history and code are not
discarded, but their complexity cannot delay or distort the native agent.

## Revisit when

Real Tox transport, local ratox-like use, authorization, and durable device commands are
working and measured, and a concrete product use case requires replicated namespaces.
