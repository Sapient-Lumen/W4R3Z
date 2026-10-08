# ChatGPT proof pack integrity

`proof-pack-integrity` makes a finalized evidence pack self-auditing. It is intentionally separate from the publish-bundle verifier: this command protects the directory of evidence artifacts before it becomes a zip, while `proof-publish-verify` protects the transferred support zip.

## Why it exists

The evidence pack contains mutable review artifacts. In particular, `privacy-redaction-review.md` can be rewritten after the exporter first creates `artifact-ledger.json`. That can leave a ledger row with an old SHA-256 even though the pack otherwise looks complete.

`proof-pack-integrity` catches that class of bug. It can refresh `artifact-ledger.json`, inventory every pack file, and write `evidence-pack-integrity.json` into the pack.

## Rehearsal/default use

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-pack-integrity \
  --pack-dir validation/latest/chatgpt-proof-rehearsal-evidence-pack \
  --refresh-ledger \
  --write-pack-file \
  --require-existing-match \
  --require-ok \
  --pretty
```

## Live use

Run this after finalization and after the human privacy review step has written its final files:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-pack-integrity \
  --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack \
  --refresh-ledger \
  --write-pack-file \
  --require-existing-match \
  --require-ok \
  --pretty
```

A passing verdict is:

```text
proof-pack-integrity-ok
```

## What it checks

- all canonical 30 artifact slots are present
- `artifact-ledger.json` exists and parses
- ledger slot rows match current file byte counts and SHA-256 values
- existing `evidence-pack-integrity.json`, when required, matches current pack bytes
- the pack inventory is non-empty

The integrity file excludes itself from the hash inventory so it is not self-referential.
