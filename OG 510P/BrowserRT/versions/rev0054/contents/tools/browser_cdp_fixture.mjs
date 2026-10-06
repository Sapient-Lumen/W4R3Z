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

export async function startProbeServer({ root = process.cwd(), pagePath = '/probe.html', pageTitle = 'BrowserRT probe', body = null, allowedPrefixes = ['src/'] } = {}) {
  const normalizedPagePath = pagePath.startsWith('/') ? pagePath : `/${pagePath}`;
  const requests = [];
  const rootResolved = resolve(root);
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
      if (url.pathname === '/' || url.pathname === normalizedPagePath) {
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

export async function terminateProcessGroup(child) {
  if (!child?.pid) return;
  try { process.kill(-child.pid, 'SIGTERM'); } catch { try { child.kill('SIGTERM'); } catch {} }
  await Promise.race([new Promise((resolveClose) => child.once('close', resolveClose)), sleep(1000)]);
  try { process.kill(-child.pid, 'SIGKILL'); } catch {}
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
  try {
    const s0 = performance.now();
    server = await startProbeServer({ root: options.root ?? process.cwd(), pagePath: options.pagePath ?? '/probe.html', pageTitle: options.pageTitle ?? 'BrowserRT probe', body: options.body, allowedPrefixes: options.allowedPrefixes ?? ['src/'] });
    mark('server-start', s0);
    const cdpPort = await freePort();
    const pageUrl = `http://${HOST}:${server.port}${server.pagePath}`;
    profile = await mkdtemp(join(tmpdir(), options.profilePrefix ?? 'browserrt-cdp-'));
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
    const { targets, target } = await waitCdpTarget(`http://${HOST}:${cdpPort}/json/list`, pageUrl, timeoutMs);
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
    callbackResult = await callback({ cdp, evalJson: (expression, ms = timeoutMs) => evalJson(cdp, expression, ms), pageState, pageUrl, target, server, mark, timeoutMs, timings });
  } finally {
    const teardownStart = performance.now();
    if (cdp) cdp.close();
    if (chrome) await terminateProcessGroup(chrome);
    if (server) await server.close();
    if (profile) await rm(profile, { recursive: true, force: true });
    await policy.restore();
    mark('teardown', teardownStart);
  }
  return {
    result: callbackResult,
    harness: {
      chromiumExecutable: chromium,
      policyRelaxation: policy.result,
      server: server ? { port: server.port, requestCount: server.requests.length, requests: server.requests.slice(0, 30) } : null,
      cdp: cdp ? { eventCount: cdp.events.length, console: cdp.console.slice(0, 20) } : null,
      timings,
      durationMs: Math.round(performance.now() - started),
      chromeStderrSummary: chromeStderrSummary(stderr, options.stderrTerms || []),
      chromeStdoutBytes: stdout.length
    }
  };
}
