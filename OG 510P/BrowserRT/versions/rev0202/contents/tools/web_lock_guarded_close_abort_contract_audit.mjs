#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-WEB-LOCK-GUARDED-CLOSE-ABORT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

export async function runAudit() {
  const guarded = await readFile('src/opfs-web-lock-guarded-block-store.mjs', 'utf8');
  const coordinator = await readFile('src/web-lock-coordinator.mjs', 'utf8');
  const probe = await readFile('tools/web_lock_guarded_close_abort_probe.mjs', 'utf8');
  const manifest = JSON.parse(await readFile('test/manifest.json', 'utf8'));
  const pkg = JSON.parse(await readFile('package.json', 'utf8'));

  assert.ok(guarded.includes('#closeController'), 'guarded store must own a close AbortController');
  assert.ok(guarded.includes('guardedAbortOptions(options, [this.#closeController?.signal])'), 'lock/provider operation options must include the close-owned signal');
  assert.ok(guarded.includes('async open(options = {})') && guarded.includes('this.store.open(providerOptions)'), 'guarded open must pass close-composed provider options to the underlying store');
  assert.ok(guarded.includes('this.#throwIfClosed(op); return callback(lock'), 'lock callbacks must re-check closed state after acquisition');
  assert.ok(guarded.includes('closeAbortSignals'), 'snapshot/stat surface must expose close-abort signaling');
  assert.ok(guarded.includes('closeSignalAborted'), 'close report/snapshot must expose close signal state');
  assert.ok(coordinator.includes('abortReasonSummary') && coordinator.includes('abortReasonCode'), 'coordinator must retain abort reason provenance for pre-acquisition aborts');
  assert.ok(probe.includes('pendingLockCloseRejectedBeforeAcquisition') && probe.includes('acquiredProviderCloseSignalPropagated') && probe.includes('acquiredOpenCloseSignalPropagated'), 'probe must cover queued, acquired put, and acquired open close-abort paths');
  assert.ok(probe.includes('BRT_OPFS_WEB_LOCK_GUARD_CLOSED') && probe.includes('BRT_WEB_LOCK_ABORTED'), 'probe must assert close-owned abort classification/provenance');

  const ids = new Set((manifest.tasks || []).map((task) => task.id));
  assert.ok(ids.has('storage:web-lock-guarded-close-abort-proof'), 'manifest must register close-abort proof');
  assert.ok(ids.has('facility:web-lock-guarded-close-abort-contract-audit'), 'manifest must register close-abort audit');
  const proofTask = manifest.tasks.find((task) => task.id === 'storage:web-lock-guarded-close-abort-proof');
  const auditTask = manifest.tasks.find((task) => task.id === 'facility:web-lock-guarded-close-abort-contract-audit');
  assert.ok(proofTask.inputs.includes('src/opfs-web-lock-guarded-block-store.mjs'), 'proof must be invalidated by guarded store changes');
  assert.ok(proofTask.inputs.includes('src/web-lock-coordinator.mjs'), 'proof must be invalidated by coordinator abort provenance changes');
  assert.ok(proofTask.outputs.includes(`artifacts/validation/${PFX}-WEB-LOCK-GUARDED-CLOSE-ABORT-PROBE.json`), 'proof must emit current revision validation artifact');
  assert.ok(auditTask.outputs.includes(`artifacts/audit/${PFX}-WEB-LOCK-GUARDED-CLOSE-ABORT-CONTRACT-AUDIT.json`), 'audit must emit current revision artifact');
  assert.ok((pkg.scripts?.['test:web-lock-guarded-close-abort'] || '').includes('web_lock_guarded_close_abort_probe.mjs'), 'package scripts should expose the close-abort proof');
  assert.ok((pkg.scripts?.['audit:web-lock-guarded-close-abort'] || '').includes('web_lock_guarded_close_abort_contract_audit.mjs'), 'package scripts should expose the close-abort audit');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'passed',
    audit_id: `${REVISION}-web-lock-guarded-close-abort-contract-audit`,
    checks: [
      { name: 'guarded-store-close-controller', status: 'passed' },
      { name: 'close-signal-fed-to-lock-and-provider-options', status: 'passed' },
      { name: 'guarded-open-forwards-provider-options', status: 'passed' },
      { name: 'post-acquisition-closed-state-rechecked', status: 'passed' },
      { name: 'coordinator-retains-abort-reason-provenance', status: 'passed' },
      { name: 'queued-acquired-put-and-acquired-open-close-abort-probe-registered', status: 'passed' }
    ],
    nonClaims: ['Static contract audit only; runtime probe supplies behavior evidence. No Web Locks fairness, cross-tab storage reservation, fsync, crash, or eviction-survival claim.']
  });
}
if (import.meta.url === `file://${process.argv[1]}`) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const report = await runAudit();
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
}
