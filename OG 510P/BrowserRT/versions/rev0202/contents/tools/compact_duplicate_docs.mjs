#!/usr/bin/env node
import { readdir, readFile, rm, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_JSON = `artifacts/datacube-audit/${PREFIX}-DUPLICATE-DOC-COMPACTION.json`;
const DEFAULT_INDEX = `docs/00-meta/revision-doc-compaction-index-${REVISION}.md`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);
async function walk(dir = 'docs') { const out = []; for (const ent of await readdir(dir, { withFileTypes: true })) { const p = `${dir}/${ent.name}`; if (ent.isDirectory()) out.push(...await walk(p)); else out.push(p); } return out; }
function sha256(bytes) { return createHash('sha256').update(bytes).digest('hex'); }
function revNumber(path) { const matches = [...String(path).matchAll(/rev(\d{4})/g)].map((m) => Number(m[1])); return matches.length ? Math.max(...matches) : -1; }
function isRevSuffixedDoc(path) { return path.startsWith('docs/') && /(?:^|-)rev\d{4}\./.test(path); }
function newestFirst(a, b) { return revNumber(b) - revNumber(a) || b.localeCompare(a); }
export async function planCompaction() {
  const groups = new Map();
  for (const path of await walk('docs')) {
    if (!isRevSuffixedDoc(path)) continue;
    const bytes = await readFile(path);
    const hash = sha256(bytes);
    if (!groups.has(hash)) groups.set(hash, []);
    groups.get(hash).push({ path, bytes: bytes.length });
  }
  const duplicateGroups = [...groups.values()].filter((group) => group.length > 1).map((group) => {
    const sorted = group.slice().sort((a, b) => newestFirst(a.path, b.path));
    const keep = sorted[0];
    const remove = sorted.slice(1);
    return { keep: keep.path, keepBytes: keep.bytes, remove: remove.map((row) => row.path), duplicateBytes: remove.reduce((sum, row) => sum + row.bytes, 0) };
  }).sort((a, b) => b.duplicateBytes - a.duplicateBytes || a.keep.localeCompare(b.keep));
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, generatedAt: new Date().toISOString(), status: 'planned', purpose: 'Compact exact duplicate rev-suffixed Markdown documents by keeping the newest byte-identical copy and indexing removed aliases.', duplicateGroupCount: duplicateGroups.length, removableFileCount: duplicateGroups.reduce((sum, group) => sum + group.remove.length, 0), duplicateBytes: duplicateGroups.reduce((sum, group) => sum + group.duplicateBytes, 0), groups: duplicateGroups, nonClaims: ['Compaction only removes byte-identical rev-suffixed docs; unique historical docs remain.', 'The compaction index is an alias ledger, not a substitute for CHANGELOG.md history.', 'This tool does not compact generated validation/proof artifacts.'] };
}
function renderIndex(report) {
  const lines = [];
  lines.push(`# Revision doc compaction index — ${REVISION}`, '', 'This index records byte-identical rev-suffixed Markdown files removed from the release package to reduce cloudtainer retrieval waste. The newest identical copy is retained; unique historical docs are not compacted.', '', `- Duplicate groups compacted: ${report.duplicateGroupCount}`, `- Removed files: ${report.removableFileCount}`, `- Bytes removed before ZIP compression: ${report.duplicateBytes}`, '', '## Alias ledger', '');
  for (const group of report.groups) { lines.push(`### Kept: \`${group.keep}\``, '', `Removed ${group.remove.length} exact duplicate file(s), ${group.duplicateBytes} byte(s):`, ''); for (const path of group.remove) lines.push(`- \`${path}\``); lines.push(''); }
  if (!report.groups.length) lines.push('No byte-identical rev-suffixed Markdown duplicates found.', '');
  lines.push('## Non-claims', ''); for (const claim of report.nonClaims) lines.push(`- ${claim}`); lines.push(''); return lines.join('\n');
}
const argv = process.argv.slice(2);
const apply = hasFlag(argv, '--apply');
const jsonOut = argValue(argv, '--json', DEFAULT_JSON);
const indexOut = argValue(argv, '--index', DEFAULT_INDEX);
const report = await planCompaction();
if (apply) { for (const group of report.groups) for (const path of group.remove) await rm(path, { force: true }); report.status = 'applied'; }
await mkdir(dirname(jsonOut), { recursive: true }); await writeFile(jsonOut, JSON.stringify(report, null, 2) + '\n');
await mkdir(dirname(indexOut), { recursive: true }); await writeFile(indexOut, renderIndex(report));
console.log(JSON.stringify({ jsonOut, indexOut, status: report.status, removed: apply ? report.removableFileCount : 0, duplicateBytes: report.duplicateBytes }, null, 2));
