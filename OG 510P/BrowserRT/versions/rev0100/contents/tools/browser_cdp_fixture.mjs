import http from 'node:http';
import net from 'node:net';
import { spawn } from 'node:child_process';
import { access, mkdtemp, readFile, rm, stat, writeFile } from 'node:fs/promises';
import { constants as fsConstants } from 'node:fs';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { performance } from 'node:perf_hooks';

export const POLICY_PATH = '/etc/chromium/policies/managed/000_policy_merge.json';
export const HOST = '127.0.0.1';

export const sleep = (ms) => new Promise((resolveSleep) => setTimeout(resolveSleep, ms));

export async function canExec(path) {
  try { await access(path, fsConstants.X_OK); return true; } catch { return false; }
}

export async function findChromium(explicit) {
  for (const candidate of [explicit, process.env.BROWSERRT_CHROMIUM, '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable'].filter(Boolean)) {
    if (await canExec(candidate)) return candidate;
  }
  return null;
}

export async function freePort() {
  return await new Promise((resolvePort, reject) => {
    const server = net.createServer();
    server.listen(0, HOST, () => {
      const port = server.address().port;
      server.close(() => resolvePort(port));
    });
    server.on('error', reject);
  });
}

export function contentType(pathname) {
  if (pathname.endsWith('.mjs') || pathname.endsWith('.js')) return 'text/javascript; charset=utf-8';
  if (pathname.endsWith('.json')) return 'application/json; charset=utf-8';
  if (pathname.endsWith('.html')) return 'text/html; charset=utf-8';
  if (pathname.endsWith('.wasm')) return 'application/wasm';
  return 'text/plain; charset=utf-8';
}

export async function startProbeServer({ root = process.cwd(), pagePath = '/probe.html', pageTitle = 'BrowserRT probe', body = null, allowedPrefixes = ['src/'], routes = {} } = {}) {
  const normalizedPagePath = pagePath.startsWith('/') ? pagePath : `/${pagePath}`;
  const requests = [];
  const rootResolved = resolve(root);
  const routeEntries = new Map(Object.entries(routes || {}).map(([key, value]) => [key.startsWith('/') ? key : `/${key}`, value]));
  const server = http.createServer(async (req, res) => {
    const started = performance.now();
    const url = new URL(req.url || '/', `http://${HOST}`);
    const row = { method: req.method, path: url.pathname, t: Date.now() };
    requests.push(row);
    res.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
    res.setHeader('Cross-Origin-Embedder-Policy', 'require-corp');
    res.setHeader('Cross-Origin-Resource-Policy', 'same-origin');
    res.setHeader('Cache-Control', 'no-store');
    try {
      if (routeEntries.has(url.pathname)) {
        const rawRoute = routeEntries.get(url.pathname);
        const route = rawRoute && typeof rawRoute === 'object' && !(rawRoute instanceof Uint8Array) ? rawRoute : { body: rawRoute };
        for (const [key, value] of Object.entries(route.headers || {})) res.setHeader(key, value);
        res.setHeader('Content-Type', route.contentType || contentType(url.pathname));
        res.end(route.body ?? '');
      } else if (url.pathname === '/' || url.pathname === normalizedPagePath) {
        res.setHeader('Content-Type', 'text/html; charset=utf-8');
        if (body !== null && body !== undefined) {
          res.end(body);
        } else {
          const rel = normalizedPagePath.replace(/^\//, '');
          const full = resolve(rootResolved, rel);
          const allowed = allowedPrefixes.some((prefix) => rel.startsWith(prefix));
          if (allowed && full.startsWith(rootResolved + '/')) {
            res.end(await readFile(full));
          } else {
            res.end(`<!doctype html><meta charset="utf-8"><title>${pageTitle}</title><body>${pageTitle}</body>`);
          }
        }
      } else if (url.pathname === '/favicon.ico') {
        res.statusCode = 204;
        res.end();
      } else {
        const rel = url.pathname.replace(/^\//, '');
        if (!allowedPrefixes.some((prefix) => rel.startsWith(prefix))) {
          res.statusCode = 404;
          res.end('not found');
          return;
        }
        const full = resolve(rootResolved, rel);
        if (!full.startsWith(rootResolved + '/')) {
          res.statusCode = 403;
          res.end('forbidden');
          return;
        }
        const data = await readFile(full);
        res.setHeader('Content-Type', contentType(full));
        res.end(data);
      }
    } catch (error) {
      res.statusCode = 500;
      res.end(String(error?.message || error));
    } finally {
      row.durationMs = Math.round(performance.now() - started);
    }
  });
  await new Promise((resolveListen) => server.listen(0, HOST, resolveListen));
  return {
    port: server.address().port,
    pagePath: normalizedPagePath,
    requests,
    close: () => new Promise((resolveClose) => server.close(resolveClose))
  };
}

export async function relaxPolicy(enabled, policyPath = POLICY_PATH) {
  const result = { requested: Boolean(enabled), path: policyPath, exists: false, applied: false, restored: false, originalHadGlobalBlock: false, error: null };
  let originalText = null;
  if (!enabled) return { result, restore: async () => { result.restored = true; } };
  try {
    await stat(policyPath);
    result.exists = true;
    originalText = await readFile(policyPath, 'utf8');
    const policy = JSON.parse(originalText);
    result.originalHadGlobalBlock = Array.isArray(policy.URLBlocklist) && policy.URLBlocklist.includes('*');
    if (result.originalHadGlobalBlock) {
      policy.URLBlocklist = [];
      await writeFile(policyPath, JSON.stringify(policy, null, 2) + '\n');
      result.applied = true;
    }
  } catch (error) {
    result.error = String(error?.message || error);
  }
  return {
    result,
    restore: async () => {
      if (originalText !== null && result.applied) await writeFile(policyPath, originalText);
      result.restored = true;
    }
  };
}

export async function waitJson(url, timeoutMs) {
  const deadline = performance.now() + timeoutMs;
  let last = null;
  while (performance.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok) return await response.json();
      last = new Error(`${response.status} ${response.statusText}`);
    } catch (error) {
      last = error;
    }
    await sleep(100);
  }
  throw new Error(`Timed out waiting for ${url}: ${last?.message || 'no response'}`);
}


