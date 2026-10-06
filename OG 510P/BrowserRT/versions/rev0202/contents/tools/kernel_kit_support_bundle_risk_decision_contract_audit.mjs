#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-support-bundle-risk-decision-audit. Contract audit for support-bundle retry/verify/stop routing.
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runProbe as runRiskDecisionProbe } from './kernel_kit_support_bundle_risk_decision_probe.mjs';

const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-KERNEL-KIT-SUPPORT-BUNDLE-RISK-DECISION-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

async function readText(path) {
  try { return await readFile(path, 'utf8'); }
  catch { return ''; }
}

function includesAll(text, needles) {
  return needles.filter((needle) => !text.includes(needle));
}

function parseJson(text) {
  try { return JSON.parse(text); }
  catch { return null; }
}

function jsonIncludes(obj, needle) {
  return JSON.stringify(obj || {}).includes(needle);
}

function manifestHasTask(manifestJson, taskId, sourcePath) {
  const tasks = Array.isArray(manifestJson?.tasks) ? manifestJson.tasks : [];
  return tasks.some((task) => task?.id === taskId && (!sourcePath || JSON.stringify(task).includes(sourcePath)));
}

function referenceTextOrJsonIncludes(text, obj, needle) {
  return text.includes(needle) || jsonIncludes(obj, needle);
}

