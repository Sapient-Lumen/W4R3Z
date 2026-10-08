# ChatGPT proof privacy review

`proof-privacy-review` turns the old placeholder `privacy-redaction-review.md` slot into a structured local review artifact.

It is intentionally conservative: it can mark an offline rehearsal as wired, but it cannot mark a live pack publishable unless a human reviewer explicitly attests that the screenshot and proof artifacts were reviewed.

## Rehearsal check

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-privacy-review \
  --pack-dir validation/latest/chatgpt-proof-rehearsal-evidence-pack \
  --pretty
```

Expected rehearsal verdict:

```text
privacy-review-rehearsal-not-live
```

## Live privacy pass

Only run the pass form after `proof-ingest` and `proof-finalize-pack --require-live` have produced a live pack.

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-privacy-review \
  --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack \
  --require-live \
  --require-pass \
  --reviewer "<name>" \
  --decision pass \
  --attest-screenshot-reviewed \
  --attest-no-unrelated-content \
  --attest-local-only \
  --pretty
```

That writes both:

```text
privacy-redaction-review.md
privacy-redaction-review.json
```

The JSON sidecar is optional for the canonical 30-slot ledger, but the pack checker and finalizer now read it when present.

## What it checks

The review checks that the pack has a manifest, evaluator output, a readable screenshot, exact checkpoint prompt artifacts, and no obvious high-risk strings such as email addresses, cookie/authorization keywords, or stray embedded data URLs in JSON/text artifacts.

The scanner is not a substitute for human review. It is a guardrail so the operator cannot accidentally treat the placeholder markdown as a completed privacy decision.
