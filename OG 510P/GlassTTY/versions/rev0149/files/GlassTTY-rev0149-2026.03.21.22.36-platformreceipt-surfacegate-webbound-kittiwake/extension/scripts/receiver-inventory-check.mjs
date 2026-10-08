import assert from 'node:assert/strict';
import {
  contentReceiverKey,
  describeContentReceiverAudit,
  isOutermostReceiver,
  mergeContentReceivers,
  messageTargetForReceivers,
  preferredContentReceiver,
  reconcileContentReceivers,
  summarizeContentReceivers,
} from '../dist/shared/receivers.js';

const now = '2026-03-08T23:40:00.000Z';

const topAndChild = mergeContentReceivers(
  mergeContentReceivers([], {
    documentId: 'doc-top',
    frameId: 0,
    receiverReady: true,
    frameType: 'outermost_frame',
    frameUrl: 'https://claude.ai/chat/top',
    frameDepth: 0,
    framePathFrameIds: [0],
    framePathUrls: ['https://claude.ai/chat/top'],
    framePathHosts: ['claude.ai'],
    framePathLabel: 'claude.ai',
    lastSeenAt: now,
  }),
  {
    documentId: 'doc-child',
    frameId: 2,
    receiverReady: true,
    frameType: 'sub_frame',
    parentFrameId: 0,
    frameUrl: 'https://claude.ai/artifacts/frame',
    frameDepth: 1,
    framePathFrameIds: [0, 2],
    framePathUrls: ['https://claude.ai/chat/top', 'https://claude.ai/artifacts/frame'],
    framePathHosts: ['claude.ai', 'claude.ai'],
    framePathLabel: 'claude.ai → claude.ai',
    lastSeenAt: '2026-03-08T23:40:01.000Z',
  },
);
const topSummary = summarizeContentReceivers(topAndChild);
assert.equal(topSummary.receiverCount, 2);
assert.equal(topSummary.receiverSelectionPolicy, 'top_frame');
assert.equal(topSummary.receiverInventoryStatus, 'multi_frame_top_frame');
assert.deepEqual(topSummary.receiverFrameIds, [0, 2]);
assert.deepEqual(messageTargetForReceivers(topAndChild), { documentId: 'doc-top' });
assert.equal(preferredContentReceiver(topAndChild)?.frameId, 0);
assert.equal(preferredContentReceiver(topAndChild)?.framePathLabel, 'claude.ai');
const topAudit = describeContentReceiverAudit(topAndChild);
assert.deepEqual(topAudit.resolverPolicy.priorities, ['lifecyclePreferred', 'outermost', 'ready', 'frameDepth', 'lastSeenAt']);
assert.equal(topAudit.receiverResolution?.receiverKey, 'doc:doc-top');
assert.equal(topAudit.receiverResolution?.rank, 1);
assert.equal(topAudit.rankedMatches[1]?.receiverKey, 'doc:doc-child');


const overrideKey = contentReceiverKey(topAndChild[1]);
assert.equal(overrideKey, 'doc:doc-child');
const overrideSummary = summarizeContentReceivers(topAndChild, { overrideKey });
assert.equal(overrideSummary.receiverSelectionPolicy, 'operator_override');
assert.equal(overrideSummary.receiverOverrideStatus, 'active');
assert.equal(overrideSummary.selectedReceiverKey, 'doc:doc-child');
assert.match(overrideSummary.selectedReceiverLabel, /claude\.ai → claude\.ai/);
assert.match(overrideSummary.selectedReceiverLabel, /depth:1/);
assert.deepEqual(messageTargetForReceivers(topAndChild, { overrideKey }), { documentId: 'doc-child' });
assert.equal(preferredContentReceiver(topAndChild, { overrideKey })?.frameId, 2);
assert.equal(preferredContentReceiver(topAndChild, { overrideKey })?.parentFrameId, 0);
assert.deepEqual(preferredContentReceiver(topAndChild, { overrideKey })?.framePathFrameIds, [0, 2]);
const overrideAudit = describeContentReceiverAudit(topAndChild, { overrideKey });
assert.equal(overrideAudit.resolverPolicy.overrideKey, 'doc:doc-child');
assert.equal(overrideAudit.resolverPolicy.overrideMatched, true);
assert.equal(overrideAudit.receiverResolution?.receiverKey, 'doc:doc-child');
assert.equal(overrideAudit.receiverResolution?.rank, 2);


