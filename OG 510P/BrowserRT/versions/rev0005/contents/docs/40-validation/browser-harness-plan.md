# Browser harness plan

Revision: rev0005.

BrowserRT will eventually need real browser tests for Worker, SharedArrayBuffer,
OPFS, WebGPU, OffscreenCanvas, media, and cross-tab primitives. Rev0005 does not
add those tests yet. It adds the rules they must follow.

## First browser slice shape

A future `browser:boot-cdp` task should:

1. start a local HTTP server;
2. start Chromium in the same command;
3. attach through CDP;
4. load one local page;
5. read a boot report;
6. capture console and failure artifacts;
7. shut everything down;
8. write a JSON report.

## Why this comes before OPFS/SAB/WebGPU tests

OPFS, SAB, and WebGPU tests all depend on correct browser setup. A browser boot
probe prevents every later capability test from rediscovering the same launch and
policy failures.

## Non-claim

A cloudtainer browser proof can validate integration and correctness paths. It is
not a real hardware performance claim.
