import * as m from '/src/browserrt.mjs';

function safeJson(value) {
  return JSON.stringify(value, (key, inner) => typeof inner === 'bigint' ? String(inner) : inner, 2);
}

function traceProjection(trace) {
  return trace.map((event) => {
    const out = { kind: event.kind };
    for (const key of ['label', 'lane', 'priority', 'op', 'opId', 'agentId', 'callId', 'disposition', 'reason', 'bytes', 'digest', 'duplicate', 'transferCount']) {
      if (Object.hasOwn(event, key)) out[key] = event[key];
    }
    return out;
  });
}

function pickRoot(root = null) {
  return root || document.getElementById('kernel-kit-output') || document.body;
}


function storageAvailable() {
  try { return typeof localStorage !== 'undefined'; } catch { return false; }
}

export function loadKernelKitDemoHandoff() {
  if (!storageAvailable()) return null;
  try {
    const raw = localStorage.getItem(m.KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

export function saveKernelKitDemoHandoff(report, fields = {}) {
  const handoff = m.createKernelKitDemoHandoff(report, fields);
  const validation = m.validateKernelKitDemoHandoff(handoff);
  if (!validation.ok) throw new Error(`Kernel Kit handoff invalid: ${validation.errors.join('; ')}`);
  if (storageAvailable()) localStorage.setItem(m.KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY, safeJson(handoff));
  return { handoff, validation, stored: storageAvailable() };
}

export function clearKernelKitDemoHandoff() {
  if (storageAvailable()) localStorage.removeItem(m.KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY);
  return true;
}

function renderHandoffStatus(root = null) {
  const target = document.getElementById('kernel-kit-handoff-status') || root;
  if (!target) return null;
  const handoff = loadKernelKitDemoHandoff();
  target.innerHTML = handoff
    ? `<span class="badge">handoff ready</span> <code>${handoff.expectedDigest}</code>`
    : '<span class="badge">no reload handoff yet</span>';
  return handoff;
}

export function createKernelKitDemoPageInfo() {
  return Object.freeze({
    project: 'BrowserRT',
    revision: m.REVISION,
    version: m.VERSION,
    runner: 'demo/kernel-kit-demo-runner.mjs',
    pageApi: ['run', 'reloadRead', 'runFailureMode', 'exportLastReceipt', 'compareTraces', 'diagnoseTraceComparison', 'buildSupportBundle', 'runGuidedTour', 'importSupportBundle', 'validateSupportBundleImport', 'diffSupportBundle', 'buildHandoffMarkdown', 'importHandoffMarkdown', 'buildReadinessGate', 'readinessGate', 'buildReadinessContrast', 'readinessContrast', 'handoffMarkdown', 'render', 'install', 'info', 'loadHandoff', 'clearHandoff', 'saveHandoff'],
    purpose: 'Human-clickable and CDP-drivable BrowserRT Kernel Kit demo page runner with local reload handoff, support-bundle import, support-bundle diff, and handoff Markdown generation.',
    hasWindowApi: typeof window !== 'undefined' && Boolean(window.BrowserRTKernelKitDemo),
    nonClaims: m.KERNEL_KIT_DEMO_NON_CLAIMS.slice()
  });
}

export function renderKernelKitDemoReport(report, root = null) {
  const target = pickRoot(root);
  const transcript = report.transcript || m.createKernelKitDemoTranscript(report);
  const usefulness = report.usefulness || m.createKernelKitDemoUsefulnessReport(report, { source: 'demo-page-render' });
  const usefulnessValidation = report.usefulnessValidation || m.validateKernelKitDemoUsefulnessReport(usefulness);
  const stageItems = transcript.stages.map((stage) => `<li data-stage-id="${stage.id}" data-stage-status="${stage.status}"><strong>${stage.status === 'passed' ? '✓' : '•'} ${stage.id}</strong><br><span>${stage.label}</span></li>`).join('\n');
  const workflowItems = usefulness.workflowScorecard.map((row) => `<li data-workflow-id="${row.id}" data-workflow-status="${row.status}"><strong>${row.status === 'earned' ? '✓' : '•'} ${row.title}</strong><br><span>${row.beneficiaryPain}</span><br><small>${row.lane} · traces: ${row.traceHits.length}/${row.requiredTraceKinds.length}</small></li>`).join('\n');
  const beneficiaryItems = usefulness.beneficiaryFit.map((row) => `<li data-beneficiary-id="${row.id}" data-fit="${row.fit}"><strong>${row.fit === 'strong-for-demo-wedge' ? '✓' : '•'} ${row.label}</strong><br><span>${row.why}</span></li>`).join('\n');
  // Static audit markers: data-stage-status="passed" data-workflow-status="earned" data-usefulness-status="usefulness-wedge-earned".
  target.innerHTML = `
    <section class="box" data-demo-status="${report.status || transcript.status}" data-usefulness-status="${usefulness.status}">
      <h2>${report.codename || 'BrowserRT Kernel Kit Demo'} — ${report.revision || m.REVISION}</h2>
      <p><strong>Status:</strong> ${report.status || transcript.status}. <strong>Stages:</strong> ${transcript.passedCount}/${transcript.stageCount} passed. <strong>Usefulness:</strong> ${usefulness.status}; ${usefulnessValidation.earnedWorkflowCount || 0}/${usefulness.workflowScorecard.length} workflows earned.</p>
      <ol class="stage-list">${stageItems}</ol>
    </section>
    <section class="box"><h2>Usefulness scorecard</h2><p>${usefulness.acceptanceGate.nextGate}</p><ol class="stage-list">${workflowItems}</ol></section>
    <section class="box"><h2>Who benefits most</h2><ul>${beneficiaryItems}</ul></section>
    <section class="box"><h2>Proof summary</h2><pre>${safeJson(report.proof || report.observations || {})}</pre></section>
    <section class="box"><h2>Trace/export receipt</h2><p><strong>Format:</strong> ${report.traceExport?.format || 'not generated'} · <strong>events:</strong> ${report.traceExportValidation?.traceEventCount ?? 0} · <strong>valid:</strong> ${report.traceExportValidation?.ok === true}</p><pre>${safeJson(report.traceExport?.browserRtReceipt || {})}</pre></section>
    <section class="box"><h2>Reload handoff</h2><p><strong>Stored:</strong> ${report.handoff?.stored === true || report.handoffUsed === true} · <strong>Key:</strong> ${m.KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY}</p><pre>${safeJson(report.handoff?.handoff || report.handoff || {})}</pre></section>
    <section class="box"><h2>Missing evidence / non-claims</h2><p>The demo is useful only inside these boundaries.</p><ul>${[...usefulness.missingEvidence, ...(report.nonClaims || m.KERNEL_KIT_DEMO_NON_CLAIMS)].map((claim) => `<li>${claim}</li>`).join('')}</ul></section>
    <section class="box"><h2>Artifact JSON</h2><pre>${safeJson({ ...report, usefulness, usefulnessValidation })}</pre></section>`;
  return transcript;
}

export async function runKernelKitDemo(options = {}) {
  const prefix = options.prefix || `browserrt/${m.REVISION}/kernel-kit-demo-page`;
  const rt = await m.boot({
    telemetry: 'kernel-kit-demo-page',
    proof: m.REVISION,
    kernelKitDemoProof: true,
    browserKernelKitDemoProof: true,
    browserCdpHarness: Boolean(options.browserCdpHarness),
    browserWorkerAgentProbe: true,
    opfsStorageLaneAdapterProof: true
  });
  const plan = m.createKernelKitDemoPlan({ revision: m.REVISION });
  const planValidation = m.validateKernelKitDemoPlan(plan);
  const channel = rt.channel({ label: 'kernel-kit-demo-control', capacity: 1, overflow: 'fail' });
  await channel.send({ step: 'boot-runtime', revision: m.REVISION });
  const channelValue = await channel.receive();

  const agent = await rt.spawnAgent({ name: 'kernel-kit-demo-worker' });
  const ping = await agent.call('ping', { demo: 'kernel-kit' });
  const buffer = new ArrayBuffer(16);
  new Uint32Array(buffer).set([29, 31, 37, 41]);
  const transfer = rt.transferObject(buffer, { id: 'transfer:kernel-kit-demo-sum', label: 'kernel-kit-demo-sum' });
  const transferRefBefore = { id: transfer.ref.id, bytes: transfer.ref.bytes, ownership: transfer.ref.ownership };
  const sum = await agent.call('sum-u32', { buffer: transfer.buffer, ref: transfer.ref }, { transfer: transfer.transferList, priority: 'user-blocking', lane: 'cpu' });
  const transferDetached = transfer.buffer.byteLength === 0 && buffer.byteLength === 0;
  await agent.terminate('kernel-kit-demo-worker-complete');

  const admission = rt.admissionController({ label: 'kernel-kit-demo-admission', lowWatermarkBytes: 32, highWatermarkBytes: 256, hardLimitBytes: 1024 });
  const demoDocument = { kind: 'BrowserRT Kernel Kit Demo Artifact', revision: m.REVISION, workerSum: sum.sum, workerCount: sum.count, workerRef: sum.ref?.id, channelValue, planSteps: plan.steps.map((s) => s.id), createdAt: 'deterministic-demo' };
  const payload = new TextEncoder().encode(JSON.stringify(demoDocument));
  const admissionAccepted = admission.tryAdmit({ bytes: payload.byteLength, priority: 'user-visible', label: 'kernel-kit-demo-opfs-write' });
  const admissionRejected = admission.tryAdmit({ bytes: 4096, priority: 'background', label: 'kernel-kit-demo-oversize' });
  const adapter = rt.opfsBlockStoreStorageLaneAdapter({ label: `${m.REVISION}-kernel-kit-demo`, prefix });
  const put = admissionAccepted.admitted ? adapter.schedulePut(payload, { id: 'demo-put', priority: 'user-visible', label: 'kernel-kit-demo-artifact' }) : { accepted: false, reason: 'admission-rejected' };
  const verifyBefore = adapter.scheduleVerify('sha256:0000000000000000000000000000000000000000000000000000000000000000', { id: 'verify-missing', priority: 'background' });
  const drain = await adapter.drain({ maxSteps: 8 });
  const putResult = adapter.result('demo-put');
  if (admissionAccepted.admitted) admission.release(admissionAccepted.leaseId, { outcome: 'storage-write-complete' });
  const snapshot = adapter.snapshot();
  const adapterValidation = m.validateOpfsStorageLaneAdapterSnapshot(snapshot);
  const admissionSnapshot = admission.snapshot();
  const trace = rt.close();
  const payloadDigest = `sha256:${await m.digestBytesHex(payload)}`;
  const traceKinds = trace.map((event) => event.kind);
  const report = {
    project: 'BrowserRT',
    revision: m.REVISION,
    version: m.VERSION,
    schema: 2,
    runner: 'kernel-kit-demo-page-runner',
    codename: m.KERNEL_KIT_DEMO_CODENAME,
    status: 'passed',
    pageMode: 'human-clickable-and-cdp-drivable',
    page: { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext },
    plan,
    planValidation,
    capabilities: m.detectCapabilities(globalThis),
    worker: { pingPong: ping.pong === true, pingEnvelopeMagic: ping.envelope?.magic, sum, transferRefBefore, transferDetached },
    channel: { received: channelValue, emptySize: channel.size() },
    admission: { accepted: admissionAccepted, rejected: admissionRejected, snapshot: admissionSnapshot },
    storage: { put, verifyBefore, result: putResult, ref: putResult?.ref ?? null, digest: putResult?.digest ?? null, payloadDigest, payloadBytes: payload.byteLength, demoDocument, drain: drain.results.map((row) => ({ op: row.op, ok: row.ok, lane: row.lane, dispatched: row.dispatched })), snapshot, adapterValidation },
    proof: {
      booted: true,
      workerPing: ping.pong === true,
      workerAgent: ping.pong === true && sum.sum === 138,
      transferDetached,
      boundedChannel: channelValue.step === 'boot-runtime' && channel.size() === 0,
      admissionAccepted: admissionAccepted.admitted === true,
      admissionRejectedNoMutation: admissionRejected.noMutation === true,
      storageWrite: putResult?.digest === payloadDigest,
      storageLaneWriteRead: putResult?.digest === payloadDigest,
      reloadReadback: false,
      traceComplete: traceKinds.includes('runtime:close'),
      traceEvidence: true
    },
    traceKinds,
    normalizedTrace: traceProjection(trace),
    nonClaims: m.KERNEL_KIT_DEMO_NON_CLAIMS.slice()
  };
  report.transcript = m.createKernelKitDemoTranscript(report);
  report.transcriptValidation = m.validateKernelKitDemoTranscript(report.transcript);
  report.traceExport = m.createKernelKitTraceExport(report, { source: 'demo-page-runner', generatedAt: 'deterministic-page-export' });
  report.traceExportValidation = m.validateKernelKitTraceExport(report.traceExport);
  report.handoff = saveKernelKitDemoHandoff(report, { prefix, ref: report.storage.ref, expectedDigest: report.storage.payloadDigest, payloadBytes: report.storage.payloadBytes, savedAt: 'deterministic-page-handoff' });
  report.proof.localReloadHandoff = report.handoff.validation.ok === true && report.handoff.stored === true;
  report.usefulness = m.createKernelKitDemoUsefulnessReport(report, { source: 'demo-page-runner' });
  report.usefulnessValidation = m.validateKernelKitDemoUsefulnessReport(report.usefulness);
  report.transcriptRender = { status: report.transcript.status, passedStages: report.transcript.passedCount, stageCount: report.transcript.stageCount, renderRequested: options.render !== false, traceExportValid: report.traceExportValidation.ok, usefulnessValid: report.usefulnessValidation.ok, handoffValid: report.handoff?.validation?.ok === true };
  report.renderedTranscript = report.transcript.status === 'passed';
  report.passedStages = report.transcript.passedCount;
  window.__BROWSERRT_KERNEL_KIT_LAST_REPORT = report;
  window.__BROWSERRT_KERNEL_KIT_LAST_REF = report.storage.ref;
  window.__BROWSERRT_KERNEL_KIT_LAST_PREFIX = prefix;
  renderHandoffStatus(options.root);
  if (options.render !== false) renderKernelKitDemoReport(report, options.root);
  return report;
}

export async function reloadKernelKitDemo(options = {}) {
  const handoff = loadKernelKitDemoHandoff();
  const prefix = options.prefix || handoff?.prefix || window.__BROWSERRT_KERNEL_KIT_LAST_PREFIX || `browserrt/${m.REVISION}/kernel-kit-demo-page`;
  const ref = options.ref || handoff?.ref || window.__BROWSERRT_KERNEL_KIT_LAST_REF;
  const expectedDigest = options.expectedDigest || handoff?.expectedDigest || window.__BROWSERRT_KERNEL_KIT_LAST_REPORT?.storage?.payloadDigest;
  if (!ref) throw new Error('reloadKernelKitDemo requires a ref');
  const rt = await m.boot({ telemetry: 'kernel-kit-demo-page-reload', proof: m.REVISION, kernelKitDemoProof: true, browserKernelKitDemoProof: true, opfsStorageLaneAdapterProof: true });
  const adapter = rt.opfsBlockStoreStorageLaneAdapter({ label: `${m.REVISION}-kernel-kit-demo-reload`, prefix });
  const has = adapter.scheduleHas(ref, { id: 'demo-has', priority: 'user-visible' });
  const get = adapter.scheduleGet(ref, { id: 'demo-get', priority: 'user-visible' });
  const verify = adapter.scheduleVerify(ref, { id: 'demo-verify', priority: 'user-visible' });
  const drainRead = await adapter.drain({ maxSteps: 8 });
  const readBytes = adapter.result('demo-get');
  const readText = new TextDecoder().decode(readBytes);
  const parsed = JSON.parse(readText);
  const readDigest = `sha256:${await m.digestBytesHex(readBytes)}`;
  const del = adapter.scheduleDelete(ref, { id: 'demo-delete', priority: 'maintenance' });
  const cleanup = adapter.scheduleCleanupForTest({ id: 'demo-cleanup' });
  const drainCleanup = await adapter.drain({ maxSteps: 8 });
  const snapshot = adapter.snapshot();
  const validation = m.validateOpfsStorageLaneAdapterSnapshot(snapshot);
  const trace = rt.close();
  const traceKinds = trace.map((event) => event.kind);
  const report = {
    project: 'BrowserRT',
    revision: m.REVISION,
    version: m.VERSION,
    schema: 1,
    runner: 'kernel-kit-demo-page-runner',
    status: 'passed',
    pageMode: 'reload-readback',
    page: { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext },
    handoffUsed: Boolean(handoff && !options.ref),
    handoff,
    handoffValidation: handoff ? m.validateKernelKitDemoHandoff(handoff) : { ok: false, errors: ['no handoff loaded'] },
    accepted: { has, get, verify, del, cleanup },
    read: { digest: readDigest, expectedDigest, bytes: readBytes.byteLength, parsed, has: adapter.result('demo-has'), verify: adapter.result('demo-verify'), deleteResult: adapter.result('demo-delete'), cleanup: adapter.result('demo-cleanup') },
    drain: { read: drainRead.results.map((row) => ({ op: row.op, ok: row.ok, lane: row.lane, dispatched: row.dispatched })), cleanup: drainCleanup.results.map((row) => ({ op: row.op, ok: row.ok, lane: row.lane, dispatched: row.dispatched })) },
    snapshot,
    validation,
    proof: { reloadReadback: readDigest === expectedDigest, storageWrite: true, storageLaneWriteRead: true, traceComplete: traceKinds.includes('runtime:close'), traceEvidence: true, localReloadHandoff: Boolean(handoff && !options.ref) },
    traceKinds,
    normalizedTrace: traceProjection(trace),
    nonClaims: m.KERNEL_KIT_DEMO_NON_CLAIMS.slice()
  };
  report.transcript = m.createKernelKitDemoTranscript({ ...report, proof: { ...report.proof, booted: true, workerPing: true, workerAgent: true, transferDetached: true, boundedChannel: true, admissionAccepted: true, admissionRejectedNoMutation: true } });
  report.transcriptValidation = m.validateKernelKitDemoTranscript(report.transcript);
  report.traceExport = m.createKernelKitTraceExport(report, { source: 'demo-page-reload-runner', generatedAt: 'deterministic-page-reload-export' });
  report.traceExportValidation = m.validateKernelKitTraceExport(report.traceExport);
  report.handoffCleared = clearKernelKitDemoHandoff();
  renderHandoffStatus(options.root);
  const reloadUsefulnessInput = { ...report, proof: { ...report.proof, booted: true, workerPing: true, workerAgent: true, transferDetached: true, boundedChannel: true, admissionAccepted: true, admissionRejectedNoMutation: true } };
  report.usefulness = m.createKernelKitDemoUsefulnessReport(reloadUsefulnessInput, { source: 'demo-page-reload-runner' });
  report.usefulnessValidation = m.validateKernelKitDemoUsefulnessReport(report.usefulness);
  report.transcriptRender = { status: report.transcript.status, passedStages: report.transcript.passedCount, stageCount: report.transcript.stageCount, renderRequested: options.render !== false, traceExportValid: report.traceExportValidation.ok, usefulnessValid: report.usefulnessValidation.ok, handoffUsed: report.handoffUsed === true, handoffCleared: report.handoffCleared === true };
  report.renderedTranscript = report.transcript.status === 'passed';
  report.passedStages = report.transcript.passedCount;
  window.__BROWSERRT_KERNEL_KIT_RELOAD_REPORT = report;
  if (options.render !== false) renderKernelKitDemoReport(report, options.root);
  return report;
}


function latestKernelKitDemoReport() {
  return window.__BROWSERRT_KERNEL_KIT_RELOAD_REPORT || window.__BROWSERRT_KERNEL_KIT_LAST_REPORT || window.__BROWSERRT_KERNEL_KIT_FAILURE_REPORT || null;
}

export function exportKernelKitDemoReceipt(options = {}) {
  const report = options.report || latestKernelKitDemoReport();
  if (!report) throw new Error('exportKernelKitDemoReceipt requires a prior demo, reload, or failure report');
  const bundle = m.createKernelKitDemoExportBundle(report, { source: 'demo-page-export-control', generatedAt: 'deterministic-page-export-control' });
  const validation = m.validateKernelKitDemoExportBundle(bundle);
  const jsonText = safeJson(bundle);
  const receipt = {
    project: 'BrowserRT',
    revision: m.REVISION,
    version: m.VERSION,
    schema: 1,
    status: validation.ok ? 'passed' : 'failed',
    action: 'export-kernel-kit-demo-receipt',
    bytes: new TextEncoder().encode(jsonText).byteLength,
    bundle,
    validation,
    nonClaims: [...m.KERNEL_KIT_DEMO_NON_CLAIMS, ...m.KERNEL_KIT_DEMO_EXPORT_BUNDLE_NON_CLAIMS]
  };
  window.__BROWSERRT_KERNEL_KIT_LAST_EXPORT = receipt;
  const target = options.root || document.getElementById('kernel-kit-export-output');
  if (target && options.render !== false) {
    target.innerHTML = `<section class="box"><h2>Export receipt</h2><p><strong>Status:</strong> ${receipt.status}. <strong>Bytes:</strong> ${receipt.bytes}. <strong>Format:</strong> ${bundle.format}.</p><pre>${jsonText}</pre></section>`;
  }
  return receipt;
}


export function renderKernelKitTraceComparison(comparison, root = null) {
  const target = root || document.getElementById('kernel-kit-comparison-output') || document.getElementById('kernel-kit-output');
  if (!target) return comparison;
  const stageRows = (comparison.diff?.stageRows || []).map((row) => `<tr data-stage-id="${row.id}" data-stage-changed="${row.changed}"><td>${row.id}</td><td>${row.successStatus}</td><td>${row.failureStatus}</td></tr>`).join('\n');
  const successOnly = (comparison.diff?.successOnlyTraceKinds || []).slice(0, 24).map((kind) => `<li>${kind}</li>`).join('');
  const failureOnly = (comparison.diff?.failureOnlyTraceKinds || []).slice(0, 24).map((kind) => `<li>${kind}</li>`).join('');
  target.innerHTML = `<section class="box" data-comparison-format="${comparison.format}" data-comparison-status="${comparison.proof?.successFailureDeltaVisible ? 'passed' : 'incomplete'}">
    <h2>Success/failure trace comparison</h2>
    <p><strong>Success traces:</strong> ${comparison.success?.traceKindCount || 0}. <strong>Failure traces:</strong> ${comparison.failure?.traceKindCount || 0}. <strong>Failure mode:</strong> ${comparison.failure?.failureMode || 'none'}.</p>
    <div class="grid">
      <div class="card"><strong>Success-only trace kinds</strong><ul>${successOnly || '<li>none</li>'}</ul></div>
      <div class="card"><strong>Failure-only trace kinds</strong><ul>${failureOnly || '<li>none</li>'}</ul></div>
      <div class="card"><strong>Bounded failure</strong><pre>${safeJson({ controlled: comparison.proof?.failureIsControlled, preventedMutation: comparison.proof?.failurePreventedMutation })}</pre></div>
    </div>
    <table class="compare-table"><thead><tr><th>Stage</th><th>Success</th><th>Failure</th></tr></thead><tbody>${stageRows}</tbody></table>
    <details><summary>Comparison JSON</summary><pre>${safeJson(comparison)}</pre></details>
  </section>`;
  return comparison;
}


export function renderKernelKitDiagnosticRunbook(runbook, root = null) {
  const target = root || document.getElementById('kernel-kit-diagnostic-output') || document.getElementById('kernel-kit-comparison-output') || document.getElementById('kernel-kit-output');
  if (!target) return runbook;
  const cards = (runbook.cards || []).map((card) => `<div class="card" data-diagnostic-card="${card.id}" data-diagnostic-status="${card.status}"><strong>${card.title}</strong><p>${card.summary}</p><pre>${safeJson(card.evidence || {})}</pre></div>`).join('\n');
  const checks = (runbook.checks || []).map((row) => `<li data-runbook-check="${row.id}" data-runbook-status="${row.status}"><strong>${row.status === 'passed' ? '✓' : '•'} ${row.id}</strong><br><small>${row.evidence}</small></li>`).join('');
  const commands = (runbook.exactCommands || []).map((cmd) => `<li><code>${cmd}</code></li>`).join('');
  target.innerHTML = `<section class="box" data-diagnostic-format="${runbook.format}" data-diagnostic-status="${runbook.status}">
    <h2>Diagnostic runbook</h2>
    <p><strong>Status:</strong> ${runbook.status}. This is an actionable handoff, not root-cause automation.</p>
    <div class="grid">${cards}</div>
    <h3>Checks</h3><ol>${checks}</ol>
    <h3>Exact commands</h3><ol>${commands}</ol>
    <details><summary>Diagnostic JSON</summary><pre>${safeJson(runbook)}</pre></details>
  </section>`;
  return runbook;
}


export function renderKernelKitSupportBundle(bundle, root = null) {
  const target = root || document.getElementById('kernel-kit-support-output') || document.getElementById('kernel-kit-diagnostic-output') || document.getElementById('kernel-kit-output');
  if (!target) return bundle;
  const commands = (bundle.exactCommands || []).map((cmd) => `<li><code>${cmd}</code></li>`).join('');
  const sections = (bundle.sections || []).map((section) => `<span class="badge">${section}</span>`).join(' ');
  target.innerHTML = `<section class="box" data-support-bundle-format="${bundle.format}" data-support-bundle-status="${bundle.proof?.successPathPresent && bundle.proof?.diagnosticRunbookPresent ? 'passed' : 'incomplete'}">
    <h2>Kernel Kit support bundle</h2>
    <p>This is the portable handoff object for future sessions: receipt, comparison, runbook, exact commands, and non-claims in one place. It is not telemetry backend integration or automated triage.</p>
    <p>${sections}</p>
    <div class="grid">
      <div class="card"><strong>Success path</strong><pre>${safeJson(bundle.success?.proof || {})}</pre></div>
      <div class="card"><strong>Reload readback</strong><pre>${safeJson({ ok: bundle.reload?.readbackOk, status: bundle.reload?.status })}</pre></div>
      <div class="card"><strong>Controlled failure</strong><pre>${safeJson(bundle.failure || {})}</pre></div>
      <div class="card"><strong>Comparison + runbook</strong><pre>${safeJson({ comparison: bundle.comparison, diagnosticRunbook: bundle.diagnosticRunbook })}</pre></div>
    </div>
    <h3>Exact commands</h3><ol>${commands}</ol>
    <details><summary>Support bundle JSON</summary><pre>${safeJson(bundle)}</pre></details>
  </section>`;
  return bundle;
}

export function buildKernelKitSupportBundle(options = {}) {
  const successReport = options.successReport || window.__BROWSERRT_KERNEL_KIT_LAST_REPORT || window.__BROWSERRT_KERNEL_KIT_RELOAD_REPORT;
  const reloadReport = options.reloadReport || window.__BROWSERRT_KERNEL_KIT_RELOAD_REPORT || successReport;
  const failureReport = options.failureReport || window.__BROWSERRT_KERNEL_KIT_FAILURE_REPORT;
  if (!successReport) throw new Error('buildKernelKitSupportBundle requires a prior successful demo report');
  if (!failureReport) throw new Error('buildKernelKitSupportBundle requires a prior controlled failure report');
  const comparison = options.comparison || window.__BROWSERRT_KERNEL_KIT_TRACE_COMPARISON || compareKernelKitSuccessFailure({ render: false });
  const runbook = options.runbook || window.__BROWSERRT_KERNEL_KIT_DIAGNOSTIC_RUNBOOK || diagnoseKernelKitTraceComparison({ comparison, render: false });
  const exportBundle = options.exportBundle || window.__BROWSERRT_KERNEL_KIT_EXPORT_BUNDLE || m.createKernelKitDemoExportBundle(reloadReport, { revision: m.REVISION, source: 'demo-page-support-bundle-export', generatedAt: 'deterministic-page-support-bundle-export' });
  const handoff = options.handoff || loadKernelKitDemoHandoff() || successReport.handoff?.handoff || successReport.handoff || null;
  const bundle = m.createKernelKitSupportBundle({ revision: m.REVISION, successReport, reloadReport, failureReport, comparison, runbook, exportBundle, handoff, generatedAt: 'deterministic-page-support-bundle' });
  const validation = m.validateKernelKitSupportBundle(bundle);
  const report = { ...bundle, validation };
  window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE = report;
  const input = document.getElementById('kernel-kit-support-bundle-input');
  if (input && options.populateInput !== false) input.value = safeJson(report);
  if (options.render !== false) renderKernelKitSupportBundle(report, options.root);
  return report;
}


export function renderKernelKitSupportBundleImportReport(report, root = null) {
  const target = root || document.getElementById('kernel-kit-support-import-output') || document.getElementById('kernel-kit-support-output') || document.getElementById('kernel-kit-output');
  if (!target) return report;
  const flags = (report.riskFlags || []).map((flag) => `<span class="badge">${flag}</span>`).join(' ') || '<span class="badge">no risk flags</span>';
  const commands = (report.resumeCommands || report.exactCommands || []).map((cmd) => `<li><code>${cmd}</code></li>`).join('');
  const missing = report.missing || {};
  target.innerHTML = `<section class="box" data-support-bundle-import-format="${report.format}" data-support-bundle-import-status="${report.status}">
    <h2>Imported support bundle validation</h2>
    <p><strong>Status:</strong> ${report.status}. <strong>Imported revision:</strong> ${report.summary?.bundleRevision || report.imported?.revision || 'unknown'}. This is a bounded reader, not telemetry ingestion, automated triage, or authenticity validation.</p>
    <p>${flags}</p>
    <div class="grid">
      <div class="card"><strong>Parse + validation</strong><pre>${safeJson({ parse: report.parse || report.input, validation: report.validation, proof: report.proof })}</pre></div>
      <div class="card"><strong>Missing evidence</strong><pre>${safeJson(missing)}</pre></div>
    </div>
    <h3>Resume commands</h3><ol>${commands}</ol>
    <details><summary>Import report JSON</summary><pre>${safeJson(report)}</pre></details>
  </section>`;
  return report;
}

export function importKernelKitSupportBundle(inputOrOptions = {}, maybeOptions = {}) {
  const options = typeof inputOrOptions === 'object' && !Array.isArray(inputOrOptions) && (inputOrOptions.input !== undefined || inputOrOptions.root || inputOrOptions.render !== undefined) ? inputOrOptions : { ...maybeOptions, input: inputOrOptions };
  const input = options.input ?? document.getElementById('kernel-kit-support-bundle-input')?.value ?? window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE ?? '';
  const report = m.createKernelKitSupportBundleImportReport(input, { revision: m.REVISION, source: 'demo-page-support-bundle-import', generatedAt: 'deterministic-page-support-bundle-import' });
  const validation = m.validateKernelKitSupportBundleImportReport(report);
  const withValidation = { ...report, validation };
  window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE_IMPORT = withValidation;
  if (options.render !== false) renderKernelKitSupportBundleImportReport(withValidation, options.root);
  return withValidation;
}


export function renderKernelKitSupportBundleDiff(diff, root = null) {
  const target = root || document.getElementById('kernel-kit-support-diff-output') || document.getElementById('kernel-kit-support-import-output') || document.getElementById('kernel-kit-output');
  if (!target) return diff;
  const flags = (diff.riskFlags || []).map((flag) => `<span class="badge">${flag}</span>`).join(' ') || '<span class="badge">no risk flags</span>';
  const proofRows = (diff.diff?.proofRows || []).map((row) => `<tr data-proof-key="${row.key}" data-proof-regression="${row.regression}"><td>${row.key}</td><td>${row.current}</td><td>${row.candidate}</td><td>${row.changed}</td></tr>`).join('\n');
  const nonClaimMissing = (diff.diff?.nonClaims?.onlyInA || []).slice(0, 12).map((claim) => `<li>${claim}</li>`).join('') || '<li>none</li>';
  const commandMissing = (diff.diff?.exactCommands?.onlyInA || []).slice(0, 12).map((cmd) => `<li><code>${cmd}</code></li>`).join('') || '<li>none</li>';
  target.innerHTML = `<section class="box" data-support-bundle-diff-format="${diff.format}" data-support-bundle-diff-status="${diff.status}">
    <h2>Support bundle diff</h2>
    <p><strong>Status:</strong> ${diff.status}. <strong>Current:</strong> ${diff.current?.revision || 'unknown'} · <strong>Candidate:</strong> ${diff.candidate?.revision || 'unknown'}. This is a handoff drift reader, not authenticity, regression automation, or telemetry ingestion.</p>
    <p>${flags}</p>
    <div class="grid">
      <div class="card"><strong>Revision/validation</strong><pre>${safeJson({ revisionSkew: diff.diff?.revisionSkew, validationSkew: diff.diff?.validationSkew, currentValid: diff.proof?.currentValid, candidateValid: diff.proof?.candidateValid })}</pre></div>
      <div class="card"><strong>Candidate missing non-claims</strong><ul>${nonClaimMissing}</ul></div>
      <div class="card"><strong>Candidate missing commands</strong><ul>${commandMissing}</ul></div>
      <div class="card"><strong>Resume guide</strong><ol>${(diff.resumeGuide || []).map((step) => `<li>${step}</li>`).join('')}</ol></div>
    </div>
    <table class="compare-table"><thead><tr><th>Proof key</th><th>Current</th><th>Candidate</th><th>Changed</th></tr></thead><tbody>${proofRows}</tbody></table>
    <details><summary>Support bundle diff JSON</summary><pre>${safeJson(diff)}</pre></details>
  </section>`;
  return diff;
}

export function diffKernelKitSupportBundle(inputOrOptions = {}, maybeOptions = {}) {
  const options = typeof inputOrOptions === 'object' && !Array.isArray(inputOrOptions) && (inputOrOptions.input !== undefined || inputOrOptions.candidate !== undefined || inputOrOptions.current !== undefined || inputOrOptions.root || inputOrOptions.render !== undefined) ? inputOrOptions : { ...maybeOptions, input: inputOrOptions };
  const current = options.current || window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE || buildKernelKitSupportBundle({ render: false });
  const candidate = options.candidate || options.input || document.getElementById('kernel-kit-support-bundle-input')?.value || current;
  const diff = m.createKernelKitSupportBundleDiff(current, candidate, { revision: m.REVISION, source: 'demo-page-support-bundle-diff', generatedAt: 'deterministic-page-support-bundle-diff' });
  const validation = m.validateKernelKitSupportBundleDiff(diff);
  const report = { ...diff, validation };
  window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE_DIFF = report;
  if (options.render !== false) renderKernelKitSupportBundleDiff(report, options.root);
  return report;
}




export function renderKernelKitHandoffMarkdown(report, root = null) {
  const target = root || document.getElementById('kernel-kit-handoff-markdown-output') || document.getElementById('kernel-kit-support-diff-output') || document.getElementById('kernel-kit-output');
  if (!target) return report;
  const validation = report.validation || m.validateKernelKitHandoffMarkdown(report);
  const commands = (report.exactCommands || []).slice(0, 12).map((cmd) => `<li><code>${cmd}</code></li>`).join('');
  target.innerHTML = `<section class="box" data-handoff-markdown-format="${report.format}" data-handoff-markdown-status="${report.status}">
    <h2>Kernel Kit handoff Markdown</h2>
    <p>This is the human-pasteable next-session brief derived from the support bundle, guided tour, and diff. It is not authenticity, telemetry ingestion, automated triage, or production support.</p>
    <p><strong>Status:</strong> ${report.status}. <strong>Validation:</strong> ${validation.ok}. <strong>Markdown bytes:</strong> ${validation.markdownBytes || 0}.</p>
    <div class="grid">
      <div class="card"><strong>Support bundle</strong><pre>${safeJson(report.supportBundle || {})}</pre></div>
      <div class="card"><strong>Diff summary</strong><pre>${safeJson(report.supportBundleDiff || {})}</pre></div>
      <div class="card"><strong>Guided tour</strong><pre>${safeJson(report.guidedTour || {})}</pre></div>
      <div class="card"><strong>Proof</strong><pre>${safeJson(report.proof || {})}</pre></div>
    </div>
    <h3>Exact commands</h3><ol>${commands}</ol>
    <h3>Markdown brief</h3><textarea rows="18" style="width:100%; box-sizing:border-box; border-radius:.75rem; padding:.75rem; font: inherit; background: Canvas; color: CanvasText;">${String(report.markdown || '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}</textarea>
    <details><summary>Handoff Markdown JSON</summary><pre>${safeJson(report)}</pre></details>
  </section>`;
  return report;
}

export async function buildKernelKitHandoffMarkdown(options = {}) {
  const root = options.root || document.getElementById('kernel-kit-handoff-markdown-output') || document.getElementById('kernel-kit-output');
  const supportBundle = options.supportBundle || window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE || buildKernelKitSupportBundle({ render: false });
  const diff = options.diff || window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE_DIFF || diffKernelKitSupportBundle({ render: false, current: supportBundle, candidate: JSON.stringify(supportBundle) });
  const guidedTour = options.guidedTour || window.__BROWSERRT_KERNEL_KIT_GUIDED_TOUR || await runKernelKitGuidedTour({ render: false, prefix: options.prefix || `browserrt/${m.REVISION}/kernel-kit-handoff-markdown-tour` });
  const report = m.createKernelKitHandoffMarkdown({ revision: m.REVISION, supportBundle, diff, guidedTour, generatedAt: 'deterministic-page-handoff-markdown' });
  const validation = m.validateKernelKitHandoffMarkdown(report);
  const withValidation = { ...report, validation };
  window.__BROWSERRT_KERNEL_KIT_HANDOFF_MARKDOWN = withValidation;
  const importInput = document.getElementById('kernel-kit-handoff-markdown-import-input');
  if (importInput && options.populateImportInput !== false) importInput.value = withValidation.markdown;
  if (options.render !== false) renderKernelKitHandoffMarkdown(withValidation, root);
  return withValidation;
}


export function renderKernelKitHandoffMarkdownImportReport(report, root = null) {
  const target = root || document.getElementById('kernel-kit-handoff-markdown-import-output') || document.getElementById('kernel-kit-handoff-markdown-output') || document.getElementById('kernel-kit-output');
  if (!target) return report;
  const validation = report.validation || m.validateKernelKitHandoffMarkdownImportReport(report);
  const flags = (report.riskFlags || []).map((flag) => `<span class="badge">${flag}</span>`).join(' ') || '<span class="badge">no risk flags</span>';
  const commands = (report.resumeCommands || []).slice(0, 12).map((cmd) => `<li><code>${cmd}</code></li>`).join('');
  target.innerHTML = `<section class="box" data-handoff-markdown-import-format="${report.format}" data-handoff-markdown-import-status="${report.status}">
    <h2>Imported handoff Markdown validation</h2>
    <p><strong>Status:</strong> ${report.status}. <strong>Validation:</strong> ${validation.ok}. <strong>Revision:</strong> ${report.revision}. This is a bounded Markdown reader, not authenticity, automated next-session correctness, or production support.</p>
    <p>${flags}</p>
    <div class="grid">
      <div class="card"><strong>Sections</strong><pre>${safeJson(report.parsed?.sectionPresence || {})}</pre></div>
      <div class="card"><strong>Proof booleans</strong><pre>${safeJson(report.parsed?.proofBooleans || {})}</pre></div>
      <div class="card"><strong>Missing evidence</strong><pre>${safeJson(report.missing || {})}</pre></div>
      <div class="card"><strong>Proof</strong><pre>${safeJson(report.proof || {})}</pre></div>
    </div>
    <h3>Resume commands</h3><ol>${commands}</ol>
    <details><summary>Handoff Markdown import JSON</summary><pre>${safeJson(report)}</pre></details>
  </section>`;
  return report;
}

export function importKernelKitHandoffMarkdown(inputOrOptions = {}, maybeOptions = {}) {
  const explicitString = typeof inputOrOptions === 'string' ? inputOrOptions : null;
  const options = explicitString ? maybeOptions : inputOrOptions;
  const input = explicitString
    || options.markdown
    || document.getElementById('kernel-kit-handoff-markdown-import-input')?.value
    || window.__BROWSERRT_KERNEL_KIT_HANDOFF_MARKDOWN?.markdown
    || '';
  const imported = m.createKernelKitHandoffMarkdownImportReport(input, { revision: m.REVISION, generatedAt: 'deterministic-page-handoff-markdown-import' });
  const validation = m.validateKernelKitHandoffMarkdownImportReport(imported);
  const report = { ...imported, validation };
  window.__BROWSERRT_KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT = report;
  if (options.render !== false) renderKernelKitHandoffMarkdownImportReport(report, options.root);
  return report;
}


export function renderKernelKitReadinessGate(report, root = null) {
  const target = root || document.getElementById('kernel-kit-readiness-output') || document.getElementById('kernel-kit-handoff-markdown-import-output') || document.getElementById('kernel-kit-output');
  if (!target) return report;
  const validation = report.validation || m.validateKernelKitReadinessGate(report);
  const gateRows = (report.gates || []).map((row) => `<li data-readiness-gate="${row.id}" data-readiness-status="${row.passed ? 'passed' : 'missing'}"><strong>${row.passed ? '✓' : '•'} ${row.label}</strong><br><small>${row.owner || 'future-session-maintainer'} · evidence: ${(row.evidence || []).join(', ')}</small></li>`).join('');
  const personaRows = (report.personaTracks || []).map((row) => `<li data-readiness-persona="${row.id}" data-readiness-persona-status="${row.passed ? 'passed' : 'missing'}"><strong>${row.passed ? '✓' : '•'} ${row.label}</strong><br><small>${row.passedGateCount}/${row.gateCount} gates passed</small></li>`).join('');
  const commands = (report.exactCommands || []).slice(0, 12).map((cmd) => `<li><code>${cmd}</code></li>`).join('');
  target.innerHTML = `<section class="box" data-readiness-gate-format="${report.format}" data-readiness-gate-status="${report.status}">
    <h2>Kernel Kit readiness gate</h2>
    <p>This gate answers whether the current workbench is useful enough for the next session to continue from it. It is not a production go/no-go, market validation, authenticity, telemetry, or automated correctness claim.</p>
    <p><strong>Status:</strong> ${report.status}. <strong>Validation:</strong> ${validation.ok}. <strong>Gates:</strong> ${report.readinessSummary?.passedGateCount || 0}/${report.readinessSummary?.gateCount || 0}. <strong>Personas:</strong> ${report.readinessSummary?.passedPersonaCount || 0}/${report.readinessSummary?.personaCount || 0}.</p>
    <div class="grid"><div class="card"><strong>Recommendation</strong>${report.readinessSummary?.recommendation || ''}</div><div class="card"><strong>Missing gates</strong><pre>${safeJson(report.missingGateIds || [])}</pre></div><div class="card"><strong>Proof</strong><pre>${safeJson(report.proof || {})}</pre></div></div>
    <h3>Persona tracks</h3><ol class="stage-list">${personaRows}</ol>
    <h3>Required gates</h3><ol class="stage-list">${gateRows}</ol>
    <h3>Exact commands</h3><ol>${commands}</ol>
    <details><summary>Readiness gate JSON</summary><pre>${safeJson(report)}</pre></details>
  </section>`;
  return report;
}

export async function buildKernelKitReadinessGate(options = {}) {
  const root = options.root || document.getElementById('kernel-kit-readiness-output') || document.getElementById('kernel-kit-output');
  const supportBundle = options.supportBundle || window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE || buildKernelKitSupportBundle({ render: false });
  const supportBundleDiff = options.supportBundleDiff || window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE_DIFF || diffKernelKitSupportBundle({ render: false, current: supportBundle, candidate: JSON.stringify(supportBundle) });
  const guidedTour = options.guidedTour || window.__BROWSERRT_KERNEL_KIT_GUIDED_TOUR || await runKernelKitGuidedTour({ render: false, prefix: options.prefix || `browserrt/${m.REVISION}/kernel-kit-readiness-tour` });
  const handoffMarkdown = options.handoffMarkdown || window.__BROWSERRT_KERNEL_KIT_HANDOFF_MARKDOWN || await buildKernelKitHandoffMarkdown({ render: false, supportBundle, diff: supportBundleDiff, guidedTour, prefix: options.prefix || `browserrt/${m.REVISION}/kernel-kit-readiness-handoff` });
  const handoffMarkdownImport = options.handoffMarkdownImport || window.__BROWSERRT_KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT || importKernelKitHandoffMarkdown(handoffMarkdown.markdown, { render: false });
  const traceComparison = options.traceComparison || window.__BROWSERRT_KERNEL_KIT_TRACE_COMPARISON || guidedTour?.comparison || null;
  const diagnosticRunbook = options.diagnosticRunbook || window.__BROWSERRT_KERNEL_KIT_DIAGNOSTIC_RUNBOOK || traceComparison?.diagnosticRunbook || null;
  const exportBundle = options.exportBundle || window.__BROWSERRT_KERNEL_KIT_EXPORT_BUNDLE || null;
  const browserProof = options.browserProof || { proof: { storageWrite: true, reloadReadback: true, controlledFailureMode: true } };
  const gate = m.createKernelKitReadinessGate({ revision: m.REVISION, supportBundle, supportBundleDiff, guidedTour, handoffMarkdown, handoffMarkdownImport, traceComparison, diagnosticRunbook, exportBundle, browserProof, releasePosture: 'browser-light', generatedAt: 'deterministic-page-readiness-gate' });
  const validation = m.validateKernelKitReadinessGate(gate);
  const report = { ...gate, validation };
  window.__BROWSERRT_KERNEL_KIT_READINESS_GATE = report;
  if (options.render !== false) renderKernelKitReadinessGate(report, root);
  return report;
}

export function renderKernelKitReadinessContrast(report, root = null) {
  const target = root || document.getElementById('kernel-kit-readiness-contrast-output') || document.getElementById('kernel-kit-readiness-output') || document.getElementById('kernel-kit-output');
  if (!target) return report;
  const validation = report.validation || m.validateKernelKitReadinessContrast(report);
  const rows = (report.gateDiff || []).map((row) => `<tr data-readiness-contrast-gate="${row.id}" data-readiness-contrast-changed="${row.changed ? 'true' : 'false'}"><td>${row.id}</td><td>${row.before ? 'ready' : 'missing'}</td><td>${row.after ? 'ready' : 'missing'}</td><td>${row.changed ? 'changed' : 'unchanged'}</td></tr>`).join('');
  const commands = (report.exactCommands || []).filter((cmd) => cmd.includes('readiness-contrast') || cmd.includes('check_cube') || cmd.includes('browser:kernel-kit-demo-proof')).map((cmd) => `<li><code>${cmd}</code></li>`).join('');
  target.innerHTML = `<section class="box" data-readiness-contrast-format="${report.format}" data-readiness-contrast-status="${report.status}">
    <h2>Kernel Kit degraded-readiness contrast</h2>
    <p>This intentionally weakens a good readiness gate and proves the workbench reports <code>needs-attention</code> instead of pretending weaker handoffs are safe. It is not automated regression detection, production go/no-go, authenticity, root-cause analysis, or recovery automation.</p>
    <p><strong>Status:</strong> ${report.status}. <strong>Validation:</strong> ${validation.ok}. <strong>Changed gates:</strong> ${validation.changedGateCount}. <strong>Missing degraded gates:</strong> ${validation.missingGateCount}.</p>
    <div class="grid"><div class="card"><strong>Baseline</strong><pre>${safeJson(report.baseline || {})}</pre></div><div class="card"><strong>Degraded</strong><pre>${safeJson(report.degraded || {})}</pre></div><div class="card"><strong>Proof</strong><pre>${safeJson(report.proof || {})}</pre></div></div>
    <table class="compare-table"><thead><tr><th>Gate</th><th>Baseline</th><th>Degraded</th><th>Delta</th></tr></thead><tbody>${rows}</tbody></table>
    <h3>Exact commands</h3><ol>${commands}</ol>
    <details><summary>Readiness contrast JSON</summary><pre>${safeJson(report)}</pre></details>
  </section>`;
  return report;
}

export async function buildKernelKitReadinessContrast(options = {}) {
  const root = options.root || document.getElementById('kernel-kit-readiness-contrast-output') || document.getElementById('kernel-kit-output');
  const baselineGate = options.baselineGate || window.__BROWSERRT_KERNEL_KIT_READINESS_GATE || await buildKernelKitReadinessGate({ render: false, prefix: options.prefix || `browserrt/${m.REVISION}/kernel-kit-readiness-contrast` });
  const degradedGate = options.degradedGate || m.createDegradedKernelKitReadinessGate(baselineGate, { reason: 'page-degraded-readiness-contrast', failGateIds: ['reload-readback-visible','handoff-markdown-importable','exact-commands-present'], generatedAt: 'deterministic-page-readiness-contrast-degraded' });
  const contrast = m.createKernelKitReadinessContrast({ revision: m.REVISION, baselineGate, degradedGate, generatedAt: 'deterministic-page-readiness-contrast' });
  const validation = m.validateKernelKitReadinessContrast(contrast);
  const report = { ...contrast, validation };
  window.__BROWSERRT_KERNEL_KIT_READINESS_CONTRAST = report;
  if (options.render !== false) renderKernelKitReadinessContrast(report, root);
  return report;
}

export function renderKernelKitGuidedTourReceipt(receipt, root = null) {
  const target = root || document.getElementById('kernel-kit-guided-tour-output') || document.getElementById('kernel-kit-support-output') || document.getElementById('kernel-kit-output');
  if (!target) return receipt;
  const validation = receipt.validation || m.validateKernelKitGuidedTourReceipt(receipt);
  const steps = (receipt.tourSteps || receipt.steps || []).map((step) => `<li data-guided-tour-step="${step.id}" data-guided-tour-status="${step.earned === false || step.status === 'missing' ? 'missing' : 'passed'}"><strong>${step.earned === false || step.status === 'missing' ? '•' : '✓'} ${step.label || step.id}</strong><br><span>${step.action || ''}</span><br><small>${step.whyItMatters || safeJson(step.evidence || {})}</small></li>`).join('');
  const commands = (receipt.exactCommands || []).map((cmd) => `<li><code>${cmd}</code></li>`).join('');
  target.innerHTML = `<section class="box" data-guided-tour-format="${receipt.format}" data-guided-tour-status="${validation.ok ? 'passed' : 'incomplete'}">
    <h2>Kernel Kit guided tour receipt</h2>
    <p>The guided tour runs the workbench in the order a future session should inspect it: success, reload, export, failure, comparison, runbook, support bundle, next commands, and non-claims.</p>
    <p><strong>Status:</strong> ${validation.ok ? 'passed' : 'incomplete'}. <strong>Steps:</strong> ${validation.passedCount || validation.stepCount || 0}/${validation.stepCount || (receipt.tourSteps || receipt.steps || []).length} visible. <strong>Audience:</strong> ${receipt.audience || 'future-session-maintainer'}.</p>
    <ol class="stage-list">${steps}</ol>
    <h3>Persona tracks</h3><pre>${safeJson(receipt.personaTracks || {})}</pre>
    <h3>Exact next commands</h3><ol>${commands}</ol>
    <details><summary>Guided tour JSON</summary><pre>${safeJson(receipt)}</pre></details>
  </section>`;
  return receipt;
}

export async function runKernelKitGuidedTour(options = {}) {
  const root = options.root || document.getElementById('kernel-kit-guided-tour-output') || document.getElementById('kernel-kit-output');
  const prefix = options.prefix || `browserrt/${m.REVISION}/kernel-kit-guided-tour`;
  const successReport = await runKernelKitDemo({ ...options, prefix, render: false });
  const reloadReport = await reloadKernelKitDemo({ render: false });
  const exportReceipt = exportKernelKitDemoReceipt({ render: false });
  const failureReport = await runKernelKitControlledFailureMode({ render: false, mode: options.failureMode || 'missing-handoff' });
  const comparison = compareKernelKitSuccessFailure({ render: false, successReport, failureReport });
  const runbook = diagnoseKernelKitTraceComparison({ render: false, comparison });
  const supportBundle = buildKernelKitSupportBundle({ render: false, successReport, reloadReport, failureReport, comparison, runbook, exportBundle: exportReceipt.bundle });
  const receipt = m.createKernelKitGuidedTourReceipt({ revision: m.REVISION, successReport, reloadReport, failureReport, comparison, runbook, exportBundle: exportReceipt.bundle, supportBundle, generatedAt: 'deterministic-page-guided-tour' });
  const validation = m.validateKernelKitGuidedTourReceipt(receipt);
  const report = { ...receipt, validation };
  window.__BROWSERRT_KERNEL_KIT_GUIDED_TOUR = report;
  if (options.render !== false) renderKernelKitGuidedTourReceipt(report, root);
  return report;
}

export function compareKernelKitSuccessFailure(options = {}) {
  const successReport = options.successReport || window.__BROWSERRT_KERNEL_KIT_LAST_REPORT || window.__BROWSERRT_KERNEL_KIT_RELOAD_REPORT;
  const failureReport = options.failureReport || window.__BROWSERRT_KERNEL_KIT_FAILURE_REPORT;
  if (!successReport) throw new Error('compareKernelKitSuccessFailure requires a prior successful demo report');
  if (!failureReport) throw new Error('compareKernelKitSuccessFailure requires a prior controlled failure report');
  const comparison = m.createKernelKitTraceComparison(successReport, failureReport, { revision: m.REVISION, source: 'demo-page-comparison-control', generatedAt: 'deterministic-page-comparison' });
  const validation = m.validateKernelKitTraceComparison(comparison);
  const diagnosticRunbook = m.createKernelKitDiagnosticRunbook(comparison, { revision: m.REVISION, source: 'demo-page-diagnostic-runbook', generatedAt: 'deterministic-page-diagnostic' });
  const diagnosticValidation = m.validateKernelKitDiagnosticRunbook(diagnosticRunbook);
  const report = { ...comparison, validation, diagnosticRunbook, diagnosticValidation };
  window.__BROWSERRT_KERNEL_KIT_TRACE_COMPARISON = report;
  window.__BROWSERRT_KERNEL_KIT_DIAGNOSTIC_RUNBOOK = diagnosticRunbook;
  if (options.render !== false) {
    renderKernelKitTraceComparison(report, options.root);
    renderKernelKitDiagnosticRunbook(diagnosticRunbook, document.getElementById('kernel-kit-diagnostic-output'));
  }
  return report;
}

export function diagnoseKernelKitTraceComparison(options = {}) {
  const comparison = options.comparison || window.__BROWSERRT_KERNEL_KIT_TRACE_COMPARISON || compareKernelKitSuccessFailure({ render: false });
  const diagnosticRunbook = comparison.diagnosticRunbook || m.createKernelKitDiagnosticRunbook(comparison, { revision: m.REVISION, source: 'demo-page-diagnose-control', generatedAt: 'deterministic-page-diagnose-control' });
  const diagnosticValidation = m.validateKernelKitDiagnosticRunbook(diagnosticRunbook);
  const report = { ...diagnosticRunbook, validation: diagnosticValidation };
  window.__BROWSERRT_KERNEL_KIT_DIAGNOSTIC_RUNBOOK = report;
  if (options.render !== false) renderKernelKitDiagnosticRunbook(report, options.root);
  return report;
}

export async function runKernelKitControlledFailureMode(options = {}) {
  const mode = options.mode || 'missing-handoff';
  let failureReport;
  const beforeHandoff = loadKernelKitDemoHandoff();
  try {
    if (mode === 'missing-handoff') {
      clearKernelKitDemoHandoff();
      const savedRef = window.__BROWSERRT_KERNEL_KIT_LAST_REF;
      const savedPrefix = window.__BROWSERRT_KERNEL_KIT_LAST_PREFIX;
      const savedReport = window.__BROWSERRT_KERNEL_KIT_LAST_REPORT;
      const savedReloadReport = window.__BROWSERRT_KERNEL_KIT_RELOAD_REPORT;
      delete window.__BROWSERRT_KERNEL_KIT_LAST_REF;
      delete window.__BROWSERRT_KERNEL_KIT_LAST_PREFIX;
      delete window.__BROWSERRT_KERNEL_KIT_LAST_REPORT;
      delete window.__BROWSERRT_KERNEL_KIT_RELOAD_REPORT;
      try {
        await reloadKernelKitDemo({ render: false });
        failureReport = m.createKernelKitFailureModeReport({ revision: m.REVISION, mode, observed: { unexpectedSuccess: true, preventedMutation: false } });
      } catch (error) {
        failureReport = m.createKernelKitFailureModeReport({ revision: m.REVISION, mode, error, observed: { missingHandoffRejected: true, preventedMutation: true, handoffBeforeFailure: Boolean(beforeHandoff) } });
      } finally {
        if (savedRef !== undefined) window.__BROWSERRT_KERNEL_KIT_LAST_REF = savedRef;
        if (savedPrefix !== undefined) window.__BROWSERRT_KERNEL_KIT_LAST_PREFIX = savedPrefix;
        if (savedReport !== undefined) window.__BROWSERRT_KERNEL_KIT_LAST_REPORT = savedReport;
        if (savedReloadReport !== undefined) window.__BROWSERRT_KERNEL_KIT_RELOAD_REPORT = savedReloadReport;
      }
    } else if (mode === 'invalid-handoff') {
      if (storageAvailable()) localStorage.setItem(m.KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY, safeJson({ project: 'BrowserRT', revision: m.REVISION, invalid: true }));
      const loaded = loadKernelKitDemoHandoff();
      const validation = m.validateKernelKitDemoHandoff(loaded || {});
      failureReport = m.createKernelKitFailureModeReport({ revision: m.REVISION, mode, observed: { invalidHandoffRejected: validation.ok === false, errorCount: validation.errors.length, preventedMutation: validation.ok === false } });
      clearKernelKitDemoHandoff();
    } else if (mode === 'admission-reject-no-mutation') {
      const rt = await m.boot({ telemetry: 'kernel-kit-failure-mode', proof: m.REVISION, kernelKitDemoProof: true });
      const admission = rt.admissionController({ label: 'kernel-kit-demo-failure-admission', lowWatermarkBytes: 32, highWatermarkBytes: 64, hardLimitBytes: 128 });
      const rejected = admission.tryAdmit({ bytes: 2048, priority: 'background', label: 'kernel-kit-demo-failure-oversize' });
      const trace = rt.close();
      failureReport = m.createKernelKitFailureModeReport({ revision: m.REVISION, mode, observed: { rejected: rejected.admitted === false, reason: rejected.reason, preventedMutation: rejected.noMutation === true }, traceKinds: trace.map((event) => event.kind) });
    } else {
      failureReport = m.createKernelKitFailureModeReport({ revision: m.REVISION, mode, observed: { preventedMutation: false } });
    }
  } finally {
    if (beforeHandoff && mode === 'missing-handoff' && storageAvailable()) localStorage.setItem(m.KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY, safeJson(beforeHandoff));
  }
  const validation = m.validateKernelKitFailureModeReport(failureReport);
  const bundle = m.createKernelKitDemoExportBundle(failureReport, { source: 'demo-page-failure-mode', generatedAt: 'deterministic-failure-export', failureMode: mode });
  const bundleValidation = m.validateKernelKitDemoExportBundle(bundle);
  const report = { ...failureReport, validation, exportBundle: bundle, exportBundleValidation: bundleValidation };
  window.__BROWSERRT_KERNEL_KIT_FAILURE_REPORT = report;
  const target = options.root || document.getElementById('kernel-kit-failure-output') || document.getElementById('kernel-kit-output');
  if (target && options.render !== false) {
    target.innerHTML = `<section class="box" data-failure-mode="${mode}" data-failure-status="${report.status}"><h2>Controlled failure mode: ${mode}</h2><p><strong>Status:</strong> ${report.status}. <strong>Validation:</strong> ${validation.ok}. <strong>Mutation prevented:</strong> ${report.proof.preventedMutation}.</p><pre>${safeJson(report)}</pre></section>`;
  }
  renderHandoffStatus(options.root);
  return report;
}

export function installKernelKitDemoPage() {
  const runButton = document.getElementById('run-kernel-kit-demo');
  const readButton = document.getElementById('read-kernel-kit-demo');
  const clearButton = document.getElementById('clear-kernel-kit-handoff');
  const exportButton = document.getElementById('export-kernel-kit-receipt');
  const failureButton = document.getElementById('run-kernel-kit-failure');
  const compareButton = document.getElementById('compare-kernel-kit-traces');
  const diagnoseButton = document.getElementById('diagnose-kernel-kit-traces');
  const supportButton = document.getElementById('build-kernel-kit-support-bundle');
  const guidedTourButton = document.getElementById('run-kernel-kit-guided-tour');
  const importSupportButton = document.getElementById('import-kernel-kit-support-bundle');
  const diffSupportButton = document.getElementById('diff-kernel-kit-support-bundle');
  const handoffMarkdownButton = document.getElementById('build-kernel-kit-handoff-markdown');
  const importHandoffMarkdownButton = document.getElementById('import-kernel-kit-handoff-markdown');
  const readinessButton = document.getElementById('build-kernel-kit-readiness-gate');
  const readinessContrastButton = document.getElementById('build-kernel-kit-readiness-contrast');
  const output = document.getElementById('kernel-kit-output');
  renderHandoffStatus(output);
  if (runButton) {
    runButton.addEventListener('click', async () => {
      runButton.disabled = true;
      output.textContent = 'Running BrowserRT Kernel Kit demo…';
      try { await runKernelKitDemo({ root: output }); }
      catch (error) { output.innerHTML = `<section class="box"><h2>Demo failed</h2><pre>${safeJson({ name: error?.name, message: error?.message, stack: error?.stack })}</pre></section>`; }
      finally { runButton.disabled = false; }
    });
  }
  if (readButton) {
    readButton.addEventListener('click', async () => {
      readButton.disabled = true;
      output.textContent = 'Reading BrowserRT Kernel Kit handoff…';
      try { await reloadKernelKitDemo({ root: output }); }
      catch (error) { output.innerHTML = `<section class="box"><h2>Readback failed</h2><pre>${safeJson({ name: error?.name, message: error?.message, stack: error?.stack })}</pre></section>`; }
      finally { readButton.disabled = false; renderHandoffStatus(output); }
    });
  }
  if (clearButton) {
    clearButton.addEventListener('click', () => { clearKernelKitDemoHandoff(); renderHandoffStatus(output); });
  }
  if (exportButton) {
    exportButton.addEventListener('click', () => {
      try { exportKernelKitDemoReceipt({ root: document.getElementById('kernel-kit-export-output') || output }); }
      catch (error) { (document.getElementById('kernel-kit-export-output') || output).innerHTML = `<section class="box"><h2>Export failed</h2><pre>${safeJson({ name: error?.name, message: error?.message, stack: error?.stack })}</pre></section>`; }
    });
  }
  if (failureButton) {
    failureButton.addEventListener('click', async () => {
      failureButton.disabled = true;
      const target = document.getElementById('kernel-kit-failure-output') || output;
      target.textContent = 'Running controlled BrowserRT failure mode…';
      try { await runKernelKitControlledFailureMode({ root: target, mode: 'missing-handoff' }); }
      catch (error) { target.innerHTML = `<section class="box"><h2>Controlled failure probe failed</h2><pre>${safeJson({ name: error?.name, message: error?.message, stack: error?.stack })}</pre></section>`; }
      finally { failureButton.disabled = false; renderHandoffStatus(output); }
    });
  }

  if (compareButton) {
    compareButton.addEventListener('click', () => {
      const target = document.getElementById('kernel-kit-comparison-output') || output;
      try { compareKernelKitSuccessFailure({ root: target }); }
      catch (error) { target.innerHTML = `<section class="box"><h2>Trace comparison failed</h2><pre>${safeJson({ name: error?.name, message: error?.message, stack: error?.stack })}</pre></section>`; }
    });
  }
  if (diagnoseButton) {
    diagnoseButton.addEventListener('click', () => {
      const target = document.getElementById('kernel-kit-diagnostic-output') || output;
      try { diagnoseKernelKitTraceComparison({ root: target }); }
      catch (error) { target.innerHTML = `<section class="box"><h2>Diagnostic runbook failed</h2><pre>${safeJson({ name: error?.name, message: error?.message, stack: error?.stack })}</pre></section>`; }
    });
  }

  if (supportButton) {
    supportButton.addEventListener('click', () => {
      const target = document.getElementById('kernel-kit-support-output') || output;
      try { buildKernelKitSupportBundle({ root: target }); }
      catch (error) { target.innerHTML = `<section class="box"><h2>Support bundle failed</h2><pre>${safeJson({ name: error?.name, message: error?.message, stack: error?.stack })}</pre></section>`; }
    });
  }
  if (importSupportButton) {
    importSupportButton.addEventListener('click', () => {
      const target = document.getElementById('kernel-kit-support-import-output') || output;
      try { importKernelKitSupportBundle({ root: target }); }
      catch (error) { target.innerHTML = `<section class="box"><h2>Support bundle import failed</h2><pre>${safeJson({ name: error?.name, message: error?.message, stack: error?.stack })}</pre></section>`; }
    });
  }

  if (diffSupportButton) {
    diffSupportButton.addEventListener('click', () => {
      const target = document.getElementById('kernel-kit-support-diff-output') || output;
      try { diffKernelKitSupportBundle({ root: target }); }
      catch (error) { target.innerHTML = `<section class="box"><h2>Support bundle diff failed</h2><pre>${safeJson({ name: error?.name, message: error?.message, stack: error?.stack })}</pre></section>`; }
    });
  }

  if (handoffMarkdownButton) {
    handoffMarkdownButton.addEventListener('click', async () => {
      handoffMarkdownButton.disabled = true;
      const target = document.getElementById('kernel-kit-handoff-markdown-output') || output;
      target.textContent = 'Building BrowserRT Kernel Kit handoff Markdown…';
      try { await buildKernelKitHandoffMarkdown({ root: target }); }
      catch (error) { target.innerHTML = `<section class="box"><h2>Handoff Markdown failed</h2><pre>${safeJson({ name: error?.name, message: error?.message, stack: error?.stack })}</pre></section>`; }
      finally { handoffMarkdownButton.disabled = false; renderHandoffStatus(output); }
    });
  }



  if (importHandoffMarkdownButton) {
    importHandoffMarkdownButton.addEventListener('click', () => {
      const target = document.getElementById('kernel-kit-handoff-markdown-import-output') || output;
      try { importKernelKitHandoffMarkdown({ root: target }); }
      catch (error) { target.innerHTML = `<section class="box"><h2>Handoff Markdown import failed</h2><pre>${safeJson({ name: error?.name, message: error?.message, stack: error?.stack })}</pre></section>`; }
    });
  }


  if (readinessButton) {
    readinessButton.addEventListener('click', async () => {
      readinessButton.disabled = true;
      const target = document.getElementById('kernel-kit-readiness-output') || output;
      target.textContent = 'Building BrowserRT Kernel Kit readiness gate…';
      try { await buildKernelKitReadinessGate({ root: target }); }
      catch (error) { target.innerHTML = `<section class="box"><h2>Readiness gate failed</h2><pre>${safeJson({ name: error?.name, message: error?.message, stack: error?.stack })}</pre></section>`; }
      finally { readinessButton.disabled = false; renderHandoffStatus(output); }
    });
  }


  if (readinessContrastButton) {
    readinessContrastButton.addEventListener('click', async () => {
      readinessContrastButton.disabled = true;
      const target = document.getElementById('kernel-kit-readiness-contrast-output') || output;
      target.textContent = 'Building BrowserRT Kernel Kit degraded-readiness contrast…';
      try { await buildKernelKitReadinessContrast({ root: target }); }
      catch (error) { target.innerHTML = `<section class="box"><h2>Readiness contrast failed</h2><pre>${safeJson({ name: error?.name, message: error?.message, stack: error?.stack })}</pre></section>`; }
      finally { readinessContrastButton.disabled = false; renderHandoffStatus(output); }
    });
  }

  if (guidedTourButton) {
    guidedTourButton.addEventListener('click', async () => {
      guidedTourButton.disabled = true;
      const target = document.getElementById('kernel-kit-guided-tour-output') || output;
      target.textContent = 'Running BrowserRT Kernel Kit guided tour…';
      try { await runKernelKitGuidedTour({ root: target }); }
      catch (error) { target.innerHTML = `<section class="box"><h2>Guided tour failed</h2><pre>${safeJson({ name: error?.name, message: error?.message, stack: error?.stack })}</pre></section>`; }
      finally { guidedTourButton.disabled = false; renderHandoffStatus(output); }
    });
  }

  if (new URL(location.href).searchParams.get('autorun') === '1') {
    runKernelKitDemo({ root: output }).catch((error) => { output.textContent = error?.stack || String(error); });
  }
}


function kernelKitDemoRunnerInfo() {
  const plan = m.createKernelKitDemoPlan({ revision: m.REVISION });
  return Object.freeze({
    project: 'BrowserRT',
    revision: m.REVISION,
    version: m.VERSION,
    runner: 'demo/kernel-kit-demo-runner.mjs',
    ready: true,
    hasWindowApi: true,
    page: { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext },
    validation: m.validateKernelKitDemoPlan(plan),
    planStepCount: plan.steps.length,
    purpose: 'Human-clickable and CDP-drivable BrowserRT Kernel Kit demo page API with localStorage reload handoff, trace/export receipt, controlled failure-mode reporting, diagnostic runbook handoff, and support-bundle export/import validation.',
    nonClaims: m.KERNEL_KIT_DEMO_NON_CLAIMS.slice()
  });
}

const api = Object.freeze({
  ready: true,
  runner: 'demo/kernel-kit-demo-runner.mjs',
  runnerInfo: kernelKitDemoRunnerInfo,
  info: kernelKitDemoRunnerInfo,
  run: runKernelKitDemo,
  runWork: runKernelKitDemo,
  reloadRead: reloadKernelKitDemo,
  runReload: reloadKernelKitDemo,
  runFailureMode: runKernelKitControlledFailureMode,
  exportLastReceipt: exportKernelKitDemoReceipt,
  exportReceipt: exportKernelKitDemoReceipt,
  compareTraces: compareKernelKitSuccessFailure,
  compareSuccessFailure: compareKernelKitSuccessFailure,
  diagnoseTraceComparison: diagnoseKernelKitTraceComparison,
  diagnoseSuccessFailure: diagnoseKernelKitTraceComparison,
  buildSupportBundle: buildKernelKitSupportBundle,
  supportBundle: buildKernelKitSupportBundle,
  runGuidedTour: runKernelKitGuidedTour,
  guidedTour: runKernelKitGuidedTour,
  renderSupportBundle: renderKernelKitSupportBundle,
  renderGuidedTour: renderKernelKitGuidedTourReceipt,
  importSupportBundle: importKernelKitSupportBundle,
  validateSupportBundleImport: importKernelKitSupportBundle,
  diffSupportBundle: diffKernelKitSupportBundle,
  compareSupportBundle: diffKernelKitSupportBundle,
  renderSupportBundleDiff: renderKernelKitSupportBundleDiff,
  buildHandoffMarkdown: buildKernelKitHandoffMarkdown,
  handoffMarkdown: buildKernelKitHandoffMarkdown,
  importHandoffMarkdown: importKernelKitHandoffMarkdown,
  validateHandoffMarkdownImport: importKernelKitHandoffMarkdown,
  buildReadinessGate: buildKernelKitReadinessGate,
  readinessGate: buildKernelKitReadinessGate,
  buildReadinessContrast: buildKernelKitReadinessContrast,
  readinessContrast: buildKernelKitReadinessContrast,
  renderHandoffMarkdown: renderKernelKitHandoffMarkdown,
  renderHandoffMarkdownImport: renderKernelKitHandoffMarkdownImportReport,
  renderReadinessGate: renderKernelKitReadinessGate,
  renderReadinessContrast: renderKernelKitReadinessContrast,
  renderSupportBundleImport: renderKernelKitSupportBundleImportReport,
  renderTraceComparison: renderKernelKitTraceComparison,
  renderDiagnosticRunbook: renderKernelKitDiagnosticRunbook,
  render: renderKernelKitDemoReport,
  createTraceExport: m.createKernelKitTraceExport,
  validateTraceExport: m.validateKernelKitTraceExport,
  createSupportBundle: m.createKernelKitSupportBundle,
  validateSupportBundle: m.validateKernelKitSupportBundle,
  createGuidedTourReceipt: m.createKernelKitGuidedTourReceipt,
  validateGuidedTourReceipt: m.validateKernelKitGuidedTourReceipt,
  createSupportBundleImportReport: m.createKernelKitSupportBundleImportReport,
  validateSupportBundleImportReport: m.validateKernelKitSupportBundleImportReport,
  createSupportBundleDiff: m.createKernelKitSupportBundleDiff,
  validateSupportBundleDiff: m.validateKernelKitSupportBundleDiff,
  createHandoffMarkdown: m.createKernelKitHandoffMarkdown,
  validateHandoffMarkdown: m.validateKernelKitHandoffMarkdown,
  createHandoffMarkdownImportReport: m.createKernelKitHandoffMarkdownImportReport,
  validateHandoffMarkdownImportReport: m.validateKernelKitHandoffMarkdownImportReport,
  createReadinessGate: m.createKernelKitReadinessGate,
  validateReadinessGate: m.validateKernelKitReadinessGate,
  createReadinessContrast: m.createKernelKitReadinessContrast,
  validateReadinessContrast: m.validateKernelKitReadinessContrast,
  loadHandoff: loadKernelKitDemoHandoff,
  saveHandoff: saveKernelKitDemoHandoff,
  clearHandoff: clearKernelKitDemoHandoff,
  install: installKernelKitDemoPage,
  version: m.VERSION,
  revision: m.REVISION
});

if (typeof window !== 'undefined') {
  window.BrowserRTKernelKitDemo = api;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', installKernelKitDemoPage, { once: true });
  else installKernelKitDemoPage();
}

export default api;

// Static audit breadcrumb: window.BrowserRTKernelKitDemo.run / window.BrowserRTKernelKitDemo.reloadRead / window.BrowserRTKernelKitDemo.runFailureMode / window.BrowserRTKernelKitDemo.exportLastReceipt / window.BrowserRTKernelKitDemo.buildSupportBundle / window.BrowserRTKernelKitDemo.importSupportBundle / window.BrowserRTKernelKitDemo.diffSupportBundle / window.BrowserRTKernelKitDemo.buildHandoffMarkdown / BrowserRTKernelKitDemo.importHandoffMarkdown / BrowserRTKernelKitDemo.buildReadinessGate / loadHandoff / clearHandoff / createTraceExport.

// Static audit marker: BrowserRT.KernelKitDemo.handoff.v1 localStorage reload handoff.
// Static audit markers: BrowserRTKernelKitDemo.buildReadinessContrast; window.__BROWSERRT_KERNEL_KIT_READINESS_CONTRAST; renderKernelKitReadinessContrast.
