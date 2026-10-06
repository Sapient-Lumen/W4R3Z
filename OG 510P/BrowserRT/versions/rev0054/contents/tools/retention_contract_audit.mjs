#!/usr/bin/env node
// BrowserRT rev0027 persisted-spill retention/compaction audit.
// Coherence guard only; no OPFS, durability, or performance claim.

import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const prefix = `REV${REVISION.slice(3)}`;
const proofPath = `artifacts/validation/${prefix}-PERSISTED-SPILL-COMPACTION-PROBE.json`;
const outArg = process.argv.indexOf('--json');
const outPath = outArg >= 0 ? process.argv[outArg + 1] : `artifacts/audit/${prefix}-RETENTION-CONTRACT-AUDIT.json`;

async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function row(path, check, passed, extra = {}) { return { path, check, status: passed ? 'passed' : 'failed', ...extra }; }
function has(body, needle) { return body.includes(needle); }

if (!existsSync(proofPath)) {
  const result = spawnSync('node', ['tools/persisted_spill_compaction_probe.mjs', '--json', proofPath], { stdio: 'inherit' });
  if (result.status !== 0) throw new Error('failed to regenerate persisted-spill compaction proof before audit');
}

const proof = await json(proofPath);
const manifest = await json('test/manifest.json');
const impact = await json('test/impact-map.json');
const inventory = await json('test/surface-inventory.json');
const validation = await json('VALIDATION-INDEX.json');
const receipt = await json('REVISION-RECEIPT.json');
const registry = await json('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json');
const source = await text('src/persisted-spill-mailbox.mjs');
const runtime = await text('src/browserrt.mjs');
const types = await text('src/types.d.ts');
const probe = await text('tools/persisted_spill_compaction_probe.mjs');
const frontier = await text('docs/20-architecture/persisted-spill-retention-compaction-frontier.md');
const slice = await text('docs/40-validation/persisted-spill-compaction-slice.md');
const auditDoc = await text(`docs/40-validation/retention-contract-audit-${REVISION}.md`);
const charter = await text('docs/00-meta/non-claims-and-goals-charter.md');
const office = await text('docs/00-meta/future-session-office-manual.md');
const tasks = new Set((manifest.tasks || []).map((task) => task.id));
const mapped = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const surfaceRefs = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const titles = new Set((registry.families || []).flatMap((family) => family.sources || []).map((source) => source.title));

const requiredObservations = [
  'dryRunFoundOnlyAckedUniqueBlock',
  'dryRunDidNotDelete',
  'firstCompactDeletedOneBlock',
  'liveDuplicatePreventedDeletion',
  'pendingAndReadySurvivedCompact',
  'compactDeleteWasJournaled',
  'compactRecordReplayedInRecovery',
  'recoveredRequeuedPending',
  'recoveredDrainSeqsExpected',
  'finalCompactionDeletesRemainingBlocks',
  'finalProviderEmpty',
  'traceHasRequiredEvents'
];
const requiredTitles = [
  'Redis XTRIM stream trimming',
  'Kafka cleanup.policy topic configuration',
  'NATS JetStream stream limits and retention',
  'RocksDB Compaction'
];

