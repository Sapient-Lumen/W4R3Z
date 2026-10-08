# Validator wall before dispatch

A signed `WireFrame` proves only that a sender signed a payload digest inside a time window.  It does not prove that a frame's payload has the correct semantic type.

`validatorwall.py` adds a local dispatch boundary:

```text
wire frame validation
  -> guarded payload parse
  -> namespace allow-list
  -> message kind / payload role binding
  -> scope check
  -> body digest and size check
  -> required flag check
  -> request-id conflict detection
```

This blocks easy mistakes like a valid `CUSTODY_PROOF` frame carrying a mutable-head envelope, a store frame carrying a foreign namespace, a body that does not match its advertised digest, or two accepted frames with the same request id but different object digests.

Design guess:

```text
Handlers should receive typed evidence, not merely signed bytes.
```
