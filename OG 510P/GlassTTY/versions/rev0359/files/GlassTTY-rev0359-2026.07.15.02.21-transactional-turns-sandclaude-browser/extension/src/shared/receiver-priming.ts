import { contentReceiverKey, isOutermostReceiver, type ContentReceiverState } from './receivers.js';

export interface ReceiverPrimingFrameCandidate {
  documentId?: string;
  frameId?: number;
  frameType?: string;
  parentFrameId?: number;
  url?: string;
}

export type RelatedFrameScheme = 'about' | 'data' | 'blob' | 'filesystem';

export interface ReceiverPrimingCandidate {
  key: string;
  documentId?: string;
  frameId?: number;
  frameType?: string;
  parentFrameId?: number;
  url?: string;
}

export type ReceiverPrimingSkipReason = 'top_frame' | 'unsupported_url' | 'related_frame_url' | 'already_observed' | 'already_primed' | 'missing_target';
export type ReceiverPrimingFrameStatus = ReceiverPrimingSkipReason | 'candidate_document' | 'candidate_frame';

export interface ReceiverPrimingPlan {
  candidates: ReceiverPrimingCandidate[];
  candidateKeys: string[];
  documentIds: string[];
  frameIds: number[];
  skipped: Array<{
    key?: string;
    frameId?: number;
    documentId?: string;
    url?: string;
    reason: ReceiverPrimingSkipReason;
  }>;
}

export interface ReceiverPrimingFrameAudit {
  key?: string;
  frameId?: number;
  documentId?: string;
  frameType?: string;
  parentFrameId?: number;
  url?: string;
  relatedFrameUrl: boolean;
  supportedUrl: boolean;
  observed: boolean;
  primed: boolean;
  status: ReceiverPrimingFrameStatus;
}

export interface ReceiverPrimingAuditSummary {
  plan: ReceiverPrimingPlan;
  counts: {
    frameCount: number;
    supportedUrlCount: number;
    relatedFrameUrlCount: number;
    observedCount: number;
    primedCount: number;
    topFrameCount: number;
    candidateCount: number;
    candidateDocumentCount: number;
    candidateFrameCount: number;
    gapCount: number;
    skippedReasonCounts: Record<ReceiverPrimingSkipReason, number>;
  };
  frames: ReceiverPrimingFrameAudit[];
}

export interface ReceiverCoverageManifestPolicy {
  allFrames: boolean;
  matchAboutBlank: boolean;
  matchOriginAsFallback: boolean;
}

export interface ReceiverCoveragePolicyHint {
  lever: 'runtime_priming' | 'manifest_all_frames' | 'manifest_match_about_blank' | 'manifest_match_origin_as_fallback';
  rationale: string;
  frameCount: number;
  frameIds?: number[];
}

export interface ReceiverCoveragePolicyHints {
  manifestPolicy: ReceiverCoverageManifestPolicy;
  runtimePrimingCandidateCount: number;
  relatedFrameGapCount: number;
  aboutBlankGapCount: number;
  opaqueRelatedFrameGapCount: number;
  missingTargetGapCount: number;
  hints: ReceiverCoveragePolicyHint[];
}

export interface ReceiverCoverageExperiment {
  id: 'current_runtime_priming' | 'manifest_all_frames' | 'manifest_match_about_blank' | 'manifest_match_origin_as_fallback';
  label: string;
  manifestPolicy: ReceiverCoverageManifestPolicy;
  rationale: string;
  addressedFrameCount: number;
  addressedFrameIds: number[];
  remainingGapCount: number;
  remainingGapFrameIds: number[];
  incrementalGapReduction: number;
  pathWildcardRequired: boolean;
  notes: string[];
}

export interface ReceiverCoverageExperimentPlan {
  manifestPolicy: ReceiverCoverageManifestPolicy;
  gapFrameCount: number;
  currentExperimentId: ReceiverCoverageExperiment['id'];
  recommendedExperimentId?: ReceiverCoverageExperiment['id'];
  recommendedRationale?: string;
  experiments: ReceiverCoverageExperiment[];
}

