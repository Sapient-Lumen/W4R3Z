import { makeEnvelope } from '../shared/protocol';
const outputNode = document.getElementById('probe-json');
const summaryNode = document.getElementById('summary');
if (!outputNode || !summaryNode)
    throw new Error('probe page root missing');
const output = outputNode;
const summary = summaryNode;
function setSummary(text, tone = 'muted') {
    summary.textContent = text;
    summary.className = tone;
}
function activeContentScriptExperimentSummary(bridge) {
    const active = bridge?.manifest?.contentScriptPolicy?.activeExperiment;
    if (!active)
        return null;
    return active.requiresNavigation
        ? `Active content-script experiment: ${active.label}. Reload or renavigate the supported tab before comparing coverage.`
        : `Active content-script experiment: ${active.label}.`;
}
function nativeStatusSummary(bridge) {
    const snapshot = bridge?.nativeStatusSnapshot;
    const inventory = snapshot?.overflow_inventory;
    if (!snapshot)
        return null;
    const parts = [
        snapshot.native_host ? `native host: ${snapshot.native_host}` : null,
        snapshot.broker?.role ? `broker role: ${snapshot.broker.role}` : null,
        snapshot.matches_persistent_host === true ? 'same host process as persistent port' : null,
        snapshot.matches_persistent_host === false ? 'different host process than persistent port' : null,
        typeof snapshot.host_identity?.pid === 'number' ? `pid: ${snapshot.host_identity.pid}` : null,
        typeof snapshot.event_count === 'number' ? `events: ${snapshot.event_count}` : null,
        typeof inventory?.artifact_count === 'number' ? `overflow artifacts: ${inventory.artifact_count}` : null,
        typeof inventory?.total_disk_bytes === 'number' ? `overflow bytes: ${inventory.total_disk_bytes}` : null,
    ].filter(Boolean);
    return parts.length ? `Native status snapshot: ${parts.join(' · ')}.` : 'Native status snapshot captured.';
}
function coverageExperimentSummary(bridge) {
    const coverageAudit = bridge?.receiverAudit?.coverageAudit;
    const plan = coverageAudit?.experimentPlan;
    if (!coverageAudit || !plan)
        return null;
    const current = plan.experiments.find((experiment) => experiment.id === plan.currentExperimentId);
    const recommended = plan.recommendedExperimentId
        ? plan.experiments.find((experiment) => experiment.id === plan.recommendedExperimentId)
        : undefined;
    if (coverageAudit.gapCount === 0)
        return 'No current receiver coverage gaps were observed.';
    if (!recommended || recommended.id === current?.id) {
        return plan.recommendedRationale ?? `Receiver coverage gaps remain (${coverageAudit.gapCount}), but the current conservative runtime-priming path is still the recommended next move.`;
    }
    return `${recommended.label} would reduce remaining gaps from ${current?.remainingGapCount ?? coverageAudit.gapCount} to ${recommended.remainingGapCount}. ${plan.recommendedRationale ?? ''}`.trim();
}
function render(result) {
    output.textContent = JSON.stringify(result, null, 2);
    document.body.dataset.probeReady = '1';
    document.body.dataset.probeOk = result.ok ? '1' : '0';
    const coverageSummary = coverageExperimentSummary(result.bridge);
    const activeExperimentSummary = activeContentScriptExperimentSummary(result.bridge);
    const nativeSummary = nativeStatusSummary(result.bridge);
    const suffix = [coverageSummary, activeExperimentSummary, nativeSummary].filter(Boolean).join(' ');
    if (suffix) {
        setSummary(`${result.ok ? 'Probe completed successfully.' : 'Probe completed with failures.'} ${suffix}`, result.ok ? 'ok' : 'bad');
        return;
    }
    setSummary(result.ok ? 'Probe completed successfully.' : 'Probe completed with failures.', result.ok ? 'ok' : 'bad');
}
async function bridgeRequest(type, payload = {}) {
    return chrome.runtime.sendMessage(makeEnvelope(type, payload));
}
function queryParams() {
    const params = {};
    new URLSearchParams(window.location.search).forEach((value, key) => {
        params[key] = value;
    });
    return params;
}
async function waitForTabComplete(tabId, timeoutMs) {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
        const tab = await chrome.tabs.get(tabId);
        if (tab.status === 'complete')
            return;
        await new Promise((resolve) => window.setTimeout(resolve, 125));
    }
}
async function waitForObservedSupportedTab(tabId, timeoutMs) {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
        const response = await bridgeRequest('bridge.probe', { limit: 60, await_health_ms: 500 });
        const supportedTabs = response.payload?.status.supportedTabs ?? [];
        if (supportedTabs.some((tab) => tab.tabId === tabId))
            return response.payload;
        await new Promise((resolve) => window.setTimeout(resolve, 200));
    }
    throw new Error(`supported tab ${tabId} was not observed before timeout`);
}
async function fixtureFlow(fixtureUrl, writeText) {
    const result = {
        fixtureUrl,
        writeText,
        errors: [],
    };
    const created = await chrome.tabs.create({ url: fixtureUrl, active: false });
    if (!created.id)
        throw new Error('failed to create fixture tab');
    result.fixtureTabId = created.id;
    await waitForTabComplete(created.id, 12_000);
    const observed = await waitForObservedSupportedTab(created.id, 12_000);
    result.observedTarget = observed.status.supportedTabs?.find((tab) => tab.tabId === created.id) ?? null;
    await bridgeRequest('bridge.set_target_tab', { tab_id: created.id });
    const initialPrompt = await bridgeRequest('prompt.read', { tab_id: created.id });
    result.initialPrompt = initialPrompt.payload?.text ?? null;
    if (writeText) {
        await bridgeRequest('prompt.write', { tab_id: created.id, text: writeText });
        const afterWrite = await bridgeRequest('prompt.read', { tab_id: created.id });
        result.afterWritePrompt = afterWrite.payload?.text ?? null;
        if (result.afterWritePrompt !== writeText) {
            result.errors.push(`prompt.write verification mismatch: expected ${JSON.stringify(writeText)} got ${JSON.stringify(result.afterWritePrompt)}`);
        }
    }
    const latest = await bridgeRequest('transcript.latest', { tab_id: created.id });
    result.latestOutput = latest.payload?.text ?? null;
    const snapshot = await bridgeRequest('state.snapshot', { tab_id: created.id });
    result.snapshot = snapshot.payload ?? null;
    const capture = await bridgeRequest('fixture.capture', { tab_id: created.id });
    result.capture = capture.payload ?? null;
    return result;
}
async function runProbe(opts) {
    document.body.dataset.probeReady = '0';
    document.body.dataset.probeOk = '0';
    const query = queryParams();
    const result = {
        ok: false,
        startedAt: new Date().toISOString(),
        completedAt: '',
        query,
        bridge: null,
        errors: [],
    };
    try {
        setSummary('Collecting bridge probe…');
        const bridge = await bridgeRequest('bridge.probe', {
            limit: 80,
            await_health_ms: 1800,
            ensure_offscreen: query.offscreen === '1',
        });
        result.bridge = bridge.payload ?? null;
        const fixtureUrl = query.fixture || 'http://127.0.0.1:8765/';
        const writeText = query.write ?? 'hello from glasstty probe';
        if (opts.includeFixture || query.fixture) {
            setSummary('Running fixture flow…', 'warn');
            result.fixture = await fixtureFlow(fixtureUrl, writeText);
        }
        const native = result.bridge?.status.nativeConnection;
        const persistentHealthy = Boolean(native && native.connected !== false && native.lastHealthOk !== false && !native.lastHealthError);
        const oneShotHealthy = Boolean(native?.lastOneShotProbeOk && !native?.lastOneShotProbeError);
        const nativeHealthy = persistentHealthy || oneShotHealthy;
        const fixtureHealthy = !result.fixture || result.fixture.errors.length === 0;
        result.ok = Boolean(result.bridge && nativeHealthy && fixtureHealthy);
        if (!nativeHealthy) {
            const diagnosis = native?.laneDiagnosis;
            const runtimeHint = result.bridge?.status.persistentDiagnostics?.runtimeHint;
            result.errors.push(`native health not confirmed: ${diagnosis?.summary ?? native?.lastHealthError ?? native?.lastOneShotProbeError ?? native?.lastDisconnectReason ?? 'not connected'}`);
            if (diagnosis?.recommendedAction) {
                result.errors.push(`native next action: ${diagnosis.recommendedAction}`);
            }
            if (runtimeHint?.summary) {
                result.errors.push(`durable runtime hint: ${runtimeHint.summary}`);
            }
            if (runtimeHint?.recommendedAction) {
                result.errors.push(`durable runtime action: ${runtimeHint.recommendedAction}`);
            }
        }
        if (result.fixture?.errors.length) {
            result.errors.push(...result.fixture.errors);
        }
    }
    catch (error) {
        result.errors.push(error instanceof Error ? error.message : String(error));
        result.ok = false;
    }
    finally {
        result.completedAt = new Date().toISOString();
        render(result);
    }
}
window.addEventListener('DOMContentLoaded', () => {
    document.getElementById('run-probe')?.addEventListener('click', () => {
        void runProbe({ includeFixture: false });
    });
    document.getElementById('run-fixture')?.addEventListener('click', () => {
        void runProbe({ includeFixture: true });
    });
    const query = queryParams();
    if (query.run === '1') {
        void runProbe({ includeFixture: Boolean(query.fixture) });
    }
});