export async function runAudit() {
  const [source, probeSource, demoRunner, manifest, packageJson, makefile, readme, startHere, contextPack, forwardDoc, researchDoc, surfaceInventory, impactMap] = await Promise.all([
    readText('src/kernel-kit-demo.mjs'),
    readText('tools/kernel_kit_support_bundle_risk_decision_probe.mjs'),
    readText('demo/kernel-kit-demo-runner.mjs'),
    readText('test/manifest.json'),
    readText('package.json'),
    readText('Makefile'),
    readText('README.md'),
    readText('START_HERE.md'),
    readText('CONTEXT-PACK.md'),
    readText('docs/00-meta/cloudtainer-forward-momentum-rev0160-2026-07-07-operator-replay-dom-fields.md'),
    readText('artifacts/research/REV0125-BROWSER-RUNTIME-SOURCE-CHECK-REV0160.json'),
    readText('test/surface-inventory.json'),
    readText('test/impact-map.json')
  ]);
  const probe = await runRiskDecisionProbe();
  const manifestJson = parseJson(manifest);
  const impactMapJson = parseJson(impactMap);
  const surfaceInventoryJson = parseJson(surfaceInventory);
  const checks = [];
  const check = (name, passed, detail = {}) => checks.push({ name, passed: passed === true, detail });

  const sourceNeedles = [
    'classifyKernelKitSupportBundleRiskDecision',
    'KERNEL_KIT_SUPPORT_BUNDLE_RISK_DECISION_FORMAT',
    'browserrt-kernel-kit-support-bundle-risk-decision-v1',
    'browserrt-kernel-kit-support-bundle-retry-authority-v1',
    'browserrt-kernel-kit-support-bundle-operator-preflight-v1',
    'browserrt-kernel-kit-support-bundle-operator-preflight-display-snapshot-v1',
    'browserrt-kernel-kit-support-bundle-operator-replay-gate-v1',
    'createKernelKitSupportBundleOperatorPreflight',
    'validateKernelKitSupportBundleOperatorPreflight',
    'createKernelKitSupportBundleOperatorPreflightDisplaySnapshot',
    'validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot',
    'createKernelKitSupportBundleOperatorReplayGate',
    'validateKernelKitSupportBundleOperatorReplayGate',
    'KERNEL_KIT_SUPPORT_BUNDLE_RISK_DECISION_MAX_EVIDENCE_AGE_MS',
    'riskDecisionEvidenceState',
    'No automatic support-bundle retry/repair claim.',
    'BRT_STORAGE_FAILURE_UNCLASSIFIED',
    'decisionRowsPresent',
    'automaticRetryLimitedToPreMutationRows',
    'mutationRowsRequireVerifyFirst',
    'serviceWorkerWaitUntilDecisionVerifyFirst',
    'stopManualReviewRowsClassified',
    'waitUntil-settlement-reviewed',
    'stale-or-expired-evidence',
    'missing-required-evidence',
    'missing-required-evidence-marker',
    'automaticRetryRequiresMarkerCoverage',
    'retryAuthorityRowsGateAutomaticRetry',
    'retryButtonHiddenUntilMarkersCovered',
    'missingMarkersVisibleBeforeRetryButton',
    'preRetryChecklist',
    'retryButtonState',
    'operatorPreflightReady',
    'visibleRowsMatchMissingMarkers',
    'missingMarkersRenderedBeforeRetry',
    'hiddenRetryRowsHaveHiddenLabel',
    'verifyFirstAndStopRowsHideRetry',
    'operatorReplayGateReady',
    'rowCountBound',
    'rowDisplayBound',
    'rowIdentityBound',
    'hiddenRowsRemainHidden',
    'retryVisibleOnlyWhenMarkerCovered',
    'verifyAndStopNeverVisible',
    'missingMarkersVisibleForHiddenRetry',
    'noRawSensitiveDisplayTokens',
    'renderableRowsCarryCanonicalDisplayFields',
    'displayRetryControlText',
    'expectedMissingEvidenceText',
    'retry',
    'verify-first',
    'stop/manual-review'
  ];
  check('source-exports-risk-decision-contract', includesAll(source, sourceNeedles).length === 0, { missing: includesAll(source, sourceNeedles) });

  const probeNeedles = [
    'demo:kernel-kit-support-bundle-risk-decision-proof',
    'retryOnlyPreMutationNoProviderMutation',
    'mutationRowsNeverAutoRetry',
    'serviceWorkerWaitUntilVerifiesSettlement',
    'unclassifiedEvidenceStops',
    'directClassifierCoversThreeOutcomes',
    'staleEvidenceNeverAutoRetries',
    'incompleteEvidenceNeverAutoRetries',
    'missingMarkersNeverAuthorizeRetry',
    'retryAuthorizationRequiresMarkerCoverage',
    'evidenceStateVisible',
    'operatorPreflightReady',
    'retryButtonHiddenUntilMarkersCovered',
    'missingMarkersVisibleBeforeRetryButton',
    'verifyFirstRowsHideRetryButton',
    'stopRowsHideRetryButton',
    'replayPreflightCarriesEvidenceState',
    'operatorDisplaySnapshotReady',
    'visibleRowsMatchMissingMarkers',
    'hiddenRetryRowsCarryVisibleText',
    'missingMarkerDisplayShowsExactMarkers',
    'displaySnapshotBlocksVerifyAndStopRetry',
    'replayPlanCarriesDisplaySnapshot',
    'operatorReplayGateReady',
    'operatorReplayGateBindsRows',
    'operatorReplayGateHidesBlockedRows',
    'operatorReplayGateNoRawDisplayTokens',
    'operatorReplayGateRenderableFieldsBound'
  ];
  check('probe-covers-runtime-risk-outcomes', includesAll(probeSource, probeNeedles).length === 0, { missing: includesAll(probeSource, probeNeedles) });

  check('probe-passed', probe.status === 'passed' && probe.proof?.retryOnlyPreMutationNoProviderMutation === true && probe.proof?.mutationRowsNeverAutoRetry === true && probe.proof?.unclassifiedEvidenceStops === true && probe.proof?.staleEvidenceNeverAutoRetries === true && probe.proof?.incompleteEvidenceNeverAutoRetries === true && probe.proof?.missingMarkersNeverAuthorizeRetry === true && probe.proof?.retryAuthorizationRequiresMarkerCoverage === true && probe.proof?.evidenceStateVisible === true && probe.proof?.operatorPreflightReady === true && probe.proof?.retryButtonHiddenUntilMarkersCovered === true && probe.proof?.missingMarkersVisibleBeforeRetryButton === true && probe.proof?.verifyFirstRowsHideRetryButton === true && probe.proof?.stopRowsHideRetryButton === true && probe.proof?.replayPreflightCarriesEvidenceState === true && probe.proof?.operatorDisplaySnapshotReady === true && probe.proof?.visibleRowsMatchMissingMarkers === true && probe.proof?.hiddenRetryRowsCarryVisibleText === true && probe.proof?.missingMarkerDisplayShowsExactMarkers === true && probe.proof?.displaySnapshotBlocksVerifyAndStopRetry === true && probe.proof?.replayPlanCarriesDisplaySnapshot === true && probe.proof?.operatorReplayGateReady === true && probe.proof?.operatorReplayGateBindsRows === true && probe.proof?.operatorReplayGateHidesBlockedRows === true && probe.proof?.operatorReplayGateNoRawDisplayTokens === true && probe.proof?.operatorReplayGateRenderableFieldsBound === true, { probe_id: probe.probe_id });
  check('three-outcome-router-present', ['retry','verify-first','stop/manual-review'].every((decision) => probe.decisionSet?.includes(decision)), { decisionSet: probe.decisionSet });
  check('service-worker-waituntil-not-auto-retry', probe.decisions?.BRT_SW_WAITUNTIL_LATE_FAILURE?.decision === 'verify-first' && probe.decisions?.BRT_SW_WAITUNTIL_LATE_FAILURE?.automaticRetryAllowed === false, probe.decisions?.BRT_SW_WAITUNTIL_LATE_FAILURE || {});
  check('unknown-or-ambiguous-stops', probe.decisions?.BRT_STORAGE_FAILURE_UNCLASSIFIED?.decision === 'stop/manual-review' && probe.decisions?.BRT_STORAGE_FAILURE_UNCLASSIFIED?.manualReviewRequired === true, probe.decisions?.BRT_STORAGE_FAILURE_UNCLASSIFIED || {});

  const demoRunnerNeedles = [
    'createKernelKitSupportBundleOperatorReplayGate',
    'data-support-bundle-operator-replay-gate-status',
    'data-support-bundle-operator-replay-gate-table',
    '__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_REPLAY_GATE',
    'rowBindings',
    'retryControlVisible',
    'displayRetryControlText',
    'expectedMissingEvidenceText',
    'Operator replay gate proof'
  ];
  check('demo-runner-renders-operator-replay-gate', includesAll(demoRunner, demoRunnerNeedles).length === 0, { missing: includesAll(demoRunner, demoRunnerNeedles) });
  check('demo-runner-uses-canonical-replay-gate-fields', demoRunner.includes('row.displayRetryControlText') && demoRunner.includes('row.expectedMissingEvidenceText') && !demoRunner.includes('row.displayRetryText') && !demoRunner.includes('row.expectedMissingText'), { staleFieldsPresent: ['row.displayRetryText','row.expectedMissingText'].filter((needle) => demoRunner.includes(needle)) });

  const taskIds = ['demo:kernel-kit-support-bundle-risk-decision-proof', 'facility:kernel-kit-support-bundle-risk-decision-audit'];
  for (const taskId of taskIds) {
    const sourcePath = `tools/kernel_kit_support_bundle_${taskId.includes('audit') ? 'risk_decision_contract_audit' : 'risk_decision_probe'}.mjs`;
    check(`manifest-has-${taskId}`, manifestHasTask(manifestJson, taskId, sourcePath) || (manifest.includes(taskId) && manifest.includes(sourcePath)), { sourcePath });
    check(`explicit-script-or-makefile-has-${taskId}`, (packageJson.includes(`--id ${taskId}`) || makefile.includes(`--id ${taskId}`)) && (packageJson + makefile).includes(taskId));
    check(`impact-map-has-${taskId}`, referenceTextOrJsonIncludes(impactMap, impactMapJson, taskId));
    check(`surface-inventory-has-${taskId}`, referenceTextOrJsonIncludes(surfaceInventory, surfaceInventoryJson, taskId));
  }

  const firstReadNeedles = ['rev0160', 'operator replay gate', 'operator display snapshot', 'support-bundle operator preflight', 'retry/verify/stop', 'rowDisplayBound', 'rowIdentityBound', 'hiddenRowsRemainHidden', 'missingMarkersVisibleForHiddenRetry', 'operatorReplayGateReady', 'renderableRowsCarryCanonicalDisplayFields', 'displayRetryControlText', 'expectedMissingEvidenceText', 'missing-required-evidence-marker', 'retryButtonHiddenUntilMarkersCovered', 'missingMarkersVisibleBeforeRetryButton', 'BRT_SW_WAITUNTIL_LATE_FAILURE', 'BRT_STORAGE_FAILURE_UNCLASSIFIED'];
  check('first-read-docs-expose-decision-lane', [readme, startHere, contextPack, forwardDoc].every((text) => includesAll(text, firstReadNeedles).length === 0), { missingByDoc: { README: includesAll(readme, firstReadNeedles), START_HERE: includesAll(startHere, firstReadNeedles), CONTEXT: includesAll(contextPack, firstReadNeedles), forwardDoc: includesAll(forwardDoc, firstReadNeedles) } });
  check('online-source-check-recorded', includesAll(researchDoc, ['MDN', 'Web Locks', 'waitUntil', 'OPFS', 'persistent storage', 'rev0160']).length === 0, { missing: includesAll(researchDoc, ['MDN', 'Web Locks', 'waitUntil', 'OPFS', 'persistent storage', 'rev0160']) });
  check('forward-doc-brief-enough', forwardDoc.length > 400 && forwardDoc.length < 4200, { bytes: forwardDoc.length });
  check('audit-is-contract-not-registry', !forwardDoc.includes('| Owner |') && !forwardDoc.includes('registry'), { forwardDocBytes: forwardDoc.length });

  const failed = checks.filter((row) => !row.passed);
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    linkedRevision: 'rev0160',
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-support-bundle-risk-decision-contract-audit`,
    status: failed.length ? 'failed' : 'passed',
    summary: failed.length ? `${failed.length} support-bundle risk decision contract check(s) failed` : 'support-bundle risk decision contract checks passed',
    checks,
    proof: {
      probePassed: probe.status === 'passed',
      staleEvidenceNeverAutoRetries: probe.proof?.staleEvidenceNeverAutoRetries === true,
      incompleteEvidenceNeverAutoRetries: probe.proof?.incompleteEvidenceNeverAutoRetries === true,
      missingMarkersNeverAuthorizeRetry: probe.proof?.missingMarkersNeverAuthorizeRetry === true,
      retryAuthorizationRequiresMarkerCoverage: probe.proof?.retryAuthorizationRequiresMarkerCoverage === true,
      evidenceStateVisible: probe.proof?.evidenceStateVisible === true,
      retryOnlyPreMutationNoProviderMutation: probe.proof?.retryOnlyPreMutationNoProviderMutation === true,
      mutationRowsNeverAutoRetry: probe.proof?.mutationRowsNeverAutoRetry === true,
      serviceWorkerWaitUntilVerifiesSettlement: probe.proof?.serviceWorkerWaitUntilVerifiesSettlement === true,
      unknownOrAmbiguousStops: probe.proof?.unclassifiedEvidenceStops === true,
      explicitTasksCovered: taskIds.every((taskId) => manifest.includes(taskId) && (packageJson + makefile).includes(`--id ${taskId}`)),
      firstReadDocsExposeRiskLane: [readme, startHere, contextPack, forwardDoc].every((text) => includesAll(text, firstReadNeedles).length === 0),
      sourceCheckRecorded: researchDoc.includes('rev0160'),
      operatorDisplaySnapshotReady: probe.proof?.operatorDisplaySnapshotReady === true,
      visibleRowsMatchMissingMarkers: probe.proof?.visibleRowsMatchMissingMarkers === true,
      hiddenRetryRowsCarryVisibleText: probe.proof?.hiddenRetryRowsCarryVisibleText === true,
      missingMarkerDisplayShowsExactMarkers: probe.proof?.missingMarkerDisplayShowsExactMarkers === true,
      displaySnapshotBlocksVerifyAndStopRetry: probe.proof?.displaySnapshotBlocksVerifyAndStopRetry === true,
      replayPlanCarriesDisplaySnapshot: probe.proof?.replayPlanCarriesDisplaySnapshot === true,
      operatorReplayGateReady: probe.proof?.operatorReplayGateReady === true,
      operatorReplayGateBindsRows: probe.proof?.operatorReplayGateBindsRows === true,
      operatorReplayGateHidesBlockedRows: probe.proof?.operatorReplayGateHidesBlockedRows === true,
      operatorReplayGateNoRawDisplayTokens: probe.proof?.operatorReplayGateNoRawDisplayTokens === true,
      operatorReplayGateRenderableFieldsBound: probe.proof?.operatorReplayGateRenderableFieldsBound === true,
      demoRunnerRendersOperatorReplayGate: includesAll(demoRunner, ['createKernelKitSupportBundleOperatorReplayGate', 'data-support-bundle-operator-replay-gate-status', '__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_REPLAY_GATE']).length === 0,
      demoRunnerCanonicalReplayGateFields: demoRunner.includes('row.displayRetryControlText') && demoRunner.includes('row.expectedMissingEvidenceText') && !demoRunner.includes('row.displayRetryText') && !demoRunner.includes('row.expectedMissingText')
    },
    nonClaims: [
      'No automatic support-bundle retry/repair claim.',
      'No Service Worker lifetime guarantee.',
      'No storage quota reservation or eviction-survival claim.',
      'No cross-browser conformance claim.'
    ]
  };
}

const isMain = process.argv[1] && import.meta.url === new URL(process.argv[1], 'file:').href;
if (isMain) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const report = await runAudit();
  if (report.status !== 'passed') {
    console.error(JSON.stringify(report, null, 2));
    process.exitCode = 1;
  }
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } else console.log(JSON.stringify(report, null, 2));
}

// Static audit markers: facility:kernel-kit-support-bundle-risk-decision-audit; demo:kernel-kit-support-bundle-risk-decision-proof; classifyKernelKitSupportBundleRiskDecision; browserrt-kernel-kit-support-bundle-retry-authority-v1; browserrt-kernel-kit-support-bundle-operator-preflight-v1; browserrt-kernel-kit-support-bundle-operator-preflight-display-snapshot-v1; browserrt-kernel-kit-support-bundle-operator-replay-gate-v1; retryButtonHiddenUntilMarkersCovered; missingMarkersVisibleBeforeRetryButton; visibleRowsMatchMissingMarkers; hiddenRetryRowsCarryVisibleText; missingMarkerDisplayShowsExactMarkers; displaySnapshotBlocksVerifyAndStopRetry; operatorReplayGateReady; rowDisplayBound; rowIdentityBound; demo-runner-renders-operator-replay-gate; demo-runner-uses-canonical-replay-gate-fields; renderableRowsCarryCanonicalDisplayFields; displayRetryControlText; expectedMissingEvidenceText; hiddenRowsRemainHidden; missingMarkersVisibleForHiddenRetry; BRT_SW_WAITUNTIL_LATE_FAILURE; BRT_STORAGE_FAILURE_UNCLASSIFIED; retryOnlyPreMutationNoProviderMutation; mutationRowsNeverAutoRetry; serviceWorkerWaitUntilVerifiesSettlement; unclassifiedEvidenceStops; staleEvidenceNeverAutoRetries; incompleteEvidenceNeverAutoRetries; missingMarkersNeverAuthorizeRetry; retryAuthorizationRequiresMarkerCoverage; evidenceStateVisible; explicit --id selection.