function compactString(value: string | null | undefined): string | undefined {
  if (typeof value !== 'string') return undefined;
  const trimmed = value.trim();
  return trimmed || undefined;
}

function uniqueStrings(values: Array<string | null | undefined>): string[] {
  const out: string[] = [];
  const seen = new Set<string>();
  for (const value of values) {
    const normalized = compactString(value);
    if (!normalized || seen.has(normalized)) continue;
    seen.add(normalized);
    out.push(normalized);
  }
  return out;
}

function uniqueNumbers(values: Array<number | null | undefined>): number[] {
  const out: number[] = [];
  const seen = new Set<number>();
  for (const value of values) {
    if (typeof value !== 'number' || seen.has(value)) continue;
    seen.add(value);
    out.push(value);
  }
  return out;
}

export function receiverPrimingKey(candidate: ReceiverPrimingFrameCandidate): string | null {
  return contentReceiverKey({ documentId: candidate.documentId, frameId: candidate.frameId });
}

export function mergePrimedReceiverKeys(existing: Array<string | null | undefined>, incoming: Array<string | null | undefined>, limit = 64): string[] {
  const merged = uniqueStrings([...existing, ...incoming]);
  return merged.slice(Math.max(0, merged.length - Math.max(1, limit)));
}

export function relatedFrameScheme(url?: string): RelatedFrameScheme | undefined {
  const normalized = compactString(url)?.toLowerCase();
  if (!normalized) return undefined;
  if (normalized.startsWith('about:')) return 'about';
  if (normalized.startsWith('data:')) return 'data';
  if (normalized.startsWith('blob:')) return 'blob';
  if (normalized.startsWith('filesystem:')) return 'filesystem';
  return undefined;
}

export function isRelatedFrameUrl(url?: string): boolean {
  return relatedFrameScheme(url) !== undefined;
}

function primingSkipReason(frame: ReceiverPrimingFrameCandidate, options: {
  observedKeys: Set<string>;
  primedKeys: Set<string>;
  candidateKeys?: Set<string>;
  isSupportedUrl: (url?: string) => boolean;
}): ReceiverPrimingSkipReason | null {
  const key = receiverPrimingKey(frame) ?? undefined;
  const documentId = compactString(frame.documentId);
  const url = compactString(frame.url);
  const frameId = typeof frame.frameId === 'number' ? frame.frameId : undefined;

  if (isOutermostReceiver({ frameId, frameType: frame.frameType, parentFrameId: frame.parentFrameId })) return 'top_frame';
  if (!options.isSupportedUrl(url)) return isRelatedFrameUrl(url) ? 'related_frame_url' : 'unsupported_url';
  if (!key) return 'missing_target';
  if (options.observedKeys.has(key)) return 'already_observed';
  if (options.primedKeys.has(key) || options.candidateKeys?.has(key)) return 'already_primed';
  if (documentId || typeof frameId === 'number') return null;
  return 'missing_target';
}

export function planReceiverPriming(
  frames: ReceiverPrimingFrameCandidate[] = [],
  options: {
    existingReceivers?: ContentReceiverState[];
    primedKeys?: string[];
    isSupportedUrl: (url?: string) => boolean;
  },
): ReceiverPrimingPlan {
  const observedKeys = new Set((options.existingReceivers || []).map((receiver) => contentReceiverKey(receiver)).filter((value): value is string => Boolean(value)));
  const primedKeys = new Set((options.primedKeys || []).map((value) => compactString(value)).filter((value): value is string => Boolean(value)));
  const candidates: ReceiverPrimingCandidate[] = [];
  const candidateKeys = new Set<string>();
  const skipped: ReceiverPrimingPlan['skipped'] = [];

  for (const frame of frames) {
    const reason = primingSkipReason(frame, { observedKeys, primedKeys, candidateKeys, isSupportedUrl: options.isSupportedUrl });
    const key = receiverPrimingKey(frame) ?? undefined;
    const documentId = compactString(frame.documentId);
    const url = compactString(frame.url);
    const frameId = typeof frame.frameId === 'number' ? frame.frameId : undefined;

    if (reason) {
      skipped.push({ key, frameId, documentId, url, reason });
      continue;
    }
    if (!key) {
      skipped.push({ frameId, documentId, url, reason: 'missing_target' });
      continue;
    }
    candidateKeys.add(key);
    candidates.push({
      key,
      ...(documentId ? { documentId } : {}),
      ...(typeof frameId === 'number' ? { frameId } : {}),
      ...(compactString(frame.frameType) ? { frameType: compactString(frame.frameType) } : {}),
      ...(typeof frame.parentFrameId === 'number' ? { parentFrameId: frame.parentFrameId } : {}),
      ...(url ? { url } : {}),
    });
  }

  return {
    candidates,
    candidateKeys: candidates.map((candidate) => candidate.key),
    documentIds: uniqueStrings(candidates.map((candidate) => candidate.documentId)),
    frameIds: uniqueNumbers(candidates.filter((candidate) => !candidate.documentId).map((candidate) => candidate.frameId)),
    skipped,
  };
}