export async function waitCdpTarget(listUrl, pageUrl, timeoutMs) {
  const deadline = performance.now() + timeoutMs;
  let last = null;
  while (performance.now() < deadline) {
    try {
      const targets = await waitJson(listUrl, Math.min(1000, Math.max(100, deadline - performance.now())));
      const pageTargets = Array.isArray(targets) ? targets.filter((x) => x?.type === 'page') : [];
      const exact = pageTargets.find((x) => x.url === pageUrl && x.webSocketDebuggerUrl);
      const anyPage = pageTargets.find((x) => x.webSocketDebuggerUrl);
      const anyTarget = Array.isArray(targets) ? targets.find((x) => x?.webSocketDebuggerUrl) : null;
      const target = exact || anyPage || anyTarget;
      if (target?.webSocketDebuggerUrl) return { targets, target };
      last = new Error(`CDP target list had ${pageTargets.length} page target(s) but no websocket URL yet`);
    } catch (error) {
      last = error;
    }
    await sleep(100);
  }
  throw new Error(`Timed out waiting for CDP page target with websocket: ${last?.message || 'no target'}`);
}

export class CdpClient {
  constructor(url) {
    this.url = url;
    this.nextId = 1;
    this.pending = new Map();
    this.events = [];
    this.console = [];
    this.ws = new WebSocket(url);
    this.ws.addEventListener('message', (event) => this.onMessage(event));
  }

  async open(timeoutMs = 5000) {
    await new Promise((resolveOpen, rejectOpen) => {
      const timer = setTimeout(() => rejectOpen(new Error('CDP WebSocket open timeout')), timeoutMs);
      this.ws.addEventListener('open', () => { clearTimeout(timer); resolveOpen(); }, { once: true });
      this.ws.addEventListener('error', () => { clearTimeout(timer); rejectOpen(new Error('CDP WebSocket error')); }, { once: true });
    });
  }

