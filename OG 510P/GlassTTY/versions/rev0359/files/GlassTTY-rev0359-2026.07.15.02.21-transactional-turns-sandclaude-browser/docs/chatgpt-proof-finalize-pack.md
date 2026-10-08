# ChatGPT proof finalizer

`proof-finalize-pack` is the operator-facing wrapper around the evidence-pack exporter and pack checker.

It exists because the live path should not depend on remembering a sequence of loose commands. One command exports the downloadable side-panel proof JSON, checks the resulting 30-slot pack, writes a final summary, and creates operator handoff files inside the pack.

## Rehearsal finalization

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-finalize-pack \
  --input validation/latest/chatgpt-proof-rehearsal.json \
  --pack-dir validation/latest/chatgpt-proof-rehearsal-evidence-pack \
  --clean \
  --pretty
```

Expected rehearsal verdict:

```text
rehearsal-proof-pack-finalized-not-live
```

This proves exporter/checker/evaluator plumbing only. It is never a live proof.

## Live finalization

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-finalize-pack \
  --input <downloaded-sidepanel-proof.json> \
  --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack \
  --require-live \
  --clean \
  --pretty
```

Expected live-ready verdict:

```text
live-proof-pack-finalized-review-ready
```

That still does not waive human privacy/redaction review. It means the machine-verifiable pack is complete enough for review.

## Outputs

By default the command writes:

```text
validation/latest/chatgpt-proof-finalize-summary.json
validation/latest/chatgpt-proof-pack-export-summary.json
validation/latest/chatgpt-proof-pack-check-summary.json
<pack-dir>/operator-handoff.json
<pack-dir>/OPERATOR-HANDOFF.md
```

The handoff files summarize blockers, suggested fixes, and the next command to run.