const staleOverrideSummary = summarizeContentReceivers(topAndChild, { overrideKey: 'doc:missing' });
assert.equal(staleOverrideSummary.receiverSelectionPolicy, 'top_frame');
assert.equal(staleOverrideSummary.receiverOverrideStatus, 'stale');
assert.deepEqual(messageTargetForReceivers(topAndChild, { overrideKey: 'doc:missing' }), { documentId: 'doc-top' });

const childOnly = mergeContentReceivers([], {
  documentId: 'doc-child-only',
  frameId: 5,
  receiverReady: true,
  frameDepth: 2,
  framePathFrameIds: [0, 3, 5],
  framePathUrls: ['https://app.example.test/', 'https://docs.example.test/shell', 'https://docs.example.test/embed'],
  framePathHosts: ['app.example.test', 'docs.example.test', 'docs.example.test'],
  framePathLabel: 'app.example.test → docs.example.test → docs.example.test',
  lastSeenAt: now,
});
const childSummary = summarizeContentReceivers(childOnly);
assert.equal(childSummary.receiverSelectionPolicy, 'single_ready');
assert.equal(childSummary.receiverInventoryStatus, 'single_subframe');
assert.deepEqual(messageTargetForReceivers(childOnly), { documentId: 'doc-child-only' });
assert.match(childSummary.selectedReceiverLabel, /app\.example\.test → docs\.example\.test → docs\.example\.test/);

const ambiguous = mergeContentReceivers(
  mergeContentReceivers([], { frameId: 7, receiverReady: false, frameDepth: 1, framePathHosts: ['claude.ai', 'claude.ai'], framePathLabel: 'claude.ai → claude.ai', lastSeenAt: now }),
  { frameId: 9, receiverReady: false, frameDepth: 2, framePathHosts: ['claude.ai', 'claude.ai', 'claude.ai'], framePathLabel: 'claude.ai → claude.ai → claude.ai', lastSeenAt: '2026-03-08T23:40:02.000Z' },
);
const ambiguousSummary = summarizeContentReceivers(ambiguous);
assert.equal(ambiguousSummary.receiverSelectionPolicy, 'latest_observed');
assert.equal(ambiguousSummary.receiverInventoryStatus, 'multi_frame_no_top_frame');
assert.deepEqual(messageTargetForReceivers(ambiguous), { frameId: 7 });

const prerenderOutermost = mergeContentReceivers(
  mergeContentReceivers([], {
    documentId: 'doc-prerender',
    frameId: 41,
    frameType: 'outermost_frame',
    frameDepth: 0,
    documentLifecycle: 'prerender',
    receiverReady: true,
    framePathFrameIds: [41],
    framePathHosts: ['claude.ai'],
    framePathLabel: 'claude.ai',
    lastSeenAt: '2026-03-09T08:40:00.000Z',
  }),
  {
    documentId: 'doc-live-child',
    frameId: 44,
    frameType: 'sub_frame',
    parentFrameId: 41,
    frameDepth: 1,
    receiverReady: true,
    framePathFrameIds: [41, 44],
    framePathHosts: ['claude.ai', 'claude.ai'],
    framePathLabel: 'claude.ai → claude.ai',
    lastSeenAt: '2026-03-09T08:40:01.000Z',
  },
);
const prerenderTop = prerenderOutermost.find((receiver) => receiver.documentId === 'doc-prerender');
const activeChild = prerenderOutermost.find((receiver) => receiver.documentId === 'doc-live-child');
assert.equal(isOutermostReceiver(prerenderTop), true);
assert.equal(isOutermostReceiver(activeChild), false);
assert.equal(preferredContentReceiver(prerenderOutermost)?.documentId, 'doc-live-child');
assert.equal(summarizeContentReceivers(prerenderOutermost).receiverSelectionPolicy, 'single_ready');
assert.equal(messageTargetForReceivers(prerenderOutermost)?.documentId, 'doc-live-child');
assert.match(preferredContentReceiver(prerenderOutermost)?.framePathLabel ?? '', /^claude\.ai → claude\.ai$/);
const prerenderAudit = describeContentReceiverAudit(prerenderOutermost);
assert.equal(prerenderAudit.receiverResolution?.receiverKey, 'doc:doc-live-child');
assert.equal(prerenderAudit.rankedMatches[0]?.receiverKey, 'doc:doc-live-child');
assert.equal(prerenderAudit.rankedMatches[1]?.receiverKey, 'doc:doc-prerender');
assert.match(prerenderAudit.rankedMatches[1]?.reasons?.[0] ?? '', /^lifecycle=prerender$/);


