export const VERSION = '0.0.5';
export const REVISION = 'rev0005';

export const LANES = Object.freeze([
  'main',
  'interactive',
  'cpu',
  'storage',
  'gpu',
  'render',
  'media',
  'audio',
  'ml',
  'network',
  'cross-tab',
  'plugin',
  'maintenance'
]);

export const PRIORITIES = Object.freeze([
  'critical',
  'user-blocking',
  'user-visible',
  'background',
  'maintenance'
]);

export const CAPABILITY_TIERS = Object.freeze([
  { id: 0, name: 'basic', meaning: 'main thread plus structured clone fallback' },
  { id: 1, name: 'workered', meaning: 'dedicated workers and transferables' },
  { id: 2, name: 'isolated', meaning: 'SharedArrayBuffer and Atomics in cross-origin-isolated contexts' },
  { id: 3, name: 'persistent', meaning: 'OPFS block store and storage worker paths' },
  { id: 4, name: 'accelerated', meaning: 'WebGPU and other accelerated adapter paths' },
  { id: 5, name: 'mesh', meaning: 'cross-tab coordination through same-origin primitives' }
]);

const OBJECT_REF_KINDS = new Set(['inline', 'transfer', 'shared', 'opfs', 'stream', 'gpu']);
const CHANNEL_OVERFLOWS = new Set(['wait', 'drop-oldest', 'drop-newest', 'fail']);
let NEXT_ID = 1;

function nextId(prefix) {
  const id = NEXT_ID++;
  return `${prefix}:${id.toString(36)}`;
}

function environmentName(g = globalThis) {
  if (typeof g.window === 'object' && g.window === g) return 'browser-window';
  if (g.process?.versions?.node) return 'node';
  return 'worker-or-unknown';
}

function describeError(error) {
  if (!error || typeof error !== 'object') return { name: 'Error', message: String(error) };
  return {
    name: error.name || 'Error',
    message: error.message || String(error),
    stack: error.stack
  };
}

function reviveError(errorLike) {
  const err = new Error(errorLike?.message || 'Unknown BrowserRT worker error');
  err.name = errorLike?.name || 'BrowserRTWorkerError';
  if (errorLike?.stack) err.stack = errorLike.stack;
  return err;
}

export function detectCapabilities(g = globalThis) {
  const nav = g.navigator || {};
  const storage = nav.storage || {};
  const scheduler = g.scheduler || {};
  const nodeLike = Boolean(g.process?.versions?.node);
  return Object.freeze({
    environment: environmentName(g),
    workers: typeof g.Worker === 'function' || nodeLike,
    moduleWorkers: typeof g.Worker === 'function' || nodeLike,
    transferableArrayBuffer: typeof g.ArrayBuffer === 'function',
    sharedArrayBuffer: typeof g.SharedArrayBuffer === 'function',
    atomics: typeof g.Atomics === 'object',
    crossOriginIsolated: Boolean(g.crossOriginIsolated),
    opfs: typeof storage.getDirectory === 'function',
    storageEstimate: typeof storage.estimate === 'function',
    webgpu: Boolean(nav.gpu),
    webnn: Boolean(nav.ml),
    offscreenCanvas: typeof g.OffscreenCanvas === 'function',
    webcodecs: typeof g.VideoEncoder === 'function' || typeof g.VideoDecoder === 'function',
    videoFrameTransfer: typeof g.VideoFrame === 'function',
    broadcastChannel: typeof g.BroadcastChannel === 'function',
    messageChannel: typeof g.MessageChannel === 'function',
    sharedWorker: typeof g.SharedWorker === 'function',
    serviceWorker: Boolean(nav.serviceWorker),
    webLocks: Boolean(nav.locks),
    schedulerPostTask: typeof scheduler.postTask === 'function',
    schedulerYield: typeof scheduler.yield === 'function',
    performanceObserver: typeof g.PerformanceObserver === 'function',
    measureMemory: Boolean(g.performance && typeof g.performance.measureUserAgentSpecificMemory === 'function')
  });
}

export function capabilityTierNames() {
  return CAPABILITY_TIERS.map((tier) => tier.name);
}

