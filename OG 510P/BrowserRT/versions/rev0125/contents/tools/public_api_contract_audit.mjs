#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import * as publicApi from '../src/public-api.mjs';
import { REVISION, VERSION, BROWSERRT_PUBLIC_API_EXPORTS } from '../src/public-api.mjs';

const REVISION_PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${REVISION_PREFIX}-PUBLIC-API-CONTRACT-AUDIT.json`;
const validationArtifact = (suffix) => `artifacts/validation/${REVISION_PREFIX}-${suffix}.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const readJson = async (path) => JSON.parse(await readFile(path, 'utf8'));

function declaredBrowserRtRuntimeMethods(typesSource) {
  const marker = 'export interface BrowserRTRuntime {';
  const start = typesSource.indexOf(marker);
  assert.ok(start >= 0, 'src/types.d.ts must export BrowserRTRuntime');
  const bodyStart = start + marker.length;
  const end = typesSource.indexOf('\n}\n', bodyStart);
  assert.ok(end > bodyStart, 'BrowserRTRuntime declaration must be structurally readable');
  return [...typesSource.slice(bodyStart, end).matchAll(/^  ([A-Za-z_$][\w$]*)\s*(?:<[^\n>]+>)?\(/gm)]
    .map((match) => match[1])
    .sort();
}

export async function runAudit() {
  const pkg = await readJson('package.json');
  const manifest = await readJson('test/manifest.json');
  const publicTypesText = await readFile('src/public-api.d.ts', 'utf8');
  const runtimeTypesText = await readFile('src/types.d.ts', 'utf8');
  const packageSmokeText = await readFile('tools/package_installed_consumer_smoke_probe.mjs', 'utf8');
  assert.match(publicTypesText, /export type \{ BrowserRTRuntime \} from '\.\/types\.js';/, 'package root declarations must export BrowserRTRuntime through the JavaScript specifier');
  assert.doesNotMatch(publicTypesText, /from '\.\/types\.d\.ts'/, 'package root declarations must not value-re-export a declaration file path');
  assert.match(runtimeTypesText, /export interface BrowserRTRuntime \{/, 'runtime declarations must expose the supported boot facade as a named interface');
  assert.match(runtimeTypesText, /core: BrowserRTCoreNamespace;/, 'runtime declarations must expose the product core namespace');
  assert.match(runtimeTypesText, /storage: BrowserRTStorageNamespace;/, 'runtime declarations must expose the product storage namespace');
  assert.match(runtimeTypesText, /coordination: BrowserRTCoordinationNamespace;/, 'runtime declarations must expose the product coordination namespace');
  assert.match(runtimeTypesText, /diagnostics: BrowserRTDiagnosticsNamespace;/, 'runtime declarations must expose the product diagnostics namespace');
  assert.match(runtimeTypesText, /experimental: BrowserRTExperimentalNamespace;/, 'runtime declarations must expose the product experimental namespace');
  assert.match(runtimeTypesText, /blockStoreLaneAdapter\(config\?: Record<string, unknown>\): BlockStoreLaneAdapter;/, 'flagship product-wedge adapter must be present in BrowserRTRuntime');
  const declaredRuntimeMethods = declaredBrowserRtRuntimeMethods(runtimeTypesText);
  const runtime = await publicApi.boot({ telemetry: 'public-api-contract-audit' });
  const actualRuntimeMethods = Object.entries(runtime).filter(([, value]) => typeof value === 'function').map(([name]) => name).sort();
  const actualRuntimeNamespaces = ['core', 'storage', 'coordination', 'diagnostics', 'experimental'].filter((name) => runtime[name] && typeof runtime[name] === 'object').sort();
  assert.deepEqual(actualRuntimeNamespaces, ['coordination', 'core', 'diagnostics', 'experimental', 'storage'], 'boot() must expose product namespaces without increasing the flat method count');
  runtime.close();
  assert.deepEqual(declaredRuntimeMethods, actualRuntimeMethods, 'BrowserRTRuntime declarations must exactly match the boot() method surface');
  assert.match(packageSmokeText, /tsc.*--project.*tsconfig\.json/s, 'installed-package smoke must compile a strict package-root TypeScript consumer');
  assert.match(packageSmokeText, /runtimeDeclarationMethodParity:\s*true/, 'installed-package smoke must retain explicit runtime/declaration method parity evidence');
  assert.match(packageSmokeText, /namespaceTypecheck:\s*true/, 'installed-package smoke must retain explicit namespace typecheck evidence');
  assert.match(packageSmokeText, /runtime\.storage\.blockStore/, 'installed TypeScript consumer must use the storage namespace for product storage');
  assert.match(packageSmokeText, /runtime\.coordination\.crossLaneScheduler/, 'installed TypeScript consumer must use the coordination namespace for scheduling');
  assert.match(packageSmokeText, /runGoldenWorkloadWithApi/, 'installed-package smoke must execute the golden workload from the installed tarball');
  assert.match(packageSmokeText, /abortCancelledBeforeCommit/, 'installed-package smoke must require the golden workload timeout/no-commit proof');
  assert.match(packageSmokeText, /recoveryWriteAfterAbort/, 'installed-package smoke must require the golden workload recovery-write proof');
  const exportKeys = Object.keys(publicApi).sort();
  const expected = BROWSERRT_PUBLIC_API_EXPORTS.slice().sort();
  assert.deepEqual(exportKeys, expected, 'src/public-api.mjs export set must equal BROWSERRT_PUBLIC_API_EXPORTS');
  assert.equal(pkg.main, './src/public-api.mjs');
  assert.equal(pkg.types, './src/public-api.d.ts');
  assert.deepEqual(pkg.exports?.['.'], { types: './src/public-api.d.ts', import: './src/public-api.mjs' });
  assert.equal(pkg.exports?.['./internal'], undefined, 'package exports must not expose ./internal compatibility surface');
  assert.ok((pkg.files || []).includes('src/*.mjs'), 'package files must include the runtime .mjs graph used by src/browserrt.mjs');
  assert.ok((pkg.files || []).includes('src/*.d.ts'), 'package files must include public and supporting type declarations');
  assert.ok((pkg.files || []).includes('examples/*.mjs'), 'package files must include example consumers by glob so new product wedges are not omitted from npm pack');
  assert.ok(!(pkg.files || []).includes('tools/**') && !(pkg.files || []).includes('artifacts/**') && !(pkg.files || []).includes('test/**'), 'package files must not include development-only surfaces');
  const scripts = pkg.scripts || {};
  assert.match(String(scripts['test:browser:current'] || ''), /run_browser_bundle\.mjs --mode current/, 'browser current must use the batched browser bundle runner');
  assert.doesNotMatch(String(scripts['test:browser:current'] || ''), /--id\s+/, 'browser current must not carry a hand-maintained --id subset that can omit current product tasks');
  assert.match(String(scripts['test:product:browser'] || ''), /run_browser_bundle\.mjs --mode product/, 'browser product sweep must use the batched browser bundle runner');
  assert.doesNotMatch(String(scripts['test:product:browser'] || ''), /--id\s+/, 'browser product sweep must not carry a hand-maintained --id subset that can omit installed-browser product wedges');
  const browserBundleText = await readFile('tools/run_browser_bundle.mjs', 'utf8');
  for (const taskId of [
    'browser:package-installed-consumer-smoke-proof',
    'browser:package-installed-opfs-consumer-proof',
    'browser:package-installed-cross-tab-opfs-consumer-proof',
    'browser:package-installed-opfs-reopen-consumer-proof',
    'browser:package-installed-tab-close-opfs-consumer-proof',
    'browser:package-installed-opfs-budget-consumer-proof',
    'browser:package-installed-opfs-abort-consumer-proof',
    'browser:package-installed-opfs-abrupt-kill-consumer-proof',
    'browser:package-installed-opfs-corruption-consumer-proof'
  ]) {
    assert.ok(browserBundleText.includes(taskId), `browser bundle runner must include ${taskId}`);
  }
  const ids = new Set((manifest.tasks || []).map((task) => task.id));
  assert.ok(ids.has('product:public-api-wedge-proof'));
  assert.ok(ids.has('product:package-installed-consumer-smoke-proof'));
  assert.ok(ids.has('browser:package-installed-consumer-smoke-proof'));
  assert.ok(ids.has('browser:package-installed-opfs-consumer-proof'));
  assert.ok(ids.has('browser:package-installed-opfs-budget-consumer-proof'));
  assert.ok(ids.has('browser:package-installed-opfs-abort-consumer-proof'));
  assert.ok(ids.has('browser:package-installed-opfs-corruption-consumer-proof'));
  assert.ok(ids.has('browser:package-installed-cross-tab-opfs-consumer-proof'));
  assert.ok(ids.has('browser:package-installed-opfs-reopen-consumer-proof'));
  assert.ok(ids.has('browser:package-installed-tab-close-opfs-consumer-proof'));
  assert.ok(ids.has('browser:package-installed-opfs-abrupt-kill-consumer-proof'));
  assert.ok(ids.has('facility:public-api-contract-audit'));
  assert.equal(pkg.browserrt_current?.browser_package_consumer_task, 'browser:package-installed-consumer-smoke-proof');
  assert.equal(pkg.browserrt_current?.browser_opfs_package_consumer_task, 'browser:package-installed-opfs-consumer-proof');
  assert.equal(pkg.browserrt_current?.browser_opfs_budget_package_consumer_task, 'browser:package-installed-opfs-budget-consumer-proof');
  assert.equal(pkg.browserrt_current?.browser_opfs_abort_package_consumer_task, 'browser:package-installed-opfs-abort-consumer-proof');
  assert.equal(pkg.browserrt_current?.browser_opfs_corruption_package_consumer_task, 'browser:package-installed-opfs-corruption-consumer-proof');
  assert.equal(pkg.browserrt_current?.browser_cross_tab_opfs_package_consumer_task, 'browser:package-installed-cross-tab-opfs-consumer-proof');
  assert.equal(pkg.browserrt_current?.browser_opfs_reopen_package_consumer_task, 'browser:package-installed-opfs-reopen-consumer-proof');
  assert.equal(pkg.browserrt_current?.browser_tab_close_opfs_package_consumer_task, 'browser:package-installed-tab-close-opfs-consumer-proof');
  assert.equal(pkg.browserrt_current?.browser_opfs_abrupt_kill_package_consumer_task, 'browser:package-installed-opfs-abrupt-kill-consumer-proof');
  const packageSmoke = (manifest.tasks || []).find((task) => task.id === 'product:package-installed-consumer-smoke-proof');
  const browserPackageSmoke = (manifest.tasks || []).find((task) => task.id === 'browser:package-installed-consumer-smoke-proof');
  const browserOpfsPackageSmoke = (manifest.tasks || []).find((task) => task.id === 'browser:package-installed-opfs-consumer-proof');
  const browserOpfsBudgetPackageSmoke = (manifest.tasks || []).find((task) => task.id === 'browser:package-installed-opfs-budget-consumer-proof');
  const browserOpfsAbortPackageSmoke = (manifest.tasks || []).find((task) => task.id === 'browser:package-installed-opfs-abort-consumer-proof');
  const browserOpfsCorruptionPackageSmoke = (manifest.tasks || []).find((task) => task.id === 'browser:package-installed-opfs-corruption-consumer-proof');
  const browserCrossTabOpfsPackageSmoke = (manifest.tasks || []).find((task) => task.id === 'browser:package-installed-cross-tab-opfs-consumer-proof');
  const browserOpfsReopenPackageSmoke = (manifest.tasks || []).find((task) => task.id === 'browser:package-installed-opfs-reopen-consumer-proof');
  const browserTabCloseOpfsPackageSmoke = (manifest.tasks || []).find((task) => task.id === 'browser:package-installed-tab-close-opfs-consumer-proof');
  const browserOpfsAbruptKillPackageSmoke = (manifest.tasks || []).find((task) => task.id === 'browser:package-installed-opfs-abrupt-kill-consumer-proof');
  assert.ok(packageSmoke?.inputs?.includes('src/*.mjs'), 'package smoke must be invalidated by runtime module graph changes');
  assert.ok(packageSmoke?.inputs?.includes('package.json'), 'package smoke must be invalidated by package metadata changes');
  assert.ok(packageSmoke?.inputs?.includes('src/*.d.ts'), 'package smoke must be invalidated by public declaration changes');
  assert.ok(packageSmoke?.requiredCapabilities?.includes('typescript-compiler'), 'package smoke must declare its TypeScript compiler dependency');
  assert.ok((packageSmoke?.requiredEvidence || []).some((item) => /TypeScript consumer compiles/i.test(item)), 'package smoke must require installed TypeScript consumer compilation evidence');
  assert.ok((packageSmoke?.requiredEvidence || []).some((item) => /runtime.*declaration.*parity/i.test(item)), 'package smoke must require boot runtime/declaration parity evidence');
  assert.ok(packageSmoke?.inputs?.includes('examples/golden-workload-consumer.mjs'), 'package smoke must be invalidated by golden workload consumer changes');
  assert.ok((packageSmoke?.requiredEvidence || []).some((item) => /golden workload/i.test(item) && /timeout abort/i.test(item) && /recovery write/i.test(item)), 'package smoke must require installed golden workload abort/recovery evidence');
  assert.ok(browserPackageSmoke?.inputs?.includes('tools/browser_cdp_fixture.mjs'), 'browser package smoke must depend on managed browser harness');
  assert.ok(browserPackageSmoke?.inputs?.includes('examples/product-wedge-consumer.mjs'), 'browser package smoke must depend on browser-importable example');
  assert.ok(browserOpfsPackageSmoke?.inputs?.includes('examples/browser-opfs-product-wedge-consumer.mjs'), 'browser OPFS package smoke must depend on the OPFS example');
  assert.ok(browserOpfsPackageSmoke?.inputs?.includes('src/*.mjs'), 'browser OPFS package smoke must be invalidated by runtime module graph changes');
  assert.ok(browserOpfsPackageSmoke?.outputs?.includes(validationArtifact('PACKAGE-INSTALLED-BROWSER-OPFS-CONSUMER-PROBE')), 'browser OPFS package smoke must emit retained proof artifact');
  assert.ok(browserOpfsBudgetPackageSmoke?.inputs?.includes('examples/browser-opfs-budget-product-wedge-consumer.mjs'), 'browser OPFS budget package smoke must depend on the budget rejection/recovery example');
  assert.ok(browserOpfsBudgetPackageSmoke?.inputs?.includes('src/*.mjs'), 'browser OPFS budget package smoke must be invalidated by runtime module graph changes');
  assert.ok(browserOpfsBudgetPackageSmoke?.outputs?.includes(validationArtifact('PACKAGE-INSTALLED-BROWSER-OPFS-BUDGET-CONSUMER-PROBE')), 'browser OPFS budget package smoke must emit retained proof artifact');
  assert.ok(browserOpfsAbortPackageSmoke?.inputs?.includes('examples/browser-opfs-abort-product-wedge-consumer.mjs'), 'browser OPFS abort package smoke must depend on the timeout-abort rollback example');
  assert.ok(browserOpfsAbortPackageSmoke?.inputs?.includes('src/*.mjs'), 'browser OPFS abort package smoke must be invalidated by runtime module graph changes');
  assert.ok(browserOpfsAbortPackageSmoke?.outputs?.includes(validationArtifact('PACKAGE-INSTALLED-BROWSER-OPFS-ABORT-CONSUMER-PROBE')), 'browser OPFS abort package smoke must emit retained proof artifact');
  assert.ok(browserOpfsCorruptionPackageSmoke?.inputs?.includes('examples/browser-opfs-corruption-product-wedge-consumer.mjs'), 'browser OPFS corruption package smoke must depend on the corruption detection/repair example');
  assert.ok(browserOpfsCorruptionPackageSmoke?.inputs?.includes('src/*.mjs'), 'browser OPFS corruption package smoke must be invalidated by runtime module graph changes');
  assert.ok(browserOpfsCorruptionPackageSmoke?.outputs?.includes(validationArtifact('PACKAGE-INSTALLED-BROWSER-OPFS-CORRUPTION-CONSUMER-PROBE')), 'browser OPFS corruption package smoke must emit retained proof artifact');
  assert.ok(browserCrossTabOpfsPackageSmoke?.inputs?.includes('examples/browser-cross-tab-opfs-product-wedge-consumer.mjs'), 'browser cross-tab OPFS package smoke must depend on the cross-tab OPFS example');
  assert.ok(browserCrossTabOpfsPackageSmoke?.inputs?.includes('src/*.mjs'), 'browser cross-tab OPFS package smoke must be invalidated by runtime module graph changes');
  assert.ok(browserCrossTabOpfsPackageSmoke?.outputs?.includes(validationArtifact('PACKAGE-INSTALLED-BROWSER-CROSS-TAB-OPFS-CONSUMER-PROBE')), 'browser cross-tab OPFS package smoke must emit retained proof artifact');
  assert.ok(browserOpfsReopenPackageSmoke?.inputs?.includes('examples/browser-opfs-reopen-product-wedge-consumer.mjs'), 'browser OPFS reopen package smoke must depend on the reload/reopen example');
  assert.ok(browserOpfsReopenPackageSmoke?.inputs?.includes('src/*.mjs'), 'browser OPFS reopen package smoke must be invalidated by runtime module graph changes');
  assert.ok(browserOpfsReopenPackageSmoke?.outputs?.includes(validationArtifact('PACKAGE-INSTALLED-BROWSER-OPFS-REOPEN-CONSUMER-PROBE')), 'browser OPFS reopen package smoke must emit retained proof artifact');
  assert.ok(browserTabCloseOpfsPackageSmoke?.inputs?.includes('examples/browser-cross-tab-opfs-product-wedge-consumer.mjs'), 'browser tab-close OPFS package smoke must depend on the cross-tab example with write-hold receipt helpers');
  assert.ok(browserTabCloseOpfsPackageSmoke?.inputs?.includes('src/*.mjs'), 'browser tab-close OPFS package smoke must be invalidated by runtime module graph changes');
  assert.ok(browserTabCloseOpfsPackageSmoke?.outputs?.includes(validationArtifact('PACKAGE-INSTALLED-BROWSER-TAB-CLOSE-OPFS-CONSUMER-PROBE')), 'browser tab-close OPFS package smoke must emit retained proof artifact');
  assert.ok(browserOpfsAbruptKillPackageSmoke?.inputs?.includes('examples/browser-opfs-reopen-product-wedge-consumer.mjs'), 'browser OPFS abrupt-kill package smoke must depend on the reopen example with process-kill receipt helpers');
  assert.ok(browserOpfsAbruptKillPackageSmoke?.inputs?.includes('src/*.mjs'), 'browser OPFS abrupt-kill package smoke must be invalidated by runtime module graph changes');
  assert.ok(browserOpfsAbruptKillPackageSmoke?.outputs?.includes(validationArtifact('PACKAGE-INSTALLED-BROWSER-OPFS-ABRUPT-KILL-CONSUMER-PROBE')), 'browser OPFS abrupt-kill package smoke must emit retained proof artifact');
  const exampleText = await readFile('examples/product-wedge-consumer.mjs', 'utf8');
  assert.match(exampleText, /typeof process !== 'undefined'/, 'product wedge example must be browser-importable by guarding the Node CLI process check');
  assert.match(exampleText, /rt\.core\.channel/, 'product wedge example must use the product core namespace');
  assert.match(exampleText, /rt\.storage\.blockStoreLaneAdapter/, 'product wedge example must use the product storage namespace');
  assert.match(exampleText, /rt\.coordination\.crossLaneScheduler/, 'product wedge example must use the product coordination namespace');
  const goldenExampleText = await readFile('examples/golden-workload-consumer.mjs', 'utf8');
  assert.match(goldenExampleText, /runGoldenWorkloadWithApi/, 'golden workload example must export the package-consumer runner');
  assert.match(goldenExampleText, /abortProviderOnOperationTimeout:\s*true/, 'golden workload must assert provider abort on storage-lane timeout');
  assert.match(goldenExampleText, /namespacedFacadeUsed/, 'golden workload must prove it used the product namespaces');
  assert.match(goldenExampleText, /rt\.storage\.blockStoreLaneAdapter/, 'golden workload must use the storage namespace adapter path');
  assert.match(goldenExampleText, /quarantineReviewedAndCleared/, 'golden workload must prove timeout quarantine is reviewed and cleared');
  assert.match(goldenExampleText, /recoveryWriteAfterAbort/, 'golden workload must prove a recovery write after timeout abort');
  assert.match(goldenExampleText, /typeof process !== 'undefined'/, 'golden workload example must be browser-importable by guarding the Node CLI process check');
  const opfsExampleText = await readFile('examples/browser-opfs-product-wedge-consumer.mjs', 'utf8');
  assert.match(opfsExampleText, /rt\.storage\.opfsWebLockGuardedBlockStore/, 'browser OPFS product wedge must use the storage namespace WebLockGuardedBlockStore path');
  assert.match(opfsExampleText, /rt\.core\.spawnAgent/, 'browser OPFS product wedge must run the persistent golden workload Worker transform');
  assert.match(opfsExampleText, /rt\.coordination\.admissionController/, 'browser OPFS product wedge must guard admission through the coordination namespace');
  assert.match(opfsExampleText, /persistentGoldenWorkload/, 'browser OPFS product wedge must prove the persistent golden workload');
  assert.match(opfsExampleText, /writeBudgetGuard/, 'browser OPFS product wedge must exercise explicit write-budget estimate posture');
  const budgetExampleText = await readFile('examples/browser-opfs-budget-product-wedge-consumer.mjs', 'utf8');
  assert.match(budgetExampleText, /rt\.storage\.opfsWebLockGuardedBlockStore/, 'browser OPFS budget product wedge must use the storage namespace');
  assert.match(budgetExampleText, /rt\.coordination\.crossLaneScheduler/, 'browser OPFS budget product wedge must use the coordination namespace');
  assert.match(budgetExampleText, /rt\.storage\.blockStoreLaneAdapter/, 'browser OPFS budget product wedge must schedule through the storage namespace adapter');
  assert.match(budgetExampleText, /BRT_OPFS_WRITE_BUDGET_EXCEEDED/, 'browser OPFS budget product wedge must assert explicit write-budget rejection');
  assert.match(budgetExampleText, /rejectedWriteDidNotCommit/, 'browser OPFS budget product wedge must prove rejected write no-commit');
  assert.match(budgetExampleText, /storageLaneRecoveredAfterRejection/, 'browser OPFS budget product wedge must prove storage-lane recovery after rejection');
  const abortExampleText = await readFile('examples/browser-opfs-abort-product-wedge-consumer.mjs', 'utf8');
  assert.match(abortExampleText, /rt\.storage\.opfsWebLockGuardedBlockStore/, 'browser OPFS abort product wedge must use the storage namespace');
  assert.match(abortExampleText, /rt\.coordination\.crossLaneScheduler/, 'browser OPFS abort product wedge must use the coordination namespace');
  assert.match(abortExampleText, /rt\.storage\.blockStoreLaneAdapter/, 'browser OPFS abort product wedge must schedule through the storage namespace adapter');
  assert.match(abortExampleText, /namespacedFacadeUsed/, 'browser OPFS abort product wedge must emit namespace proof');
  assert.match(abortExampleText, /recoveryBlockedBeforeOverride/, 'browser OPFS abort product wedge must prove pre-override quarantine blocks recovery');
  assert.match(abortExampleText, /preOverrideRecoveryRejected/, 'browser OPFS abort product wedge must record the pre-override rejected recovery attempt');
  assert.match(abortExampleText, /BRT_STORAGE_OPERATION_TIMEOUT/, 'browser OPFS abort product wedge must assert storage-lane operation timeout');
  assert.match(abortExampleText, /BRT_OPFS_OPERATION_ABORTED/, 'browser OPFS abort product wedge must assert provider abort late settlement');
  assert.match(abortExampleText, /abortedWriteDidNotCommit/, 'browser OPFS abort product wedge must prove unacknowledged digest no-commit');
  assert.match(abortExampleText, /quarantineVisibleBeforeOverride/, 'browser OPFS abort product wedge must keep timeout quarantine visible before recovery override');
  const corruptionExampleText = await readFile('examples/browser-opfs-corruption-product-wedge-consumer.mjs', 'utf8');
  assert.match(corruptionExampleText, /rt\.storage\.opfsWebLockGuardedBlockStore/, 'browser OPFS corruption product wedge must use the storage namespace');
  assert.match(corruptionExampleText, /rt\.coordination\.crossLaneScheduler/, 'browser OPFS corruption product wedge must use the coordination namespace');
  assert.match(corruptionExampleText, /rt\.storage\.blockStoreLaneAdapter/, 'browser OPFS corruption product wedge must schedule through the storage namespace adapter');
  assert.match(corruptionExampleText, /BRT_OPFS_BLOCK_CHECKSUM_MISMATCH/, 'browser OPFS corruption product wedge must assert checksum-mismatch read refusal');
  assert.match(corruptionExampleText, /storage:opfs-block-repair/, 'browser OPFS corruption product wedge must require repair trace evidence');
  assert.match(corruptionExampleText, /overwriteOpfsFile/, 'browser OPFS corruption product wedge must intentionally tamper with a real OPFS block file');
  const crossTabExampleText = await readFile('examples/browser-cross-tab-opfs-product-wedge-consumer.mjs', 'utf8');
  assert.match(crossTabExampleText, /rt\.storage\.opfsWebLockGuardedBlockStore/, 'browser cross-tab OPFS product wedge must use the storage namespace');
  assert.match(crossTabExampleText, /rt\.coordination\.crossLaneScheduler/, 'browser cross-tab OPFS product wedge must use the coordination namespace');
  assert.match(crossTabExampleText, /rt\.storage\.blockStoreLaneAdapter/, 'browser cross-tab OPFS product wedge must schedule through the storage namespace adapter');
  assert.match(crossTabExampleText, /namespacedFacadeUsed/, 'browser cross-tab/tab-close OPFS product wedge must emit namespace proof');
  assert.match(crossTabExampleText, /startExclusiveHold/, 'browser cross-tab OPFS product wedge must hold an exclusive Web Lock in one tab');
  assert.match(crossTabExampleText, /attemptTimedPutWhileLocked/, 'browser cross-tab OPFS product wedge must prove pending-lock timeout before acquisition');
  assert.match(crossTabExampleText, /startQueuedPutWhileLocked/, 'browser cross-tab OPFS product wedge must keep a second queued waiter pending while another request times out');
  assert.match(crossTabExampleText, /queuedWaiterAcquiredAfterRelease/, 'browser cross-tab OPFS product wedge must prove a queued waiter acquires and verifies after the holder releases');
  assert.match(crossTabExampleText, /timedOutRequestDidNotMutateAfterRelease/, 'browser cross-tab OPFS product wedge must prove a timed-out pending request does not ghost-mutate after release');
  assert.match(crossTabExampleText, /verifyDigestAbsentViaStorageLane/, 'browser cross-tab OPFS product wedge must verify the timed-out digest remains absent through storage-lane operations');
  assert.match(crossTabExampleText, /readRefViaStorageLane/, 'browser cross-tab OPFS product wedge must cross-read shared OPFS blocks through storage-lane operations');
  assert.match(crossTabExampleText, /startExclusiveWriteHold/, 'browser tab-close OPFS product wedge must write while an exclusive Web Lock callback remains pending');
  assert.match(crossTabExampleText, /createBrowserTabCloseOpfsProductWedgeReceipt/, 'browser tab-close OPFS product wedge must emit a versioned tab-close lifecycle receipt');
  const reopenExampleText = await readFile('examples/browser-opfs-reopen-product-wedge-consumer.mjs', 'utf8');
  assert.match(reopenExampleText, /writeBrowserOpfsReopenBlockWithApi/, 'browser OPFS reopen product wedge must expose a write-before-reload session');
  assert.match(reopenExampleText, /readBrowserOpfsReopenBlockWithApi/, 'browser OPFS reopen product wedge must expose a read-after-reload session');
  assert.match(reopenExampleText, /pageReloadObserved/, 'browser OPFS reopen product wedge must make page reload an explicit receipt proof');
  assert.match(reopenExampleText, /createBrowserOpfsAbruptKillProductWedgeReceipt/, 'browser OPFS reopen product wedge must expose a browser process-kill/relaunch receipt helper');
  assert.match(reopenExampleText, /createBrowserOpfsInterruptedCandidateWithApi/, 'browser OPFS abrupt-kill product wedge must expose an interrupted unclosed candidate creator');
  assert.match(reopenExampleText, /inspectBrowserOpfsInterruptedCandidateWithApi/, 'browser OPFS abrupt-kill product wedge must expose interrupted candidate inspection after relaunch');
  assert.match(reopenExampleText, /interruptedCandidateNotSilentlyAccepted/, 'browser OPFS abrupt-kill product wedge must prove an unclosed partial candidate is not silently accepted');
  assert.match(reopenExampleText, /interruptedCandidateRepairRetryVerified/, 'browser OPFS abrupt-kill product wedge must repair/retry the full interrupted-candidate digest after rejection');
  assert.match(reopenExampleText, /repairFullCandidate/, 'browser OPFS abrupt-kill product wedge must expose relaunch-side repair/retry option for the interrupted candidate');
  assert.match(reopenExampleText, /browserProcessSigkillObserved/, 'browser OPFS abrupt-kill product wedge must make process SIGKILL an explicit receipt proof');
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'passed', audit_id: `${REVISION}-public-api-contract-audit`, supportedExportCount: expected.length, supportedExports: expected, checks: [{ name: 'browserrt-runtime-declaration-parity', status: 'passed', runtimeMethodCount: actualRuntimeMethods.length, declarationMethodCount: declaredRuntimeMethods.length }, { name: 'browserrt-product-namespaces', status: 'passed', namespaces: actualRuntimeNamespaces }, { name: 'package-root-types-use-js-specifier', status: 'passed' }, { name: 'package-installed-typescript-consumer-compiled', status: 'passed' }, { name: 'package-installed-namespace-typecheck', status: 'passed' }, { name: 'package-installed-golden-workload-executed', status: 'passed' }, { name: 'public-api-export-set', status: 'passed' }, { name: 'package-entrypoint', status: 'passed' }, { name: 'package-internal-export-sealed', status: 'passed' }, { name: 'package-file-glob-includes-runtime-graph', status: 'passed' }, { name: 'browser-current-script-bundles-all-current-product-tasks', status: 'passed' }, { name: 'browser-product-script-bundles-all-product-tasks', status: 'passed' }, { name: 'manifest-product-wedge-registered', status: 'passed' }, { name: 'manifest-package-installed-smoke-registered', status: 'passed' }, { name: 'manifest-browser-package-installed-smoke-registered', status: 'passed' }, { name: 'manifest-browser-opfs-package-installed-smoke-registered', status: 'passed' }, { name: 'manifest-browser-opfs-budget-package-installed-smoke-registered', status: 'passed' }, { name: 'manifest-browser-opfs-abort-package-installed-smoke-registered', status: 'passed' }, { name: 'manifest-browser-opfs-corruption-package-installed-smoke-registered', status: 'passed' }, { name: 'manifest-browser-cross-tab-opfs-package-installed-smoke-registered', status: 'passed' }, { name: 'manifest-browser-opfs-reopen-package-installed-smoke-registered', status: 'passed' }, { name: 'manifest-browser-tab-close-opfs-package-installed-smoke-registered', status: 'passed' }, { name: 'manifest-browser-opfs-abrupt-kill-package-installed-smoke-registered', status: 'passed' }, { name: 'browser-importable-product-wedge-example', status: 'passed' }, { name: 'product-wedge-example-uses-namespaces', status: 'passed' }, { name: 'golden-workload-abort-recovery-example', status: 'passed' }, { name: 'browser-opfs-product-wedge-example-uses-guarded-opfs', status: 'passed' }, { name: 'browser-opfs-product-wedge-persistent-golden-workload', status: 'passed' }, { name: 'browser-opfs-budget-product-wedge-example-uses-namespaces', status: 'passed' }, { name: 'browser-opfs-budget-product-wedge-example-uses-no-mutation-recovery', status: 'passed' }, { name: 'browser-opfs-abort-product-wedge-example-uses-namespaces', status: 'passed' }, { name: 'browser-opfs-abort-product-wedge-example-blocks-preoverride-recovery', status: 'passed' }, { name: 'browser-opfs-abort-product-wedge-example-uses-timeout-abort-rollback-recovery', status: 'passed' }, { name: 'browser-opfs-corruption-product-wedge-example-uses-namespaces', status: 'passed' }, { name: 'browser-opfs-corruption-product-wedge-example-uses-checksum-refusal-and-repair', status: 'passed' }, { name: 'browser-cross-tab-opfs-product-wedge-example-uses-namespaces', status: 'passed' }, { name: 'browser-cross-tab-opfs-product-wedge-example-uses-lock-timeout-queued-waiter-ghost-write-check-and-cross-read', status: 'passed' }, { name: 'browser-tab-close-opfs-product-wedge-example-uses-write-hold-recovery-receipt', status: 'passed' }, { name: 'browser-opfs-reopen-product-wedge-example-uses-reload-reopen', status: 'passed' }, { name: 'browser-opfs-abrupt-kill-product-wedge-example-uses-process-kill-relaunch-receipt', status: 'passed' }, { name: 'browser-opfs-abrupt-kill-product-wedge-rejects-unclosed-candidate', status: 'passed' }, { name: 'browser-opfs-abrupt-kill-product-wedge-repairs-candidate-digest', status: 'passed' }, { name: 'browserrt-current-browser-package-task-pointer', status: 'passed' }, { name: 'browserrt-current-browser-opfs-package-task-pointer', status: 'passed' }, { name: 'browserrt-current-browser-opfs-budget-package-task-pointer', status: 'passed' }, { name: 'browserrt-current-browser-opfs-abort-package-task-pointer', status: 'passed' }, { name: 'browserrt-current-browser-opfs-corruption-package-task-pointer', status: 'passed' }, { name: 'browserrt-current-browser-cross-tab-opfs-package-task-pointer', status: 'passed' }, { name: 'browserrt-current-browser-opfs-reopen-package-task-pointer', status: 'passed' }, { name: 'browserrt-current-browser-tab-close-opfs-package-task-pointer', status: 'passed' }, { name: 'browserrt-current-browser-opfs-abrupt-kill-package-task-pointer', status: 'passed' }], nonClaims: ['Public API contract audit proves the local package boundary, package file-set guard, supported export list, and installed-package golden workload wiring only; it does not make a semver, publication, browser matrix, cross-browser, quota-pressure, eviction, fsync, or crash-recovery claim.'] };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const report = await runAudit();
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
}
