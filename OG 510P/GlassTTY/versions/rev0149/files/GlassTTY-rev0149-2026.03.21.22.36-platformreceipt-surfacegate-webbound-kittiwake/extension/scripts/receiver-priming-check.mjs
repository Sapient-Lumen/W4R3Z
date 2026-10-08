import assert from 'node:assert/strict';
import { mergeContentReceivers } from '../dist/shared/receivers.js';
import { describeReceiverCoverageExperimentPlan, describeReceiverCoveragePolicyHints, describeReceiverPrimingAudit, mergePrimedReceiverKeys, planReceiverPriming, receiverPrimingKey, relatedFrameScheme } from '../dist/shared/receiver-priming.js';

const supported = (url) => typeof url === 'string' && (url.startsWith('https://claude.ai/') || url.startsWith('http://127.0.0.1:8765/') || url.startsWith('http://localhost:8765/'));

const frames = [
  { documentId: 'doc-top', frameId: 0, frameType: 'outermost_frame', url: 'https://claude.ai/chat' },
  { documentId: 'doc-prerender-top', frameId: 12, frameType: 'outermost_frame', parentFrameId: -1, url: 'https://claude.ai/chat/prerender' },
  { documentId: 'doc-child-a', frameId: 4, frameType: 'sub_frame', parentFrameId: 0, url: 'https://claude.ai/artifacts/compose' },
  { documentId: 'doc-child-b', frameId: 6, frameType: 'sub_frame', parentFrameId: 0, url: 'https://claude.ai/project/sidebar' },
  { frameId: 8, frameType: 'sub_frame', parentFrameId: 0, url: 'https://claude.ai/fallback/no-document-id' },
  { documentId: 'doc-related', frameId: 9, frameType: 'sub_frame', parentFrameId: 0, url: 'about:blank' },
  { documentId: 'doc-unsupported', frameId: 10, frameType: 'sub_frame', parentFrameId: 0, url: 'https://example.com/embed' },
];

const observedReceivers = mergeContentReceivers([], {
  documentId: 'doc-child-a',
  frameId: 4,
  receiverReady: true,
  lastSeenAt: '2026-03-09T00:00:00.000Z',
});
const primedKeys = ['doc:doc-child-b'];
const plan = planReceiverPriming(frames, {
  existingReceivers: observedReceivers,
  primedKeys,
  isSupportedUrl: supported,
});
const audit = describeReceiverPrimingAudit(frames, {
  existingReceivers: observedReceivers,
  primedKeys,
  isSupportedUrl: supported,
});
const manifestPolicy = {
  allFrames: false,
  matchAboutBlank: false,
  matchOriginAsFallback: false,
};
const policyHints = describeReceiverCoveragePolicyHints(audit, manifestPolicy);
const experimentPlan = describeReceiverCoverageExperimentPlan(audit, manifestPolicy);

