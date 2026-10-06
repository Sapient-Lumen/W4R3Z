#!/usr/bin/env node
import { readdir, readFile, stat, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, relative } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const PREVIOUS_REV = `rev${String(Number(REVISION.slice(3)) - 1).padStart(4, '0')}`;
const PREVIOUS_PREFIX = `REV${PREVIOUS_REV.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-ARTIFACT-BUDGET-AUDIT.json`;
const SOFT_TOTAL_BYTES = 8 * 1024 * 1024;
const SOFT_DUPLICATE_DOC_BYTES = 256 * 1024;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

async function walk(dir = '.') {
  const out = [];
  for (const ent of await readdir(dir, { withFileTypes: true })) {
    if (['.git', 'node_modules', '__pycache__', 'out'].includes(ent.name)) continue;
    const path = `${dir}/${ent.name}`;
    if (ent.isDirectory()) out.push(...await walk(path));
    else out.push(path);
  }
  return out;
}
function sha256(bytes) { return createHash('sha256').update(bytes).digest('hex'); }
function revNumberFromPath(path) { const hits = [...String(path).matchAll(/(?:rev|REV)(\d{4})/g)].map((match) => Number(match[1])); return hits.length ? Math.max(...hits) : -1; }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function sortObjectByValueDesc(obj) { return Object.fromEntries(Object.entries(obj).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function addBucket(map, key, bytes) { map[key] = (map[key] || 0) + bytes; }

export async function runAudit() {
  const rows = [];
  let historicalRevTombstoneCount = 0;
  const historicalCompactionPath = `artifacts/datacube-audit/${PREFIX}-HISTORICAL-REVISION-DOC-COMPACTION.json`;
  let historicalCompaction = null;
  const hashGroups = new Map();
  for (const file of await walk('.')) {
    const rel = relative('.', file);
    if (rel.endsWith('.zip') || rel === 'RELEASE-MANIFEST.json') continue;
    const info = await stat(file);
    const bytes = await readFile(file);
    const hash = sha256(bytes);
    const topLevel = rel.includes('/') ? rel.slice(0, rel.indexOf('/')) : '<root>';
    const docText = rel.startsWith('docs/') ? bytes.toString('utf8') : '';
    if (rel.startsWith('docs/') && /rev\d{4}/.test(rel) && !rel.includes(REVISION) && docText.includes('Compacted historical revision document') && docText.includes('HISTORICAL-REVISION-DOC-COMPACTION')) historicalRevTombstoneCount += 1;
    const row = { path: rel, bytes: info.size, topLevel, hash };
    rows.push(row);
    if (!hashGroups.has(hash)) hashGroups.set(hash, []);
    hashGroups.get(hash).push(row);
  }
  rows.sort((a, b) => b.bytes - a.bytes || a.path.localeCompare(b.path));
  const totalBytes = rows.reduce((sum, row) => sum + row.bytes, 0);
  const byTopLevel = {}, byArtifactArea = {}, byArtifactPrefix = {};
  const revSuffixedDocRows = [];
  for (const row of rows) {
    addBucket(byTopLevel, row.topLevel, row.bytes);
    if (row.path.startsWith('artifacts/')) {
      const parts = row.path.split('/');
      addBucket(byArtifactArea, parts[1] || '<unknown>', row.bytes);
      const prefix = row.path.match(/REV\d{4}/)?.[0] || '<unversioned>';
      addBucket(byArtifactPrefix, prefix, row.bytes);
    }
    if (row.path.startsWith('docs/') && /rev\d{4}/.test(row.path)) revSuffixedDocRows.push(row);
  }
  try { historicalCompaction = JSON.parse(await readFile(historicalCompactionPath, 'utf8')); } catch { historicalCompaction = null; }
  const duplicateGroups = [...hashGroups.values()].filter((group) => group.length > 1).map((group) => {
    const sorted = group.slice().sort((a, b) => revNumberFromPath(b.path) - revNumberFromPath(a.path) || a.path.localeCompare(b.path));
    const bytes = sorted[0].bytes;
    return { hash: sorted[0].hash, bytes, count: sorted.length, duplicateBytes: bytes * (sorted.length - 1), paths: sorted.map((row) => row.path) };
  }).sort((a, b) => b.duplicateBytes - a.duplicateBytes || a.paths[0].localeCompare(b.paths[0]));
  const duplicateDocGroups = duplicateGroups.filter((group) => group.paths.every((path) => path.startsWith('docs/')));
  const duplicateDocBytes = duplicateDocGroups.reduce((sum, group) => sum + group.duplicateBytes, 0);
  const artifactPrefixes = Object.keys(byArtifactPrefix).filter((prefix) => /^REV\d{4}$/.test(prefix));
  const oldArtifactPrefixes = artifactPrefixes.filter((prefix) => prefix !== PREFIX && prefix !== PREVIOUS_PREFIX).sort();
  const largestFiles = rows.slice(0, 15).map(({ hash, ...row }) => row);
  const largestDuplicateDocGroups = duplicateDocGroups.slice(0, 15).map(({ hash, ...group }) => group);
  const currentArtifactBytes = byArtifactPrefix[PREFIX] || 0;
  const previousArtifactBytes = byArtifactPrefix[PREVIOUS_PREFIX] || 0;
  const checks = [
    check('total-source-bytes-under-soft-budget', totalBytes <= SOFT_TOTAL_BYTES, { totalBytes, softBudgetBytes: SOFT_TOTAL_BYTES }),
    check('artifact-prefixes-current-or-previous', oldArtifactPrefixes.length === 0, { currentPrefix: PREFIX, previousPrefix: PREVIOUS_PREFIX, oldArtifactPrefixes }),
    check('duplicate-doc-bytes-under-soft-budget', duplicateDocBytes <= SOFT_DUPLICATE_DOC_BYTES, { duplicateDocBytes, softBudgetBytes: SOFT_DUPLICATE_DOC_BYTES, duplicateDocGroupCount: duplicateDocGroups.length }),
    check('current-artifacts-present', currentArtifactBytes > 0, { currentPrefix: PREFIX, currentArtifactBytes }),
    check('previous-artifacts-retained-but-bounded', previousArtifactBytes < totalBytes * 0.6, { previousPrefix: PREVIOUS_PREFIX, previousArtifactBytes, totalBytes }),
    check('historical-revision-doc-compaction-recorded', Boolean(historicalCompaction?.counts?.compactedCount) && historicalCompaction.counts.compactedCount === historicalRevTombstoneCount && historicalCompaction.counts.estimatedSavingsBytes > SOFT_DUPLICATE_DOC_BYTES, { historicalCompactionPath, historicalRevTombstoneCount, estimatedSavingsBytes: historicalCompaction?.counts?.estimatedSavingsBytes || 0 })
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(),
    purpose: 'Cloudtainer artifact budget and duplicate-content audit: make package waste visible enough to correct without adding another prose-only registry.',
    budgets: { softTotalBytes: SOFT_TOTAL_BYTES, softDuplicateDocBytes: SOFT_DUPLICATE_DOC_BYTES },
    counts: { fileCount: rows.length, totalBytes, artifactFileCount: rows.filter((row) => row.path.startsWith('artifacts/')).length, revSuffixedDocCount: revSuffixedDocRows.length, historicalRevTombstoneCount, duplicateGroupCount: duplicateGroups.length, duplicateDocGroupCount: duplicateDocGroups.length, duplicateDocBytes, potentialDuplicateSavingsBytes: duplicateGroups.reduce((sum, group) => sum + group.duplicateBytes, 0) },
    bytes: { byTopLevel: sortObjectByValueDesc(byTopLevel), byArtifactArea: sortObjectByValueDesc(byArtifactArea), byArtifactPrefix: sortObjectByValueDesc(byArtifactPrefix) },
    checks, largestFiles, largestDuplicateDocGroups,
    historicalCompaction: historicalCompaction ? { status: historicalCompaction.status, counts: historicalCompaction.counts } : null,
    recommendations: [duplicateDocGroups.length ? 'Compact exact duplicate rev-suffixed docs by keeping the newest copy plus a compaction index.' : null, oldArtifactPrefixes.length ? 'Remove artifacts older than current and previous revision from release zips or summarize them under artifacts/datacube-audit/.' : null, totalBytes > SOFT_TOTAL_BYTES * 0.75 ? 'Keep current proof artifacts and previous differential artifacts; move older generated evidence to a changelog/index.' : null].filter(Boolean),
    nonClaims: ['Artifact budget audit does not prove runtime correctness or browser behavior.', 'Duplicate-content grouping is byte-identical only; it does not judge whether distinct historical wording remains useful.', 'Soft budgets are cloudtainer ergonomics checks, not product-size requirements.']
  };
}
const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2));
if (report.status !== 'passed') process.exitCode = 1;
