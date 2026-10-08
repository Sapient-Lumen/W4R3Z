# Public trace capture preflight handoff audit — REV0147

Status: `pass`  
Promotion allowed: `false`

Prevents the active public-trace wrapper from paying the same import-light capture-start and static handoff gates twice. The stable wrapper now hands an explicit done/contract/env flag into the one-shot; the one-shot still preserves its full direct fallback path for forensic replay.

## Errors

- none

## Runtime handoff seen

```json
{
  "PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE": null,
  "PUBLIC_TRACE_CAPTURE_PREFLIGHT_CONTRACT": null,
  "PUBLIC_TRACE_CAPTURE_PREFLIGHT_ENV": null,
  "LOCAL_SNAPSHOT_DIR_present": false
}
```
