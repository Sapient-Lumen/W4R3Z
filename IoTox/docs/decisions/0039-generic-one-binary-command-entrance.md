# ADR 0039 — Generic one-binary command entrance

**Status:** accepted and implemented in rev0010  
**Date:** 2026-08-14 America/New_York

## Context

A modern ratox successor needs an ordinary operator surface, but one subcommand per machine
operation would hard-code protocol growth into CLI plumbing. A second executable or a second local
queue would also violate the one-product rule and split durability semantics.

## Decision

The public local entrance is:

```text
iotox command FRIEND OPERATION
```

It resolves the public-key-first friend selector, parses `OPERATION` through the command registry,
and sends one bounded `command-issue` request over the existing private Unix `SOCK_SEQPACKET`
control socket. The agent reserves and commits the same durable transaction used by automatic
retry, CLI inspection, and future filesystem/FIFO adapters.

Local-control protocol v1.13 assigns operation 55 to `command-issue`. Its current payload is one
big-endian uint32 friend number followed by one uint8 command operation. rev0010 accepts only
`device.describe`, which has no arguments. `iotox device-describe FRIEND` remains a compatibility
alias and does not define a second command engine.

## Consequences

- There remains one installed executable and one authoritative durable path.
- Future operations extend the bounded command request rather than adding products.
- The ratox-style write façade must translate to this same operation and durable key.
- Arguments, schema versions, watch behavior, and admission limits must be frozen before the first
  additional operation is exposed.