const navigatedSameFrame = mergeContentReceivers(
  mergeContentReceivers([], {
    documentId: 'doc-old-top',
    frameId: 0,
    frameType: 'outermost_frame',
    receiverReady: true,
    frameDepth: 0,
    framePathFrameIds: [0],
    framePathHosts: ['claude.ai'],
    framePathLabel: 'claude.ai',
    lastSeenAt: '2026-03-09T08:45:00.000Z',
  }),
  {
    documentId: 'doc-new-top',
    frameId: 0,
    frameType: 'outermost_frame',
    documentLifecycle: 'active',
    receiverReady: true,
    frameDepth: 0,
    framePathFrameIds: [0],
    framePathHosts: ['claude.ai'],
    framePathLabel: 'claude.ai',
    lastSeenAt: '2026-03-09T08:45:02.000Z',
  },
);
assert.equal(navigatedSameFrame.length, 1);
assert.equal(navigatedSameFrame[0].documentId, 'doc-new-top');
assert.equal(messageTargetForReceivers(navigatedSameFrame)?.documentId, 'doc-new-top');

const reconciled = reconcileContentReceivers(topAndChild, [
  {
    documentId: 'doc-top',
    frameId: 0,
    frameType: 'outermost_frame',
    frameDepth: 0,
    frameUrl: 'https://claude.ai/chat/refreshed',
    framePathFrameIds: [0],
    framePathUrls: ['https://claude.ai/chat/refreshed'],
    framePathHosts: ['claude.ai'],
    framePathLabel: 'claude.ai',
  },
]);
assert.deepEqual(reconciled.removedKeys, ['doc:doc-child']);
assert.deepEqual(reconciled.retainedKeys, ['doc:doc-top']);
assert.equal(reconciled.receivers.length, 1);
assert.equal(reconciled.receivers[0].frameUrl, 'https://claude.ai/chat/refreshed');
assert.equal(summarizeContentReceivers(reconciled.receivers).receiverInventoryStatus, 'single_top_frame');

const result = {
  ok: true,
  cases: {
    topAndChild: {
      receivers: topAndChild,
      summary: topSummary,
      audit: topAudit,
      target: messageTargetForReceivers(topAndChild),
    },
    overrideTopAndChild: {
      overrideKey,
      summary: overrideSummary,
      audit: overrideAudit,
      target: messageTargetForReceivers(topAndChild, { overrideKey }),
    },
    staleOverrideTopAndChild: {
      overrideKey: 'doc:missing',
      summary: staleOverrideSummary,
      target: messageTargetForReceivers(topAndChild, { overrideKey: 'doc:missing' }),
    },
    childOnly: {
      receivers: childOnly,
      summary: childSummary,
      target: messageTargetForReceivers(childOnly),
    },
    ambiguous: {
      receivers: ambiguous,
      summary: ambiguousSummary,
      target: messageTargetForReceivers(ambiguous),
    },
    prerenderOutermost: {
      receivers: prerenderOutermost,
      summary: summarizeContentReceivers(prerenderOutermost),
      audit: prerenderAudit,
      target: messageTargetForReceivers(prerenderOutermost),
    },
    navigatedSameFrame: {
      receivers: navigatedSameFrame,
      summary: summarizeContentReceivers(navigatedSameFrame),
      target: messageTargetForReceivers(navigatedSameFrame),
    },
    reconciled: {
      summary: summarizeContentReceivers(reconciled.receivers),
      removedKeys: reconciled.removedKeys,
      receivers: reconciled.receivers,
    },
  },
};

process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