assert.equal(receiverPrimingKey(frames[2]), 'doc:doc-child-a');
assert.equal(relatedFrameScheme('about:blank'), 'about');
assert.equal(relatedFrameScheme('blob:https://claude.ai/id'), 'blob');
assert.deepEqual(plan.candidateKeys, ['frame:8']);
assert.deepEqual(plan.documentIds, []);
assert.deepEqual(plan.frameIds, [8]);
assert.equal(plan.skipped.find((entry) => entry.reason === 'top_frame' && entry.frameId === 0)?.frameId, 0);
assert.equal(plan.skipped.find((entry) => entry.reason === 'top_frame' && entry.frameId === 12)?.key, 'doc:doc-prerender-top');
assert.equal(plan.skipped.find((entry) => entry.reason === 'already_observed')?.key, 'doc:doc-child-a');
assert.equal(plan.skipped.find((entry) => entry.reason === 'already_primed')?.key, 'doc:doc-child-b');
assert.equal(plan.skipped.find((entry) => entry.reason === 'related_frame_url')?.frameId, 9);
assert.equal(plan.skipped.find((entry) => entry.reason === 'unsupported_url')?.frameId, 10);
assert.equal(audit.counts.relatedFrameUrlCount, 1);
assert.equal(audit.counts.candidateCount, 1);
assert.equal(audit.counts.candidateFrameCount, 1);
assert.equal(audit.counts.candidateDocumentCount, 0);
assert.equal(audit.counts.skippedReasonCounts.related_frame_url, 1);
assert.equal(audit.frames.find((frame) => frame.frameId === 8)?.status, 'candidate_frame');
assert.equal(audit.frames.find((frame) => frame.frameId === 9)?.status, 'related_frame_url');
assert.equal(audit.frames.find((frame) => frame.frameId === 10)?.status, 'unsupported_url');
assert.equal(policyHints.relatedFrameGapCount, 1);
assert.equal(policyHints.aboutBlankGapCount, 1);
assert.equal(policyHints.hints.find((hint) => hint.lever === 'runtime_priming')?.frameCount, 1);
assert.equal(policyHints.hints.find((hint) => hint.lever === 'manifest_match_about_blank')?.frameCount, 1);
assert.equal(policyHints.hints.find((hint) => hint.lever === 'manifest_match_origin_as_fallback')?.frameIds?.[0], 9);
assert.equal(experimentPlan.gapFrameCount, 2);
assert.equal(experimentPlan.currentExperimentId, 'current_runtime_priming');
assert.equal(experimentPlan.recommendedExperimentId, 'manifest_match_about_blank');
assert.equal(experimentPlan.experiments.find((experiment) => experiment.id === 'current_runtime_priming')?.remainingGapCount, 1);
assert.equal(experimentPlan.experiments.find((experiment) => experiment.id === 'manifest_match_about_blank')?.remainingGapCount, 0);
assert.equal(experimentPlan.experiments.find((experiment) => experiment.id === 'manifest_match_origin_as_fallback')?.pathWildcardRequired, true);

const freshPlan = planReceiverPriming(frames, {
  existingReceivers: [],
  primedKeys: [],
  isSupportedUrl: supported,
});
const freshAudit = describeReceiverPrimingAudit(frames, {
  existingReceivers: [],
  primedKeys: [],
  isSupportedUrl: supported,
});
assert.deepEqual(freshPlan.documentIds, ['doc-child-a', 'doc-child-b']);
assert.deepEqual(freshPlan.frameIds, [8]);
assert.equal(freshAudit.counts.candidateDocumentCount, 2);
assert.equal(freshAudit.counts.gapCount, 4);
const opaqueFrames = [...frames, { documentId: 'doc-blob-gap', frameId: 11, frameType: 'sub_frame', parentFrameId: 0, url: 'blob:https://claude.ai/example' }];
const opaqueAudit = describeReceiverPrimingAudit(opaqueFrames, {
  existingReceivers: observedReceivers,
  primedKeys,
  isSupportedUrl: supported,
});
const opaquePlan = describeReceiverCoverageExperimentPlan(opaqueAudit, manifestPolicy);
assert.equal(opaquePlan.recommendedExperimentId, 'manifest_match_origin_as_fallback');
assert.equal(opaquePlan.experiments.find((experiment) => experiment.id === 'manifest_match_about_blank')?.remainingGapCount, 1);
assert.equal(opaquePlan.experiments.find((experiment) => experiment.id === 'manifest_match_origin_as_fallback')?.remainingGapCount, 0);

assert.deepEqual(
  mergePrimedReceiverKeys(['doc:alpha', 'frame:1'], ['frame:1', 'doc:beta']),
  ['doc:alpha', 'frame:1', 'doc:beta'],
);

process.stdout.write(`${JSON.stringify({ ok: true, plan, audit, policyHints, experimentPlan, freshPlan, freshAudit, opaquePlan }, null, 2)}\n`);
