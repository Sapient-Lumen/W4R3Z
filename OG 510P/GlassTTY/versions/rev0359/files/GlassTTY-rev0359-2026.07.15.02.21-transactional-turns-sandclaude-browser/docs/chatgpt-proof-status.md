# ChatGPT proof status / resumable operator state

`glassttyd proof-status` is the one-command checkpoint for the ChatGPT live proof pipeline. It does not create a proof and it does not publish anything. It inspects the current repo state, writes a resumable operator state file, and tells the next exact command to run.

## Default command

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-status --pretty
```

Default output file:

```text
validation/latest/chatgpt-proof-operator-state.json
```

The command exits non-zero until the live proof pipeline is complete. Use this for automation and handoff safety.

## Diagnostic mode

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-status --no-require-live --pretty
```

This still reports the next action, but exits zero even when the live proof is incomplete. Smoke tests use this mode because the checked-in cube should not contain a live proof.

## What it inspects

- active ChatGPT surface contract,
- latest proof preflight summary,
- normalized live capture and ingest summary,
- rehearsal evidence pack,
- live evidence pack,
- live evidence pack with privacy gate,
- publish summary,
- publish bundle verifier result.

## Main stages

```text
surface-contract-missing
run-preflight
capture-live-proof
ingest-downloaded-proof-json
finalize-live-pack
privacy-review
publish-and-verify
complete
```

Only `complete` means a verified live support bundle is ready. Rehearsal packs should never reach `complete`.