export function availableCapabilityTierNames(capabilities = detectCapabilities()) {
  const names = ['basic'];
  if (capabilities.workers && capabilities.transferableArrayBuffer) names.push('workered');
  if (capabilities.sharedArrayBuffer && capabilities.atomics && capabilities.crossOriginIsolated) names.push('isolated');
  if (capabilities.opfs) names.push('persistent');
  if (capabilities.webgpu) names.push('accelerated');
  if (capabilities.broadcastChannel && capabilities.webLocks) names.push('mesh');
  return names;
}

export function createObjectRef(kind, fields = {}) {
  if (!OBJECT_REF_KINDS.has(kind)) throw new Error(`Unsupported object ref kind: ${kind}`);
  const bytes = fields.bytes ?? fields.length ?? 0;
  if (!Number.isFinite(bytes) || bytes < 0) {
    throw new Error('Object ref bytes/length must be a non-negative finite number');
  }
  return Object.freeze({
    kind,
    id: fields.id ?? nextId(kind),
    bytes,
    ownership: fields.ownership ?? (kind === 'transfer' ? 'owned-main' : 'unspecified'),
    createdAt: fields.createdAt ?? Date.now(),
    ...fields
  });
}

export function createTransferObjectRef(buffer, fields = {}) {
  if (!(buffer instanceof ArrayBuffer)) throw new Error('createTransferObjectRef requires an ArrayBuffer');
  return createObjectRef('transfer', {
    id: fields.id ?? nextId('transfer'),
    bytes: buffer.byteLength,
    transferType: 'ArrayBuffer',
    ownership: 'owned-main',
    ...fields
  });
}

export function createTransferObject(buffer, fields = {}) {
  const ref = createTransferObjectRef(buffer, fields);
  return Object.freeze({ ref, buffer, transferList: [buffer] });
}

export function createEnvelope(op, fields = {}) {
  if (typeof op !== 'string' || op.length === 0) throw new Error('Envelope op must be a non-empty string');
  return Object.freeze({
    magic: 'BRT1',
    version: 1,
    id: fields.id ?? nextId('env'),
    parentId: fields.parentId ?? null,
    traceId: fields.traceId ?? null,
    op,
    lane: fields.lane ?? 'cpu',
    priority: fields.priority ?? 'user-visible',
    deadlineMs: fields.deadlineMs ?? 0,
    flags: fields.flags ?? 0,
    payloadRef: fields.payloadRef ?? null
  });
}

export class TraceLog {
  #events = [];
  #nextSeq = 1;

