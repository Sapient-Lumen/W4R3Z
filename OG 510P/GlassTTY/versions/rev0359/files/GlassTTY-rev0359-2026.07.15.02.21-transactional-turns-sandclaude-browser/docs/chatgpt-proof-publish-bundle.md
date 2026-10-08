# ChatGPT proof publish bundle

`proof-publish-bundle` is the final support/publication guard. It does not create a zip unless the evidence pack already passes the strict live and privacy gates.

Default live command:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-publish-bundle \
  --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack \
  --out validation/latest/chatgpt-proof-publish-bundle.zip \
  --pretty
```

The command runs the same safety check as:

```bash
glassttyd proof-check-pack --require-live --require-privacy-pass
```

It blocks rehearsal packs, placeholder screenshots, missing live evaluator verdicts, and missing `privacy-review-pass` attestations. When blocked, it writes `validation/latest/chatgpt-proof-publish-summary.json` with the exact blockers and creates no publish zip.

A ready live bundle gets:

```text
proof-publish-bundle-ready
```

and the output zip contains the evidence pack plus a `publish-bundle-manifest.json` and `PUBLISH-README.md`.

Do not use `--no-require-live` or `--no-require-privacy-pass` for support/publication. Those flags exist only for diagnostics.