  async send(method, params = {}, timeoutMs = 5000) {
    const id = this.nextId++;
    this.ws.send(JSON.stringify({ id, method, params }));
    return await new Promise((resolveSend, rejectSend) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        rejectSend(new Error(`CDP command timeout: ${method}`));
      }, timeoutMs);
      this.pending.set(id, { resolveSend, rejectSend, timer, method });
    });
  }

  onMessage(event) {
    const message = JSON.parse(event.data);
    if (message.id && this.pending.has(message.id)) {
      const pending = this.pending.get(message.id);
      this.pending.delete(message.id);
      clearTimeout(pending.timer);
      if (message.error) pending.rejectSend(new Error(`${pending.method}: ${JSON.stringify(message.error)}`));
      else pending.resolveSend(message);
      return;
    }
    this.events.push(message);
    if (message.method === 'Runtime.consoleAPICalled') {
      this.console.push({ type: message.params?.type, args: (message.params?.args || []).map((arg) => arg.value ?? arg.description ?? arg.type) });
    }
  }

  close() {
    try { this.ws.close(); } catch {}
  }
}

export async function evalJson(cdp, expression, timeoutMs) {
  const response = await cdp.send('Runtime.evaluate', {
    expression,
    awaitPromise: true,
    returnByValue: true,
    timeout: timeoutMs
  }, timeoutMs + 1000);
  if (response.result?.exceptionDetails) throw new Error(`Runtime.evaluate failed: ${JSON.stringify(response.result.exceptionDetails)}`);
  const value = response.result?.result?.value;
  return typeof value === 'string' ? JSON.parse(value) : value;
}


export async function getStorageUsageAndQuota(cdp, origin, timeoutMs = 5000) {
  const response = await cdp.send('Storage.getUsageAndQuota', { origin }, timeoutMs);
  return response.result || {};
}

export async function overrideStorageQuotaForOrigin(cdp, { origin, quotaSize }, timeoutMs = 5000) {
  if (!origin) throw new Error('overrideStorageQuotaForOrigin requires origin');
  if (!Number.isFinite(quotaSize) || quotaSize <= 0) throw new Error('overrideStorageQuotaForOrigin requires positive quotaSize');
  const before = await getStorageUsageAndQuota(cdp, origin, timeoutMs);
  await cdp.send('Storage.overrideQuotaForOrigin', { origin, quotaSize }, timeoutMs);
  const after = await getStorageUsageAndQuota(cdp, origin, timeoutMs);
  return { origin, quotaSize, before, after };
}

export async function resetStorageQuotaOverrideForOrigin(cdp, origin, timeoutMs = 5000) {
  if (!origin) throw new Error('resetStorageQuotaOverrideForOrigin requires origin');
  const before = await getStorageUsageAndQuota(cdp, origin, timeoutMs);
  await cdp.send('Storage.overrideQuotaForOrigin', { origin }, timeoutMs);
  const after = await getStorageUsageAndQuota(cdp, origin, timeoutMs);
  return { origin, before, after };
}

export async function connectBrowserCdp(cdpPort, timeoutMs = 5000) {
  const versionUrl = `http://${HOST}:${cdpPort}/json/version`;
  const version = await waitJson(versionUrl, timeoutMs);
  if (!version?.webSocketDebuggerUrl) throw new Error(`CDP browser websocket unavailable at ${versionUrl}`);
  const cdp = new CdpClient(version.webSocketDebuggerUrl);
  await cdp.open(timeoutMs);
  return { cdp, version, versionUrl };
}

