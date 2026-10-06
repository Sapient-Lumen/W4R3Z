#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-handoff-markdown-import-audit. Release-tier contract audit for the handoff Markdown import/reader surface.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, validateKernelKitHandoffMarkdownImportReport } from '../src/browserrt.mjs';
import { runProbe as runHandoffMarkdownImportProbe } from './kernel_kit_handoff_markdown_import_probe.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-KERNEL-KIT-HANDOFF-MARKDOWN-IMPORT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runHandoffMarkdownImportProbe();
  const validation = validateKernelKitHandoffMarkdownImportReport(proof.importReport);
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const inventory = await json('test/surface-inventory.json');
  const receipt = await json('REVISION-RECEIPT.json');
  const source = await text('src/kernel-kit-handoff-reader.mjs');
  const runtime = await text('src/browserrt.mjs');
  const types = await text('src/types.d.ts');
  const page = await text('demo/kernel-kit-demo.html');
  const runner = await text('demo/kernel-kit-demo-runner.mjs');
  const browserTool = await text('tools/browser_kernel_kit_demo_probe.mjs');
  const proofTool = await text('tools/kernel_kit_handoff_markdown_import_probe.mjs');
  const docs = await Promise.all([
    `docs/20-architecture/kernel-kit-handoff-markdown-import-frontier.md`,
    `docs/40-validation/kernel-kit-handoff-markdown-import-slice.md`,
    `docs/40-validation/kernel-kit-handoff-markdown-import-contract-audit-${REVISION}.md`,
    `docs/50-roadmap/kernel-kit-handoff-markdown-import-roadmap-${REVISION}.md`,
    `docs/00-meta/cube-audit-${REVISION}.md`
  ].map(async (path) => [path, await text(path)]));
  const tasks = new Map((manifest.tasks || []).map((task) => [task.id, task]));
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => (surface.currentTaskIds || []).concat(surface.manifestTasks || [])));
  const docNeedles = ['Kernel Kit handoff Markdown import', 'browserrt-kernel-kit-handoff-markdown-import-v1', 'demo:kernel-kit-handoff-markdown-import-proof', 'facility:kernel-kit-handoff-markdown-import-audit', 'No production handoff-markdown import claim.'];
  const docsMissing = docs.flatMap(([path, body]) => missing(body, docNeedles).map((needle) => ({ path, needle })));
  const checks = [
    check('proof-validates', validation.ok, { validation }),
    check('source-exports-import-reader', missing(source, ['KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT','createKernelKitHandoffMarkdownImportReport','validateKernelKitHandoffMarkdownImportReport','No production handoff-markdown import claim.']).length === 0),
    check('runtime-exports-import-reader', missing(runtime, ['createKernelKitHandoffMarkdownImportReport','validateKernelKitHandoffMarkdownImportReport','KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT','kernelKitHandoffMarkdownImport']).length === 0),
    check('types-exports-import-reader', missing(types, ['KernelKitHandoffMarkdownImportReport','createKernelKitHandoffMarkdownImportReport','validateKernelKitHandoffMarkdownImportReport']).length === 0),
    check('page-has-import-controls', missing(page, ['Validate handoff Markdown','kernel-kit-handoff-markdown-import-input','kernel-kit-handoff-markdown-import-output','No production handoff-markdown import claim.']).length === 0),
    check('runner-exposes-import-api', missing(runner, ['importKernelKitHandoffMarkdown','renderKernelKitHandoffMarkdownImportReport','BrowserRTKernelKitDemo.importHandoffMarkdown','window.__BROWSERRT_KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT']).length === 0),
    check('browser-proof-drives-import-api', missing(browserTool, ['exprForHandoffMarkdownImport','validateKernelKitHandoffMarkdownImportReport','handoffMarkdownImport']).length === 0),
    check('proof-tool-names-slice', missing(proofTool, ['demo:kernel-kit-handoff-markdown-import-proof','browserrt-kernel-kit-handoff-markdown-import-v1','No production handoff-markdown import claim.']).length === 0),
    check('manifest-proof-task-present', Boolean(tasks.get('demo:kernel-kit-handoff-markdown-import-proof')) && tasks.get('demo:kernel-kit-handoff-markdown-import-proof').tiers?.includes('release')),
    check('manifest-audit-task-present', Boolean(tasks.get('facility:kernel-kit-handoff-markdown-import-audit')) && tasks.get('facility:kernel-kit-handoff-markdown-import-audit').tiers?.includes('release')),
    check('impact-map-covers-import', ['demo:kernel-kit-handoff-markdown-import-proof','facility:kernel-kit-handoff-markdown-import-audit','browser:kernel-kit-demo-proof'].every((id) => impactIds.has(id))),
    check('surface-inventory-covers-import', ['demo:kernel-kit-handoff-markdown-import-proof','facility:kernel-kit-handoff-markdown-import-audit','browser:kernel-kit-demo-proof'].every((id) => inventoryIds.has(id))),
    check('docs-cover-import', docsMissing.length === 0, { docsMissing }),
    check('receipt-current-or-carried-forward-audit-slice', receipt.current_audit_slice === 'facility:kernel-kit-handoff-markdown-import-audit' || (receipt.carried_forward_audits || []).includes('facility:kernel-kit-handoff-markdown-import-audit'), { current_audit_slice: receipt.current_audit_slice, carried_forward_audits: receipt.carried_forward_audits || [] }),
    check('receipt-nonclaims-preserved', (receipt.non_claims || []).includes('No production handoff-markdown import claim.') && (receipt.non_claims || []).includes('No automated next-session correctness claim.'))
  ];
  const failed = checks.filter((row) => row.status === 'failed');
  assert.equal(failed.length, 0, JSON.stringify(failed, null, 2));
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-handoff-markdown-import-contract-audit`,
    status: 'passed',
    proofProbeId: proof.probe_id,
    checks,
    proof: {
      importValid: validation.ok,
      pageApiWired: checks.find((row) => row.name === 'runner-exposes-import-api')?.status === 'passed',
      browserProofDrivesImport: checks.find((row) => row.name === 'browser-proof-drives-import-api')?.status === 'passed',
      manifestWired: checks.find((row) => row.name === 'manifest-proof-task-present')?.status === 'passed',
      docsCurrent: checks.find((row) => row.name === 'docs-cover-import')?.status === 'passed',
      nonClaimsVisible: checks.find((row) => row.name === 'receipt-nonclaims-preserved')?.status === 'passed'
    },
    nonClaims: proof.importReport.nonClaims
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(report, null, 2));

// Static audit markers: browserrt-kernel-kit-handoff-markdown-import-v1; No production handoff-markdown import claim.; facility:kernel-kit-handoff-markdown-import-audit.
