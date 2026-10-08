# ChatGPT proof autopilot

`proof-autopilot` is the guided operator command for the ChatGPT-only proof pipeline. It is intentionally conservative: by default it only reports the current state and next action. It does not ingest, finalize, publish, or mark anything live unless explicitly asked.

## Dry run

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-autopilot --pretty
```

This writes:

```text
validation/latest/chatgpt-proof-autopilot-summary.json
```

The summary includes the initial stage, final stage, next action, and every step that was attempted or intentionally skipped.

## Safe refresh

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-autopilot --execute-safe --pretty
```

This may refresh the offline preflight/rehearsal gates, but it will not ingest a downloaded proof JSON and will not touch the live evidence pack.

## Live guarded run

After the side panel has produced a downloaded proof JSON:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-autopilot \
  --execute-live \
  --input ~/Downloads/glasstty-chatgpt-proof-<attempt>.json \
  --clean \
  --pretty
```

This can ingest and finalize the capture if the proof JSON passes the live-candidate gate. It still will not publish unless the live pack has a privacy-review pass.

To continue all the way through privacy and publish verification, provide the human review attestation:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-autopilot \
  --execute-live \
  --input ~/Downloads/glasstty-chatgpt-proof-<attempt>.json \
  --clean \
  --reviewer "<name>" \
  --decision pass \
  --attest-screenshot-reviewed \
  --attest-no-unrelated-content \
  --attest-local-only \
  --require-complete \
  --pretty
```

`--require-complete` returns non-zero unless the pipeline reaches a verified live support bundle. Without it, the command is allowed to stop at the next human-required stage and report the next action.

## Safety posture

The command refuses to silently skip blockers. Incomplete stages remain visible as `proof-autopilot-awaiting-operator`, and failed stages become `proof-autopilot-halted` with blockers. Rehearsal output is still never treated as live proof.
