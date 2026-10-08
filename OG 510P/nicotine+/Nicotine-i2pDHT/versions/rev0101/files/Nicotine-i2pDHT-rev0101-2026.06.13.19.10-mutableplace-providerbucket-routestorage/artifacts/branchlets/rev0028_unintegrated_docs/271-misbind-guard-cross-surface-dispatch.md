# Misbind guard before handler dispatch

A signed frame, validated payload, capability grant, namespace policy, and admission decision can all be locally valid and still be wired together incorrectly. That is the cross-surface misbinding class.

`misbindguard.py` introduces `HandlerIntent` and `guard_handler_intent()`.

It checks that the future expensive handler remains bound to the same:

```text
wire message kind
payload role
namespace
scope id
actor public key
request id
body digest
```

This guard is intentionally stricter than any one upstream report. It is designed to catch the bug where a valid proof for one action authorizes a different action because a caller reused a request id, swapped a body, or confused a provider claim with a mutable-head write.
