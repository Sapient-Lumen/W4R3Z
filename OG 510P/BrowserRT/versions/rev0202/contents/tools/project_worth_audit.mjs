#!/usr/bin/env node
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, createProjectContinuationAssessment, validateProjectContinuationAssessment } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
};
const prefix = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${prefix}-PROJECT-WORTH-AUDIT.json`);
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function hasAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }

const assessment = createProjectContinuationAssessment();
const validation = validateProjectContinuationAssessment(assessment);
const manifest = await json('test/manifest.json');
const tasks = new Map((manifest.tasks || []).map((task) => [task.id, task]));
const registry = await json('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json');
const docs = {
  assessment: await text('docs/00-meta/project-continuation-assessment-rev0044.md'),
  research: await text('docs/05-research/related-work-research-pass-036.md'),
  architecture: await text('docs/20-architecture/project-worth-and-beneficiaries.md'),
  slice: await text('docs/40-validation/project-worth-audit-slice.md'),
  roadmap: await text('docs/50-roadmap/continue-narrow-wedge-roadmap.md'),
  context: await text('CONTEXT-PACK.md'),
  charter: await text('docs/00-meta/non-claims-and-goals-charter.md'),
  office: await text('docs/00-meta/future-session-office-manual.md'),
  readme: await text('README.md'),
  start: await text('START_HERE.md')
};
const task = tasks.get('facility:project-worth-audit');
const titles = new Set((registry.families || []).flatMap((fam) => fam.sources || []).map((src) => src.title));
const sourceTitles = ['WebContainers browser runtime','Comlink worker RPC','workerd open source Workers runtime','Deno permission model','DuckDB-Wasm browser client','SQLite Wasm OPFS persistence options','Tauri cross-platform app framework','Ray actors and object refs','Origin private file system - MDN','SharedArrayBuffer cross-origin isolation - MDN','WebGPU API - MDN','Web Locks API same-origin coordination'];
const nonClaims = assessment.requiredNonClaims;
const requiredDocNeedles = ['continue-but-narrow','BrowserRT Kernel Kit','Who benefits','No market validation claim','No product-market-fit claim','No production runtime claim'];
const requiredNonClaimLiteralsForCubeAudit = ['No market validation claim.','No product-market-fit claim.','No production runtime claim.'];

const checks = [
  check('assessment-validates', validation.ok, { errors: validation.errors }),
  check('verdict-continue-but-narrow', assessment.verdict === 'continue-but-narrow' && assessment.decision.continue === true && assessment.decision.kill === false),
  check('beneficiary-map-complete', assessment.beneficiaries.length >= 6 && assessment.nonBeneficiaries.length >= 5),
  check('competition-map-complete', assessment.competitionMap.length >= 6),
  check('continuation-and-kill-gates-complete', assessment.continuationGates.length >= 5 && assessment.killConditions.length >= 5),
  check('manifest-task-present-release-browser-light', Boolean(task) && task.tiers?.includes('release') && task.lane !== 'browser'),
  check('source-registry-covers-assessment', sourceTitles.every((title) => titles.has(title)), { missing: sourceTitles.filter((title) => !titles.has(title)) }),
  ...Object.entries(docs).map(([name, body]) => check(`doc-${name}-legible`, hasAll(body, requiredDocNeedles).length === 0, { missing: hasAll(body, requiredDocNeedles) })),
  check('non-claims-carried-by-handoff', ['context','charter','office','assessment','slice'].every((key) => nonClaims.every((claim) => docs[key].includes(claim))), {
    missing: Object.fromEntries(['context','charter','office','assessment','slice'].map((key) => [key, nonClaims.filter((claim) => !docs[key].includes(claim))]))
  })
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  schema: 1,
  task: 'facility:project-worth-audit',
  status: failed.length ? 'failed' : 'passed',
  generatedAt: new Date().toISOString(),
  purpose: 'Audit that BrowserRT carries a legible continue/narrow/kill decision surface without promoting unearned market, runtime, performance, durability, or conformance claims.',
  verdict: assessment.verdict,
  recommendedNextWedge: assessment.recommendedNextWedge,
  checks,
  nonClaims: [
    'Project worth audit does not prove market demand, product-market fit, production readiness, browser performance, durability, or cross-browser conformance.',
    ...requiredNonClaimLiteralsForCubeAudit,
    ...nonClaims
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (failed.length) process.exitCode = 1;
