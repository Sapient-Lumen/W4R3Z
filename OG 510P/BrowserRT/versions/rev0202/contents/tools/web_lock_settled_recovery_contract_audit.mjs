#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'facility:web-lock-settled-recovery-contract-audit';

function parseArgs(argv = process.argv.slice(2)) {
  const out = { json: null };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--json') out.json = argv[++i];
  }
  return out;
}

async function read(rel) {
  return readFile(new URL(`../${rel}`, import.meta.url), 'utf8');
}

function check(id, description, ok, details = {}) {
  return { id, description, status: ok ? 'passed' : 'failed', ...details };
}

function hasAll(text, needles) {
  const missing = needles.filter((needle) => !text.includes(needle));
  return { ok: missing.length === 0, missing };
}

function jsonHasTask(manifest, id) {
  return Boolean((manifest.tasks || []).some((task) => task.id === id));
}

async function main() {
  const started = Date.now();
  const args = parseArgs();
  const files = {};
  for (const rel of [
    'src/opfs-web-lock-guarded-block-store.mjs',
    'src/block-store-lane-adapter.mjs',
    'tools/storage_lane_web_lock_settled_recovery_probe.mjs',
    'tools/browser_opfs_web_lock_settled_recovery_probe.mjs',
    'docs/40-validation/browser-opfs-web-lock-settled-recovery-slice.md',
    'docs/40-validation/storage-lane-web-lock-settled-recovery-slice.md',
    'test/manifest.json',
    'test/impact-map.json',
    'test/surface-inventory.json',
    'src/types.d.ts',
  ]) {
    files[rel] = await read(rel);
  }

  const manifest = JSON.parse(files['test/manifest.json']);
  const impact = JSON.parse(files['test/impact-map.json']);
  const inventory = JSON.parse(files['test/surface-inventory.json']);
  const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));

  const guardHooks = hasAll(files['src/opfs-web-lock-guarded-block-store.mjs'], [
    'queryLocks(',
    'waitForSettled(',
    'storage:opfs-web-lock-guard-query',
    'storage:opfs-web-lock-guard-settled',
    'storage:opfs-web-lock-guard-still-contended',
  ]);
  const adapterHooks = hasAll(files['src/block-store-lane-adapter.mjs'], [
    'recoverWhenStoreSettled(',
    'block-store-lane:recover-settled',
    'block-store-lane:recover-settled-blocked',
    'store-coordination-still-contended',
    'markHealthy',
  ]);
  const typeHooks = hasAll(files['src/types.d.ts'], [
    'recoverWhenStoreSettled',
    'waitForSettled',
    'queryLocks',
    `revision: '${REVISION}'`,
    `version: '${VERSION}'`,
  ]);
  const releaseProbe = hasAll(files['tools/storage_lane_web_lock_settled_recovery_probe.mjs'], [
    'scheduler:storage-lane-web-lock-settled-recovery-proof',
    'recoverWhenStoreSettled',
    'BRT_WEB_LOCK_TIMEOUT',
    'rejected-lane-unhealthy',
    'store-coordination-still-contended',
  ]);
  const browserProbe = hasAll(files['tools/browser_opfs_web_lock_settled_recovery_probe.mjs'], [
    'browser:opfs-web-lock-settled-recovery-proof',
    'closePageTarget',
    'recoverWhenStoreSettled',
    'lockQueryWhilePending',
    'timeoutPresent',
  ]);
  const browserDoc = hasAll(files['docs/40-validation/browser-opfs-web-lock-settled-recovery-slice.md'].toLowerCase(), [
    'cross-browser',
    'quota',
    'eviction',
    'crash',
    'browser-light',
    'explicit maintenance-driven',
    'no automatic recovery',
  ]);
  const releaseDoc = hasAll(files['docs/40-validation/storage-lane-web-lock-settled-recovery-slice.md'].toLowerCase(), [
    'cross-browser',
    'quota',
    'eviction',
    'crash',
    'browser-light',
    'explicit maintenance-driven',
    'no automatic recovery',
  ]);

  const requiredTasks = [
    'scheduler:storage-lane-web-lock-settled-recovery-proof',
    'browser:opfs-web-lock-settled-recovery-proof',
    TASK_ID,
  ];
  const missingManifestTasks = requiredTasks.filter((id) => !jsonHasTask(manifest, id));
  const missingImpactTasks = requiredTasks.filter((id) => !impactTaskIds.has(id));
  const requiredSurfaces = [
    'surface:browser-opfs-web-lock-settled-recovery',
    'surface:storage-lane-web-lock-settled-recovery',
  ];
  const missingSurfaces = requiredSurfaces.filter((id) => !surfaceIds.has(id));

  const checks = [
    check('guard-settled-hooks', 'Guarded OPFS store exposes query/wait-for-settled lock helpers and trace events.', guardHooks.ok, guardHooks),
    check('adapter-settled-recovery', 'Block-store lane adapter exposes explicit maintenance recovery after guarded store coordination settles.', adapterHooks.ok, adapterHooks),
    check('types-settled-recovery', 'Type surface names the new settled recovery helpers and current revision constants.', typeHooks.ok, typeHooks),
    check('release-probe', 'Browser-light storage-lane settled recovery proof covers timeout, blocked recovery, recovery, and follow-on success.', releaseProbe.ok, releaseProbe),
    check('browser-probe', 'Browser settled recovery proof covers multi-page held lock, page close, recovery, and OPFS verification.', browserProbe.ok, browserProbe),
    check('browser-doc-nonclaims', 'Browser settled recovery slice keeps non-claims visible.', browserDoc.ok, browserDoc),
    check('release-doc-nonclaims', 'Browser-light settled recovery slice keeps non-claims visible.', releaseDoc.ok, releaseDoc),
    check('manifest-tasks', 'Manifest contains settled recovery release, browser, and audit tasks.', missingManifestTasks.length === 0, { missing: missingManifestTasks }),
    check('impact-tasks', 'Impact map routes settled recovery changes to release, browser, and audit tasks.', missingImpactTasks.length === 0, { missing: missingImpactTasks }),
    check('surface-inventory', 'Surface inventory records browser and storage-lane settled recovery surfaces.', missingSurfaces.length === 0, { missing: missingSurfaces }),
  ];
  const status = checks.every((row) => row.status === 'passed') ? 'passed' : 'failed';
  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-web-lock-settled-recovery-contract-audit`,
    task_id: TASK_ID,
    status,
    generatedAt: new Date().toISOString(),
    durationMs: Date.now() - started,
    checks,
    evidence: {
      releaseProofTask: 'scheduler:storage-lane-web-lock-settled-recovery-proof',
      browserProofTask: 'browser:opfs-web-lock-settled-recovery-proof',
      expectedArtifacts: [
        `artifacts/validation/${PREFIX}-STORAGE-LANE-WEB-LOCK-SETTLED-RECOVERY-PROBE.json`,
        `artifacts/validation/${PREFIX}-BROWSER-OPFS-WEB-LOCK-SETTLED-RECOVERY-PROBE.json`,
        `artifacts/audit/${PREFIX}-WEB-LOCK-SETTLED-RECOVERY-CONTRACT-AUDIT.json`,
      ],
    },
    claims: [
      'The cube has runtime hooks and tests for explicit maintenance-driven lane recovery after a guarded Web Lock store reports zero held/pending lock rows.',
    ],
    nonClaims: [
      'No automatic recovery claim.',
      'No cross-browser Web Locks or OPFS behavior claim.',
      'No quota, eviction, crash, durability, fsync, or persistent-storage retention claim.',
      'No fairness, starvation-freedom, mobile/background lifecycle, service-worker lifecycle, or production readiness claim.',
    ],
  };
  if (args.json) {
    await mkdir(dirname(args.json), { recursive: true });
    await writeFile(args.json, `${JSON.stringify(report, null, 2)}\n`);
  }
  if (status !== 'passed') {
    console.error(JSON.stringify(report, null, 2));
    process.exitCode = 1;
  } else {
    console.log(JSON.stringify(report, null, 2));
  }
}

main().catch(async (error) => {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: TASK_ID, status: 'failed', error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, generatedAt: new Date().toISOString() };
  const args = parseArgs();
  if (args.json) {
    await mkdir(dirname(args.json), { recursive: true });
    await writeFile(args.json, `${JSON.stringify(report, null, 2)}\n`);
  }
  console.error(JSON.stringify(report, null, 2));
  process.exit(1);
});
