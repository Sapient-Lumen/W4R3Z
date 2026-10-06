#!/usr/bin/env node
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-WEB-LOCK-TIMEOUT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

const files = {
  coordinator: await text('src/web-lock-coordinator.mjs'),
  guarded: await text('src/opfs-web-lock-guarded-block-store.mjs'),
  releaseProbe: await text('tools/web_lock_timeout_probe.mjs'),
  browserProbe: await text('tools/browser_opfs_web_lock_timeout_probe.mjs'),
  doc: await text('docs/40-validation/browser-opfs-web-lock-timeout-slice.md'),
  manifest: await text('test/manifest.json'),
  impact: await text('test/impact-map.json'),
  inventory: await text('test/surface-inventory.json')
};

const checks = [
  check('coordinator-timeout-classification', missing(files.coordinator, ['BRT_WEB_LOCK_TIMEOUT', 'coord:web-lock-timeout-arm', 'coord:web-lock-timeout-fired', 'coord:web-lock-timeout', 'timeoutMs']).length === 0, { missing: missing(files.coordinator, ['BRT_WEB_LOCK_TIMEOUT', 'coord:web-lock-timeout-arm', 'coord:web-lock-timeout-fired', 'coord:web-lock-timeout', 'timeoutMs']) }),
  check('coordinator-abort-classification', missing(files.coordinator, ['BRT_WEB_LOCK_ABORTED', 'AbortController', 'signal']).length === 0, { missing: missing(files.coordinator, ['BRT_WEB_LOCK_ABORTED', 'AbortController', 'signal']) }),
  check('guarded-store-timeout-plumbing', missing(files.guarded, ['lockTimeoutMs', 'timeoutMs', 'storage:opfs-web-lock-guard-op-error']).length === 0, { missing: missing(files.guarded, ['lockTimeoutMs', 'timeoutMs', 'storage:opfs-web-lock-guard-op-error']) }),
  check('release-timeout-proof-present', missing(files.releaseProbe, ['FakeWebLocksWithAbort', 'BRT_WEB_LOCK_TIMEOUT', 'timeoutPresent', 'recoveryVerify']).length === 0, { missing: missing(files.releaseProbe, ['FakeWebLocksWithAbort', 'BRT_WEB_LOCK_TIMEOUT', 'timeoutPresent', 'recoveryVerify']) }),
  check('browser-timeout-proof-present', missing(files.browserProbe, ['browser:opfs-web-lock-timeout-proof', 'worker', 'BRT_WEB_LOCK_TIMEOUT', 'timeoutPresentAfterRelease', 'recoveryVerify']).length === 0, { missing: missing(files.browserProbe, ['browser:opfs-web-lock-timeout-proof', 'worker', 'BRT_WEB_LOCK_TIMEOUT', 'timeoutPresentAfterRelease', 'recoveryVerify']) }),
  check('doc-nonclaims-present', missing(files.doc, ['BRT_WEB_LOCK_TIMEOUT', 'AbortSignal', 'acquisition', 'does not cancel work after a lock has already been granted', 'cross-browser', 'OPFS durability']).length === 0, { missing: missing(files.doc, ['BRT_WEB_LOCK_TIMEOUT', 'AbortSignal', 'acquisition', 'does not cancel work after a lock has already been granted', 'cross-browser', 'OPFS durability']) }),
  check('manifest-wired', missing(files.manifest, ['coord:web-lock-timeout-proof', 'browser:opfs-web-lock-timeout-proof', 'facility:web-lock-timeout-contract-audit']).length === 0, { missing: missing(files.manifest, ['coord:web-lock-timeout-proof', 'browser:opfs-web-lock-timeout-proof', 'facility:web-lock-timeout-contract-audit']) }),
  check('impact-inventory-wired', missing(files.impact + files.inventory, ['impact:opfs-web-lock-timeout', 'surface:browser-opfs-web-lock-timeout']).length === 0, { missing: missing(files.impact + files.inventory, ['impact:opfs-web-lock-timeout', 'surface:browser-opfs-web-lock-timeout']) })
];
const status = checks.every((row) => row.status === 'passed') ? 'passed' : 'failed';
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  probe_id: `${REVISION}-web-lock-timeout-contract-audit`, status, generatedAt: new Date().toISOString(),
  purpose: 'Contract audit for rev0062 Web Lock timeout work: runtime code, guarded-store wrapper, release/browser proofs, docs, manifest, impact map, and surface inventory must all carry the bounded-wait timeout semantics and non-claims.',
  checks,
  nonClaims: [
    'Static/source audit only; it does not replace the release fake-lock timeout proof or the managed Chromium OPFS/Web Locks timeout proof.',
    'This audit does not prove cross-browser behavior, fairness, background lifecycle, or OPFS durability.'
  ]
};
const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
else console.log(JSON.stringify(report, null, 2));
if (status !== 'passed') process.exitCode = 1;
