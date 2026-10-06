#!/usr/bin/env node
import { readdir, readFile, rm, writeFile, mkdir, stat } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, relative } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_JSON = `artifacts/datacube-audit/${PREFIX}-INACTIVE-EVIDENCE-COMPACTION.json`;
const DEFAULT_MD = 'docs/00-meta/inactive-evidence-compaction-index-rev0151.md';
const CORE_JSON = ['package.json', 'CUBE-META.json', 'REVISION-RECEIPT.json', 'REENTRY-CONTRACT.json', 'SURFACE-STATUS.json', 'VALIDATION-INDEX.json'];
const CENTRAL_REF_FIELDS = ['added','changed','must_read','current_artifacts','artifacts','artifacts_added_or_updated','current_validations','current_commands','current_validation_commands','last_verified_commands','validation_commands','package_commands'];
const ALWAYS_KEEP = new Set([
  `artifacts/audit/${PREFIX}-CUBE-AUDIT.json`,
  `artifacts/audit/${PREFIX}-DEEP-CUBE-AUDIT.json`,
  `artifacts/audit/${PREFIX}-ARTIFACT-BUDGET-AUDIT.json`,
  `artifacts/audit/${PREFIX}-PRODUCT-CONTRACT-MATRIX-AUDIT.json`,
  `artifacts/audit/${PREFIX}-LINKED-CURRENT-AUDIT.json`,
  `artifacts/datacube-audit/${PREFIX}-INACTIVE-EVIDENCE-COMPACTION.json`,
  `artifacts/datacube-audit/${PREFIX}-TEST-REGISTRY-COMPACTION.json`
]);

