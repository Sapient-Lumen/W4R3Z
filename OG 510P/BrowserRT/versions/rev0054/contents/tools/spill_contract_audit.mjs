#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-SPILL-CONTRACT-AUDIT.json`;

function argValue(argv, flag, fallback = null) {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
}

async function text(path) {
  return await readFile(path, 'utf8');
}

async function json(path) {
  return JSON.parse(await text(path));
}

async function main() {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const source = await text('src/persisted-spill-mailbox.mjs');
  const probe = await text('tools/persisted_spill_recovery_probe.mjs');
  const frontier = await text('docs/20-architecture/persisted-spill-recovery-frontier.md');
  const slice = await text('docs/40-validation/persisted-spill-recovery-slice.md');
  const charter = await text('docs/00-meta/non-claims-and-goals-charter.md');
  const artifact = await json(`artifacts/validation/${PREFIX}-PERSISTED-SPILL-RECOVERY-PROBE.json`);

  const checks = [
    { name: 'source-has-checkpoint-recover-journal', passed: ['checkpoint', 'recover', 'exportJournal', 'tornRecordForTest'].every((needle) => source.includes(needle)) },
    { name: 'source-exposes-pending-redelivery', passed: source.includes('requeuePending') && source.includes('pendingRequeued') },
    { name: 'probe-asserts-at-least-once-non-claim', passed: probe.includes('No exactly-once delivery claim') && probe.includes('pendingRedeliveredAfterRecovery') },
    { name: 'frontier-states-durability-boundary', passed: frontier.includes('No OPFS') && frontier.includes('at-least-once') && frontier.includes('checkpoint') },
    { name: 'slice-states-release-tier-economics', passed: slice.includes('release tier') && slice.includes('browser-light') && slice.includes('Revision: rev0027') },
    { name: 'charter-keeps-non-claim-legible', passed: charter.includes('persisted spill') && charter.includes('exactly-once') },
    { name: 'proof-artifact-current-passed', passed: artifact.revision === REVISION && artifact.status === 'passed' },
    { name: 'proof-observations-cover-recovery', passed: Boolean(artifact.observations?.pendingRedeliveredAfterRecovery && artifact.observations?.ackedMessagesNotRedelivered && artifact.observations?.tornTailIgnored && artifact.observations?.repeatRecoveryDeterministic) }
  ];
  for (const check of checks) assert.equal(check.passed, true, check.name);
  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    status: 'passed',
    audit_id: 'cube:spill-contract-audit',
    generatedAt: new Date().toISOString(),
    purpose: 'Audit the persisted-spill recovery slice for source/probe/doc/non-claim coherence before future sessions build on it.',
    checks,
    warnings: [
      'This audit verifies legibility and current slice evidence; it does not prove OPFS durability or browser behavior.',
      'Future OPFS work must keep these fake-provider recovery semantics as the cheap reference model.'
    ]
  };
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
