# Turn-start procedure

Revision: rev0005.

Default first command after extracting a future cube:

```bash
make turn-start
```

This runs the smoke tier, writes a timing sample, and records the process-start
policy. It is deliberately cheaper than `make lint`.

## What not to start immediately

Do not start a browser, server, watch process, or daemon just because a turn
began. Those processes may be valuable inside a selected test command, but they
must not be required to survive a later assistant response.

## What to start when a slice needs it

- Browser slice: start local HTTP server and Chromium/CDP inside that command.
- GPU slice: start browser capability command and capture adapter/device report.
- Storage slice: create isolated OPFS namespace and cleanup marker inside the
  command.
- Stress slice: dry-run the plan, shard it, then execute the shard.

## Useful planning commands

```bash
node tools/run_tests.mjs --list --tier release
node tools/plan_tests.mjs --changed src/browserrt.mjs --tier release
node tools/plan_tests.mjs --changed src/browserrt.mjs 
node tools/run_tests.mjs --tier release --changed src/browserrt.mjs 
```
