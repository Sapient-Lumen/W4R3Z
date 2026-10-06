# RFC-0086: Distributed unprivileged builds (pbulk lessons)

Status: Draft

## Summary

Make builder pools and distributed builds a first-class concept, with unprivileged builds by default.

Reference: pkgsrc bulk builds (`pbulk`) support unprivileged and distributed builds. https://www.netbsd.org/docs/pkgsrc/bulk.html

## Goals

- Scale builds without increasing host authority.
- Reuse CAS/action cache semantics.
- Integrate with witness rebuilders.

## Design sketch

- Builder nodes must declare:
  - builder base digest
  - toolchain digests
  - sandbox tier
- Scheduler assigns Plan tasks to nodes that match required base/toolchain.

See: `docs/118-distributed-builds-pbulk.md`.
