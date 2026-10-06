#!/usr/bin/env node
// BrowserRT rev0033 provider-resilience history contract audit.
// Future-session coherence guard only; no runtime/provider performance or durability claim.

import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PREFIX}-PROVIDER-RESILIENCE-HISTORY-CONTRACT-AUDIT.json`);
const proofPath = `artifacts/validation/${PREFIX}-PROVIDER-RESILIENCE-HISTORY-PROBE.json`;

async function text(path) { return await readTextWithRevisionFallback(path); }
async function json(path) { return JSON.parse(await text(path)); }
if (!existsSync(proofPath)) {
  const result = spawnSync('node', ['tools/provider_resilience_history_probe.mjs', '--json', proofPath], { stdio: 'inherit' });
  if (result.status !== 0) throw new Error('failed to regenerate provider-resilience history proof before audit');
}
function hasAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

const [source, runtime, ipc, types, manifest, impact, inventory, registry, receipt, charter, office, frontier, sliceDoc, auditDoc, proof] = await Promise.all([
  text('src/provider-resilience-history.mjs'),
  text('src/browserrt.mjs'),
  text('src/ipc.mjs'),
  text('src/types.d.ts'),
  json('test/manifest.json'),
  json('test/impact-map.json'),
  json('test/surface-inventory.json'),
  json('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json'),
  json('REVISION-RECEIPT.json'),
  text('docs/00-meta/non-claims-and-goals-charter.md'),
  text('docs/00-meta/future-session-office-manual.md'),
  text('docs/20-architecture/provider-integrated-resilience-history-frontier.md'),
  text('docs/40-validation/provider-resilience-history-slice.md'),
  text(`docs/40-validation/provider-resilience-history-contract-audit-${REVISION}.md`).catch(() => text('docs/40-validation/provider-resilience-history-contract-audit-rev0033.md')),
  json(proofPath)
]);
const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const titles = new Set((registry.families || []).flatMap((family) => family.sources || []).map((source) => source.title));
const sourceNeedles = ['class ProviderResilienceHistoryRunner', 'runMailboxEnqueue', 'validateProviderResilienceHistorySnapshot', 'provider-resilience:operation-final', 'No OPFS, browser'];
const runtimeNeedles = ['ProviderResilienceHistoryRunner', 'createProviderResilienceHistoryRunner', 'validateProviderResilienceHistorySnapshot', 'providerResilienceHistoryProof', 'providerResilienceHistoryRunner'];
const docsNeedles = ['ProviderResilienceHistoryRunner', 'scheduler:provider-resilience-history-proof', 'No OPFS provider-resilience proof', 'No browser Worker provider-resilience proof'];
const nonClaimNeedles = ['No OPFS provider-resilience proof', 'No browser Worker provider-resilience proof', 'No production resilience', 'No WebGPU proof'];
const checks = [
  check('source-contract-needles-present', hasAll(source, sourceNeedles).length === 0, { missing: hasAll(source, sourceNeedles) }),
  check('runtime-export-and-factory-present', hasAll(runtime, runtimeNeedles).length === 0, { missing: hasAll(runtime, runtimeNeedles) }),
  check('ipc-and-types-present', ipc.includes('ProviderResilienceHistoryRunner') && types.includes('ProviderResilienceHistoryRunner') && types.includes('providerResilienceHistoryRunner')),
  check('manifest-tasks-present', taskIds.has('scheduler:provider-resilience-history-proof') && taskIds.has('facility:provider-resilience-history-contract-audit')),
  check('impact-map-covers-tasks', impactIds.has('scheduler:provider-resilience-history-proof') && impactIds.has('facility:provider-resilience-history-contract-audit')),
  check('surface-inventory-covers-tasks', inventoryIds.has('scheduler:provider-resilience-history-proof') && inventoryIds.has('facility:provider-resilience-history-contract-audit')),
  check('research-registry-has-rev0033-sources', ['Resilience4j decorator composition and event stream', 'Envoy retry budgets and circuit breaking', 'Google SRE overload and cascading failure retry amplification', 'Temporal retry policies and bounded retries'].every((title) => titles.has(title))),
  check('docs-present-and-current', hasAll(frontier + sliceDoc + auditDoc, docsNeedles).length === 0, { missing: hasAll(frontier + sliceDoc + auditDoc, docsNeedles) }),
  check('handoff-nonclaims-legible', hasAll(charter + office + JSON.stringify(receipt), nonClaimNeedles).length === 0, { missing: hasAll(charter + office + JSON.stringify(receipt), nonClaimNeedles) }),
  check('proof-current-passed', proof.revision === REVISION && proof.status === 'passed' && proof.slice === 'scheduler:provider-resilience-history-proof'),
  check('proof-observations-cover-composition', Boolean(proof.observations?.transientRetrySucceeded && proof.observations?.retryBudgetAcquiredBeforeRetry && proof.observations?.circuitOpenedAfterFailures && proof.observations?.bulkheadRejectionCausedNoProviderMutation && proof.observations?.generatedHistoryCount === 12))
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(),
  slice: 'facility:provider-resilience-history-contract-audit',
  purpose: 'Audit source/runtime/docs/manifest/research/proof/non-claim coherence for the provider-integrated resilience history slice.',
  proofPath,
  checks,
  nonClaims: [
    'Provider-resilience contract audit does not prove OPFS, browser Worker, durability, performance, or production resilience behavior.',
    'Provider-resilience contract audit guards future-session coherence and claim boundaries only.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (failed.length) process.exitCode = 1;
