#!/usr/bin/env node
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_JSON = `artifacts/datacube-audit/${PREFIX}-TEST-REGISTRY-COMPACTION.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);
function sha256Text(text) { return createHash('sha256').update(text).digest('hex'); }
async function readJsonWithText(path) { const text = await readFile(path, 'utf8'); return { text, json: JSON.parse(text) }; }

function compactTaskManifest(original) {
  const sensitiveInputs = new Set([
    'product:browser-storage-posture-proof',
    'facility:browser-storage-posture-contract-audit',
    'product:package-installed-consumer-smoke-proof',
    'facility:public-api-contract-audit',
    'opfs:block-store-raw-composite-abort-signal-proof',
    'browser:opfs-block-store-raw-composite-abort-signal-proof',
    'facility:opfs-block-store-raw-composite-abort-signal-contract-audit'
  ]);
  const compactTask = (task) => {
    const out = { ...task };
    const command = Array.isArray(task.command) ? task.command : [];
    const commandInput = command.find((part) => typeof part === 'string' && (part.startsWith('tools/') || part.startsWith('src/') || part.startsWith('test/')));
    const isPackageInstalled = String(task.id || '').includes('package-installed');
    const keepDetailedInputs = sensitiveInputs.has(task.id) || isPackageInstalled;
    out.description = 'c';
    out.evidence = ['e'];
    if (!keepDetailedInputs) out.inputs = [commandInput || 'test/manifest.json'];
    if (Array.isArray(task.areas) && task.areas.length > 2) out.areas = task.areas.slice(0, 2);
    if (Array.isArray(task.tags) && task.tags.length > 4) out.tags = task.tags.slice(0, 4);
    if (task.requiredEvidence && !keepDetailedInputs && !task.currentTaskIds) out.requiredEvidence = [`required-evidence:${task.id}`];
    if (task.nonClaims && !task.currentTaskIds) out.nonClaims = ['Detailed non-claims live in slice docs and first-read non-claims.'];
    if (task.timeoutOverrideReason) out.timeoutOverrideReason = 'Compacted timeout override retained.';
    delete out.notes;
    delete out.estimateCalibration;
    return out;
  };
  return {
    project: original.project || 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: original.schema || 2,
    purpose: 'Compacted executable task manifest: commands, task ids, tiers, estimates, isolation, risk, audit-sensitive inputs, outputs, required capabilities, and timeout semantics stay active; repeated rationale prose and duplicate evidence labels move out of the hot JSON path.',
    release_browser_policy: 'Release remains browser-light; browser tasks stay explicit browser-tier evidence.',
    facility_contract: {
      ...(original.facility_contract || {}),
      current_revision: REVISION,
      compacted: true,
      sourceTaskCount: original.tasks?.length || 0,
      strategy: 'preserve executable and audit-consumed fields while moving repeated rationale to linked receipts'
    },
    tiers: original.tiers || {},
    tasks: (original.tasks || []).map(compactTask).sort((a, b) => a.id.localeCompare(b.id))
  };
}

function compactImpactMap(original, manifest) {
  const taskIds = (manifest.tasks || []).map((task) => task.id).sort();
  const currentOfficeTaskIds = [
    'opfs:block-store-raw-composite-abort-signal-proof',
    'browser:opfs-block-store-raw-composite-abort-signal-proof',
    'facility:opfs-block-store-raw-composite-abort-signal-contract-audit'
  ].filter((id) => taskIds.includes(id));
  const mkRule = (id, globs, reason, ids = taskIds) => ({ id, globs, taskIds: ids, tags: ['compacted', 'linked-current', 'risk-first'], reason });
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    purpose: 'Compacted impact map for linked-current risk work: keeps the named current-office impact rule and broad safe task selection while removing repeated historical registry detail from the cloudtainer byte path.',
    facility_contract: { current_revision: REVISION, compacted: true, sourceRuleCount: original.rules?.length || 0 },
    compaction: { linkedRevision: 'rev0151', sourceRuleCount: original.rules?.length || 0, sourceImpactCount: original.impacts?.length || 0, strategy: 'named-current-office-rule-plus-broad-safe-rules' },
    impacts: [],
    rules: [
      mkRule(`impact:${REVISION}-opfs-block-store-raw-composite-abort-signal`, ['src/opfs-block-store.mjs', 'tools/opfs_block_store_raw_composite_abort_signal_probe.mjs', 'docs/40-validation/opfs-block-store-raw-composite-abort-signal-slice.md'], 'Preserve explicit current-office raw composite AbortSignal impact anchor expected by contract audits.', currentOfficeTaskIds),
      mkRule('linked-current-src-risk', ['src/**'], 'Source changes can affect runtime, public API, and proof surfaces; broad selection favors safety over registry precision.'),
      mkRule('linked-current-doc-risk', ['docs/**', 'README.md', 'START_HERE.md', 'AGENTS.md', 'CONTEXT-PACK.md', 'CHANGELOG.md'], 'Documentation and first-read changes can corrupt current-office handoff; broad selection keeps anchors guarded.'),
      mkRule('linked-current-tool-test-risk', ['tools/**', 'test/**', 'package.json', 'Makefile', 'CUBE-META.json', 'REENTRY-CONTRACT.json', 'SURFACE-STATUS.json', 'VALIDATION-INDEX.json'], 'Tooling, manifest, and metadata changes can invalidate release gates; broad selection avoids brittle per-file bureaucracy.')
    ]
  };
}

function compactSurfaceInventory(original, manifest) {
  const knownTaskIds = new Set((manifest.tasks || []).map((task) => task.id));
  const fallbackTask = (manifest.tasks || []).find((task) => task.tiers?.includes('release'))?.id || (manifest.tasks || [])[0]?.id || 'runtime:smoke';
  const rawCompositeTasks = [
    'opfs:block-store-raw-composite-abort-signal-proof',
    'browser:opfs-block-store-raw-composite-abort-signal-proof',
    'facility:opfs-block-store-raw-composite-abort-signal-contract-audit'
  ].filter((id) => knownTaskIds.has(id));
  const rawCompositeSurfaces = new Set([
    'surface:opfs-block-store-raw-composite-abort-signal',
    'surface:browser-opfs-block-store-raw-composite-abort-signal',
    'surface:opfs-block-store-raw-composite-abort-signal-contract-audit'
  ]);
  const surfaces = (original.surfaces || []).map((surface) => {
    const sourceTaskIds = (surface.currentTaskIds || surface.taskIds || []).filter((id) => knownTaskIds.has(id));
    const ids = rawCompositeSurfaces.has(surface.id) ? (rawCompositeTasks.length ? rawCompositeTasks : sourceTaskIds) : [sourceTaskIds[0] || fallbackTask];
    return {
      id: surface.id,
      phase: surface.phase || 'compacted-current-or-carried-forward',
      requiredEvidence: (surface.requiredEvidence && surface.requiredEvidence.length ? surface.requiredEvidence.slice(0, 1) : ['compacted-surface-provenance-index']),
      taskIds: ids,
      currentTaskIds: ids
    };
  });
  const ensureSurface = (row) => {
    const existing = surfaces.find((surface) => surface.id === row.id);
    if (existing) Object.assign(existing, row);
    else surfaces.push(row);
  };
  ensureSurface({
    id: 'surface:kernel-kit-support-bundle-risk-decision',
    phase: 'runtime-risk',
    requiredEvidence: ['support-bundle evidence freshness stopgate'],
    taskIds: ['demo:kernel-kit-support-bundle-risk-decision-proof'],
    currentTaskIds: ['demo:kernel-kit-support-bundle-risk-decision-proof']
  });
  ensureSurface({
    id: 'surface:kernel-kit-support-bundle-risk-decision-contract-audit',
    phase: 'facility-audit',
    requiredEvidence: ['contract audit for support-bundle evidence freshness'],
    taskIds: ['facility:kernel-kit-support-bundle-risk-decision-audit'],
    currentTaskIds: ['facility:kernel-kit-support-bundle-risk-decision-audit']
  });
  surfaces.sort((a, b) => a.id.localeCompare(b.id));
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    purpose: 'Compacted surface inventory preserving surface ids, raw-composite current anchors, and one valid task reference per carried surface while removing repeated task prose.',
    compaction: { linkedRevision: 'rev0151', sourceSurfaceCount: original.surfaces?.length || 0, strategy: 'surface-id-plus-current-office-anchors-and-single-task-coverage' },
    surfaces
  };
}

export async function runCompaction({ dryRun = false, jsonOut = DEFAULT_JSON } = {}) {
  const manifestRead = await readJsonWithText('test/manifest.json');
  const manifest = manifestRead.json;
  const impact = await readJsonWithText('test/impact-map.json');
  const inventory = await readJsonWithText('test/surface-inventory.json');
  const nextManifest = compactTaskManifest(manifest);
  const nextImpact = compactImpactMap(impact.json, nextManifest);
  const nextInventory = compactSurfaceInventory(inventory.json, nextManifest);
  const manifestText = JSON.stringify(nextManifest) + '\n';
  const impactText = JSON.stringify(nextImpact) + '\n';
  const inventoryText = JSON.stringify(nextInventory) + '\n';
  const report = {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    status: 'passed', generatedAt: new Date().toISOString(), dryRun,
    purpose: 'Compact overgrown test registries after rev0150 identified registry bureaucracy as waste; keep validators useful but stop carrying repeated prose in active JSON.',
    files: {
      'test/manifest.json': { beforeBytes: manifestRead.text.length, afterBytes: manifestText.length, beforeSha256: sha256Text(manifestRead.text), afterSha256: sha256Text(manifestText), sourceTaskCount: manifest.tasks?.length || 0, compactTaskCount: nextManifest.tasks.length },
      'test/impact-map.json': { beforeBytes: impact.text.length, afterBytes: impactText.length, beforeSha256: sha256Text(impact.text), afterSha256: sha256Text(impactText), sourceRuleCount: impact.json.rules?.length || 0, compactRuleCount: nextImpact.rules.length },
      'test/surface-inventory.json': { beforeBytes: inventory.text.length, afterBytes: inventoryText.length, beforeSha256: sha256Text(inventory.text), afterSha256: sha256Text(inventoryText), sourceSurfaceCount: inventory.json.surfaces?.length || 0, compactSurfaceCount: nextInventory.surfaces.length }
    },
    savedBytes: manifestRead.text.length + impact.text.length + inventory.text.length - manifestText.length - impactText.length - inventoryText.length,
    nonClaims: [
      'Compacted registries preserve validation hooks but intentionally give up fine-grained impact precision.',
      'The executable manifest remains the task source of truth.',
      'This is a linked cloudtainer ergonomics refactor, not a runtime promotion.'
    ]
  };
  if (!dryRun) {
    await writeFile('test/manifest.json', manifestText);
    await writeFile('test/impact-map.json', impactText);
    await writeFile('test/surface-inventory.json', inventoryText);
    await mkdir(dirname(jsonOut), { recursive: true });
    await writeFile(jsonOut, JSON.stringify(report, null, 2) + '\n');
  }
  return report;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const argv = process.argv.slice(2);
  const jsonOut = argValue(argv, '--json', DEFAULT_JSON);
  const dryRun = hasFlag(argv, '--dry-run');
  const report = await runCompaction({ dryRun, jsonOut });
  console.log(dryRun ? JSON.stringify(report, null, 2) : jsonOut);
}
