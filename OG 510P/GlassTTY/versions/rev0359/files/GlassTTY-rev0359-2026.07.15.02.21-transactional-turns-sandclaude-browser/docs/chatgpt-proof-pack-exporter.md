# ChatGPT proof pack exporter

The exporter turns a side-panel ChatGPT proof capture, or the offline proof rehearsal bundle, into the canonical 30-slot evidence-pack layout.

It exists because a single nested JSON blob is hard to review. The live proof needs discrete artifacts for route, composer readback, gated submit, transcript latest readback, turn-pair witness, settled-generation witness, schema validation, bundle audit, evaluator output, and human privacy review.

## Rehearsal export

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-export-pack \
  --input validation/latest/chatgpt-proof-rehearsal.json \
  --pack-dir validation/latest/chatgpt-proof-rehearsal-evidence-pack \
  --summary-out validation/latest/chatgpt-proof-pack-export-summary.json \
  --clean \
  --pretty
```

A rehearsal export should return:

```text
exported-rehearsal-evidence-pack-not-live
```

and the embedded evaluator should still return:

```text
rehearsal-harness-ok-not-live
```

That is deliberate. The dry-run pack proves the pack/export/ledger/schema/audit/evaluator wiring, but it is not a live ChatGPT proof.

## Live export later

After a real side-panel attempt, save the assembled side-panel JSON as:

```text
<downloaded-sidepanel-proof.json>
```

Then run:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-export-pack \
  --input <downloaded-sidepanel-proof.json> \
  --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack \
  --summary-out validation/latest/chatgpt-proof-pack-export-summary.json \
  --clean \
  --pretty
```

Do not use a placeholder screenshot for live proof review. Live publication still requires human privacy/redaction review.

## Safety rules

- Rehearsal exports may create a generated placeholder PNG for slot 2.
- Live exports should use a real local screenshot, not a generated placeholder.
- The exporter never widens support claims.
- A pack is not public-citable unless the live evaluator, ledger, schema validation, bundle audit, and privacy review all pass.


## Follow-up check

After every export, run `glassttyd proof-check-pack`. For live proof review, use `--require-live` so rehearsal placeholders and non-live evaluator verdicts are blocked.
