# 12 — Non-goals and escalation rules

## Non-goals

TimeSync does not currently define:

```text
a complete time protocol
a universal profile registry
a standards catalog
a source path provenance graph
a clock compliance certificate
a global downgrade table
a global applicability vocabulary
a native request bundle system
a namespace hierarchy for discovery
a mandatory profile-signing infrastructure
a universal revocation service
```

## Escalation rule

A feature should move upward only when lower layers fail.

```text
profile-local example       before shared hook
shared hook                 before core field
requestable item            before profile-default item
profile-default item        before invariant-core item
local policy overlay        before global policy lattice
boundary context            before provenance graph
profile reference digest    before signed binding
signed binding              before certification infrastructure
```

## Evidence rule

Core growth needs repeated pressure across materially different profiles. A single strong sector case usually belongs in that sector profile first.
