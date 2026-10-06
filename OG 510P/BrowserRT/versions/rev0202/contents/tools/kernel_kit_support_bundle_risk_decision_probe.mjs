#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-support-bundle-risk-decision-proof. Release-tier proof for support-bundle retry/verify/stop routing.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import {
  classifyKernelKitSupportBundleRiskDecision,
  createKernelKitSupportBundleReplayPlan,
  createKernelKitSupportBundleOperatorPreflight,
  validateKernelKitSupportBundleOperatorPreflight,
  createKernelKitSupportBundleOperatorPreflightDisplaySnapshot,
  validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot,
  createKernelKitSupportBundleOperatorReplayGate,
  validateKernelKitSupportBundleOperatorReplayGate,
  KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_PREFLIGHT_FORMAT,
  KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_PREFLIGHT_DISPLAY_SNAPSHOT_FORMAT,
  KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_REPLAY_GATE_FORMAT,
  KERNEL_KIT_SUPPORT_BUNDLE_RISK_DECISION_FORMAT,
  KERNEL_KIT_SUPPORT_BUNDLE_RISK_DECISION_NON_CLAIM
} from '../src/kernel-kit-demo.mjs';
import { runProbe as runSupportBundleProbe } from './kernel_kit_support_bundle_probe.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-SUPPORT-BUNDLE-RISK-DECISION-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const unique = (values) => Array.from(new Set(values));

function decisionByCode(rows) {
  return Object.fromEntries(rows.map((row) => [row.code, row]));
}

