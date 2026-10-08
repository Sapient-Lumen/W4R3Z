# 08 — Relay and boundary context

## Problem

Relays and aggregators can preserve, weaken, restate, or obscure upstream timing state. The model needs a small explanation surface without becoming a provenance graph.

## Boundary action vocabulary

```text
preserve
downgrade
restate
unknown
```

Meaning:

```text
preserve   downstream state preserves the relevant upstream assessment
downgrade  downstream state weakens a claim or applicability boundary
restate    downstream state is newly assessed at the relay or boundary
unknown    boundary action is not known or not safely characterized
```

## Optional reason vocabulary

```text
loss
recovery
conflict
reconfiguration
```

## Shape

```text
boundary_context:
  action: preserve | downgrade | restate | unknown
  reason?: loss | recovery | conflict | reconfiguration
```

## Lifetime

`boundary_context` expires with the local assessed state it explains. It does not need an independent lifetime until a profile proves otherwise.

## Visibility

`boundary_context` is requestable by default and may be profile-default where omission would mislead downstream users.

## Non-goal

Boundary context is not a source path, provenance chain, audit trail, or relay certificate.
