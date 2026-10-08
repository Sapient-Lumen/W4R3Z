# Dispatch fence

Dispatch fence joins native load loopback, native call canary, revalidation seal, and native call hold.

It is the rev0093 reminder that joined evidence is still not execution authority:

```text
dispatch_fenced = true
native_load_allowed = false
native_dispatch_allowed = false
native_call_executed = false
```

The fence quarantines if a native load, dispatch, or call occurred before the cube has a later, explicit, no-network release boundary.