export async function openPageTarget(browserCdp, { listUrl, url, timeoutMs = 5000, enableRuntime = true, enablePage = true } = {}) {
  if (!browserCdp) throw new Error('openPageTarget requires browserCdp');
  if (!url) throw new Error('openPageTarget requires url');
  const created = await browserCdp.send('Target.createTarget', { url, newWindow: false }, timeoutMs);
  const targetId = created.result?.targetId;
  if (!targetId) throw new Error(`Target.createTarget did not return targetId for ${url}`);
  const deadline = performance.now() + timeoutMs;
  let target = null;
  let targets = [];
  while (performance.now() < deadline) {
    targets = await waitJson(listUrl, Math.min(1000, Math.max(100, deadline - performance.now())));
    target = Array.isArray(targets) ? targets.find((row) => row.id === targetId && row.webSocketDebuggerUrl) : null;
    if (target) break;
    await sleep(50);
  }
  if (!target?.webSocketDebuggerUrl) throw new Error(`Timed out waiting for created page target ${targetId}`);
  const cdp = new CdpClient(target.webSocketDebuggerUrl);
  await cdp.open(timeoutMs);
  if (enableRuntime) await cdp.send('Runtime.enable', {}, timeoutMs);
  if (enablePage) await cdp.send('Page.enable', {}, timeoutMs);
  return {
    target,
    targetId,
    cdp,
    close: async () => {
      try { cdp.close(); } catch {}
      try { return await browserCdp.send('Target.closeTarget', { targetId }, timeoutMs); } catch (error) { return { error: String(error?.message || error) }; }
    }
  };
}

export async function closePageTarget(browserCdp, targetId, timeoutMs = 5000) {
  if (!browserCdp || !targetId) return { ok: false, reason: 'missing-browser-cdp-or-target-id' };
  try {
    const response = await browserCdp.send('Target.closeTarget', { targetId }, timeoutMs);
    return { ok: response.result?.success !== false, response: response.result || response };
  } catch (error) {
    return { ok: false, error: String(error?.message || error) };
  }
}


export async function listCdpTargets(browserCdp, timeoutMs = 5000) {
  if (!browserCdp) throw new Error('listCdpTargets requires browserCdp');
  const response = await browserCdp.send('Target.getTargets', {}, timeoutMs);
  return Array.isArray(response.result?.targetInfos) ? response.result.targetInfos : [];
}

export async function findCdpTargets(browserCdp, { type = null, urlIncludes = null, titleIncludes = null, timeoutMs = 5000 } = {}) {
  const targets = await listCdpTargets(browserCdp, timeoutMs);
  return targets.filter((target) => {
    if (type && target.type !== type) return false;
    if (urlIncludes && !String(target.url || '').includes(urlIncludes)) return false;
    if (titleIncludes && !String(target.title || '').includes(titleIncludes)) return false;
    return true;
  });
}

export async function closeCdpTargets(browserCdp, targets, timeoutMs = 5000) {
  const rows = [];
  for (const target of targets || []) {
    const targetId = target?.targetId || target?.id;
    if (!targetId) {
      rows.push({ ok: false, reason: 'missing-target-id', target });
      continue;
    }
    rows.push({ targetId, type: target.type || null, url: target.url || null, close: await closePageTarget(browserCdp, targetId, timeoutMs) });
  }
  return rows;
}

export async function closeServiceWorkerTargets(browserCdp, { urlIncludes = null, timeoutMs = 5000 } = {}) {
  const before = await findCdpTargets(browserCdp, { type: 'service_worker', urlIncludes, timeoutMs });
  const closed = await closeCdpTargets(browserCdp, before, timeoutMs);
  await sleep(50);
  const after = await findCdpTargets(browserCdp, { type: 'service_worker', urlIncludes, timeoutMs });
  return { before, closed, after, closedCount: closed.filter((row) => row.close?.ok !== false).length, afterCount: after.length };
}


async function runCommandForCleanup(command, args = [], timeoutMs = 1000) {
  return await new Promise((resolve) => {
    let stdout = '';
    let stderr = '';
    let settled = false;
    const child = spawn(command, args, { stdio: ['ignore', 'pipe', 'pipe'] });
    const timer = setTimeout(() => {
      if (settled) return;
      try { child.kill('SIGKILL'); } catch {}
      settled = true;
      resolve({ command, args, code: null, signal: 'SIGKILL', timedOut: true, stdout, stderr });
    }, timeoutMs);
    child.stdout?.on('data', (bytes) => { stdout += bytes.toString(); });
    child.stderr?.on('data', (bytes) => { stderr += bytes.toString(); });
    child.once('close', (code, signal) => {
      if (settled) return;
      clearTimeout(timer);
      settled = true;
      resolve({ command, args, code, signal, timedOut: false, stdout, stderr });
    });
    child.once('error', (error) => {
      if (settled) return;
      clearTimeout(timer);
      settled = true;
      resolve({ command, args, code: null, signal: null, timedOut: false, error: error?.message || String(error), stdout, stderr });
    });
  });
}

