import assert from 'node:assert/strict';
import { deriveNativeLaneDiagnosis } from '../dist/shared/native-lane.js';

const persistentHealthy = deriveNativeLaneDiagnosis({
  nativeConnection: {
    connected: true,
    lastHealthOk: true,
    persistentBroker: { role: 'owner' },
  },
  lastNativeStatusSnapshot: {
    capturedAt: '2026-03-17T17:00:00.000Z',
    broker: { role: 'secondary' },
    matches_persistent_host: true,
  },
  now: Date.parse('2026-03-17T17:00:05.000Z'),
});
assert.equal(persistentHealthy.status, 'persistent_healthy');
assert.equal(persistentHealthy.persistentBrokerRole, 'owner');

const oneShotOnly = deriveNativeLaneDiagnosis({
  nativeConnection: {
    connected: false,
    lastOneShotProbeOk: true,
    lastOneShotProbeBroker: { role: 'secondary' },
  },
  lastNativeStatusSnapshot: {
    capturedAt: '2026-03-17T17:01:00.000Z',
    native_host: 'com.glasstty.bridge',
    broker: { role: 'secondary' },
  },
  now: Date.parse('2026-03-17T17:01:05.000Z'),
});
assert.equal(oneShotOnly.status, 'oneshot_only');
assert.match(oneShotOnly.recommendedAction, /immediate persistent reconnect/i);

const reconnectPending = deriveNativeLaneDiagnosis({
  nativeConnection: {
    connected: false,
    reconnectScheduledFor: '2026-03-17T17:03:00.000Z',
    reconnectAttempt: 2,
    lastOneShotProbeOk: true,
  },
  now: Date.parse('2026-03-17T17:01:05.000Z'),
});
assert.equal(reconnectPending.status, 'reconnect_pending');
assert.equal(reconnectPending.reconnectAttempt, 2);

const degraded = deriveNativeLaneDiagnosis({
  nativeConnection: {
    connected: true,
    lastHealthOk: false,
    lastHealthError: 'timeout after 1500ms',
    lastOneShotProbeOk: true,
  },
  lastNativeStatusSnapshot: {
    capturedAt: '2026-03-17T17:05:00.000Z',
    native_host: 'com.glasstty.bridge',
  },
  now: Date.parse('2026-03-17T17:05:05.000Z'),
});
assert.equal(degraded.status, 'persistent_degraded');
assert.match(degraded.summary, /one-shot native diagnostics still reach the host/i);

const unreachable = deriveNativeLaneDiagnosis({
  nativeConnection: {
    connected: false,
    lastDisconnectReason: 'native host not found',
  },
});
assert.equal(unreachable.status, 'native_host_unreachable');

console.log(JSON.stringify({
  ok: true,
  cases: {
    persistentHealthy,
    oneShotOnly,
    reconnectPending,
    degraded,
    unreachable,
  },
}, null, 2));
