function parsedTime(value) {
    if (!value)
        return Number.NaN;
    return Date.parse(value);
}
function snapshotIsFresh(snapshot, now, maxAgeMs = 15_000) {
    const capturedAt = parsedTime(snapshot?.capturedAt);
    return Boolean(snapshot && Number.isFinite(capturedAt) && (now - capturedAt) <= maxAgeMs);
}
function snapshotLooksReachable(snapshot, lastNativeStatusError, now) {
    return Boolean(snapshot && !lastNativeStatusError && (snapshot.native_host || snapshotIsFresh(snapshot, now)));
}
function oneShotLooksReachable(nativeConnection) {
    return Boolean(nativeConnection?.lastOneShotProbeOk && !nativeConnection?.lastOneShotProbeError);
}
export function deriveNativeLaneDiagnosis(input) {
    const nativeConnection = input.nativeConnection;
    const snapshot = input.lastNativeStatusSnapshot;
    const now = typeof input.now === 'number' ? input.now : Date.now();
    const persistentConnected = nativeConnection?.connected === true;
    const persistentHealthy = persistentConnected && nativeConnection?.lastHealthOk !== false && !nativeConnection?.lastHealthError;
    const oneShotReachable = oneShotLooksReachable(nativeConnection);
    const snapshotReachable = snapshotLooksReachable(snapshot, input.lastNativeStatusError, now);
    const reconnectPending = Boolean(!persistentConnected && nativeConnection?.reconnectScheduledFor);
    const persistentBrokerRole = nativeConnection?.persistentBroker?.role;
    const oneShotBrokerRole = nativeConnection?.lastOneShotProbeBroker?.role;
    const snapshotBrokerRole = snapshot?.broker?.role;
    if (persistentHealthy) {
        return {
            status: 'persistent_healthy',
            summary: 'Persistent connectNative() lane is healthy.',
            recommendedAction: 'No action needed.',
            persistentConnected: true,
            persistentBrokerRole,
            oneShotBrokerRole,
            snapshotBrokerRole,
            reconnectScheduledFor: nativeConnection?.reconnectScheduledFor,
            reconnectAttempt: nativeConnection?.reconnectAttempt,
            snapshotMatchesPersistent: snapshot?.matches_persistent_host,
        };
    }
    if (persistentConnected) {
        return {
            status: 'persistent_degraded',
            summary: oneShotReachable || snapshotReachable
                ? 'Persistent lane is connected but health is degraded; one-shot native diagnostics still reach the host.'
                : 'Persistent lane is connected but health is degraded.',
            recommendedAction: oneShotReachable || snapshotReachable
                ? 'Reseat the long-lived native port and compare persistent vs one-shot host identity.'
                : 'Inspect the native host log and reconnect the long-lived native port.',
            persistentConnected: true,
            persistentBrokerRole,
            oneShotBrokerRole,
            snapshotBrokerRole,
            reconnectScheduledFor: nativeConnection?.reconnectScheduledFor,
            reconnectAttempt: nativeConnection?.reconnectAttempt,
            snapshotMatchesPersistent: snapshot?.matches_persistent_host,
        };
    }
    if (oneShotReachable || snapshotReachable) {
        return {
            status: reconnectPending ? 'reconnect_pending' : 'oneshot_only',
            summary: reconnectPending
                ? 'One-shot sendNativeMessage() diagnostics reach the native host, but the persistent connectNative() lane is still disconnected and waiting to reconnect.'
                : 'One-shot sendNativeMessage() diagnostics reach the native host, but the persistent connectNative() lane is disconnected.',
            recommendedAction: reconnectPending
                ? 'Wait for or trigger an immediate persistent reconnect; the host manifest appears reachable.'
                : 'Trigger an immediate persistent reconnect; the host manifest appears reachable.',
            persistentConnected: false,
            persistentBrokerRole,
            oneShotBrokerRole,
            snapshotBrokerRole,
            reconnectScheduledFor: nativeConnection?.reconnectScheduledFor,
            reconnectAttempt: nativeConnection?.reconnectAttempt,
            snapshotMatchesPersistent: snapshot?.matches_persistent_host,
        };
    }
    if (nativeConnection?.lastHealthError || nativeConnection?.lastOneShotProbeError || nativeConnection?.lastDisconnectReason || input.lastNativeStatusError) {
        return {
            status: 'native_host_unreachable',
            summary: 'Neither the persistent lane nor one-shot diagnostics currently confirm native-host reachability.',
            recommendedAction: 'Inspect native-host installation, manifest targets, and browser logs, then retry reconnect.',
            persistentConnected: false,
            persistentBrokerRole,
            oneShotBrokerRole,
            snapshotBrokerRole,
            reconnectScheduledFor: nativeConnection?.reconnectScheduledFor,
            reconnectAttempt: nativeConnection?.reconnectAttempt,
            snapshotMatchesPersistent: snapshot?.matches_persistent_host,
        };
    }
    return {
        status: 'unknown',
        summary: 'Native-lane state has not been established yet.',
        recommendedAction: 'Run bridge.status or bridge.probe to collect native-lane evidence.',
        persistentConnected,
        persistentBrokerRole,
        oneShotBrokerRole,
        snapshotBrokerRole,
        reconnectScheduledFor: nativeConnection?.reconnectScheduledFor,
        reconnectAttempt: nativeConnection?.reconnectAttempt,
        snapshotMatchesPersistent: snapshot?.matches_persistent_host,
    };
}