export async function runProbe() {
  const supportReport = await runSupportBundleProbe();
  const guidance = supportReport.supportBundle.storageRecoveryGuidance;
  const rows = Array.isArray(guidance?.rows) ? guidance.rows : [];
  const byCode = decisionByCode(rows);

  const requiredRows = {
    BRT_BROWSER_STORAGE_ADMISSION_REJECTED: 'retry',
    BRT_WEB_LOCK_TIMEOUT: 'retry',
    BRT_OPFS_QUOTA_EXCEEDED: 'verify-first',
    BRT_OPFS_OPERATION_ABORTED: 'verify-first',
    BRT_SW_WAITUNTIL_LATE_FAILURE: 'verify-first',
    BRT_STORAGE_FAILURE_UNCLASSIFIED: 'stop/manual-review'
  };

  for (const [code, decision] of Object.entries(requiredRows)) {
    assert.equal(byCode[code]?.decision, decision, `${code} must route to ${decision}`);
    assert.ok(Array.isArray(byCode[code]?.requiredEvidence) && byCode[code].requiredEvidence.length > 0, `${code} must list required evidence`);
  }

  const admissionRetryMarkers = ['no-provider-grant-no-mutation-receipt-no-quarantine-row', 'fresh-storage-posture-or-user/product-storage-policy', 'stable-operation-id-or-human-review'];
  const lockRetryMarkers = ['no-provider-grant-no-mutation-receipt-no-quarantine-row', 'same-origin-Web-Lock-drained-or-query-reviewed', 'stable-operation-id-or-human-review'];
  const directCases = [
    { code: 'BRT_BROWSER_STORAGE_ADMISSION_REJECTED', expected: 'retry', expectedAutomaticRetryAllowed: true, evidenceMarkers: admissionRetryMarkers, detail: { phase: 'admission', op: 'put' } },
    { code: 'BRT_WEB_LOCK_TIMEOUT', expected: 'retry', expectedAutomaticRetryAllowed: true, evidenceMarkers: lockRetryMarkers, detail: { lock: { name: 'browserrt-lane', timeoutMs: 50 }, op: 'put' } },
    { code: 'BRT_BROWSER_STORAGE_ADMISSION_REJECTED', expected: 'retry', expectedAutomaticRetryAllowed: false, detail: { phase: 'admission', op: 'put' } },
    { code: 'BRT_OPFS_QUOTA_EXCEEDED', expected: 'verify-first', expectedAutomaticRetryAllowed: false, detail: { requestedBytes: 4096, op: 'put' } },
    { code: 'BRT_OPFS_OPERATION_ABORTED', expected: 'verify-first', expectedAutomaticRetryAllowed: false, detail: { abortPhase: 'provider', op: 'put' } },
    { code: 'BRT_SW_WAITUNTIL_LATE_FAILURE', expected: 'verify-first', expectedAutomaticRetryAllowed: false, detail: { event: 'fetch', waitUntilRejected: true, op: 'put' } },
    { code: 'BRT_STORAGE_FAILURE_UNCLASSIFIED', expected: 'stop/manual-review', expectedAutomaticRetryAllowed: false, ambiguous: true, evidenceComplete: false, detail: { op: 'put' } },
    { code: 'BRT_BROWSER_STORAGE_ADMISSION_REJECTED', expected: 'stop/manual-review', expectedAutomaticRetryAllowed: false, staleEvidence: true, evidenceAgeMs: 600000, maxEvidenceAgeMs: 30000, evidenceMarkers: admissionRetryMarkers, detail: { phase: 'admission', op: 'put' } },
    { code: 'BRT_WEB_LOCK_TIMEOUT', expected: 'stop/manual-review', expectedAutomaticRetryAllowed: false, contradictory: true, evidenceMarkers: lockRetryMarkers, detail: { lock: { name: 'browserrt-lane', timeoutMs: 50 }, op: 'put' } },
    { code: 'BRT_SW_WAITUNTIL_LATE_FAILURE', expected: 'stop/manual-review', expectedAutomaticRetryAllowed: false, evidenceComplete: false, detail: { event: 'fetch', waitUntilRejected: true, op: 'put' } }
  ].map((input) => {
    const decision = classifyKernelKitSupportBundleRiskDecision(input);
    assert.equal(decision.format, KERNEL_KIT_SUPPORT_BUNDLE_RISK_DECISION_FORMAT);
    assert.equal(decision.decision, input.expected, `direct ${input.code} must route to ${input.expected}`);
    assert.equal(decision.automaticRetryAllowed, input.expectedAutomaticRetryAllowed, `direct ${input.code} automatic retry authority must be ${input.expectedAutomaticRetryAllowed}`);
    assert.equal(decision.proof.nonClaimVisible, true);
    return {
      code: input.code,
      expected: input.expected,
      decision: decision.decision,
      automaticRetryAllowed: decision.automaticRetryAllowed,
      retryAuthority: decision.retryAuthority,
      verificationRequired: decision.verificationRequired,
      manualReviewRequired: decision.manualReviewRequired,
      reason: decision.reason,
      requiredEvidence: decision.requiredEvidence,
      verificationBeforeRetry: decision.verificationBeforeRetry,
      stopConditions: decision.stopConditions,
      evidenceState: decision.evidenceState,
      evidenceFresh: decision.evidenceFresh,
      proof: decision.proof
    };
  });

  const replayPlan = createKernelKitSupportBundleReplayPlan(supportReport.supportBundle, { revision: REVISION, generatedAt: 'deterministic-risk-decision-probe-replay-plan' });
  const operatorPreflight = replayPlan.operatorPreflight;
  const operatorPreflightValidation = validateKernelKitSupportBundleOperatorPreflight(operatorPreflight);
  const operatorDisplaySnapshot = createKernelKitSupportBundleOperatorPreflightDisplaySnapshot(operatorPreflight, { revision: REVISION, generatedAt: 'deterministic-risk-decision-probe-operator-display-snapshot' });
  const operatorDisplaySnapshotValidation = validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot(operatorDisplaySnapshot);
  const operatorReplayGate = createKernelKitSupportBundleOperatorReplayGate(replayPlan, { revision: REVISION, generatedAt: 'deterministic-risk-decision-probe-operator-replay-gate' });
  const operatorReplayGateValidation = validateKernelKitSupportBundleOperatorReplayGate(operatorReplayGate);
  const missingMarkerCase = directCases.find((row) => row.retryAuthority?.reason === 'missing-required-evidence-marker');
  const missingMarkerPreflight = createKernelKitSupportBundleOperatorPreflight({ rows: [missingMarkerCase] }, { revision: REVISION, generatedAt: 'deterministic-risk-decision-probe-missing-marker-preflight' });
  const missingMarkerDisplaySnapshot = createKernelKitSupportBundleOperatorPreflightDisplaySnapshot(missingMarkerPreflight, { revision: REVISION, generatedAt: 'deterministic-risk-decision-probe-missing-marker-display-snapshot' });
  const retryRows = rows.filter((row) => row.decision === 'retry');
  const mutationRows = rows.filter((row) => row.mutationAttempted === true || row.mutationCommitted === true);
  const manualRows = rows.filter((row) => row.decision === 'stop/manual-review');
  const preflightRows = Array.isArray(operatorPreflight?.rows) ? operatorPreflight.rows : [];
  const proof = Object.freeze({
    supportBundleProbePassed: supportReport.status === 'passed',
    supportBundleValidationPassed: supportReport.validation?.ok === true,
    decisionRowsPresent: guidance?.proof?.decisionRowsPresent === true,
    everyRowHasDecision: rows.length >= 6 && rows.every((row) => ['retry','verify-first','stop/manual-review'].includes(row.decision)),
    retryOnlyPreMutationNoProviderMutation: retryRows.length > 0 && retryRows.every((row) => row.preMutationRejected === true && row.mutationAttempted !== true && row.mutationCommitted === false),
    mutationRowsNeverAutoRetry: mutationRows.length > 0 && mutationRows.every((row) => row.decision === 'verify-first' && row.automaticRetryAllowed === false && row.verificationRequired === true),
    serviceWorkerWaitUntilVerifiesSettlement: byCode.BRT_SW_WAITUNTIL_LATE_FAILURE?.decision === 'verify-first' && byCode.BRT_SW_WAITUNTIL_LATE_FAILURE?.verificationBeforeRetry?.includes('waitUntil-settlement-reviewed') === true,
    unclassifiedEvidenceStops: byCode.BRT_STORAGE_FAILURE_UNCLASSIFIED?.decision === 'stop/manual-review' && byCode.BRT_STORAGE_FAILURE_UNCLASSIFIED?.manualReviewRequired === true,
    manualRowsListStopConditions: manualRows.length > 0 && manualRows.every((row) => Array.isArray(row.stopConditions) && row.stopConditions.length > 0),
    directClassifierCoversThreeOutcomes: ['retry','verify-first','stop/manual-review'].every((decision) => directCases.some((row) => row.decision === decision)),
    staleEvidenceNeverAutoRetries: directCases.filter((row) => row.evidenceState?.status === 'stale').every((row) => row.decision === 'stop/manual-review' && row.automaticRetryAllowed === false),
    incompleteEvidenceNeverAutoRetries: directCases.filter((row) => ['incomplete','contradictory'].includes(row.evidenceState?.status)).every((row) => row.decision === 'stop/manual-review' && row.automaticRetryAllowed === false),
    missingMarkersNeverAuthorizeRetry: directCases.some((row) => row.decision === 'retry' && row.retryAuthority?.reason === 'missing-required-evidence-marker' && row.automaticRetryAllowed === false),
    retryAuthorizationRequiresMarkerCoverage: directCases.filter((row) => row.automaticRetryAllowed === true).every((row) => row.retryAuthority?.proof?.requiredMarkersCovered === true),
    evidenceStateVisible: directCases.every((row) => ['complete','stale','incomplete','contradictory','missing'].includes(row.evidenceState?.status) && typeof row.evidenceFresh === 'boolean'),
    operatorPreflightReady: replayPlan.status === 'replay-plan-ready' && operatorPreflight?.format === KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_PREFLIGHT_FORMAT && operatorPreflightValidation.ok === true,
    retryButtonHiddenUntilMarkersCovered: operatorPreflight?.proof?.retryButtonHiddenUntilMarkersCovered === true && preflightRows.every((row) => row.retryButtonState !== 'enabled' || row.retryAuthorityAllowed === true),
    missingMarkersVisibleBeforeRetryButton: operatorPreflight?.proof?.missingMarkersVisibleBeforeRetryButton === true && missingMarkerPreflight.rows?.[0]?.retryButtonState === 'hidden' && missingMarkerPreflight.rows?.[0]?.missingEvidenceMarkers?.length > 0,
    verifyFirstRowsHideRetryButton: operatorPreflight?.proof?.verifyFirstRowsHideRetryButton === true && preflightRows.filter((row) => row.decision === 'verify-first').every((row) => row.retryButtonState === 'hidden'),
    stopRowsHideRetryButton: operatorPreflight?.proof?.stopRowsHideRetryButton === true && preflightRows.filter((row) => row.decision === 'stop/manual-review').every((row) => row.retryButtonState === 'hidden'),
    replayPreflightCarriesEvidenceState: preflightRows.every((row) => ['complete','stale','incomplete','contradictory','missing'].includes(row.evidenceState?.status) && typeof row.evidenceFresh === 'boolean'),
    operatorDisplaySnapshotReady: operatorDisplaySnapshot?.format === KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_PREFLIGHT_DISPLAY_SNAPSHOT_FORMAT && operatorDisplaySnapshot.status === 'ready' && operatorDisplaySnapshotValidation.ok === true,
    replayPlanCarriesDisplaySnapshot: replayPlan.operatorDisplaySnapshot?.format === KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_PREFLIGHT_DISPLAY_SNAPSHOT_FORMAT && replayPlan.proof?.operatorDisplaySnapshotReady === true,
    operatorReplayGateReady: operatorReplayGate?.format === KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_REPLAY_GATE_FORMAT && operatorReplayGate.status === 'ready' && operatorReplayGateValidation.ok === true,
    operatorReplayGateBindsRows: operatorReplayGate?.proof?.rowCountBound === true && operatorReplayGate?.proof?.rowDisplayBound === true && operatorReplayGate?.proof?.rowIdentityBound === true,
    operatorReplayGateHidesBlockedRows: operatorReplayGate?.proof?.hiddenRowsRemainHidden === true && operatorReplayGate?.proof?.verifyAndStopNeverVisible === true && operatorReplayGate?.proof?.missingMarkersVisibleForHiddenRetry === true,
    operatorReplayGateNoRawDisplayTokens: operatorReplayGate?.proof?.noRawSensitiveDisplayTokens === true,
    operatorReplayGateRenderableFieldsBound: operatorReplayGate?.proof?.renderableRowsCarryCanonicalDisplayFields === true && operatorReplayGate.rowBindings?.every((row) => typeof row.displayRetryControlText === 'string' && typeof row.expectedMissingEvidenceText === 'string' && Object.hasOwn(row, 'stopReason')) === true,
    visibleRowsMatchMissingMarkers: operatorDisplaySnapshot?.proof?.visibleRowsMatchMissingMarkers === true && operatorDisplaySnapshot?.proof?.missingMarkersRenderedBeforeRetry === true,
    hiddenRetryRowsCarryVisibleText: operatorDisplaySnapshot?.proof?.hiddenRetryRowsHaveHiddenLabel === true && operatorDisplaySnapshot.rows?.filter((row) => row.retryButtonState === 'hidden').every((row) => row.retryControlText === 'Retry hidden' && String(row.visibleRowText).includes('Missing markers:')) === true,
    missingMarkerDisplayShowsExactMarkers: missingMarkerDisplaySnapshot.status === 'ready' && missingMarkerDisplaySnapshot.rows?.[0]?.retryButtonState === 'hidden' && missingMarkerDisplaySnapshot.rows?.[0]?.visibleMissingEvidenceText === (missingMarkerDisplaySnapshot.rows?.[0]?.missingEvidenceMarkers || []).join(', ') && (missingMarkerDisplaySnapshot.rows?.[0]?.missingEvidenceMarkers || []).every((marker) => String(missingMarkerDisplaySnapshot.rows?.[0]?.visibleRowText).includes(marker)),
    displaySnapshotBlocksVerifyAndStopRetry: operatorDisplaySnapshot?.proof?.verifyFirstAndStopRowsHideRetry === true,
    privacyBoundedRows: guidance?.proof?.noRawErrorMessageStackPathDigestOrLockName === true && operatorPreflight?.proof?.noRawErrorMessageStackPathDigestOrLockName === true,
    nonClaimVisible: directCases.every((row) => row.proof?.nonClaimVisible === true)
  });

  for (const [key, value] of Object.entries(proof)) assert.equal(value, true, `proof.${key} must be true`);

  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-support-bundle-risk-decision-probe`,
    status: 'passed',
    supportBundleProbeId: supportReport.probe_id,
    supportBundleGuidanceFormat: guidance?.format || null,
    decisionFormat: KERNEL_KIT_SUPPORT_BUNDLE_RISK_DECISION_FORMAT,
    rowCount: rows.length,
    rowCodes: rows.map((row) => row.code),
    decisions: Object.freeze(Object.fromEntries(rows.map((row) => [row.code, {
      decision: row.decision,
      automaticRetryAllowed: row.automaticRetryAllowed,
      retryAuthority: row.retryAuthority,
      verificationRequired: row.verificationRequired,
      manualReviewRequired: row.manualReviewRequired,
      requiredEvidence: row.requiredEvidence,
      verificationBeforeRetry: row.verificationBeforeRetry,
      stopConditions: row.stopConditions,
      evidenceState: row.evidenceState,
      evidenceFresh: row.evidenceFresh
    }]))),
    decisionSet: unique(rows.map((row) => row.decision)),
    directCases,
    replayPlan: Object.freeze({ status: replayPlan.status, operatorPreflight: operatorPreflight ? Object.freeze({ format: operatorPreflight.format, status: operatorPreflight.status, rowCount: operatorPreflight.rowCount, proof: operatorPreflight.proof, rows: operatorPreflight.rows }) : null }),
    operatorDisplaySnapshot,
    operatorReplayGate,
    missingMarkerDisplaySnapshot,
    missingMarkerPreflight: Object.freeze({ status: missingMarkerPreflight.status, rows: missingMarkerPreflight.rows, proof: missingMarkerPreflight.proof }),
    proof,
    nonClaims: Object.freeze([KERNEL_KIT_SUPPORT_BUNDLE_RISK_DECISION_NON_CLAIM])
  });
}

const isMain = process.argv[1] && import.meta.url === new URL(process.argv[1], 'file:').href;
if (isMain) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const report = await runProbe();
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } else console.log(JSON.stringify(report, null, 2));
}

// Static audit markers: demo:kernel-kit-support-bundle-risk-decision-proof; browserrt-kernel-kit-support-bundle-risk-decision-v1; browserrt-kernel-kit-support-bundle-retry-authority-v1; browserrt-kernel-kit-support-bundle-operator-preflight-display-snapshot-v1; browserrt-kernel-kit-support-bundle-operator-replay-gate-v1; classifyKernelKitSupportBundleRiskDecision; BRT_BROWSER_STORAGE_ADMISSION_REJECTED; BRT_WEB_LOCK_TIMEOUT; BRT_OPFS_QUOTA_EXCEEDED; BRT_OPFS_OPERATION_ABORTED; BRT_SW_WAITUNTIL_LATE_FAILURE; BRT_STORAGE_FAILURE_UNCLASSIFIED; retry; verify-first; stop/manual-review; visibleRowsMatchMissingMarkers; hiddenRetryRowsCarryVisibleText; missingMarkerDisplayShowsExactMarkers; displaySnapshotBlocksVerifyAndStopRetry; missingMarkersNeverAuthorizeRetry; retryAuthorizationRequiresMarkerCoverage; waitUntil-settlement-reviewed; No automatic support-bundle retry/repair claim.
