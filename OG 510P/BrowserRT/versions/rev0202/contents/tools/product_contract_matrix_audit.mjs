#!/usr/bin/env node
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_JSON = `artifacts/audit/${PREFIX}-PRODUCT-CONTRACT-MATRIX-AUDIT.json`;
const DOC = 'docs/20-architecture/product-contract-matrix-rev0151.md';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

async function readText(path) {
  try { return await readFile(path, 'utf8'); }
  catch (error) { return null; }
}

function missingNeedles(body, needles) {
  const lower = body.toLowerCase();
  return needles.filter((needle) => !lower.includes(needle.toLowerCase()));
}

export async function runAudit({ jsonOut = DEFAULT_JSON } = {}) {
  const body = await readText(DOC);
  const checks = [];
  const add = (name, status, details = {}) => checks.push({ name, status: status ? 'passed' : 'failed', ...details });
  add('matrix-doc-exists', Boolean(body), { doc: DOC });
  const required = [
    'supportable browser-local failure kernel',
    'admission before mutation',
    'OPFS timing side-channel',
    'FROST',
    'Web Locks',
    'AbortSignal',
    'StorageManager.estimate',
    'persistent storage grant',
    'quota reservation',
    'dogfood',
    'Next change',
    'https://developer.mozilla.org/en-US/docs/Web/API/File_System_API/Origin_private_file_system',
    'https://www.w3.org/TR/web-locks/',
    'https://developer.chrome.com/docs/web-platform/storage-buckets',
    'https://hannesweissteiner.com/pdfs/frost.pdf',
    'https://sqlite.org/wasm/doc/trunk/persistence.md',
    'https://web.dev/articles/cross-origin-isolation-guide'
  ];
  const missing = body ? missingNeedles(body, required) : required;
  add('matrix-covers-product-risk-research-and-nonclaims', missing.length === 0, { missing });
  const rows = body ? (body.match(/^\| [^\n]+ \|$/gm) || []).length : 0;
  add('matrix-has-substantive-row-count', rows >= 10, { rows });
  const stopDoing = body ? missingNeedles(body, ['Stop doing', 'registry', 'generated artifacts', 'browser-heavy probes']) : [];
  add('matrix-has-stop-doing-section', body && stopDoing.length === 0, { missing: stopDoing });
  const status = checks.every((check) => check.status === 'passed') ? 'passed' : 'failed';
  const report = {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status,
    generatedAt: new Date().toISOString(),
    purpose: 'Audit the rev0151 product contract matrix: keep the mission product-shaped, web-researched, and non-claim-safe rather than registry-shaped.',
    doc: DOC,
    checks,
    nonClaims: [
      'This audit validates product-risk framing, not runtime behavior.',
      'Storage Buckets, SQLite OPFS, and cross-origin isolation notes remain research posture, not current BrowserRT claims.',
      'Current proof office remains OPFS Raw Composite AbortSignal.'
    ]
  };
  await mkdir(dirname(jsonOut), { recursive: true });
  await writeFile(jsonOut, JSON.stringify(report, null, 2) + '\n');
  return report;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const jsonOut = argValue(process.argv.slice(2), '--json', DEFAULT_JSON);
  const report = await runAudit({ jsonOut });
  console.log(jsonOut);
  if (report.status !== 'passed') process.exitCode = 1;
}