async function listBrowserProfileProcesses(pattern, timeoutMs = 1000) {
  const ps = await runCommandForCleanup('ps', ['-eo', 'pid=,ppid=,pgid=,args='], timeoutMs);
  if (ps.error || ps.timedOut) return { rows: [], ps };
  const rows = String(ps.stdout || '').split('\n').map((line) => line.trim()).filter(Boolean).map((line) => {
    const match = line.match(/^(\d+)\s+(\d+)\s+(\d+)\s+(.+)$/);
    if (!match) return null;
    return { pid: Number(match[1]), ppid: Number(match[2]), pgid: Number(match[3]), args: match[4] };
  }).filter(Boolean).filter((row) => row.args.includes(pattern));
  return { rows, ps };
}

function signalRows(rows, signal) {
  const requestedGroups = [];
  const requestedPids = [];
  const seenGroups = new Set();
  for (const row of rows || []) {
    if (Number.isFinite(row.pgid) && row.pgid > 1 && !seenGroups.has(row.pgid)) {
      seenGroups.add(row.pgid);
      try { process.kill(-row.pgid, signal); requestedGroups.push(row.pgid); } catch {}
    }
  }
  for (const row of rows || []) {
    if (Number.isFinite(row.pid) && row.pid > 1) {
      try { process.kill(row.pid, signal); requestedPids.push(row.pid); } catch {}
    }
  }
  return { signal, requestedGroups, requestedPids };
}

export async function reapBrowserProfileProcesses(profileDir, { graceMs = 250, killMs = 750 } = {}) {
  if (!profileDir || !String(profileDir).startsWith('/tmp/browserrt')) return { profileDir, skipped: true, reason: 'non-browserrt-temp-profile' };
  const pattern = String(profileDir).replace(/[\n\r]/g, '');
  const before = await listBrowserProfileProcesses(pattern);
  const termSignal = signalRows(before.rows, 'SIGTERM');
  const term = await runCommandForCleanup('pkill', ['-TERM', '-f', pattern], Math.max(100, graceMs));
  await sleep(Math.max(50, graceMs));
  const afterTerm = await listBrowserProfileProcesses(pattern);
  const killSignal = signalRows(afterTerm.rows, 'SIGKILL');
  const kill = await runCommandForCleanup('pkill', ['-KILL', '-f', pattern], Math.max(100, killMs));
  await sleep(Math.max(50, killMs));
  const afterKill = await listBrowserProfileProcesses(pattern);
  return { profileDir, skipped: false, beforeCount: before.rows.length, afterTermCount: afterTerm.rows.length, afterKillCount: afterKill.rows.length, beforeRows: before.rows, afterTermRows: afterTerm.rows, afterKillRows: afterKill.rows, termSignal, killSignal, term, kill };
}

async function waitForChildClose(child, timeoutMs = 1000) {
  if (!child?.pid) return { pid: null, code: null, signal: null, alreadyExited: true, timedOut: false };
  if (child.exitCode !== null || child.signalCode !== null) {
    return { pid: child.pid, code: child.exitCode, signal: child.signalCode, alreadyExited: true, timedOut: false };
  }
  let settled = false;
  const closed = new Promise((resolveClose) => {
    child.once('close', (code, signal) => {
      settled = true;
      resolveClose({ pid: child.pid, code, signal, alreadyExited: false, timedOut: false });
    });
  });
  const timeout = sleep(timeoutMs).then(() => ({ pid: child.pid, code: child.exitCode, signal: child.signalCode, alreadyExited: false, timedOut: !settled }));
  return await Promise.race([closed, timeout]);
}