export function describeReceiverPrimingAudit(
  frames: ReceiverPrimingFrameCandidate[] = [],
  options: {
    existingReceivers?: ContentReceiverState[];
    primedKeys?: string[];
    isSupportedUrl: (url?: string) => boolean;
  },
): ReceiverPrimingAuditSummary {
  const observedKeys = new Set((options.existingReceivers || []).map((receiver) => contentReceiverKey(receiver)).filter((value): value is string => Boolean(value)));
  const primedKeys = new Set((options.primedKeys || []).map((value) => compactString(value)).filter((value): value is string => Boolean(value)));
  const plan = planReceiverPriming(frames, options);
  const candidateDocumentKeys = new Set(plan.candidates.filter((candidate) => candidate.documentId).map((candidate) => candidate.key));
  const candidateFrameKeys = new Set(plan.candidates.filter((candidate) => !candidate.documentId).map((candidate) => candidate.key));
  const skippedByKey = new Map<string, ReceiverPrimingSkipReason>();
  const skippedByFrameId = new Map<number, ReceiverPrimingSkipReason>();
  for (const entry of plan.skipped) {
    if (entry.key) skippedByKey.set(entry.key, entry.reason);
    if (typeof entry.frameId === 'number') skippedByFrameId.set(entry.frameId, entry.reason);
  }

  const framesAudit: ReceiverPrimingFrameAudit[] = frames.map((frame) => {
    const key = receiverPrimingKey(frame) ?? undefined;
    const frameId = typeof frame.frameId === 'number' ? frame.frameId : undefined;
    const documentId = compactString(frame.documentId);
    const url = compactString(frame.url);
    const relatedFrameUrl = isRelatedFrameUrl(url);
    const supportedUrl = options.isSupportedUrl(url);
    const observed = Boolean(key && observedKeys.has(key));
    const primed = Boolean(key && primedKeys.has(key));
    const status: ReceiverPrimingFrameStatus = key && candidateDocumentKeys.has(key)
      ? 'candidate_document'
      : key && candidateFrameKeys.has(key)
        ? 'candidate_frame'
        : (key ? skippedByKey.get(key) : undefined)
          ?? (typeof frameId === 'number' ? skippedByFrameId.get(frameId) : undefined)
          ?? 'missing_target';
    return {
      ...(key ? { key } : {}),
      ...(typeof frameId === 'number' ? { frameId } : {}),
      ...(documentId ? { documentId } : {}),
      ...(compactString(frame.frameType) ? { frameType: compactString(frame.frameType) } : {}),
      ...(typeof frame.parentFrameId === 'number' ? { parentFrameId: frame.parentFrameId } : {}),
      ...(url ? { url } : {}),
      relatedFrameUrl,
      supportedUrl,
      observed,
      primed,
      status,
    };
  });

  const skippedReasonCounts: Record<ReceiverPrimingSkipReason, number> = {
    top_frame: 0,
    unsupported_url: 0,
    related_frame_url: 0,
    already_observed: 0,
    already_primed: 0,
    missing_target: 0,
  };
  for (const skipped of plan.skipped) skippedReasonCounts[skipped.reason] += 1;
  const topFrameCount = framesAudit.filter((frame) => frame.status === 'top_frame').length;
  const relatedFrameUrlCount = framesAudit.filter((frame) => frame.relatedFrameUrl).length;
  const supportedUrlCount = framesAudit.filter((frame) => frame.supportedUrl).length;
  const observedCount = framesAudit.filter((frame) => frame.observed).length;
  const primedCount = framesAudit.filter((frame) => frame.primed).length;
  const gapCount = framesAudit.filter((frame) => ['candidate_document', 'candidate_frame', 'related_frame_url', 'missing_target'].includes(frame.status)).length;

  return {
    plan,
    counts: {
      frameCount: framesAudit.length,
      supportedUrlCount,
      relatedFrameUrlCount,
      observedCount,
      primedCount,
      topFrameCount,
      candidateCount: plan.candidates.length,
      candidateDocumentCount: candidateDocumentKeys.size,
      candidateFrameCount: candidateFrameKeys.size,
      gapCount,
      skippedReasonCounts,
    },
    frames: framesAudit,
  };
}