const findings = [];
findings.push(row('src/persisted-spill-mailbox.mjs', 'source exposes compact()', has(source, 'async compact')));
findings.push(row('src/persisted-spill-mailbox.mjs', 'source tracks retained/live refs', has(source, '#retainedRefs') && has(source, '#liveRefDigestSet')));
findings.push(row('src/persisted-spill-mailbox.mjs', 'compact-delete is journaled and replayed', has(source, "#append('compact-delete'") && has(source, "record.op === 'compact-delete'")));
findings.push(row('src/browserrt.mjs', 'runtime exports persisted-spill compaction path', has(runtime, 'persistedSpillCompactionProbe') && has(runtime, 'PersistedSpillMailbox')));
findings.push(row('src/types.d.ts', 'types expose compact()', has(types, 'compact(options?:')));
findings.push(row('tools/persisted_spill_compaction_probe.mjs', 'probe asserts live-ref protection', has(probe, 'liveDuplicatePreventedDeletion')));
findings.push(row('test/manifest.json', 'manifest includes proof task', tasks.has('ipc:persisted-spill-compaction-proof')));
findings.push(row('test/manifest.json', 'manifest includes audit task', tasks.has('facility:retention-contract-audit')));
findings.push(row('test/impact-map.json', 'impact map covers proof task', mapped.has('ipc:persisted-spill-compaction-proof')));
findings.push(row('test/impact-map.json', 'impact map covers audit task', mapped.has('facility:retention-contract-audit')));
findings.push(row('test/surface-inventory.json', 'surface inventory covers retention task', surfaceRefs.has('ipc:persisted-spill-compaction-proof')));
findings.push(row('VALIDATION-INDEX.json', 'validation index names proof artifact', JSON.stringify(validation).includes(`${prefix}-PERSISTED-SPILL-COMPACTION-PROBE.json`)));
findings.push(row('REVISION-RECEIPT.json', 'receipt carries compaction non-claims', JSON.stringify(receipt.non_claims || receipt.important_non_claims || []).includes('production retention')));
findings.push(row('docs/20-architecture/persisted-spill-retention-compaction-frontier.md', 'frontier states retention/compaction boundary', has(frontier, 'retention/compaction') && has(frontier, 'No OPFS persisted-spill proof')));
findings.push(row('docs/40-validation/persisted-spill-compaction-slice.md', 'slice names manifest id and artifact', has(slice, 'ipc:persisted-spill-compaction-proof') && has(slice, `${prefix}-PERSISTED-SPILL-COMPACTION-PROBE.json`)));
findings.push(row(`docs/40-validation/retention-contract-audit-${REVISION}.md`, 'audit doc names facility id', has(auditDoc, 'facility:retention-contract-audit')));
findings.push(row('docs/00-meta/non-claims-and-goals-charter.md', 'charter keeps fake-provider boundary', has(charter, 'Rev0026 persisted-spill retention/compaction amendment') && has(charter, 'No production retention')));
findings.push(row('docs/00-meta/future-session-office-manual.md', 'office manual tells future sessions how to resume retention rung', has(office, 'Rev0026 retention/compaction amendment') && has(office, 'ipc:persisted-spill-compaction-proof')));
for (const title of requiredTitles) findings.push(row('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json', `registry includes ${title}`, titles.has(title)));
for (const key of requiredObservations) findings.push(row(proofPath, `observation ${key}`, proof.observations?.[key] === true));
findings.push(row(proofPath, 'proof artifact current and passed', proof.revision === REVISION && proof.status === 'passed'));
findings.push(row('test/manifest.json', 'release remains browser-light', (manifest.tasks || []).filter((task) => task.tiers.includes('release') && task.lane === 'browser').length === 0));

const failed = findings.filter((finding) => finding.status !== 'passed');
for (const finding of failed) assert.equal(finding.status, 'passed', `${finding.path}: ${finding.check}`);
const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  slice: 'facility:retention-contract-audit',
  status: 'passed',
  generatedAt: new Date().toISOString(),
  purpose: 'Coherence audit for the persisted-spill retention/compaction proof: retained/live ref semantics, compact-delete journal replay, docs, manifest, impact map, inventory, research registry, artifact, and non-claim boundaries.',
  proofPath,
  findingCount: findings.length,
  failedCount: 0,
  findings,
  nonClaimsChecked: [
    'No OPFS persisted-spill proof.',
    'No browser Worker persisted-spill proof.',
    'No production retention, compaction, or garbage-collection algorithm claim.',
    'No fsync, quota, eviction, or durability claim.',
    'No exactly-once delivery claim.',
    'No throughput or latency claim.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ status: report.status, slice: report.slice, findingCount: report.findingCount }, null, 2));