export async function terminateProcessGroup(child, { graceMs = 1000 } = {}) {
  if (!child?.pid) return { mode: 'terminate', requestedSignals: [], pid: null, code: null, signal: null, timedOut: false };
  const requestedSignals = [];
  try { process.kill(-child.pid, 'SIGTERM'); requestedSignals.push('SIGTERM:pgid'); } catch { try { child.kill('SIGTERM'); requestedSignals.push('SIGTERM:child'); } catch {} }
  let close = await waitForChildClose(child, graceMs);
  if (close.timedOut) {
    try { process.kill(-child.pid, 'SIGKILL'); requestedSignals.push('SIGKILL:pgid'); } catch { try { child.kill('SIGKILL'); requestedSignals.push('SIGKILL:child'); } catch {} }
    close = await waitForChildClose(child, 1000);
  }
  return { mode: 'terminate', requestedSignals, ...close };
}

export async function killProcessGroup(child, { waitMs = 2000 } = {}) {
  if (!child?.pid) return { mode: 'kill', requestedSignals: [], pid: null, code: null, signal: null, timedOut: false };
  const requestedSignals = [];
  try { process.kill(-child.pid, 'SIGKILL'); requestedSignals.push('SIGKILL:pgid'); } catch { try { child.kill('SIGKILL'); requestedSignals.push('SIGKILL:child'); } catch {} }
  const close = await waitForChildClose(child, waitMs);
  return { mode: 'kill', requestedSignals, ...close };
}

export function chromeStderrSummary(stderr, terms = []) {
  const lines = stderr.split('\n').filter(Boolean);
  const regex = new RegExp(['ERROR', 'Error', 'policy', ...terms].join('|'), 'i');
  return {
    lineCount: lines.length,
    devtoolsListening: /DevTools listening/.test(stderr),
    policyMentions: (stderr.match(/policy/gi) || []).length,
    errorLineSample: lines.filter((line) => regex.test(line)).slice(0, 12)
  };
}

