import assert from 'node:assert/strict';

export const EXPECTED_FINGERPRINT_RESTORE_TRACE_KINDS = Object.freeze([
  'block-store-lane:quarantine-ledger-restore-expected-fingerprint-rejected',
  'block-store-lane:quarantine-clearance-receipt-restore-expected-fingerprint-rejected',
  'block-store-lane:quarantine-ledger-restored',
  'block-store-lane:quarantine-clearance-receipt-restored',
  'storage-lane:timed-out-quarantine-import-replay-rejected'
]);

export const EXPECTED_FINGERPRINT_RESTORE_CLAIMS = Object.freeze([
  'blank expected quarantine/receipt fingerprint intent rejects instead of silently disabling the pin',
  'valid but unexpected quarantine ledger restore rejects before import',
  'valid but unexpected clearance receipt restore rejects before replay-guard registration',
  'wrong pre-clearance fingerprint rejects even when receipt fingerprint matches',
  'matching expected fingerprints permit restore and stale replay guard still works'
]);

export const EXPECTED_FINGERPRINT_RESTORE_NON_CLAIMS = Object.freeze([
  'Expected fingerprint binding is operator/handoff intent checking, not cryptographic attestation or tamper-proof storage.',
  'The proof does not claim provider cancellation, rollback, no-mutation-on-timeout, durability, quota, eviction, crash recovery, cross-browser behavior, throughput SLOs, or production readiness.'
]);

export function assertExpectedFingerprintRestoreReport(result, { browser = false } = {}) {
  assert.equal(result.blankLedgerRestore?.ok, false);
  assert.equal(result.blankLedgerRestore?.disposition, 'rejected-quarantine-ledger-expected-fingerprint');
  assert.equal(result.blankLedgerRestore?.code, 'timed-out-quarantine-restore-expected-fingerprint-blank');
  assert.equal(result.wrongLedgerRestore?.ok, false);
  assert.equal(result.wrongLedgerRestore?.disposition, 'rejected-quarantine-ledger-expected-fingerprint');
  assert.equal(result.ledgerQuarantineAfterRejected?.totalCount, 0);
  assert.equal(result.ledgerLaneAfterRejected?.healthy, true);
  assert.equal(result.rightLedgerRestore?.ok, true);
  assert.equal(result.rightLedgerRestore?.importResult?.markUnhealthyForced, true);
  assert.equal(result.ledgerQuarantineAfterAccepted?.totalCount, 2);

  assert.equal(result.blankReceiptRestore?.ok, false);
  assert.equal(result.blankReceiptRestore?.disposition, 'rejected-clearance-receipt-expected-fingerprint');
  assert.equal(result.blankReceiptRestore?.code, 'timed-out-quarantine-clearance-receipt-restore-expected-fingerprint-blank');
  assert.equal(result.wrongReceiptRestore?.ok, false);
  assert.equal(result.wrongReceiptRestore?.disposition, 'rejected-clearance-receipt-expected-fingerprint');
  assert.equal(result.receiptsAfterWrong?.length, 0);
  assert.equal(result.importAfterRejectedReceipt?.ok, true);
  assert.equal(result.importAfterRejectedReceipt?.markUnhealthyForced, true);
  assert.equal(result.wrongPreclearanceRestore?.ok, false);
  assert.equal(result.wrongPreclearanceRestore?.disposition, 'rejected-clearance-receipt-expected-fingerprint');
  assert.equal(result.rightReceiptRestore?.ok, true);
  assert.equal(result.staleReplay?.ok, false);
  assert.equal(result.staleReplay?.disposition, 'rejected-cleared-quarantine-replay');

  const traceKinds = Array.isArray(result.traceKinds) ? result.traceKinds : [];
  for (const kind of EXPECTED_FINGERPRINT_RESTORE_TRACE_KINDS) {
    assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);
  }
  if (browser) {
    assert.equal(result.capabilities?.opfs, true);
    assert.equal(result.capabilities?.webLocks, true);
    assert.equal(result.recoveryVerify?.ok, true);
    for (const verify of Object.values(result.persistedVerifies || {})) assert.equal(verify?.ok, true);
    assert.equal(result.cleanup, true);
    assert.equal(result.locksAfterCleanup?.heldCount, 0);
    assert.equal(result.locksAfterCleanup?.pendingCount, 0);
    assert.equal(result.profileReap?.afterKillCount, 0);
    assert.ok(traceKinds.includes('coord:web-lock-acquired'), 'missing trace kind coord:web-lock-acquired');
    assert.ok(traceKinds.includes('coord:web-lock-released'), 'missing trace kind coord:web-lock-released');
  }
}
