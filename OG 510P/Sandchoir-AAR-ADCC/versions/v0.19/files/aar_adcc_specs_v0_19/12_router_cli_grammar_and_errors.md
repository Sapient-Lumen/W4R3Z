# 12 — Router CLI Grammar + Errors (v0.19)

## Command grammar (minimal)
- Commands are single-line.
- Options are `--key=value`.
- Output is either:
  - `OK <payload>`
  - `ERR <code> <message>`

## Error codes (examples)
- `E_BADARGS` invalid args
- `E_MODE` operation not allowed in current mode
- `E_PARSE` could not parse payload (e.g., vote)
- `E_CONFLICT` lease/patch conflict
- `E_NOTFOUND` unknown id
- `E_UNSUPPORTED` capability not available
- `E_INTERNAL` unexpected failure

## Idempotency expectations
- `state show`, `lease list`, `snapshot list` are idempotent.
- `patch apply` should fail safely if already applied (or be explicitly idempotent).