  emit(kind, detail = {}) {
    const event = Object.freeze({ seq: this.#nextSeq++, t: Date.now(), kind, ...detail });
    this.#events.push(event);
    return event;
  }

  snapshot() {
    return this.#events.slice();
  }

  find(kind) {
    return this.#events.filter((event) => event.kind === kind);
  }

  count(kind) {
    return this.find(kind).length;
  }

  kinds() {
    return [...new Set(this.#events.map((event) => event.kind))];
  }
}

export class BoundedChannel {
  constructor({ capacity = 1, overflow = 'wait', label = 'channel', trace = null } = {}) {
    if (!Number.isInteger(capacity) || capacity < 1) throw new Error('BoundedChannel capacity must be a positive integer');
    if (!CHANNEL_OVERFLOWS.has(overflow)) throw new Error(`Unsupported overflow policy: ${overflow}`);
    this.capacity = capacity;
    this.overflow = overflow;
    this.label = label;
    this.queue = [];
    this.waitingReceivers = [];
    this.waitingSenders = [];
    this.trace = trace;
    this.trace?.emit('channel:create', { label: this.label, capacity: this.capacity, overflow: this.overflow });
  }

  async send(value) {
    if (this.waitingReceivers.length) {
      const resolve = this.waitingReceivers.shift();
      resolve(value);
      this.trace?.emit('channel:send', { label: this.label, disposition: 'delivered', size: this.size() });
      return { disposition: 'delivered' };
    }
    if (this.queue.length < this.capacity) {
      this.queue.push(value);
      this.trace?.emit('channel:send', { label: this.label, disposition: 'queued', size: this.size() });
      return { disposition: 'queued' };
    }
    if (this.overflow === 'drop-oldest') {
      this.queue.shift();
      this.queue.push(value);
      this.trace?.emit('channel:send', { label: this.label, disposition: 'dropped-oldest', size: this.size() });
      return { disposition: 'dropped-oldest' };
    }
    if (this.overflow === 'drop-newest') {
      this.trace?.emit('channel:send', { label: this.label, disposition: 'dropped-newest', size: this.size() });
      return { disposition: 'dropped-newest' };
    }
    if (this.overflow === 'fail') {
      this.trace?.emit('channel:send', { label: this.label, disposition: 'failed-full', size: this.size() });
      throw new Error(`BoundedChannel ${this.label} is full`);
    }
    this.trace?.emit('channel:send', { label: this.label, disposition: 'waiting', size: this.size() });
    return await new Promise((resolve) => this.waitingSenders.push({ value, resolve }));
  }

  async receive() {
    if (this.queue.length) {
      const value = this.queue.shift();
      if (this.waitingSenders.length) {
        const sender = this.waitingSenders.shift();
        this.queue.push(sender.value);
        sender.resolve({ disposition: 'queued-after-wait' });
      }
      this.trace?.emit('channel:receive', { label: this.label, size: this.size() });
      return value;
    }
    this.trace?.emit('channel:receive-wait', { label: this.label, size: this.size() });
    return await new Promise((resolve) => this.waitingReceivers.push(resolve));
  }

  size() {
    return this.queue.length;
  }
}

export class WorkerAgent {
  #worker;
  #trace;
  #pending = new Map();
  #readyResolve;
  #readyReject;
  #exitCallbacks = new Set();
  #closed = false;
  #failed = false;
  #exitNotified = false;

  constructor({ worker, name = 'agent', trace = new TraceLog() }) {
    this.name = name;
    this.id = nextId('agent');
    this.#worker = worker;
    this.#trace = trace;
    this.ready = new Promise((resolve, reject) => {
      this.#readyResolve = resolve;
      this.#readyReject = reject;
    });
    this.#wireWorker(worker);
    this.#trace.emit('agent:spawn', { agentId: this.id, name: this.name });
  }

  get closed() { return this.#closed; }
  get failed() { return this.#failed; }
  get trace() { return this.#trace; }

  onExit(callback) {
    this.#exitCallbacks.add(callback);
    return () => this.#exitCallbacks.delete(callback);
  }

  async call(op, payload = {}, { transfer = [], timeoutMs = 0, lane = 'cpu', priority = 'user-visible' } = {}) {
    if (this.#closed) throw new Error(`WorkerAgent ${this.name} is closed`);
    await this.ready;
    const id = nextId('call');
    const envelope = createEnvelope(op, { lane, priority, payloadRef: payload.objectRef || payload.ref || null });
    const message = { type: 'agent:call', id, envelope, op, payload };
    this.#trace.emit('agent:call', { agentId: this.id, callId: id, op, transferCount: transfer.length, lane, priority });
    return await new Promise((resolve, reject) => {
      let timer = null;
      if (timeoutMs > 0) {
        timer = setTimeout(() => {
          this.#pending.delete(id);
          const err = new Error(`WorkerAgent call timed out: ${op}`);
          this.#trace.emit('agent:call-timeout', { agentId: this.id, callId: id, op, timeoutMs });
          reject(err);
        }, timeoutMs);
      }
      this.#pending.set(id, { resolve, reject, timer, op });
      try {
        if (transfer.length) this.#worker.postMessage(message, transfer);
        else this.#worker.postMessage(message);
      } catch (error) {
        this.#pending.delete(id);
        if (timer) clearTimeout(timer);
        this.#trace.emit('agent:post-error', { agentId: this.id, callId: id, op, error: describeError(error) });
        reject(error);
      }
    });
  }

  async terminate(reason = 'caller-terminate') {
    if (this.#closed) return { disposition: 'already-closed' };
    this.#trace.emit('agent:terminate', { agentId: this.id, name: this.name, reason });
    this.#closed = true;
    this.#rejectPending(new Error(`WorkerAgent terminated: ${reason}`));
    const result = this.#worker.terminate?.();
    if (result && typeof result.then === 'function') await result;
    return { disposition: 'terminated' };
  }

  #wireWorker(worker) {
    if (typeof worker.on === 'function') {
      worker.on('message', (message) => this.#handleMessage(message));
      worker.on('error', (error) => this.#handleError(error));
      worker.on('exit', (code) => this.#handleExit({ code }));
      return;
    }
    worker.addEventListener('message', (event) => this.#handleMessage(event.data));
    worker.addEventListener('error', (event) => this.#handleError(event.error || event.message || event));
  }

  #handleMessage(message) {
    if (!message || typeof message !== 'object') return;
    if (message.type === 'agent:ready') {
      this.#trace.emit('agent:ready', { agentId: this.id, name: this.name, detail: message.detail || {} });
      this.#readyResolve?.(this);
      return;
    }
    if (message.type === 'agent:trace') {
      this.#trace.emit(message.kind || 'agent:trace', { agentId: this.id, ...(message.detail || {}) });
      return;
    }
    if (message.type === 'agent:result' || message.type === 'agent:error') {
      const pending = this.#pending.get(message.id);
      if (!pending) return;
      this.#pending.delete(message.id);
      if (pending.timer) clearTimeout(pending.timer);
      if (message.type === 'agent:result') {
        this.#trace.emit('agent:result', { agentId: this.id, callId: message.id, op: pending.op });
        pending.resolve(message.result);
      } else {
        const err = reviveError(message.error);
        this.#trace.emit('agent:call-error', { agentId: this.id, callId: message.id, op: pending.op, error: describeError(err) });
        pending.reject(err);
      }
    }
  }

  #handleError(error) {
    const err = error instanceof Error ? error : new Error(String(error));
    this.#failed = true;
    this.#closed = true;
    this.#trace.emit('agent:error', { agentId: this.id, name: this.name, error: describeError(err) });
    this.#readyReject?.(err);
    this.#rejectPending(err);
    this.#notifyExit({ code: null, error: err });
  }

  #handleExit({ code = null } = {}) {
    const err = new Error(`WorkerAgent ${this.name} exited with code ${code}`);
    this.#closed = true;
    this.#trace.emit('agent:exit', { agentId: this.id, name: this.name, code });
    this.#readyReject?.(err);
    this.#rejectPending(err);
    this.#notifyExit({ code, error: err });
  }

  #notifyExit({ code, error }) {
    if (this.#exitNotified) return;
    this.#exitNotified = true;
    for (const callback of this.#exitCallbacks) callback({ agent: this, code, error });
  }

  #rejectPending(error) {
    for (const [id, pending] of this.#pending) {
      if (pending.timer) clearTimeout(pending.timer);
      pending.reject(error);
      this.#trace.emit('agent:pending-reject', { agentId: this.id, callId: id, op: pending.op, error: describeError(error) });
    }
    this.#pending.clear();
  }
}

export async function spawnWorkerAgent({ workerURL = null, name = 'browserrt-agent', trace = new TraceLog(), workerOptions = {} } = {}) {
  let worker;
  if (typeof globalThis.Worker === 'function' && environmentName() === 'browser-window') {
    const url = workerURL || new URL('./browser-agent-worker.mjs', import.meta.url);
    worker = new globalThis.Worker(url, { type: 'module', name, ...workerOptions });
  } else {
    const { Worker } = await import('node:worker_threads');
    const url = workerURL || new URL('./node-agent-worker.mjs', import.meta.url);
    worker = new Worker(url, { name, ...workerOptions });
  }
  const agent = new WorkerAgent({ worker, name, trace });
  await agent.ready;
  return agent;
}

export class Supervisor {
  constructor({ name = 'supervisor', workerURL = null, trace = new TraceLog(), restartLimit = 1 } = {}) {
    if (!Number.isInteger(restartLimit) || restartLimit < 0) throw new Error('Supervisor restartLimit must be a non-negative integer');
    this.name = name;
    this.workerURL = workerURL;
    this.trace = trace;
    this.restartLimit = restartLimit;
    this.restartCount = 0;
    this.agent = null;
    this.closed = false;
  }

  async start() {
    await this.#ensureAgent('start');
    return this;
  }

  async call(op, payload = {}, options = {}) {
    const agent = await this.#ensureAgent('call');
    try {
      return await agent.call(op, payload, options);
    } catch (error) {
      if (agent.closed || agent.failed) this.agent = null;
      this.trace.emit('supervisor:call-error', { supervisor: this.name, op, error: describeError(error) });
      throw error;
    }
  }

  snapshot() {
    return Object.freeze({
      name: this.name,
      restartCount: this.restartCount,
      restartLimit: this.restartLimit,
      agentId: this.agent?.id ?? null,
      agentAlive: Boolean(this.agent && !this.agent.closed)
    });
  }

  async close() {
    this.closed = true;
    this.trace.emit('supervisor:close', { supervisor: this.name, restartCount: this.restartCount });
    if (this.agent && !this.agent.closed) await this.agent.terminate('supervisor-close');
    return this.snapshot();
  }

  async #ensureAgent(reason) {
    if (this.closed) throw new Error(`Supervisor ${this.name} is closed`);
    if (this.agent && !this.agent.closed) return this.agent;
    if (this.agent?.closed) this.agent = null;
    if (this.restartCount >= this.restartLimit && reason !== 'start') {
      throw new Error(`Supervisor ${this.name} restart limit reached`);
    }
    if (reason !== 'start') {
      this.restartCount += 1;
      this.trace.emit('supervisor:restart', { supervisor: this.name, reason, restartCount: this.restartCount });
    }
    this.trace.emit('supervisor:spawn-request', { supervisor: this.name, reason, restartCount: this.restartCount });
    const agent = await spawnWorkerAgent({ workerURL: this.workerURL, name: `${this.name}-agent-${this.restartCount}`, trace: this.trace });
    agent.onExit(({ code }) => {
      this.trace.emit('supervisor:observed-exit', { supervisor: this.name, code, restartCount: this.restartCount });
      if (this.agent === agent) this.agent = null;
    });
    this.agent = agent;
    this.trace.emit('supervisor:agent-ready', { supervisor: this.name, agentId: agent.id, reason });
    return agent;
  }
}

export function createSupervisor(config = {}) {
  return new Supervisor(config);
}

export function createBootReport({ capabilities = detectCapabilities(), options = {} } = {}) {
  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    environment: capabilities.environment,
    createdAt: new Date().toISOString(),
    options: Object.freeze({ ...options }),
    capabilities,
    availableTierNames: availableCapabilityTierNames(capabilities),
    lanes: LANES.slice(),
    priorities: PRIORITIES.slice(),
    capabilityTiers: CAPABILITY_TIERS.map((tier) => ({ ...tier })),
    executableProofs: Object.freeze({
      traceLog: true,
      boundedChannel: true,
      transferableObjectRef: true,
      workerAgent: true,
      supervisorRestart: true,
      storageLane: false,
      gpuLane: false,
      browserCdpHarness: false,
      testFacility: true
    })
  });
}

export async function boot(options = {}) {
  const trace = new TraceLog();
  const capabilities = detectCapabilities();
  const report = createBootReport({ capabilities, options });
  trace.emit('runtime:boot', { revision: REVISION, version: VERSION, capabilities });
  trace.emit('runtime:boot-report', { report });
  return Object.freeze({
    version: VERSION,
    revision: REVISION,
    options: Object.freeze({ ...options }),
    capabilities,
    report,
    trace,
    channel(config) { return new BoundedChannel({ ...(config || {}), trace }); },
    objectRef(kind, fields) {
      const ref = createObjectRef(kind, fields);
      trace.emit('object:ref', { refKind: ref.kind, id: ref.id, bytes: ref.bytes });
      return ref;
    },
    transferObject(buffer, fields) {
      const obj = createTransferObject(buffer, fields);
      trace.emit('object:transfer-ref', { id: obj.ref.id, bytes: obj.ref.bytes, transferType: obj.ref.transferType });
      return obj;
    },
    async spawnAgent(config = {}) { return await spawnWorkerAgent({ ...config, trace: config.trace || trace }); },
    supervisor(config = {}) { return createSupervisor({ ...config, trace: config.trace || trace }); },
    close() {
      trace.emit('runtime:close', { revision: REVISION });
      return trace.snapshot();
    }
  });
}
