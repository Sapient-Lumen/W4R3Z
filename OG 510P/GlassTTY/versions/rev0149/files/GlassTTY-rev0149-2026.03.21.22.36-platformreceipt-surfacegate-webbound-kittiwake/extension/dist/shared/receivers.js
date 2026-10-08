function compactString(value) {
    if (typeof value !== 'string')
        return undefined;
    const trimmed = value.trim();
    return trimmed || undefined;
}
function compactStrings(values) {
    if (!Array.isArray(values))
        return undefined;
    const normalized = values.map((value) => compactString(value)).filter((value) => Boolean(value));
    return normalized.length ? normalized : undefined;
}
function compactNumbers(values) {
    if (!Array.isArray(values))
        return undefined;
    const normalized = values.filter((value) => typeof value === 'number');
    return normalized.length ? normalized : undefined;
}
function compactOrigin(value) {
    const trimmed = compactString(value);
    if (!trimmed)
        return undefined;
    try {
        return new URL(trimmed).origin;
    }
    catch {
        return trimmed;
    }
}
function hostnameFromUrl(value) {
    const trimmed = compactString(value);
    if (!trimmed)
        return undefined;
    try {
        return new URL(trimmed).hostname || undefined;
    }
    catch {
        return undefined;
    }
}
function originFromUrl(value) {
    const trimmed = compactString(value);
    if (!trimmed)
        return undefined;
    try {
        return new URL(trimmed).origin;
    }
    catch {
        return undefined;
    }
}
function inferredFramePathHosts(receiver) {
    const fromState = compactStrings(receiver.framePathHosts);
    if (fromState?.length)
        return fromState;
    const currentHost = hostnameFromUrl(receiver.frameUrl) ?? hostnameFromUrl(receiver.frameOrigin);
    if (currentHost)
        return [currentHost];
    return undefined;
}
export function isReceiverLifecyclePreferred(receiver) {
    const lifecycle = compactString(receiver.documentLifecycle);
    return !lifecycle || lifecycle === 'active';
}
export function isReceiverLifecycleInactive(receiver) {
    const lifecycle = compactString(receiver.documentLifecycle);
    return lifecycle === 'prerender' || lifecycle === 'cached' || lifecycle === 'pending_deletion';
}
export function isOutermostReceiver(receiver) {
    if (compactString(receiver.frameType) === 'outermost_frame')
        return true;
    if (typeof receiver.frameDepth === 'number')
        return receiver.frameDepth <= 0;
    if (Array.isArray(receiver.framePathFrameIds) && receiver.framePathFrameIds.length > 0)
        return receiver.framePathFrameIds.length === 1;
    if (typeof receiver.parentFrameId === 'number')
        return receiver.parentFrameId < 0;
    return receiver.frameId === 0;
}
export function contentReceiverFramePathLabel(receiver) {
    const explicit = compactString(receiver.framePathLabel);
    if (explicit)
        return explicit;
    const hosts = inferredFramePathHosts(receiver);
    if (hosts?.length) {
        const prefix = !isOutermostReceiver(receiver) ? ['top-frame'] : [];
        return [...prefix, ...hosts].join(' → ');
    }
    if (typeof receiver.frameId === 'number') {
        return isOutermostReceiver(receiver) ? 'top-frame' : `top-frame → frame:${receiver.frameId}`;
    }
    return undefined;
}
export function contentReceiverKey(receiver) {
    const documentId = compactString(receiver.documentId);
    if (documentId)
        return `doc:${documentId}`;
    if (typeof receiver.frameId === 'number')
        return `frame:${receiver.frameId}`;
    return null;
}
export function contentReceiverLabel(receiver) {
    const segments = [];
    if (typeof receiver.frameId === 'number') {
        segments.push(isOutermostReceiver(receiver) ? 'top-frame' : `frame:${receiver.frameId}`);
    }
    const documentId = compactString(receiver.documentId);
    if (documentId) {
        segments.push(`doc:${documentId.slice(0, 8)}`);
    }
    const frameType = compactString(receiver.frameType);
    if (frameType && frameType !== 'outermost_frame')
        segments.push(frameType);
    const host = hostnameFromUrl(receiver.frameUrl) ?? hostnameFromUrl(receiver.frameOrigin);
    if (host)
        segments.push(host);
    const framePath = contentReceiverFramePathLabel(receiver);
    if (framePath && framePath !== host && framePath !== 'top-frame')
        segments.push(framePath);
    if (typeof receiver.frameDepth === 'number' && receiver.frameDepth > 0)
        segments.push(`depth:${receiver.frameDepth}`);
    if (receiver.receiverReady === true)
        segments.push('ready');
    else if (receiver.receiverReady === false)
        segments.push('observed');
    const lifecycle = compactString(receiver.documentLifecycle);
    if (lifecycle)
        segments.push(lifecycle);
    return segments.join(' · ') || 'receiver';
}
export function describeContentReceiverResolution(receiver, options = {}) {
    const depth = typeof receiver.frameDepth === 'number' ? receiver.frameDepth : undefined;
    const lifecycle = compactString(receiver.documentLifecycle);
    const ready = receiver.receiverReady === true;
    const summary = {
        receiverKey: contentReceiverKey(receiver),
        receiverLabel: contentReceiverLabel(receiver),
        lifecyclePreferred: isReceiverLifecyclePreferred(receiver),
        activeOutermost: isOutermostReceiver(receiver) && isReceiverLifecyclePreferred(receiver),
        outermost: isOutermostReceiver(receiver),
        ready,
        ...(typeof depth === 'number' ? { frameDepth: depth } : {}),
        ...(compactString(receiver.lastSeenAt) ? { lastSeenAt: compactString(receiver.lastSeenAt) } : {}),
        ...(lifecycle ? { documentLifecycle: lifecycle } : {}),
        rankingVector: {
            lifecyclePreferred: isReceiverLifecyclePreferred(receiver),
            outermost: isOutermostReceiver(receiver),
            ready,
            ...(typeof depth === 'number' ? { frameDepth: depth } : {}),
            ...(compactString(receiver.lastSeenAt) ? { lastSeenAt: compactString(receiver.lastSeenAt) } : {}),
        },
        reasons: [
            isReceiverLifecyclePreferred(receiver) ? 'lifecycle=active_or_unknown' : `lifecycle=${lifecycle ?? 'unknown'}`,
            isOutermostReceiver(receiver) ? 'frame=outermost' : 'frame=subframe',
            ready ? 'receiver=ready' : 'receiver=observed_only',
            typeof depth === 'number' ? `frameDepth=${depth}` : 'frameDepth=unknown',
            compactString(receiver.lastSeenAt) ? `lastSeenAt=${compactString(receiver.lastSeenAt)}` : 'lastSeenAt=unknown',
        ],
        ...(typeof options.rank === 'number' ? { rank: options.rank } : {}),
    };
    return summary;
}
function sortReceivers(receivers) {
    return [...receivers].sort((left, right) => {
        const leftLifecyclePreferred = isReceiverLifecyclePreferred(left) ? 1 : 0;
        const rightLifecyclePreferred = isReceiverLifecyclePreferred(right) ? 1 : 0;
        if (leftLifecyclePreferred !== rightLifecyclePreferred)
            return rightLifecyclePreferred - leftLifecyclePreferred;
        const leftTop = isOutermostReceiver(left) ? 1 : 0;
        const rightTop = isOutermostReceiver(right) ? 1 : 0;
        if (leftTop !== rightTop)
            return rightTop - leftTop;
        const leftReady = left.receiverReady === true ? 1 : 0;
        const rightReady = right.receiverReady === true ? 1 : 0;
        if (leftReady !== rightReady)
            return rightReady - leftReady;
        const leftDepth = typeof left.frameDepth === 'number' ? left.frameDepth : Number.MAX_SAFE_INTEGER;
        const rightDepth = typeof right.frameDepth === 'number' ? right.frameDepth : Number.MAX_SAFE_INTEGER;
        if (leftDepth !== rightDepth)
            return leftDepth - rightDepth;
        return String(right.lastSeenAt).localeCompare(String(left.lastSeenAt));
    });
}
function findOverrideReceiver(receivers = [], overrideKey) {
    const wanted = compactString(overrideKey);
    if (!wanted)
        return null;
    return sortReceivers(receivers).find((receiver) => contentReceiverKey(receiver) === wanted) ?? null;
}
export function mergeContentReceivers(existing = [], incoming) {
    if (!incoming)
        return sortReceivers(existing);
    const key = contentReceiverKey(incoming);
    if (!key)
        return sortReceivers(existing);
    const incomingDocumentId = compactString(incoming.documentId);
    const incomingFrameId = typeof incoming.frameId === 'number' ? incoming.frameId : undefined;
    const nowish = compactString(incoming.lastSeenAt) || new Date().toISOString();
    const normalizedIncoming = {
        ...(compactString(incoming.documentId) ? { documentId: compactString(incoming.documentId) } : {}),
        ...(typeof incoming.frameId === 'number' ? { frameId: incoming.frameId } : {}),
        ...(compactString(incoming.documentLifecycle) ? { documentLifecycle: compactString(incoming.documentLifecycle) } : {}),
        ...(compactString(incoming.adapter) ? { adapter: compactString(incoming.adapter) } : {}),
        ...(typeof incoming.receiverReady === 'boolean' ? { receiverReady: incoming.receiverReady } : {}),
        ...(compactString(incoming.frameType) ? { frameType: compactString(incoming.frameType) } : {}),
        ...(typeof incoming.parentFrameId === 'number' ? { parentFrameId: incoming.parentFrameId } : {}),
        ...(compactString(incoming.parentDocumentId) ? { parentDocumentId: compactString(incoming.parentDocumentId) } : {}),
        ...(compactString(incoming.frameUrl) ? { frameUrl: compactString(incoming.frameUrl) } : {}),
        ...((compactOrigin(incoming.frameOrigin) ?? originFromUrl(incoming.frameUrl)) ? { frameOrigin: compactOrigin(incoming.frameOrigin) ?? originFromUrl(incoming.frameUrl) } : {}),
        ...(typeof incoming.frameDepth === 'number' ? { frameDepth: incoming.frameDepth } : {}),
        ...(compactNumbers(incoming.framePathFrameIds) ? { framePathFrameIds: compactNumbers(incoming.framePathFrameIds) } : {}),
        ...(compactStrings(incoming.framePathUrls) ? { framePathUrls: compactStrings(incoming.framePathUrls) } : {}),
        ...(compactStrings(incoming.framePathHosts) ? { framePathHosts: compactStrings(incoming.framePathHosts) } : {}),
        ...((compactString(incoming.framePathLabel) ?? contentReceiverFramePathLabel(incoming)) ? { framePathLabel: compactString(incoming.framePathLabel) ?? contentReceiverFramePathLabel(incoming) } : {}),
        lastSeenAt: nowish,
    };
    const merged = [];
    let replaced = false;
    for (const receiver of existing) {
        const receiverKey = contentReceiverKey(receiver);
        if (receiverKey === key) {
            merged.push({ ...receiver, ...normalizedIncoming, lastSeenAt: nowish });
            replaced = true;
            continue;
        }
        const receiverFrameId = typeof receiver.frameId === 'number' ? receiver.frameId : undefined;
        const receiverDocumentId = compactString(receiver.documentId);
        const shouldEvictSameFrameDocument = typeof incomingFrameId === 'number'
            && receiverFrameId === incomingFrameId
            && incomingDocumentId
            && receiverDocumentId !== incomingDocumentId;
        if (shouldEvictSameFrameDocument) {
            continue;
        }
        merged.push(receiver);
    }
    if (!replaced)
        merged.push(normalizedIncoming);
    return sortReceivers(merged).slice(0, 8);
}
export function reconcileContentReceivers(existing = [], liveFrames = []) {
    if (!existing.length) {
        return { receivers: [], removed: [], removedKeys: [], retainedKeys: [] };
    }
    const liveIndex = new Map();
    for (const frame of liveFrames) {
        const key = contentReceiverKey(frame);
        if (!key)
            continue;
        liveIndex.set(key, frame);
    }
    if (!liveIndex.size) {
        return { receivers: sortReceivers(existing), removed: [], removedKeys: [], retainedKeys: existing.map((receiver) => contentReceiverKey(receiver)).filter((value) => Boolean(value)) };
    }
    const receivers = [];
    const removed = [];
    const retainedKeys = [];
    const removedKeys = [];
    for (const receiver of sortReceivers(existing)) {
        const key = contentReceiverKey(receiver);
        if (!key) {
            receivers.push(receiver);
            continue;
        }
        const live = liveIndex.get(key);
        if (!live) {
            removed.push(receiver);
            removedKeys.push(key);
            continue;
        }
        retainedKeys.push(key);
        receivers.push({
            ...receiver,
            ...(compactString(live.documentId) ? { documentId: compactString(live.documentId) } : {}),
            ...(typeof live.frameId === 'number' ? { frameId: live.frameId } : {}),
            ...(compactString(live.documentLifecycle) ? { documentLifecycle: compactString(live.documentLifecycle) } : {}),
            ...(compactString(live.frameType) ? { frameType: compactString(live.frameType) } : {}),
            ...(typeof live.parentFrameId === 'number' ? { parentFrameId: live.parentFrameId } : {}),
            ...(compactString(live.parentDocumentId) ? { parentDocumentId: compactString(live.parentDocumentId) } : {}),
            ...(compactString(live.frameUrl) ? { frameUrl: compactString(live.frameUrl) } : {}),
            ...((compactOrigin(live.frameOrigin) ?? originFromUrl(live.frameUrl)) ? { frameOrigin: compactOrigin(live.frameOrigin) ?? originFromUrl(live.frameUrl) } : {}),
            ...(typeof live.frameDepth === 'number' ? { frameDepth: live.frameDepth } : {}),
            ...(compactNumbers(live.framePathFrameIds) ? { framePathFrameIds: compactNumbers(live.framePathFrameIds) } : {}),
            ...(compactStrings(live.framePathUrls) ? { framePathUrls: compactStrings(live.framePathUrls) } : {}),
            ...(compactStrings(live.framePathHosts) ? { framePathHosts: compactStrings(live.framePathHosts) } : {}),
            ...((compactString(live.framePathLabel) ?? contentReceiverFramePathLabel(live)) ? { framePathLabel: compactString(live.framePathLabel) ?? contentReceiverFramePathLabel(live) } : {}),
        });
    }
    return { receivers: sortReceivers(receivers), removed, removedKeys, retainedKeys };
}
export function describeContentReceiverAudit(receivers = [], options = {}) {
    const summary = summarizeContentReceivers(receivers, options);
    const sorted = sortReceivers(receivers);
    const rankedMatches = sorted.map((receiver, index) => describeContentReceiverResolution(receiver, { rank: index + 1 }));
    const selected = preferredContentReceiver(receivers, options);
    return {
        resolverPolicy: {
            priorities: ['lifecyclePreferred', 'outermost', 'ready', 'frameDepth', 'lastSeenAt'],
            overrideKey: options.overrideKey ?? null,
            overrideMatched: Boolean(compactString(options.overrideKey) && summary.receiverOverrideStatus === 'active'),
            selectionPolicy: summary.receiverSelectionPolicy,
            inventoryStatus: summary.receiverInventoryStatus,
        },
        ...(selected ? { receiverResolution: describeContentReceiverResolution(selected, { rank: rankedMatches.find((candidate) => candidate.receiverKey === contentReceiverKey(selected))?.rank }) } : {}),
        rankedMatches,
    };
}
export function preferredContentReceiver(receivers = [], options = {}) {
    if (!receivers.length)
        return null;
    const override = findOverrideReceiver(receivers, options.overrideKey);
    if (override)
        return override;
    const sorted = sortReceivers(receivers);
    const lifecyclePreferred = sorted.filter((receiver) => isReceiverLifecyclePreferred(receiver));
    return lifecyclePreferred.find((receiver) => isOutermostReceiver(receiver) && receiver.receiverReady === true)
        ?? (lifecyclePreferred.length === 1 && lifecyclePreferred[0].receiverReady === true ? lifecyclePreferred[0] : null)
        ?? lifecyclePreferred.find((receiver) => receiver.receiverReady === true)
        ?? (lifecyclePreferred.length === 1 ? lifecyclePreferred[0] : null)
        ?? lifecyclePreferred.find((receiver) => isOutermostReceiver(receiver))
        ?? sorted.find((receiver) => isOutermostReceiver(receiver) && receiver.receiverReady === true)
        ?? (sorted.length === 1 && sorted[0].receiverReady === true ? sorted[0] : null)
        ?? sorted.find((receiver) => receiver.receiverReady === true)
        ?? (sorted.length === 1 ? sorted[0] : null)
        ?? sorted.find((receiver) => isOutermostReceiver(receiver))
        ?? sorted[0]
        ?? null;
}
export function summarizeContentReceivers(receivers = [], options = {}) {
    const frameIds = Array.from(new Set(receivers.filter((receiver) => typeof receiver.frameId === 'number').map((receiver) => receiver.frameId))).sort((left, right) => left - right);
    const documentIds = Array.from(new Set(receivers.map((receiver) => compactString(receiver.documentId)).filter((value) => Boolean(value))));
    const readyReceiverCount = receivers.filter((receiver) => receiver.receiverReady === true).length;
    const lifecyclePreferredReceivers = receivers.filter((receiver) => isReceiverLifecyclePreferred(receiver));
    const preferredReadyReceiverCount = lifecyclePreferredReceivers.filter((receiver) => receiver.receiverReady === true).length;
    const effectiveReadyReceiverCount = lifecyclePreferredReceivers.length ? preferredReadyReceiverCount : readyReceiverCount;
    const receiverTopFrameReady = receivers.some((receiver) => isOutermostReceiver(receiver) && receiver.receiverReady === true && isReceiverLifecyclePreferred(receiver));
    const receiverHasTopFrame = receivers.some((receiver) => isOutermostReceiver(receiver));
    const overrideReceiver = findOverrideReceiver(receivers, options.overrideKey);
    const receiverOverrideStatus = compactString(options.overrideKey)
        ? (overrideReceiver ? 'active' : 'stale')
        : 'none';
    let receiverSelectionPolicy = 'none';
    if (receivers.length) {
        if (overrideReceiver)
            receiverSelectionPolicy = 'operator_override';
        else if (receiverTopFrameReady)
            receiverSelectionPolicy = 'top_frame';
        else if (effectiveReadyReceiverCount === 1)
            receiverSelectionPolicy = 'single_ready';
        else if (effectiveReadyReceiverCount > 1)
            receiverSelectionPolicy = 'latest_ready';
        else if (lifecyclePreferredReceivers.length === 1)
            receiverSelectionPolicy = 'single_observed';
        else if (receivers.length === 1)
            receiverSelectionPolicy = 'single_observed';
        else
            receiverSelectionPolicy = 'latest_observed';
    }
    let receiverInventoryStatus = 'none';
    if (receivers.length) {
        if (receivers.length === 1 && receiverHasTopFrame)
            receiverInventoryStatus = 'single_top_frame';
        else if (receiverHasTopFrame)
            receiverInventoryStatus = 'multi_frame_top_frame';
        else if (frameIds.length <= 1)
            receiverInventoryStatus = 'single_subframe';
        else
            receiverInventoryStatus = 'multi_frame_no_top_frame';
    }
    const selected = preferredContentReceiver(receivers, options);
    return {
        receiverCount: receivers.length,
        readyReceiverCount,
        receiverFrameIds: frameIds,
        receiverDocumentIds: documentIds,
        receiverSelectionPolicy,
        receiverInventoryStatus,
        receiverTopFrameReady,
        receiverOverrideStatus,
        ...(selected ? {
            selectedReceiverKey: contentReceiverKey(selected) ?? undefined,
            selectedReceiverLabel: contentReceiverLabel(selected),
        } : {}),
    };
}
export function messageTargetForReceivers(receivers = [], options = {}) {
    const preferred = preferredContentReceiver(receivers, options);
    if (!preferred)
        return undefined;
    if (preferred.documentId)
        return { documentId: preferred.documentId };
    if (typeof preferred.frameId === 'number')
        return { frameId: preferred.frameId };
    return undefined;
}
