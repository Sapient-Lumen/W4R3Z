# ChatGPT proof publish verify

`proof-publish-verify` is the post-transfer integrity gate for a ChatGPT proof support bundle.

It is intentionally separate from `proof-publish-bundle`:

1. `proof-publish-bundle` creates the support zip only from a live, privacy-reviewed pack.
2. `proof-publish-verify` proves that a zip still contains the expected evidence pack, that each manifest-listed file still matches its recorded size/hash, and that the extracted pack still passes the live/privacy pack gate.

## Live use

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-publish-verify \
  --bundle validation/latest/chatgpt-proof-publish-bundle.zip \
  --expected-sha256 <sha256-from-handoff-or-transfer> \
  --pretty
```

A passing result returns:

```text
proof-publish-verify-ok
```

A blocked result returns:

```text
proof-publish-verify-blocked
```

Do not share a bundle as support/proof evidence unless this command passes.

## What it checks

- the zip exists and is readable,
- no zip entry uses an absolute path or `..` traversal,
- the zip contains `chatgpt-proof-evidence-pack/`,
- `publish-bundle-manifest.json` exists and parses,
- every manifest-listed file exists and matches its byte count and SHA-256,
- the extracted pack passes `proof-check-pack --require-live --require-privacy-pass`,
- optional `--expected-sha256` matches the zip bytes.

## Diagnostic mode

For local debugging only:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-publish-verify \
  --bundle validation/latest/chatgpt-proof-publish-bundle.zip \
  --no-require-live \
  --no-require-privacy-pass \
  --pretty
```

This is not a publication gate. It is only useful for inspecting malformed or partial zips.
