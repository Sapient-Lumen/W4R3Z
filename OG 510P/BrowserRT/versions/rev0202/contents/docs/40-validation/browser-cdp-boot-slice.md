# Browser/CDP boot slice

Revision: rev0028

## Purpose

The first browser slice proves that the cloudtainer can run a managed local browser fixture without pretending that real browser performance has been validated.

It answers one question:

> Can a one-shot test command launch Chromium, serve a local isolated page, attach through CDP, import BrowserRT, observe browser capabilities, emit timing evidence, and clean up?

## Manifest task

Task id:

```txt
browser:cdp-boot-report
```

Command:

```txt
node tools/browser_cdp_boot_probe.mjs --json artifacts/validation/REV0044-BROWSER-CDP-BOOT-PROBE.json
```

The task is in `release`, `browser`, and `full` tiers because future runtime code can easily break browser boot assumptions.

## Fixture lifecycle

The fixture owns the whole lifecycle:

```txt
read/relax managed policy
start local HTTP server
launch Chromium with a temporary user profile
wait for CDP target list
connect to page target
Runtime.evaluate page state
Runtime.evaluate dynamic BrowserRT import
write artifact
close CDP
kill Chromium process group
close server
remove temp profile
restore policy
```

No browser process should remain alive after the command exits.

## Evidence expected

The artifact must include:

- revision and version,
- Chromium executable and target URL,
- local server request log,
- policy relaxation and restoration status,
- page state,
- BrowserRT boot report,
- observed capabilities,
- trace kinds,
- per-phase timings,
- stderr summary,
- non-claims.

## Non-claims

This slice does not prove:

- browser worker-agent correctness,
- OPFS sync access handle correctness,
- SAB ring correctness,
- WebGPU correctness,
- cross-browser conformance,
- mobile or hardware GPU performance,
- page-frame smoothness.

## Future splits

Do not grow this task into a monster. Add separate manifest tasks for:

- browser Worker spawn,
- OPFS async write/read,
- OPFS sync worker handle,
- SAB mailbox,
- WebGPU compute smoke,
- OffscreenCanvas render smoke,
- browser trace collection,
- multi-tab mesh.
