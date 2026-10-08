# 60 — State Format + Migrations (v0.19)

Weeks-long sessions require durable on-disk state that survives upgrades.

## 1) On-disk layout (suggested)
- `state/`
  - `kernel_version`
  - `config.json` (weights, caps, budget profiles)
  - `threads/`
    - `<thread_id>/`
      - `events.log` (append-only, line-delimited)
      - `ws.json` (current snapshot)
      - `ledger/` (blob files / compressed logs)
      - `checkpoints/`
        - `SNAP0001/` (ws.json + pointers + config hash)
  - `worktrees/` (optional metadata pointers)

## 2) Encoding choices
- Events: line-delimited JSON (debuggable)
- WS snapshot: JSON or msgpack (choose later)
- Large logs: compressed blobs in ledger directory

## 3) Migration policy
- Keep kernel invariants stable.
- When schema changes:
  - write a migration function `vX -> vY`
  - store a `schema_version` in each file
  - migrations are deterministic and reversible where possible

## 4) Crash safety
- events.log is append-only (fsync if you care)
- snapshots written to temp + atomic rename
- checkpoints are immutable once created

## 5) “Time travel” correctness
Restoring a checkpoint must also restore:
- config hash
- plugin config hashes
- canonical workspace pointer (git commit / snapshot id)