const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

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
async function readJson(path) { return JSON.parse(await readFile(path, 'utf8')); }
async function maybeStat(path) { try { return await stat(path); } catch { return null; } }
function artifactRefsFromCentral(obj) {
  const refs = new Set();
  const re = new RegExp(`artifacts/(?:validation|audit|proof|datacube-audit|pruned-index)/${PREFIX}-[A-Z0-9-]+\\.json`, 'g');
  for (const field of CENTRAL_REF_FIELDS) {
    if (!(field in obj)) continue;
    for (const hit of JSON.stringify(obj[field]).match(re) || []) refs.add(hit);
  }
  return refs;
}
async function centralKeepSet() {
  const keep = new Set(ALWAYS_KEEP);
  for (const rel of CORE_JSON) {
    const obj = await readJson(rel);
    for (const ref of artifactRefsFromCentral(obj)) keep.add(ref);
  }
  return keep;
}
async function removeEmptyDirs(dir) {
  let entries;
  try { entries = await readdir(dir, { withFileTypes: true }); } catch { return; }
  for (const ent of entries) if (ent.isDirectory()) await removeEmptyDirs(`${dir}/${ent.name}`);
  try {
    const after = await readdir(dir);
    if (after.length === 0 && dir !== 'docs/00-meta' && dir !== 'artifacts' && dir !== 'artifacts/validation' && dir !== 'artifacts/audit' && dir !== 'artifacts/proof' && dir !== 'artifacts/datacube-audit') await rm(dir, { recursive: true, force: true });
  } catch {}
}
function shouldCompactDocValidation(rel) {
  return rel.startsWith('docs/00-meta/') && rel.includes('-validation-artifacts/');
}
function shouldCompactInactiveArtifact(rel, keep) {
  if (!/^artifacts\/(validation|audit|proof)\//.test(rel)) return false;
  if (rel.includes(`${PREFIX}-BROWSER-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json`)) return false;
  if (rel.includes(`${PREFIX}-BROWSER-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.checkpoints/`)) return false;
  if (keep.has(rel)) return false;
  return true;
}
function summarizeRows(rows) {
  const byReason = {};
  const byArea = {};
  for (const row of rows) {
    byReason[row.reason] = (byReason[row.reason] || 0) + row.bytes;
    const area = row.path.split('/').slice(0, 2).join('/');
    byArea[area] = (byArea[area] || 0) + row.bytes;
  }
  const sortObj = (obj) => Object.fromEntries(Object.entries(obj).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
  return { byReason: sortObj(byReason), byArea: sortObj(byArea) };
}
async function buildRows(keep) {
  const rows = [];
  for (const file of await walk('.')) {
    const rel = relative('.', file);
    if (rel === DEFAULT_JSON || rel === DEFAULT_MD) continue;
    let reason = null;
    if (shouldCompactDocValidation(rel)) reason = 'historical-linked-validation-artifact';
    else if (shouldCompactInactiveArtifact(rel, keep)) reason = 'inactive-generated-artifact';
    else if (/^artifacts\/(validation|audit|proof)\/TMP-/.test(rel)) reason = 'temporary-cloudtainer-artifact';
    if (!reason) continue;
    const bytes = await readFile(file);
    rows.push({ path: rel, bytes: bytes.length, sha256: sha256(bytes), reason });
  }
  rows.sort((a, b) => b.bytes - a.bytes || a.path.localeCompare(b.path));
  return rows;
}
function markdownIndex(report) {
  const sample = report.compacted.slice(0, 120).map((row) => `| ${row.path} | ${row.bytes} | ${row.sha256.slice(0, 16)}… | ${row.reason} |`).join('\n');
  return `# Inactive evidence compaction index — linked rev0151\n\nRuntime current office remains ${REVISION} / OPFS Raw Composite AbortSignal. This linked refactor removes regenerated or historical raw evidence from the active cloudtainer and preserves path, byte count, SHA-256, and reason so the old proof material remains attributable without crowding current work.\n\n## Summary\n\n- Status: ${report.status}\n- Files compacted: ${report.counts.compactedFileCount}\n- Bytes compacted: ${report.counts.compactedBytes}\n- Central/current artifacts retained: ${report.counts.centralArtifactKeepCount}\n- JSON receipt: \`${DEFAULT_JSON}\`\n\n## Largest compacted rows\n\n| Path | Bytes | SHA-256 prefix | Reason |\n|---|---:|---|---|\n${sample}\n\n## Non-claims\n\nThis does not delete the executable tools, source code, or current-office anchors. It does not claim historical validation is unimportant; it moves old/generated evidence out of the active byte path so current risk work can finish. Raw compacted artifacts are not recoverable from this package without an older archive; the retained hash index is provenance, not content.\n`;
}
export async function runCompaction({ dryRun = false, jsonOut = DEFAULT_JSON, markdownOut = DEFAULT_MD } = {}) {
  const keep = await centralKeepSet();
  const compacted = await buildRows(keep);
  const beforeBytes = compacted.reduce((sum, row) => sum + row.bytes, 0);
  if (!dryRun) {
    for (const row of compacted) await rm(row.path, { force: true });
    await removeEmptyDirs('docs/00-meta');
    await removeEmptyDirs('artifacts');
  }
  const report = {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Compact historical linked validation blobs and inactive generated artifacts into a hash/provenance index so cloudtainer work stays product-risk focused rather than proof-archive bound.',
    dryRun,
    counts: { compactedFileCount: compacted.length, compactedBytes: beforeBytes, centralArtifactKeepCount: keep.size },
    bytes: summarizeRows(compacted),
    retainedCentralArtifacts: [...keep].sort(),
    compacted,
    nonClaims: [
      'Compaction does not prove runtime correctness or browser behavior.',
      'Compaction preserves hashes and paths, not raw historical artifact bodies.',
      'Current-office source files, tools, manifest, and central artifact references are intentionally retained.'
    ]
  };
  if (!dryRun) {
    await mkdir(dirname(jsonOut), { recursive: true });
    await writeFile(jsonOut, JSON.stringify(report, null, 2) + '\n');
    await mkdir(dirname(markdownOut), { recursive: true });
    await writeFile(markdownOut, markdownIndex(report));
  }
  return report;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const argv = process.argv.slice(2);
  const jsonOut = argValue(argv, '--json', DEFAULT_JSON);
  const markdownOut = argValue(argv, '--markdown', DEFAULT_MD);
  const dryRun = hasFlag(argv, '--dry-run');
  const report = await runCompaction({ dryRun, jsonOut, markdownOut });
  console.log(dryRun ? JSON.stringify(report, null, 2) : jsonOut);
}