export function describeReceiverCoveragePolicyHints(audit: ReceiverPrimingAuditSummary, manifestPolicy: ReceiverCoverageManifestPolicy): ReceiverCoveragePolicyHints {
  const candidateFrames = audit.frames.filter((frame) => frame.status === 'candidate_document' || frame.status === 'candidate_frame');
  const relatedFrames = audit.frames.filter((frame) => frame.status === 'related_frame_url');
  const aboutBlankFrames = relatedFrames.filter((frame) => relatedFrameScheme(frame.url) === 'about');
  const opaqueRelatedFrames = relatedFrames.filter((frame) => {
    const scheme = relatedFrameScheme(frame.url);
    return scheme === 'data' || scheme === 'blob' || scheme === 'filesystem';
  });
  const missingTargetFrames = audit.frames.filter((frame) => frame.status === 'missing_target');
  const hints: ReceiverCoveragePolicyHint[] = [];
  if (candidateFrames.length) {
    hints.push({
      lever: 'runtime_priming',
      rationale: 'Supported subframes exist without observed receivers; runtime document/frame-targeted reinjection remains the lowest-surface recovery path.',
      frameCount: candidateFrames.length,
      frameIds: uniqueNumbers(candidateFrames.map((frame) => frame.frameId)),
    });
  }
  if (relatedFrames.length && !manifestPolicy.allFrames) {
    hints.push({
      lever: 'manifest_all_frames',
      rationale: 'Static content scripts only auto-run in the top frame by default; reaching matching child frames declaratively would require all_frames.',
      frameCount: relatedFrames.length,
      frameIds: uniqueNumbers(relatedFrames.map((frame) => frame.frameId)),
    });
  }
  if (aboutBlankFrames.length && !manifestPolicy.matchAboutBlank) {
    hints.push({
      lever: 'manifest_match_about_blank',
      rationale: "Observed about:blank-related gaps match Chrome's dedicated related-frame hook; this is the focused declarative experiment for about:blank descendants.",
      frameCount: aboutBlankFrames.length,
      frameIds: uniqueNumbers(aboutBlankFrames.map((frame) => frame.frameId)),
    });
  }
  if (relatedFrames.length && !manifestPolicy.matchOriginAsFallback) {
    hints.push({
      lever: 'manifest_match_origin_as_fallback',
      rationale: "Observed about:/data:/blob:/filesystem: gaps match Chrome's initiator-origin fallback path; note that declarative patterns must use path * when this lever is enabled.",
      frameCount: relatedFrames.length,
      frameIds: uniqueNumbers(relatedFrames.map((frame) => frame.frameId)),
    });
  }
  return {
    manifestPolicy,
    runtimePrimingCandidateCount: candidateFrames.length,
    relatedFrameGapCount: relatedFrames.length,
    aboutBlankGapCount: aboutBlankFrames.length,
    opaqueRelatedFrameGapCount: opaqueRelatedFrames.length,
    missingTargetGapCount: missingTargetFrames.length,
    hints,
  };
}


