#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-support-bundle-privacy-scrub-proof. Release-tier proof for support-bundle privacy scrub handoff.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitSupportBundlePrivacyScrub,
  validateKernelKitSupportBundle,
  validateKernelKitSupportBundlePrivacyScrub,
  KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_FORMAT
} from '../src/browserrt.mjs';
import { runProbe as runSupportBundleProbe } from './kernel_kit_support_bundle_probe.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-SUPPORT-BUNDLE-PRIVACY-SCRUB-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function asString(value) { return JSON.stringify(value || {}); }
function findRawNeedles(bundle) {
  return [
    bundle?.handoff?.storageKey,
    bundle?.handoff?.prefix,
    bundle?.handoff?.digest,
    bundle?.handoff?.digest?.digest,
    bundle?.success?.proof?.digest,
    ...(bundle?.exactCommands || [])
  ].filter((value) => typeof value === 'string' && value.length > 8);
}

export async function runProbe() {
  const bundleProbe = await runSupportBundleProbe();
  const supportBundle = bundleProbe.supportBundle;
  const bundleValidation = validateKernelKitSupportBundle(supportBundle);
  assert.equal(bundleValidation.ok, true, bundleValidation.errors.join('; '));
  assert.equal(supportBundle.proof?.privacyScrubPresent, true);
  const embeddedValidation = validateKernelKitSupportBundlePrivacyScrub(supportBundle.privacyScrub);
  assert.equal(embeddedValidation.ok, true, embeddedValidation.errors.join('; '));
  const scrub = createKernelKitSupportBundlePrivacyScrub(supportBundle, {
    revision: REVISION,
    generatedAt: 'deterministic-support-bundle-privacy-scrub-probe',
    source: 'kernel-kit-support-bundle-privacy-scrub-probe'
  });
  const validation = validateKernelKitSupportBundlePrivacyScrub(scrub);
  assert.equal(scrub.format, KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_FORMAT);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(scrub.status, 'passed');
  assert.ok(validation.redactedFieldCount > 0, 'privacy scrub should redact sensitive support-bundle fields');
  assert.equal(scrub.proof?.sensitiveFieldsRedacted, true);
  assert.equal(scrub.proof?.exactCommandTextRedacted, true);
  assert.equal(scrub.proof?.proofBooleansPreserved, true);
  assert.equal(scrub.proof?.scrubDoesNotClaimAnonymization, true);
  assert.equal(scrub.proof?.scrubDoesNotValidateAuthenticity, true);
  const scrubbedText = asString(scrub.scrubbed);
  for (const forbidden of ['sha256:', 'browserrt/rev', 'BrowserRT.KernelKitDemo.handoff', 'http://', 'https://']) {
    assert.equal(scrubbedText.includes(forbidden), false, `scrubbed output leaked ${forbidden}`);
  }
  const rawNeedles = findRawNeedles(supportBundle);
  const leakedNeedles = rawNeedles.filter((needle) => scrubbedText.includes(needle));
  assert.deepEqual(leakedNeedles, [], `scrubbed output leaked raw support-bundle values: ${leakedNeedles.join(', ')}`);
  assert.ok((scrub.sourceSummary?.commandIds || []).every((id) => String(id).startsWith('fnv32:')), 'command IDs should be digests, not command text');
  assert.ok(scrub.nonClaims.includes('No anonymization, differential-privacy, or irreversible de-identification claim.'));
  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-support-bundle-privacy-scrub-probe`,
    status: 'passed',
    sourceProbeId: bundleProbe.probe_id,
    scrub,
    validation,
    proof: {
      bundleValidationOk: bundleValidation.ok === true,
      embeddedPrivacyScrubValid: embeddedValidation.ok === true,
      regeneratedPrivacyScrubValid: validation.ok === true,
      redactedFieldCount: validation.redactedFieldCount,
      sensitiveFieldsRedacted: scrub.proof?.sensitiveFieldsRedacted === true,
      exactCommandTextRedacted: scrub.proof?.exactCommandTextRedacted === true,
      proofBooleansPreserved: scrub.proof?.proofBooleansPreserved === true,
      rawSensitiveTokensAbsent: leakedNeedles.length === 0 && !['sha256:', 'browserrt/rev', 'BrowserRT.KernelKitDemo.handoff', 'http://', 'https://'].some((needle) => scrubbedText.includes(needle)),
      commandDigestsOnly: (scrub.sourceSummary?.commandIds || []).every((id) => String(id).startsWith('fnv32:')),
      doesNotClaimAnonymization: scrub.proof?.scrubDoesNotClaimAnonymization === true,
      doesNotValidateAuthenticity: scrub.proof?.scrubDoesNotValidateAuthenticity === true,
      nonClaimsVisible: scrub.nonClaims.includes('No production support-bundle privacy claim.')
    },
    compactSummary: {
      sourceSectionCount: scrub.sourceSummary?.sectionCount || 0,
      sourceCommandCount: scrub.sourceSummary?.commandCount || 0,
      redactedFieldCount: validation.redactedFieldCount,
      retainedFieldCount: scrub.redaction?.retainedFieldCount || 0,
      sensitiveDigestCount: scrub.redaction?.sensitiveDigestCount || 0
    },
    nonClaims: scrub.nonClaims
  };
  return report;
}

const isMain = process.argv[1] && import.meta.url === new URL(process.argv[1], 'file:').href;
if (isMain) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const report = await runProbe();
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } else console.log(JSON.stringify(report, null, 2));
}

// Static audit markers: demo:kernel-kit-support-bundle-privacy-scrub-proof; browserrt-kernel-kit-support-bundle-privacy-scrub-v1; privacy-scrub-checkpoint; privacyScrubPresent; sensitiveFieldsRedacted; exactCommandTextRedacted; No production support-bundle privacy claim.; No anonymization, differential-privacy, or irreversible de-identification claim.
