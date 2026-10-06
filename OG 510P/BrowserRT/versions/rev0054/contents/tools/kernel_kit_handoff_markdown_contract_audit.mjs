#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-handoff-markdown-audit. Release-tier contract audit for the handoff Markdown workbench.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, createKernelKitHandoffMarkdown, validateKernelKitHandoffMarkdown } from '../src/browserrt.mjs';
import { runProbe as runHandoffMarkdownProbe } from './kernel_kit_handoff_markdown_probe.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-KERNEL-KIT-HANDOFF-MARKDOWN-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function includesAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runHandoffMarkdownProbe();
  const validation = validateKernelKitHandoffMarkdown(proof.handoffMarkdown);
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const inventory = await json('test/surface-inventory.json');
  const receipt = await json('REVISION-RECEIPT.json');
  const source = await text('src/kernel-kit-handoff-markdown.mjs');
  const runtime = await text('src/browserrt.mjs');
  const types = await text('src/types.d.ts');
  const page = await text('demo/kernel-kit-demo.html');
  const runner = await text('demo/kernel-kit-demo-runner.mjs');
  const browserTool = await text('tools/browser_kernel_kit_demo_probe.mjs');
  const proofTool = await text('tools/kernel_kit_handoff_markdown_probe.mjs');
  const docs = await Promise.all([
    `docs/20-architecture/kernel-kit-handoff-markdown-frontier.md`,
    `docs/40-validation/kernel-kit-handoff-markdown-slice.md`,
    `docs/40-validation/kernel-kit-handoff-markdown-contract-audit-${REVISION}.md`,
    `docs/50-roadmap/kernel-kit-handoff-markdown-roadmap-${REVISION}.md`,
    `docs/00-meta/cube-audit-${REVISION}.md`
  ].map(async (path) => [path, await text(path)]));
  const tasks = new Map((manifest.tasks || []).map((task) => [task.id, task]));
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []).concat((inventory.surfaces || []).flatMap((surface) => surface.manifestTasks || [])));
  const docNeedles = ['Kernel Kit handoff Markdown', 'browserrt-kernel-kit-handoff-markdown-v1', 'demo:kernel-kit-handoff-markdown-proof', 'facility:kernel-kit-handoff-markdown-audit', 'No production handoff-markdown claim.'];
  const docsMissing = docs.flatMap(([path, body]) => includesAll(body, docNeedles).map((needle) => ({ path, needle })));
  const checks = [
    check('proof-validates', validation.ok, { validation }),
    check('source-exports-format-and-nonclaims', includesAll(source, ['KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT', 'createKernelKitHandoffMarkdown', 'validateKernelKitHandoffMarkdown', 'No production handoff-markdown claim.']).length === 0),
    check('runtime-exports-handoff-markdown', includesAll(runtime, ['createKernelKitHandoffMarkdown', 'validateKernelKitHandoffMarkdown', 'KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT', 'kernelKitHandoffMarkdown']).length === 0),
    check('types-exports-handoff-markdown', includesAll(types, ['KernelKitHandoffMarkdown', 'createKernelKitHandoffMarkdown', 'validateKernelKitHandoffMarkdown']).length === 0),
    check('page-has-handoff-markdown-controls', includesAll(page, ['Build handoff Markdown', 'kernel-kit-handoff-markdown-output', 'demo:kernel-kit-handoff-markdown-proof']).length === 0),
    check('runner-exposes-handoff-markdown-api', includesAll(runner, ['buildKernelKitHandoffMarkdown', 'renderKernelKitHandoffMarkdown', 'BrowserRTKernelKitDemo.buildHandoffMarkdown', 'window.__BROWSERRT_KERNEL_KIT_HANDOFF_MARKDOWN']).length === 0),
    check('browser-proof-drives-handoff-markdown', includesAll(browserTool, ['exprForHandoffMarkdown', 'validateKernelKitHandoffMarkdown', 'handoffMarkdown']).length === 0),
    check('proof-tool-names-slice', includesAll(proofTool, ['demo:kernel-kit-handoff-markdown-proof', 'browserrt-kernel-kit-handoff-markdown-v1', 'No production handoff-markdown claim.']).length === 0),
    check('manifest-proof-task-present', Boolean(tasks.get('demo:kernel-kit-handoff-markdown-proof')) && tasks.get('demo:kernel-kit-handoff-markdown-proof').tiers?.includes('release')),
    check('manifest-audit-task-present', Boolean(tasks.get('facility:kernel-kit-handoff-markdown-audit')) && tasks.get('facility:kernel-kit-handoff-markdown-audit').tiers?.includes('release')),
    check('impact-map-covers-handoff-markdown', ['demo:kernel-kit-handoff-markdown-proof','facility:kernel-kit-handoff-markdown-audit','browser:kernel-kit-demo-proof'].every((id) => impactIds.has(id))),
    check('surface-inventory-covers-handoff-markdown', ['demo:kernel-kit-handoff-markdown-proof','facility:kernel-kit-handoff-markdown-audit','browser:kernel-kit-demo-proof'].every((id) => inventoryIds.has(id))),
    check('docs-cover-handoff-markdown', docsMissing.length === 0, { docsMissing }),
    check('receipt-current-audit-slice', receipt.current_audit_slice === 'facility:kernel-kit-handoff-markdown-audit', { current_audit_slice: receipt.current_audit_slice }),
    check('receipt-nonclaims-preserved', (receipt.non_claims || []).includes('No production handoff-markdown claim.') && (receipt.non_claims || []).includes('No support-bundle authenticity or signature claim.'))
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-handoff-markdown-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    generatedAt: new Date().toISOString(),
    purpose: 'Release-tier audit for the Kernel Kit handoff Markdown workbench. It checks source/export/type/page/proof/doc/manifest/impact/inventory/non-claim wiring without launching Chromium.',
    checks,
    proofValidation: validation,
    nonClaims: proof.handoffMarkdown.nonClaims
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(report, null, 2));
assert.equal(report.status, 'passed');

// Static audit markers: browserrt-kernel-kit-handoff-markdown-v1; facility:kernel-kit-handoff-markdown-audit; No production handoff-markdown claim.