export async function runManagedBrowserPage(options = {}, callback) {
  if (typeof callback !== 'function') throw new Error('runManagedBrowserPage requires a callback');
  const started = performance.now();
  const timings = [];
  const mark = (name, t0) => timings.push({ name, durationMs: Math.round(performance.now() - t0) });
  const timeoutMs = options.timeoutMs ?? 14000;
  const chromium = await findChromium(options.chromium);
  if (!chromium) throw new Error('No Chromium executable found.');
  const policyStart = performance.now();
  const policy = await relaxPolicy(options.relaxPolicy !== false, options.policyPath ?? POLICY_PATH);
  mark('policy-relaxation', policyStart);
  let server = null;
  let chrome = null;
  let cdp = null;
  let profile = null;
  let stderr = '';
  let stdout = '';
  let callbackResult;
  let browserTeardown = null;
  let profileReap = null;
  let cdpPort = null;
  let listUrl = null;
  let versionUrl = null;
  let browserVersion = null;
  const externalServer = Boolean(options.server);
  const callerProvidedProfile = Boolean(options.profileDir);
  const teardownMode = options.teardownMode === 'kill' ? 'kill' : 'terminate';
  try {
    const s0 = performance.now();
    if (externalServer) {
      server = options.server;
      mark('server-reuse', s0);
    } else {
      server = await startProbeServer({ root: options.root ?? process.cwd(), pagePath: options.pagePath ?? '/probe.html', pageTitle: options.pageTitle ?? 'BrowserRT probe', body: options.body, allowedPrefixes: options.allowedPrefixes ?? ['src/'], routes: options.routes ?? {} });
      mark('server-start', s0);
    }
    cdpPort = await freePort();
    const pagePath = server.pagePath ?? options.pagePath ?? '/probe.html';
    const pageUrl = options.pageUrl ?? `http://${HOST}:${server.port}${pagePath}`;
    profile = options.profileDir ?? await mkdtemp(join(tmpdir(), options.profilePrefix ?? 'browserrt-cdp-'));
    const args = [
      '--headless=new',
      '--no-sandbox',
      '--disable-gpu',
      '--disable-dev-shm-usage',
      '--disable-extensions',
      '--disable-crash-reporter',
      '--no-first-run',
      '--no-default-browser-check',
      `--remote-debugging-port=${cdpPort}`,
      `--user-data-dir=${profile}`,
      ...(options.chromeArgs || []),
      pageUrl
    ];
    const launch = performance.now();
    chrome = spawn(chromium, args, { stdio: ['ignore', 'pipe', 'pipe'], detached: true });
    chrome.stdout.on('data', (bytes) => { stdout += bytes.toString(); });
    chrome.stderr.on('data', (bytes) => { stderr += bytes.toString(); });
    listUrl = `http://${HOST}:${cdpPort}/json/list`;
    versionUrl = `http://${HOST}:${cdpPort}/json/version`;
    const { targets, target } = await waitCdpTarget(listUrl, pageUrl, timeoutMs);
    browserVersion = await waitJson(versionUrl, timeoutMs);
    mark('chromium-launch-to-cdp-list', launch);
    const c0 = performance.now();
    cdp = new CdpClient(target.webSocketDebuggerUrl);
    await cdp.open(timeoutMs);
    await cdp.send('Runtime.enable');
    await cdp.send('Page.enable');
    mark('cdp-connect', c0);
    const pageStateStart = performance.now();
    let pageState = await evalJson(cdp, 'JSON.stringify({ location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext })', timeoutMs);
    mark('page-state-eval', pageStateStart);
    if (pageState.location !== pageUrl || pageState.location.startsWith('chrome-error:')) {
      const navStart = performance.now();
      await cdp.send('Page.navigate', { url: pageUrl }, timeoutMs);
      const deadline = performance.now() + timeoutMs;
      let lastState = pageState;
      while (performance.now() < deadline) {
        await sleep(100);
        lastState = await evalJson(cdp, 'JSON.stringify({ location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext })', Math.min(1000, timeoutMs));
        if (lastState.location === pageUrl && lastState.readyState !== 'loading') {
          pageState = lastState;
          break;
        }
      }
      mark('page-renavigate-if-needed', navStart);
      if (pageState.location !== pageUrl || pageState.location.startsWith('chrome-error:')) {
        throw new Error(`Chromium failed to reach probe page: ${pageState.location}; last=${JSON.stringify(lastState)}`);
      }
    }
    callbackResult = await callback({ cdp, evalJson: (expression, ms = timeoutMs) => evalJson(cdp, expression, ms), pageState, pageUrl, target, targets, server, mark, timeoutMs, timings, profileDir: profile, browserProcess: chrome, teardownMode, cdpPort, listUrl, versionUrl, browserVersion });
  } finally {
    const teardownStart = performance.now();
    if (chrome && teardownMode === 'kill') {
      browserTeardown = await killProcessGroup(chrome, { waitMs: options.killWaitMs ?? 2000 });
      if (cdp) cdp.close();
    } else {
      if (cdp) cdp.close();
      if (chrome) browserTeardown = await terminateProcessGroup(chrome, { graceMs: options.terminateGraceMs ?? 1000 });
    }
    if (profile && !options.keepProfile) profileReap = await reapBrowserProfileProcesses(profile, { graceMs: options.profileReapGraceMs ?? 250, killMs: options.profileReapKillMs ?? 750 });
    if (server && !externalServer) await server.close();
    if (profile && !options.keepProfile && !callerProvidedProfile) await rm(profile, { recursive: true, force: true });
    await policy.restore();
    mark(teardownMode === 'kill' ? 'teardown-kill' : 'teardown', teardownStart);
  }
  return {
    result: callbackResult,
    harness: {
      chromiumExecutable: chromium,
      policyRelaxation: policy.result,
      server: server ? { port: server.port, external: externalServer, requestCount: server.requests?.length ?? null, requests: (server.requests || []).slice(0, 30) } : null,
      profile: profile ? { path: profile, kept: Boolean(options.keepProfile), callerProvided: callerProvidedProfile } : null,
      cdp: cdp ? { eventCount: cdp.events.length, console: cdp.console.slice(0, 20), port: typeof cdpPort === 'number' ? cdpPort : null, browserVersion: typeof browserVersion === 'object' ? { Browser: browserVersion.Browser, ProtocolVersion: browserVersion['Protocol-Version'] } : null } : null,
      process: browserTeardown,
      profileReap,
      teardownMode,
      timings,
      durationMs: Math.round(performance.now() - started),
      chromeStderrSummary: chromeStderrSummary(stderr, options.stderrTerms || []),
      chromeStdoutBytes: stdout.length
    }
  };
}
