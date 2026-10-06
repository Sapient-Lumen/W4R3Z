#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-RECOVERY-CONTRACT-AUDIT.json`;
const TASK_ID = 'ipc:persisted-spill-recovery-proof';
const AUDIT_ID = 'facility:recovery-contract-audit';

function argValue(argv, flag, fallback = null) {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
}
async function text(path) { return await readTextWithRevisionFallback(path); }
async function json(path) { return JSON.parse(await text(path)); }
function taskById(manifest, id) { return (manifest.tasks || []).find((task) => task.id === id); }
function allTrue(obj, keys) { return keys.every((key) => obj?.[key] === true); }
function titles(registry) { return (registry.families || []).flatMap((family) => family.sources || []).map((source) => source.title); }

async function main() {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const source = await text('src/persisted-spill-mailbox.mjs');
  const probe = await text('tools/persisted_spill_recovery_probe.mjs');
  const frontier = await text('docs/20-architecture/persisted-spill-recovery-frontier.md');
  const slice = await text('docs/40-validation/persisted-spill-recovery-slice.md');
  const auditDoc = await text(`docs/40-validation/recovery-contract-audit-${REVISION}.md`);
  const charter = await text('docs/00-meta/non-claims-and-goals-charter.md');
  const office = await text('docs/00-meta/future-session-office-manual.md');
  const validation = await json('VALIDATION-INDEX.json');
  const receipt = await json('REVISION-RECEIPT.json');
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const inventory = await json('test/surface-inventory.json');
  const registry = await json('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json');
  const artifact = await json(`artifacts/validation/${PREFIX}-PERSISTED-SPILL-RECOVERY-PROBE.json`);

  const recoveryTask = taskById(manifest, TASK_ID);
  const auditTask = taskById(manifest, AUDIT_ID);
  const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
  const sourceTitles = titles(registry);
  const requiredSourceTitles = [
    'Amazon SQS visibility timeout',
    'RabbitMQ consumer acknowledgements and publisher confirms',
    'RabbitMQ durable queues',
    'NATS JetStream streams',
    'Apache Kafka retention and log compaction',
    'Storage Buckets / Storage API',
    'Web Locks API'
  ];
  const requiredObservations = [
    'checkpointCapturedQueueAndPending',
    'pendingRedeliveredAfterRecovery',
    'ackedMessagesNotRedelivered',
    'fifoAfterRecovery',
    'payloadChecksumsMatch',
    'tornTailIgnored',
    'corruptManifestRejected',
    'ackDeletedRecoveredBlocks',
    'traceHasRequiredEvents'
  ];

  const checks = [
    { name: 'source-has-checkpoint-recover-journal', passed: ['class PersistedSpillMailbox', 'checkpoint', 'recover', 'exportJournal', 'tornRecordForTest'].every((needle) => source.includes(needle)) },
    { name: 'source-exposes-pending-redelivery-events', passed: ['mailbox:persisted-requeue-pending', 'mailbox:persisted-torn-record-ignored', 'mailbox:persisted-recover'].every((needle) => source.includes(needle)) },
    { name: 'probe-asserts-at-least-once-non-claim', passed: probe.includes('No exactly-once delivery claim') && probe.includes('pendingRedeliveredAfterRecovery') },
    { name: 'manifest-has-recovery-proof-release-task', passed: Boolean(recoveryTask) && recoveryTask.tiers.includes('release') && recoveryTask.lane !== 'browser' && recoveryTask.outputs.includes(`artifacts/validation/${PREFIX}-PERSISTED-SPILL-RECOVERY-PROBE.json`) },
    { name: 'manifest-has-recovery-contract-audit-release-task', passed: Boolean(auditTask) && auditTask.tiers.includes('release') && auditTask.outputs.includes(`artifacts/audit/${PREFIX}-RECOVERY-CONTRACT-AUDIT.json`) },
    { name: 'impact-map-covers-new-tasks', passed: impactTaskIds.has(TASK_ID) && impactTaskIds.has(AUDIT_ID) },
    { name: 'surface-inventory-covers-persisted-spill', passed: surfaceIds.has('surface:persisted-spill-recovery') },
    { name: 'validation-index-covers-new-artifacts', passed: JSON.stringify(validation).includes(`${PREFIX}-PERSISTED-SPILL-RECOVERY-PROBE.json`) && JSON.stringify(validation).includes(`${PREFIX}-RECOVERY-CONTRACT-AUDIT.json`) },
    { name: 'receipt-carries-non-claims', passed: receipt.revision === REVISION && JSON.stringify(receipt.non_claims || []).includes('exactly-once') && JSON.stringify(receipt.non_claims || []).includes('OPFS persisted-spill') },
    { name: 'frontier-states-durability-boundary', passed: frontier.includes('No OPFS') && frontier.includes('at-least-once') && frontier.includes('recovery ladder') },
    { name: 'slice-states-release-tier-economics', passed: slice.includes('release tier') && slice.includes('browser-light') && slice.includes(`Revision: ${REVISION}`) },
    { name: 'audit-doc-explains-factor-purpose', passed: auditDoc.includes(AUDIT_ID) && auditDoc.includes('source, docs, manifest, impact map') },
    { name: 'office-and-charter-keep-non-claims-legible', passed: `${office}\n${charter}`.includes('fake-provider recovery model') && `${office}\n${charter}`.includes('exactly-once') && `${office}\n${charter}`.includes('No OPFS persisted-spill proof') },
    { name: 'research-registry-remembers-official-sources', passed: requiredSourceTitles.every((title) => sourceTitles.includes(title)), missingTitles: requiredSourceTitles.filter((title) => !sourceTitles.includes(title)) },
    { name: 'proof-artifact-current-passed', passed: artifact.revision === REVISION && artifact.status === 'passed' },
    { name: 'proof-observations-cover-recovery', passed: allTrue(artifact.observations, requiredObservations), requiredObservations },
    { name: 'release-browser-light-policy-intact', passed: (manifest.tasks || []).filter((task) => task.tiers.includes('release') && task.lane === 'browser').length === 0 }
  ];
  for (const check of checks) assert.equal(check.passed, true, check.name);

  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    status: 'passed',
    audit_id: AUDIT_ID,
    generatedAt: new Date().toISOString(),
    purpose: 'Audit the persisted-spill recovery slice for source/probe/doc/manifest/impact/inventory/registry/proof/non-claim coherence before future sessions build on it.',
    checks,
    warnings: [
      'This audit verifies legibility and current slice evidence; it does not prove OPFS durability or browser behavior.',
      'Future OPFS work must keep these fake-provider recovery semantics as the cheap reference model.',
      'At-least-once redelivery is intentional; exactly-once remains a non-claim.'
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
