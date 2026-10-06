#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-handoff-markdown-proof. Release-tier proof for human-pasteable Kernel Kit next-session Markdown.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitSupportBundleDiff,
  createKernelKitGuidedTourReceipt,
  createKernelKitHandoffMarkdown,
  validateKernelKitHandoffMarkdown,
  KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT
} from '../src/browserrt.mjs';
import { runProbe as runSupportBundleProbe } from './kernel_kit_support_bundle_probe.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-HANDOFF-MARKDOWN-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

export async function runProbe() {
  const supportSource = await runSupportBundleProbe();
  const supportBundle = supportSource.supportBundle;
  const diff = createKernelKitSupportBundleDiff(supportBundle, JSON.stringify(supportBundle), { revision: REVISION, generatedAt: 'deterministic-handoff-markdown-diff' });
  const guidedTour = createKernelKitGuidedTourReceipt({ revision: REVISION, supportBundle, generatedAt: 'deterministic-handoff-markdown-guided-tour' });
  const handoffMarkdown = createKernelKitHandoffMarkdown({ revision: REVISION, supportBundle, diff, guidedTour, generatedAt: 'deterministic-handoff-markdown-probe' });
  const validation = validateKernelKitHandoffMarkdown(handoffMarkdown);

  assert.equal(handoffMarkdown.format, KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(handoffMarkdown.status, 'handoff-ready');
  assert.ok(handoffMarkdown.markdown.includes('# BrowserRT Kernel Kit Handoff'));
  assert.ok(handoffMarkdown.markdown.includes('## Exact commands'));
  assert.ok(handoffMarkdown.markdown.includes('demo:kernel-kit-handoff-markdown-proof'));
  assert.ok(handoffMarkdown.markdown.includes('facility:kernel-kit-handoff-markdown-audit'));
  assert.ok(handoffMarkdown.markdown.includes('browser:kernel-kit-demo-proof'));
  assert.ok(handoffMarkdown.markdown.includes('No production handoff-markdown claim.'));
  assert.equal(handoffMarkdown.proof.successPathPresent, true);
  assert.equal(handoffMarkdown.proof.controlledFailurePresent, true);
  assert.equal(handoffMarkdown.proof.diagnosticRunbookPresent, true);
  assert.equal(handoffMarkdown.proof.exactCommandsPresent, true);
  assert.equal(handoffMarkdown.proof.nonClaimsVisible, true);
  assert.ok(validation.markdownBytes > 1500, 'handoff markdown should be substantial enough to hand off');

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-handoff-markdown-probe`,
    status: 'passed',
    supportProbeId: supportSource.probe_id,
    handoffMarkdown,
    validation,
    proof: {
      handoffMarkdownValid: validation.ok,
      handoffReady: handoffMarkdown.status === 'handoff-ready',
      markdownHasTitle: handoffMarkdown.markdown.includes('# BrowserRT Kernel Kit Handoff'),
      exactCommandsPresent: handoffMarkdown.proof.exactCommandsPresent,
      nonClaimsVisible: handoffMarkdown.proof.nonClaimsVisible,
      supportBundleValid: handoffMarkdown.supportBundle.validation.ok,
      guidedTourValid: handoffMarkdown.guidedTour.validation.ok,
      sameBundleDiffValid: handoffMarkdown.supportBundleDiff.validation.ok,
      markdownBytes: validation.markdownBytes
    },
    nonClaims: handoffMarkdown.nonClaims
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runProbe();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(report, null, 2));

// Static audit markers: browserrt-kernel-kit-handoff-markdown-v1; No production handoff-markdown claim.; demo:kernel-kit-handoff-markdown-proof.