type CoverageGapStatus = 'candidate_document' | 'candidate_frame' | 'related_frame_url' | 'missing_target';

function coverageGapFrames(audit: ReceiverPrimingAuditSummary): ReceiverPrimingFrameAudit[] {
  return audit.frames.filter((frame): frame is ReceiverPrimingFrameAudit & { status: CoverageGapStatus } =>
    frame.status === 'candidate_document'
    || frame.status === 'candidate_frame'
    || frame.status === 'related_frame_url'
    || frame.status === 'missing_target');
}

function uniqueFrameIds(frames: ReceiverPrimingFrameAudit[]): number[] {
  return uniqueNumbers(frames.map((frame) => frame.frameId));
}

function experimentAddressesFrame(frame: ReceiverPrimingFrameAudit, manifestPolicy: ReceiverCoverageManifestPolicy): boolean {
  if (frame.status === 'candidate_document' || frame.status === 'candidate_frame') return true;
  if (frame.status === 'missing_target') return false;
  if (frame.status !== 'related_frame_url') return false;
  if (!manifestPolicy.allFrames) return false;
  const scheme = relatedFrameScheme(frame.url);
  if (manifestPolicy.matchOriginAsFallback) return scheme === 'about' || scheme === 'data' || scheme === 'blob' || scheme === 'filesystem';
  if (manifestPolicy.matchAboutBlank) return scheme === 'about';
  return false;
}

function experimentNotes(experimentId: ReceiverCoverageExperiment['id'], currentPolicy: ReceiverCoverageManifestPolicy): string[] {
  if (experimentId === 'current_runtime_priming') {
    return [
      'Keeps GlassTTY on the conservative runtime-priming path for matching child frames.',
      'Related-frame gaps remain evidence for a later declarative manifest experiment rather than a default scope change.',
    ];
  }
  if (experimentId === 'manifest_all_frames') {
    return [
      'Matching child frames would receive declarative content scripts without waiting for runtime priming.',
      'Related about:/data:/blob:/filesystem: gaps would still remain unless a related-frame lever is added too.',
    ];
  }
  if (experimentId === 'manifest_match_about_blank') {
    return [
      'Models a narrower declarative experiment focused on about:blank descendants.',
      'Chrome only reaches child-frame about:blank documents declaratively when all_frames is also enabled.',
    ];
  }
  return [
    'Models the broadest related-frame declarative experiment Chrome documents for about:/data:/blob:/filesystem: descendants.',
    currentPolicy.matchOriginAsFallback
      ? 'match_origin_as_fallback is already enabled in the current policy, so this scenario mainly serves as a saved proof baseline.'
      : 'Chrome requires a * path when match_origin_as_fallback is enabled, and it takes priority over match_about_blank.',
  ];
}

