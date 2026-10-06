#!/usr/bin/env node
import { readFile, writeFile, readdir, stat, mkdir } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const LINKED_REVISION = 'rev0160';
const DEFAULT_JSON = `artifacts/audit/${PREFIX}-LINKED-CURRENT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

async function exists(path) { try { await stat(path); return true; } catch { return false; } }
async function readText(path) { return await readFile(path, 'utf8'); }
async function readJson(path) { return JSON.parse(await readText(path)); }
async function walk(dir) {
  const rows = [];
  if (!await exists(dir)) return rows;
  for (const ent of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, ent.name);
    if (ent.isDirectory()) rows.push(...await walk(p));
    else rows.push(p.replace(/\\/g, '/'));
  }
  return rows;
}
function includesAll(text, needles) { return needles.filter((needle) => !text.includes(needle)); }

export async function runAudit({ jsonOut = DEFAULT_JSON } = {}) {
  const checks = [];
  const add = (name, ok, details = {}) => checks.push({ name, status: ok ? 'passed' : 'failed', ...details });
  const requiredFiles = [
    'docs/00-meta/cloudtainer-forward-momentum-rev0160-2026-07-07-operator-replay-dom-fields.md',
    `artifacts/validation/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-RISK-DECISION-PROBE.json`,
    `artifacts/audit/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-RISK-DECISION-CONTRACT-AUDIT.json`,
    `artifacts/datacube-audit/${PREFIX}-SUPPORT-BUNDLE-OPERATOR-REPLAY-DOM-FIELDS-REV0160.json`,
    `artifacts/research/${PREFIX}-BROWSER-RUNTIME-SOURCE-CHECK-REV0160.json`,
    'REV0160-LINKED-REVISION-RECEIPT.json',
    `artifacts/audit/${PREFIX}-ARTIFACT-BUDGET-AUDIT.json`
  ];
  const missingFiles = [];
  for (const file of requiredFiles) if (!await exists(file)) missingFiles.push(file);
  add('linked-revision-required-files-present', missingFiles.length === 0, { linkedRevision: LINKED_REVISION, missingFiles });

  const validationArtifactDocs = (await walk('docs/00-meta')).filter((p) => p.includes('-validation-artifacts/'));
  add('historical-validation-artifact-docs-compacted', validationArtifactDocs.length === 0, { remaining: validationArtifactDocs.slice(0, 12), count: validationArtifactDocs.length });
  const tmpArtifacts = (await walk('artifacts')).filter((p) => /\/TMP-|TMP-|\.tmp\b/i.test(p));
  add('tmp-artifacts-absent', tmpArtifacts.length === 0, { remaining: tmpArtifacts.slice(0, 12), count: tmpArtifacts.length });

  let probe = null, riskAudit = null, budget = null, sourceCheck = null, receipt = null;
  try { probe = await readJson(`artifacts/validation/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-RISK-DECISION-PROBE.json`); } catch {}
  try { riskAudit = await readJson(`artifacts/audit/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-RISK-DECISION-CONTRACT-AUDIT.json`); } catch {}
  try { budget = await readJson(`artifacts/audit/${PREFIX}-ARTIFACT-BUDGET-AUDIT.json`); } catch {}
  try { sourceCheck = await readJson(`artifacts/research/${PREFIX}-BROWSER-RUNTIME-SOURCE-CHECK-REV0160.json`); } catch {}
  try { receipt = await readJson('REV0160-LINKED-REVISION-RECEIPT.json'); } catch {}

  const proof = probe?.proof || {};
  add('operator-replay-dom-field-proof-green', probe?.status === 'passed'
    && proof.operatorDisplaySnapshotReady === true
    && proof.visibleRowsMatchMissingMarkers === true
    && proof.hiddenRetryRowsCarryVisibleText === true
    && proof.missingMarkerDisplayShowsExactMarkers === true
    && proof.displaySnapshotBlocksVerifyAndStopRetry === true
    && proof.operatorReplayGateReady === true
    && proof.operatorReplayGateRenderableFieldsBound === true,
    { status: probe?.status || null, proof: {
      operatorDisplaySnapshotReady: proof.operatorDisplaySnapshotReady === true,
      visibleRowsMatchMissingMarkers: proof.visibleRowsMatchMissingMarkers === true,
      hiddenRetryRowsCarryVisibleText: proof.hiddenRetryRowsCarryVisibleText === true,
      missingMarkerDisplayShowsExactMarkers: proof.missingMarkerDisplayShowsExactMarkers === true,
      displaySnapshotBlocksVerifyAndStopRetry: proof.displaySnapshotBlocksVerifyAndStopRetry === true,
      operatorReplayGateReady: proof.operatorReplayGateReady === true,
      operatorReplayGateRenderableFieldsBound: proof.operatorReplayGateRenderableFieldsBound === true
    } });

  add('support-bundle-risk-audit-linked-to-rev0160', riskAudit?.status === 'passed' && riskAudit?.linkedRevision === LINKED_REVISION, { status: riskAudit?.status || null, linkedRevision: riskAudit?.linkedRevision || null });
  add('browser-runtime-source-check-current-linked', sourceCheck?.status === 'passed' && sourceCheck?.linkedRevision === LINKED_REVISION && (sourceCheck?.keywords || []).includes('rev0160'), { status: sourceCheck?.status || null, linkedRevision: sourceCheck?.linkedRevision || null, keywordCount: sourceCheck?.keywords?.length || 0 });
  add('artifact-budget-green-after-linked-work', budget?.status === 'passed', { status: budget?.status || null, totalBytes: budget?.counts?.totalBytes || null, softTotalBytes: budget?.budgets?.softTotalBytes || null });
  add('linked-receipt-covers-operator-replay-dom-fields', receipt?.status === 'passed' && receipt?.linkedRevision === LINKED_REVISION && JSON.stringify(receipt).includes('operator replay DOM field'), { status: receipt?.status || null, linkedRevision: receipt?.linkedRevision || null });

  const firstReadNeedles = ['rev0160','operator replay gate','operator display snapshot','support-bundle operator preflight','retry/verify/stop','renderableRowsCarryCanonicalDisplayFields','displayRetryControlText','expectedMissingEvidenceText','operatorReplayGateRenderableFieldsBound','missing-required-evidence-marker','retryButtonHiddenUntilMarkersCovered','missingMarkersVisibleBeforeRetryButton'];
  const firstReadMissing = {};
  for (const file of ['README.md','START_HERE.md','CONTEXT-PACK.md','AGENTS.md']) {
    try { firstReadMissing[file] = includesAll(await readText(file), firstReadNeedles); }
    catch { firstReadMissing[file] = firstReadNeedles; }
  }
  add('first-read-docs-expose-linked-product-risk', Object.values(firstReadMissing).every((missing) => missing.length === 0), { missing: firstReadMissing });

  const status = checks.every((check) => check.status === 'passed') ? 'passed' : 'failed';
  const report = {
    project: 'BrowserRT', revision: REVISION, version: VERSION, linkedRevision: LINKED_REVISION, schema: 2, status,
    generatedAt: new Date().toISOString(),
    purpose: 'Linked-current audit for rev0160: prove support-bundle operator replay DOM fields are executable, visible, source-checked, budget-safe, and not a runtime promotion.',
    checks,
    nonClaims: [
      'This linked audit is not a runtime promotion.',
      'It does not claim production readiness, cross-browser behavior, quota reservation, eviction survival, crash recovery, Service Worker lifetime, or Web Lock fairness.',
      'Operator replay DOM field binding proves visible row text and gating only; it does not execute commands, repair storage, or authorize production retry.',
      'browser-light validation remains distinct from managed-browser lifecycle proof.'
    ]
  };
  await mkdir(dirname(jsonOut), { recursive: true });
  await writeFile(jsonOut, JSON.stringify(report, null, 2) + '\n');
  return report;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const jsonOut = argValue(process.argv.slice(2), '--json', DEFAULT_JSON);
  const report = await runAudit({ jsonOut });
  console.log(jsonOut);
  if (report.status !== 'passed') process.exitCode = 1;
}
