import assert from 'node:assert/strict';
import {
  BoundedChannel,
  LANES,
  PRIORITIES,
  REVISION,
  VERSION,
  availableCapabilityTierNames,
  boot,
  capabilityTierNames,
  createEnvelope,
  createObjectRef,
  createTransferObject,
  createTransferObjectRef,
  detectCapabilities,
  spawnWorkerAgent
} from '../src/browserrt.mjs';

assert.equal(REVISION, 'rev0005');
assert.equal(VERSION, '0.0.5');
assert.ok(LANES.includes('storage'));
assert.ok(LANES.includes('gpu'));
assert.ok(LANES.includes('plugin'));
assert.ok(PRIORITIES.includes('user-blocking'));
assert.ok(capabilityTierNames().includes('mesh'));

const caps = detectCapabilities();
assert.equal(typeof caps.sharedArrayBuffer, 'boolean');
assert.equal(typeof caps.transferableArrayBuffer, 'boolean');
assert.equal(typeof caps.opfs, 'boolean');
assert.equal(typeof caps.webLocks, 'boolean');
assert.equal(typeof caps.measureMemory, 'boolean');
assert.ok(availableCapabilityTierNames(caps).includes('basic'));

const ref = createObjectRef('opfs', { id: 'opfs:demo-block', bytes: 128, block: 'demo-block' });
assert.deepEqual({ kind: ref.kind, id: ref.id, bytes: ref.bytes, block: ref.block }, { kind: 'opfs', id: 'opfs:demo-block', bytes: 128, block: 'demo-block' });
assert.throws(() => createObjectRef('bogus', { bytes: 1 }), /Unsupported object ref kind/);
assert.throws(() => createObjectRef('inline', { bytes: -1 }), /non-negative/);

const transferRef = createTransferObjectRef(new ArrayBuffer(8), { id: 'transfer:ref-only' });
assert.equal(transferRef.kind, 'transfer');
assert.equal(transferRef.bytes, 8);
const env = createEnvelope('demo-op', { lane: 'cpu', priority: 'user-visible', payloadRef: transferRef });
assert.equal(env.magic, 'BRT1');
assert.equal(env.payloadRef.id, 'transfer:ref-only');

const rt = await boot({ telemetry: 'always', proof: 'rev0005' });
assert.equal(rt.revision, 'rev0005');
assert.equal(rt.report.executableProofs.workerAgent, true);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'runtime:boot'));

const tracedTransfer = rt.transferObject(new Uint8Array([1, 2, 3, 4]).buffer, { id: 'transfer:object' });
assert.equal(tracedTransfer.ref.bytes, 4);
assert.equal(tracedTransfer.transferList.length, 1);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'object:transfer-ref'));

const ch = rt.channel({ capacity: 2, overflow: 'drop-newest', label: 'proof-channel' });
const channelReceipts = [await ch.send('a'), await ch.send('b'), await ch.send('c')];
assert.deepEqual(channelReceipts, [
  { disposition: 'queued' },
  { disposition: 'queued' },
  { disposition: 'dropped-newest' }
]);
assert.equal(await ch.receive(), 'a');
assert.equal(await ch.receive(), 'b');

const directChannel = new BoundedChannel({ capacity: 1, overflow: 'drop-oldest', label: 'direct-smoke' });
assert.deepEqual(await directChannel.send('a'), { disposition: 'queued' });
assert.deepEqual(await directChannel.send('b'), { disposition: 'dropped-oldest' });
assert.equal(await directChannel.receive(), 'b');

const waiting = rt.channel({ capacity: 1, overflow: 'wait', label: 'wait-smoke' });
await waiting.send(1);
const sendPromise = waiting.send(2);
assert.equal(waiting.size(), 1);
assert.equal(await waiting.receive(), 1);
assert.deepEqual(await sendPromise, { disposition: 'queued-after-wait' });
assert.equal(await waiting.receive(), 2);
assert.ok(rt.trace.count('channel:create') >= 1);

const agent = await spawnWorkerAgent({ name: 'smoke-agent', trace: rt.trace });
const ping = await agent.call('ping', { value: 'hello' });
assert.equal(ping.pong, true);
assert.equal(ping.protocol, 1);
assert.equal(ping.payload.value, 'hello');
assert.equal(ping.envelope.magic, 'BRT1');

const sumBuffer = new ArrayBuffer(16);
new Uint32Array(sumBuffer).set([1, 2, 3, 4]);
const transferObject = createTransferObject(sumBuffer, { id: 'transfer:sum-u32' });
const sumResult = await agent.call('sum-u32', { buffer: transferObject.buffer, ref: transferObject.ref }, { transfer: transferObject.transferList, priority: 'user-blocking' });
assert.equal(sumResult.sum, 10);
assert.equal(sumResult.count, 4);
assert.equal(sumResult.bytes, 16);
assert.equal(sumResult.ref.id, 'transfer:sum-u32');
assert.equal(transferObject.buffer.byteLength, 0, 'transferred ArrayBuffer should detach in sender');
await agent.terminate('smoke-agent-complete');

const supervisor = rt.supervisor({ name: 'smoke-supervisor', restartLimit: 1 });
await supervisor.start();
const supervisorPingBefore = await supervisor.call('ping', { phase: 'before-crash' });
assert.equal(supervisorPingBefore.pong, true);
await assert.rejects(() => supervisor.call('crash-now', {}, { timeoutMs: 1000 }), /exited|terminated|call timed out/);
const supervisorPingAfter = await supervisor.call('ping', { phase: 'after-crash' });
assert.equal(supervisorPingAfter.pong, true);
assert.equal(supervisor.snapshot().restartCount, 1);
await supervisor.close();

const closeTrace = rt.close();
const eventKinds = rt.trace.kinds();
for (const required of ['runtime:boot', 'runtime:boot-report', 'channel:send', 'channel:receive', 'agent:spawn', 'agent:ready', 'agent:call', 'agent:result', 'agent:exit', 'supervisor:spawn-request', 'supervisor:observed-exit', 'runtime:close']) {
  assert.ok(eventKinds.includes(required), `missing trace event ${required}`);
}
assert.ok(closeTrace.length >= 20);
console.log('BrowserRT smoke test passed');
