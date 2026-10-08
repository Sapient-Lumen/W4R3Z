# ChatGPT proof rehearsal

The rehearsal command exercises the checkpoint proof evaluator while live
ChatGPT submission is unavailable. It builds a synthetic local bundle that has
the same shape as the intended live proof path, then runs the evaluator against
it.

The rehearsal is deliberately marked:

```json
{
  "proof_mode": "offline-rehearsal",
  "rehearsal_only": true,
  "live_proof": false
}
```

The evaluator returns `rehearsal-harness-ok-not-live` when all proof-shape
checks pass. That means the harness is coherent. It does not mean the project
has a live proof.

## Run

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts \
  glassttyd proof-rehearse --pretty
```

Outputs:

```text
validation/latest/chatgpt-proof-rehearsal.json
validation/latest/chatgpt-proof-rehearsal-evaluation/chatgpt-proof-rehearsal-evaluation.json
validation/latest/chatgpt-proof-rehearsal-evaluation/SUMMARY.json
```

## Run against a fresh surface report

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts \
  glassttyd proof-rehearse \
  --surface-report path/to/tampermonkey-report.json \
  --contract validation/latest/chatgpt-live-surface-contract-rev0336-2026.06.13.json \
  --strict-surface \
  --pretty
```

With `--strict-surface`, a drift warning/blocker makes the rehearsal summary
not-ok. This is useful before a live proof window opens.

## Promotion rule

Never copy a rehearsal payload into the live proof evidence pack. The evaluator
blocks rehearsal payloads from returning `reviewable-no-claim-widening` even
when every proof-shape check passes.