export function describeReceiverCoverageExperimentPlan(audit: ReceiverPrimingAuditSummary, manifestPolicy: ReceiverCoverageManifestPolicy): ReceiverCoverageExperimentPlan {
  const gaps = coverageGapFrames(audit);
  const candidateFrames = gaps.filter((frame) => frame.status === 'candidate_document' || frame.status === 'candidate_frame');
  const aboutBlankFrames = gaps.filter((frame) => frame.status === 'related_frame_url' && relatedFrameScheme(frame.url) === 'about');
  const opaqueRelatedFrames = gaps.filter((frame) => frame.status === 'related_frame_url' && relatedFrameScheme(frame.url) !== 'about');
  const missingTargetFrames = gaps.filter((frame) => frame.status === 'missing_target');

  const proposals: Array<{
    id: ReceiverCoverageExperiment['id'];
    label: string;
    manifestPolicy: ReceiverCoverageManifestPolicy;
    rationale: string;
  }> = [
    {
      id: 'current_runtime_priming',
      label: 'Current policy + runtime priming',
      manifestPolicy,
      rationale: 'Use the current conservative manifest posture and let runtime priming recover matching child frames.',
    },
    {
      id: 'manifest_all_frames',
      label: 'Declarative matching child frames',
      manifestPolicy: { ...manifestPolicy, allFrames: true },
      rationale: 'Enable all_frames so matching child frames can receive the content script declaratively instead of waiting for runtime reinjection.',
    },
    {
      id: 'manifest_match_about_blank',
      label: 'Declarative about:blank descendant experiment',
      manifestPolicy: { ...manifestPolicy, allFrames: true, matchAboutBlank: true },
      rationale: 'Enable all_frames plus match_about_blank to test whether about:blank descendants are the missing reach.',
    },
    {
      id: 'manifest_match_origin_as_fallback',
      label: 'Declarative related-frame fallback experiment',
      manifestPolicy: { ...manifestPolicy, allFrames: true, matchOriginAsFallback: true },
      rationale: "Enable all_frames plus match_origin_as_fallback to test Chrome's initiator-origin fallback for about:/data:/blob:/filesystem: descendants.",
    },
  ];

  const currentAddressed = gaps.filter((frame) => experimentAddressesFrame(frame, manifestPolicy));
  const currentAddressedCount = currentAddressed.length;
  const seenPolicies = new Set<string>();
  const experiments: ReceiverCoverageExperiment[] = [];
  for (const proposal of proposals) {
    const policyKey = JSON.stringify(proposal.manifestPolicy);
    if (seenPolicies.has(policyKey)) continue;
    seenPolicies.add(policyKey);
    const addressed = gaps.filter((frame) => experimentAddressesFrame(frame, proposal.manifestPolicy));
    const remaining = gaps.filter((frame) => !experimentAddressesFrame(frame, proposal.manifestPolicy));
    experiments.push({
      id: proposal.id,
      label: proposal.label,
      manifestPolicy: proposal.manifestPolicy,
      rationale: proposal.rationale,
      addressedFrameCount: addressed.length,
      addressedFrameIds: uniqueFrameIds(addressed),
      remainingGapCount: remaining.length,
      remainingGapFrameIds: uniqueFrameIds(remaining),
      incrementalGapReduction: Math.max(0, addressed.length - currentAddressedCount),
      pathWildcardRequired: proposal.manifestPolicy.matchOriginAsFallback,
      notes: experimentNotes(proposal.id, manifestPolicy),
    });
  }

  let recommendedExperimentId: ReceiverCoverageExperiment['id'] | undefined;
  let recommendedRationale: string | undefined;
  const originFallback = experiments.find((experiment) => experiment.id === 'manifest_match_origin_as_fallback');
  const aboutBlank = experiments.find((experiment) => experiment.id === 'manifest_match_about_blank');
  const current = experiments.find((experiment) => experiment.id === 'current_runtime_priming') ?? experiments[0];
  if (opaqueRelatedFrames.length && originFallback && originFallback.remainingGapCount < (current?.remainingGapCount ?? Number.MAX_SAFE_INTEGER)) {
    recommendedExperimentId = originFallback.id;
    recommendedRationale = 'Opaque related-frame gaps are present; the next evidence-backed declarative experiment is all_frames plus match_origin_as_fallback.';
  } else if (aboutBlankFrames.length && aboutBlank && aboutBlank.remainingGapCount < (current?.remainingGapCount ?? Number.MAX_SAFE_INTEGER)) {
    recommendedExperimentId = aboutBlank.id;
    recommendedRationale = 'Observed about:blank gaps suggest a narrower all_frames + match_about_blank experiment before broader related-frame fallback.';
  } else if (candidateFrames.length) {
    recommendedExperimentId = current?.id;
    recommendedRationale = 'Matching child-frame gaps are already recoverable with runtime priming, so GlassTTY should stay conservative until a real related-frame artifact appears.';
  } else if (missingTargetFrames.length) {
    recommendedExperimentId = current?.id;
    recommendedRationale = 'The remaining gaps are missing target identifiers, so better navigation/document evidence matters more than a manifest change.';
  }

  return {
    manifestPolicy,
    gapFrameCount: gaps.length,
    currentExperimentId: current?.id ?? 'current_runtime_priming',
    ...(recommendedExperimentId ? { recommendedExperimentId } : {}),
    ...(recommendedRationale ? { recommendedRationale } : {}),
    experiments,
  };
}
