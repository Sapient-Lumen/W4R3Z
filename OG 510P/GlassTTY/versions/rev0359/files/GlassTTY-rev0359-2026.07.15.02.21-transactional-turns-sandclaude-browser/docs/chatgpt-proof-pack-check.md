# ChatGPT proof pack check

`proof-export-pack` materializes the 30-slot evidence pack. `proof-check-pack` then verifies that the pack is complete, parseable, and safe to classify as rehearsal or live.

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-check-pack \
  --pack-dir validation/latest/chatgpt-proof-rehearsal-evidence-pack \
  --pretty
```

For a real live proof, require live semantics:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-check-pack \
  --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack \
  --require-live \
  --pretty
```

The live gate fails if the manifest declares `rehearsal_only`, if the screenshot is a generated placeholder, if the screenshot is the 1x1 rehearsal PNG, or if the evaluator verdict is not `reviewable-no-claim-widening`.

## Finalizer wrapper

Most operators should run `proof-finalize-pack` instead of calling exporter and checker separately. The checker remains the lower-level validation primitive, while the finalizer writes the operator handoff and recommended next actions.
