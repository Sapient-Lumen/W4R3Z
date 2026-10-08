# SAM trace scope boundary

`samtrace.py` joins four pre-network facts:

```text
ScopeFenceReport
SamWireScriptReport
EgressWindowReport
ShadowValidationReport(s)
```

The module asks whether a future SAM send is still bound to the exact validated request and object. It rejects cross-request and cross-object shadow frames, invalid SAM scripts, rejected egress, rejected shadow frames, and send-count mismatch.

This remains no-network SAM shadowing. Its purpose is to make future live SAM integration carry precise scope/object/request intent instead of merely carrying signed bytes.
