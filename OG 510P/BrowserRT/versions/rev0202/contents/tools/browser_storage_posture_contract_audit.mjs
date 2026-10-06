#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import * as publicApi from '../src/public-api.mjs';
import { REVISION, VERSION, BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT, BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT } from '../src/public-api.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-BROWSER-STORAGE-POSTURE-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }

export async function runAudit() {
  const pkg = await json('package.json');
  const manifest = await json('test/manifest.json');
  const source = await text('src/browser-storage-posture.mjs');
  const recoveryGuidance = await text('src/browser-storage-recovery-guidance.mjs');
  const runtime = await text('src/browserrt.mjs');
  const types = await text('src/types.d.ts');
  const publicDts = await text('src/public-api.d.ts');
  const publicMjs = await text('src/public-api.mjs');
  const productWedge = await text('src/product-wedge.mjs');
  const packageSmoke = await text('tools/package_installed_consumer_smoke_probe.mjs');
  const abortProductWedge = await text('examples/browser-opfs-abort-product-wedge-consumer.mjs');
  const abortProductWedgeProbe = await text('tools/package_installed_browser_abort_opfs_consumer_probe.mjs');
  const budgetProductWedge = await text('examples/browser-opfs-budget-product-wedge-consumer.mjs');
  const budgetProductWedgeProbe = await text('tools/package_installed_browser_budget_opfs_consumer_probe.mjs');
  const corruptionProductWedge = await text('examples/browser-opfs-corruption-product-wedge-consumer.mjs');
  const corruptionProductWedgeProbe = await text('tools/package_installed_browser_corruption_opfs_consumer_probe.mjs');
  const crossTabProductWedge = await text('examples/browser-cross-tab-opfs-product-wedge-consumer.mjs');
  const crossTabProductWedgeProbe = await text('tools/package_installed_browser_cross_tab_opfs_consumer_probe.mjs');
  const tabCloseProductWedgeProbe = await text('tools/package_installed_browser_tab_close_opfs_consumer_probe.mjs');
  const reopenProductWedge = await text('examples/browser-opfs-reopen-product-wedge-consumer.mjs');
  const reopenProductWedgeProbe = await text('tools/package_installed_browser_reopen_opfs_consumer_probe.mjs');
  const abruptKillProductWedgeProbe = await text('tools/package_installed_browser_abrupt_kill_opfs_consumer_probe.mjs');

  assert.equal(BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT, 'browserrt.browser-storage-posture.v1');
  assert.equal(BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT, 'browserrt.browser-storage-recovery-guidance.v1');
  assert.equal(typeof publicApi.diagnoseBrowserStoragePosture, 'function', 'public API must export diagnoseBrowserStoragePosture');
  assert.equal(typeof publicApi.createBrowserStorageRecoveryGuidance, 'function', 'public API must export createBrowserStorageRecoveryGuidance');
  assert.ok(recoveryGuidance.includes('BRT_WEB_LOCK_TIMEOUT') && recoveryGuidance.includes('BRT_OPFS_WRITE_BUDGET_EXCEEDED') && recoveryGuidance.includes('BRT_BROWSER_STORAGE_ADMISSION_REJECTED') && recoveryGuidance.includes('BRT_SW_WAITUNTIL_LATE_FAILURE'), 'recovery guidance must classify lock timeout, write-budget, posture-admission, and Service Worker waitUntil late failures');
  assert.ok(recoveryGuidance.includes('BRT_BROWSER_WEB_LOCK_UNBOUNDED_TIMEOUT_REJECTED') && recoveryGuidance.includes('BRT_OPFS_WEB_LOCK_TIMEOUT_OVERRIDE_REJECTED') && recoveryGuidance.includes('posture-lock-policy'), 'recovery guidance must classify postured Web-Lock unbounded-timeout policy rejections');
  assert.ok(recoveryGuidance.includes('BRT_BROWSER_WEB_LOCK_SINGLE_OWNER_FALLBACK_REJECTED') && recoveryGuidance.includes('coordination-fallback-policy') && recoveryGuidance.includes('allowUnsafeSingleOwnerFallback'), 'recovery guidance must classify postured unlocked single-owner fallback policy rejections');
  assert.ok(recoveryGuidance.includes('preMutationRejected') && recoveryGuidance.includes('shouldQueryLocks') && recoveryGuidance.includes('shouldRefreshStoragePosture') && recoveryGuidance.includes('serviceWorkerSettlementRequired'), 'recovery guidance must expose actionable retry/inspection hints, including Service Worker settlement requirement');
  assert.ok(source.includes('StorageManager.estimate()'), 'diagnostic must explicitly observe StorageManager.estimate()');
  assert.ok(source.includes('StorageManager.persisted()'), 'diagnostic must explicitly observe StorageManager.persisted()');
  assert.ok(source.includes('requestPersistentStorage === true'), 'persist() must be gated behind explicit requestPersistentStorage === true');
  assert.ok(source.includes('best-effort-storage'), 'best-effort storage warning must be part of the product diagnostic');
  assert.ok(source.includes('BROWSERRT_BROWSER_STORAGE_ADMISSION_POLICY_FORMAT'), 'diagnostic must define a storage admission policy format');
  assert.ok(source.includes('buildBrowserStorageAdmissionPolicy'), 'diagnostic must derive an actionable admission policy from quota posture');
  assert.ok(source.includes('writeBudgetGuard') && source.includes('quota-posture-derived-preflight'), 'diagnostic must expose a writeBudgetGuard that can be fed to OPFS before mutation');
  assert.ok(source.includes('plannedWriteBytes') && source.includes('plannedBudgetedBytes') && source.includes('transientWriteMultiplier') && source.includes('plannedWriteFits') && source.includes('reject-planned-write-over-budget') && source.includes('storage-admission-planned-write-over-budget'), 'diagnostic must let callers preflight an expected write batch before OPFS store creation');
  assert.ok(source.includes('storagePrivacyPolicy') && source.includes('storage-timing-side-channel-review') && source.includes('noStorageTimingMitigationClaim'), 'diagnostic must surface advisory OPFS storage-timing privacy review without claiming mitigation');
  assert.ok(types.includes('plannedWriteBytes: number | null') && types.includes('plannedBudgetedBytes: number | null') && types.includes('transientWriteMultiplier: number') && types.includes('plannedWriteFits: boolean | null') && types.includes('storagePrivacyPolicy: Readonly<Record<string, unknown>>'), 'public types must surface planned-write admission and storage privacy posture fields');
  assert.ok(source.includes('browserrt.browser-storage-posture-receipt.v1') && source.includes('opfsPostureReceipt') && source.includes('internalByteLedger') && source.includes('lastMutationReceipt'), 'diagnostic must expose an OPFS posture receipt with quota estimate, internal byte ledger, and last mutation receipt fields');
  assert.ok(source.includes('noQuotaReservationClaim') && source.includes('noEvictionSurvivalClaim') && source.includes('noPrivacySideChannelClaim'), 'OPFS posture receipt must carry quota, eviction, and privacy non-claims');
  const opfsBlockStore = await text('src/opfs-block-store.mjs');
  assert.ok(opfsBlockStore.includes('policySource') && types.includes('policySource?: string | null'), 'OPFS write-budget normalization must preserve posture policy provenance through constructor/per-put normalization');
  assert.ok(opfsBlockStore.includes('allowWriteBudgetGuardOverride') && opfsBlockStore.includes('BRT_OPFS_WRITE_BUDGET_OVERRIDE_REJECTED') && opfsBlockStore.includes('store-disallows-weaker-per-put-write-budget-override'), 'OPFS block store must support rejecting weaker per-put write-budget overrides for postured factory instances');
  assert.ok(source.includes('opfsAsyncBlockStoreWithPosture'), 'diagnostic guidance must point callers to the postured OPFS factory');
  assert.ok(source.includes('opfsWebLockGuardedBlockStoreWithPosture'), 'diagnostic guidance must prefer the postured Web-Lock-guarded OPFS factory for shared browser-local state');
  assert.ok(source.includes('bounded default lock-acquisition wait') && source.includes('bounded acquisition'), 'diagnostic guidance must make Web Lock acquisition bounds visible for shared browser-local state');
  assert.ok(source.includes('storage-admission-rejecting-new-writes') && source.includes('storage-admission-planned-write-over-budget'), 'diagnostic must warn when quota posture cannot admit new guarded writes or an expected write batch');
  assert.ok(source.includes('web-locks-unavailable'), 'Web Locks availability warning must be part of the product diagnostic');
  assert.ok(source.includes('noEvictionSurvivalClaim') && source.includes('noFsyncDurabilityClaim') && source.includes('noCrossBrowserMatrixClaim') && source.includes('noStorageTimingMitigationClaim'), 'diagnostic must carry durability/browser/privacy non-claim proof flags');
  assert.ok(runtime.includes("import { diagnoseBrowserStoragePosture, BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT } from './browser-storage-posture.mjs';"), 'runtime must import the shared diagnostic module');
  assert.ok(runtime.includes('async browserStoragePosture(config = {})'), 'boot runtime must expose browserStoragePosture()');
  assert.ok(runtime.includes('async opfsAsyncBlockStoreWithPosture(config = {})'), 'boot runtime must expose an async postured OPFS factory');
  assert.ok(runtime.includes('async opfsWebLockGuardedBlockStoreWithPosture(config = {})'), 'boot runtime must expose an async postured Web-Lock-guarded OPFS factory');
  assert.ok(runtime.includes('async opfsWebLockGuardedStorageLaneAdapterWithPosture(config = {})'), 'boot runtime must expose an async postured Web-Lock-guarded OPFS storage-lane adapter factory');
  assert.ok(runtime.includes("'browserStoragePosture'"), 'storage namespace must expose browserStoragePosture()');
  assert.ok(runtime.includes("'browserStorageRecoveryGuidance'"), 'storage namespace must expose browserStorageRecoveryGuidance()');
  assert.ok(runtime.includes("'opfsAsyncBlockStoreWithPosture'"), 'storage namespace must expose opfsAsyncBlockStoreWithPosture()');
  assert.ok(runtime.includes("'opfsWebLockGuardedBlockStoreWithPosture'"), 'storage namespace must expose opfsWebLockGuardedBlockStoreWithPosture()');
  assert.ok(runtime.includes("'opfsWebLockGuardedStorageLaneAdapterWithPosture'"), 'storage namespace must expose opfsWebLockGuardedStorageLaneAdapterWithPosture()');
  assert.ok(runtime.includes('BRT_BROWSER_STORAGE_ADMISSION_REJECTED'), 'postured OPFS factory must fail closed when posture rejects store creation');
  assert.ok(runtime.includes('resolvePosturedWriteBudgetGuard') && runtime.includes('BRT_BROWSER_STORAGE_GUARD_OVERRIDE_REJECTED') && runtime.includes('storage:opfs-block-store-posture-guard-override-rejected') && runtime.includes('postureGuardPolicy'), 'postured OPFS factory must reject explicit writeBudgetGuard overrides by default and expose the posture guard policy');
  assert.ok(runtime.includes('allowWriteBudgetGuardOverride: false'), 'postured OPFS factory must reject weaker per-put write-budget override attempts after admission');
  assert.ok(runtime.includes('allowPostureWriteBudgetGuardOverride') && runtime.includes('allowUnsafeWriteBudgetGuardOverride'), 'postured OPFS factory must require explicit unsafe opt-in before accepting guard overrides');
  assert.ok(runtime.includes('mutationAttempted: false'), 'postured guard override rejection must be explicitly pre-mutation');
  assert.ok(runtime.includes('runtime:browser-storage-recovery-guidance'), 'runtime must emit structured browser storage recovery guidance rows');
  assert.ok(runtime.includes('object:opfs-async-block-store-with-posture-ref'), 'postured OPFS factory must emit a specific trace row');
  assert.ok(runtime.includes('object:opfs-web-lock-guarded-block-store-with-posture-ref'), 'postured Web-Lock-guarded OPFS factory must emit a specific trace row');
  assert.ok(runtime.includes('object:opfs-web-lock-guarded-storage-lane-adapter-with-posture-ref'), 'postured Web-Lock-guarded storage-lane adapter factory must emit a specific trace row');
  assert.ok(runtime.includes('postureReceipt: posture.opfsPostureReceipt') && runtime.includes('postureReceipt: posturedGuarded.postureReceipt'), 'postured OPFS factories must return the OPFS posture receipt instead of hiding it inside diagnostic prose');
  assert.ok(runtime.includes('postured-web-lock-guarded-storage-lane-adapter-factory'), 'postured storage-lane adapter factory must preserve factory provenance');
  assert.ok(runtime.includes('POSTURED_WEB_LOCK_DEFAULT_TIMEOUT_MS') && runtime.includes('normalizePosturedWebLockTimeoutMs'), 'postured Web-Lock-guarded OPFS factory must install a bounded default lock-acquisition wait');
  assert.ok(runtime.includes('BRT_BROWSER_WEB_LOCK_UNBOUNDED_TIMEOUT_REJECTED') && runtime.includes('allowUnboundedPostureLockWait') && runtime.includes('allowUnboundedLockTimeoutOverride'), 'postured Web-Lock-guarded OPFS factory must reject unbounded lock waits unless explicitly opted in and freeze per-operation unbounded overrides');
  assert.ok(runtime.includes('lockContentionPolicy') && runtime.includes('lockTimeoutMs: lockContentionPolicy.lockTimeoutMs'), 'postured Web-Lock-guarded OPFS factory must pass its lock-contention policy into the guard');
  assert.ok(runtime.includes('BRT_BROWSER_WEB_LOCKS_REQUIRED'), 'postured Web-Lock-guarded OPFS factory must fail before mutation when Web Locks are unavailable and required');
  assert.ok(runtime.includes('normalizePosturedWebLockFallbackPolicy') && runtime.includes('BRT_BROWSER_WEB_LOCK_SINGLE_OWNER_FALLBACK_REJECTED') && runtime.includes('allowUnsafeSingleOwnerFallback') && runtime.includes('admitted-single-owner-fallback'), 'postured Web-Lock-guarded OPFS factory must reject unlocked fallback unless explicitly unsafe opted-in and label admitted fallback');
  assert.ok(runtime.includes("createBrowserStorageRecoveryGuidance({ name: 'BrowserRTWebLocksRequiredError'") && runtime.includes('coordination-admission') && runtime.includes('mutationAttempted: false'), 'Web Locks required rejection must attach recovery guidance before OPFS posture/store mutation');
  assert.ok(packageSmoke.includes('webLocksRequiredRecovery') && packageSmoke.includes('BRT_BROWSER_WEB_LOCKS_REQUIRED') && packageSmoke.includes('traceGuidanceObserved'), 'installed package smoke must prove Web Locks required recovery guidance through the package root');
  assert.ok(runtime.includes('browserStoragePostureDiagnostic'), 'kernelKitStoragePosture must be refactored through the shared diagnostic');
  assert.ok(runtime.includes('admissionPolicyDerived') && runtime.includes('mutationGuardActionable'), 'Kernel Kit storage posture must surface the derived admission guard proof');
  assert.ok(types.includes('RtBrowserStoragePostureReport'), 'types must declare the storage posture report');
  assert.ok(types.includes('RtBrowserStoragePostureReceipt') && types.includes('postureReceipt: Readonly<RtBrowserStoragePostureReceipt>'), 'types must declare the OPFS posture receipt and postured factory receipt return');
  assert.ok(types.includes('internalByteLedger?: Record<string, unknown>') && types.includes('lastMutationReceipt?: Record<string, unknown>'), 'types must expose caller-supplied internal byte ledger and last mutation receipt inputs');
  assert.ok(types.includes('RtBrowserStorageRecoveryGuidance') && types.includes('browserStorageRecoveryGuidance(error:'), 'types must declare the storage recovery guidance helper and runtime method');
  assert.ok(types.includes('RtPosturedOpfsAsyncBlockStore'), 'types must declare the postured OPFS factory result');
  assert.ok(types.includes('RtPosturedWebLockGuardedOpfsBlockStore'), 'types must declare the postured Web-Lock-guarded OPFS factory result');
  assert.ok(types.includes('RtPosturedWebLockGuardedOpfsStorageLaneAdapter'), 'types must declare the postured Web-Lock-guarded OPFS storage-lane adapter factory result');
  assert.ok(types.includes('opfsWebLockGuardedStorageLaneAdapterWithPosture(config?:'), 'types must declare the postured storage-lane adapter factory runtime method');
  assert.ok(types.includes('RtBrowserStorageLockContentionPolicy') && types.includes('lockContentionPolicy: Readonly<RtBrowserStorageLockContentionPolicy>'), 'types must declare the postured lock contention policy returned by the guarded factory');
  assert.ok(types.includes('RtBrowserStorageAdmissionPolicy') && types.includes('RtBrowserStorageWriteBudgetGuard'), 'types must declare the admission policy and write budget guard');
  assert.ok(types.includes('RtBrowserStoragePostureGuardPolicy') && types.includes('postureGuardPolicy: Readonly<RtBrowserStoragePostureGuardPolicy>') && types.includes('allowPostureWriteBudgetGuardOverride?: boolean'), 'types must declare the postured guard override policy and explicit unsafe override opt-in');
  assert.ok(types.includes('allowWriteBudgetGuardOverride?: boolean') && types.includes('readonly allowWriteBudgetGuardOverride: boolean'), 'types must declare the raw-store per-put write-budget override freeze knob and snapshot field');
  assert.ok(types.includes('browserStoragePosture(config?:'), 'BrowserRTRuntime declaration must expose browserStoragePosture');
  assert.ok(types.includes('browserStorageRecoveryGuidance(error:'), 'BrowserRTRuntime declaration must expose browserStorageRecoveryGuidance');
  assert.ok(types.includes('opfsAsyncBlockStoreWithPosture(config?:'), 'BrowserRTRuntime declaration must expose opfsAsyncBlockStoreWithPosture');
  assert.ok(types.includes('opfsWebLockGuardedBlockStoreWithPosture(config?:'), 'BrowserRTRuntime declaration must expose opfsWebLockGuardedBlockStoreWithPosture');
  assert.ok(types.includes('budgetPolicy?: Record<string, unknown>'), 'storage posture declaration must expose budgetPolicy tuning without adding another public method');
  assert.ok(types.includes('lockContentionTimeoutMs?: number'), 'postured guarded factory declaration must expose a lock contention timeout override');
  assert.ok(types.includes('allowUnsafeSingleOwnerFallback?: boolean') && types.includes('lockFallbackPolicy') && types.includes("'admitted-single-owner-fallback'"), 'types must expose explicit unsafe single-owner fallback policy and status');
  assert.ok(types.includes('allowUnboundedPostureLockWait?: boolean') && types.includes('allowUnsafeUnboundedPostureLockWait?: boolean') && types.includes('allowUnboundedLockTimeoutOverride?: boolean'), 'types must expose the explicit unsafe unbounded-lock-wait opt-in and raw guard override knob');
  assert.ok(types.includes("| 'browserStoragePosture'"), 'storage namespace declaration must include browserStoragePosture');
  assert.ok(types.includes("| 'browserStorageRecoveryGuidance'"), 'storage namespace declaration must include browserStorageRecoveryGuidance');
  assert.ok(types.includes("| 'opfsWebLockGuardedBlockStoreWithPosture'"), 'storage namespace declaration must include opfsWebLockGuardedBlockStoreWithPosture');
  assert.ok(types.includes("| 'opfsWebLockGuardedStorageLaneAdapterWithPosture'"), 'storage namespace declaration must include opfsWebLockGuardedStorageLaneAdapterWithPosture');
  assert.ok(publicDts.includes('diagnoseBrowserStoragePosture') && publicDts.includes('BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT'), 'package-root declarations must export the diagnostic');
  assert.ok(publicDts.includes('createBrowserStorageRecoveryGuidance') && publicDts.includes('BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT'), 'package-root declarations must export recovery guidance');
  assert.ok(publicMjs.includes('diagnoseBrowserStoragePosture') && publicMjs.includes('BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT'), 'package-root JS API must export the diagnostic');
  assert.ok(publicMjs.includes('createBrowserStorageRecoveryGuidance') && publicMjs.includes('BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT'), 'package-root JS API must export recovery guidance');
  assert.ok(productWedge.includes('diagnoseBrowserStoragePosture') && productWedge.includes('BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT'), 'public export manifest must include the diagnostic');
  assert.ok(productWedge.includes('createBrowserStorageRecoveryGuidance') && productWedge.includes('BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT'), 'public export manifest must include recovery guidance');
  assert.ok(packageSmoke.includes('runtime.storage.browserStoragePosture'), 'installed TypeScript smoke must compile the namespaced diagnostic');
  assert.ok(packageSmoke.includes('runtime.storage.browserStorageRecoveryGuidance'), 'installed TypeScript smoke must compile the namespaced recovery guidance helper');
  assert.ok(packageSmoke.includes('createBrowserStorageRecoveryGuidance'), 'installed TypeScript smoke must compile the package-root recovery guidance helper');
  assert.ok(packageSmoke.includes('runtime.storage.opfsAsyncBlockStoreWithPosture'), 'installed TypeScript smoke must compile the postured OPFS factory');
  assert.ok(packageSmoke.includes('runtime.storage.opfsWebLockGuardedBlockStoreWithPosture'), 'installed TypeScript smoke must compile the postured Web-Lock-guarded OPFS factory');
  assert.ok(packageSmoke.includes('runtime.storage.opfsWebLockGuardedStorageLaneAdapterWithPosture'), 'installed TypeScript smoke must compile the postured Web-Lock-guarded storage-lane adapter factory');
  assert.ok(packageSmoke.includes('113'), 'installed package smoke must update runtime method count intentionally');
  const postureProbe = await text('tools/browser_storage_posture_probe.mjs');
  assert.ok(postureProbe.includes('directRecoveryGuidanceExported'), 'storage posture probe must prove recovery guidance is package-exported and classifies pre-mutation lock contention');
  assert.ok(postureProbe.includes('opfsPostureReceiptNamesQuotaLedgerPersistenceLocksAndNonClaims') && postureProbe.includes('internalByteLedgerReceiptObserved'), 'storage posture probe must prove the OPFS posture receipt names quota, internal ledger, persistence, locks, last mutation, and non-claims');
  assert.ok(postureProbe.includes('serviceWorkerWaitUntilGuidanceClassified'), 'storage posture probe must prove Service Worker waitUntil late-failure guidance requires settlement and digest verification');
  assert.ok(postureProbe.includes('posturedFactoryRejectsBeforeStoreCreation'), 'storage posture probe must prove the postured factory rejects before store creation under pressure');
  assert.ok(postureProbe.includes('posturedGuardOverrideRejectedBeforeStoreCreation') && postureProbe.includes('BRT_BROWSER_STORAGE_GUARD_OVERRIDE_REJECTED'), 'storage posture probe must prove explicit guard override rejection before store creation');
  assert.ok(postureProbe.includes('pressureAdmissionRejectsBeforeMutation'), 'storage posture probe must prove the derived guard rejects before fake-OPFS mutation under pressure');
  assert.ok(postureProbe.includes('posturedFactoryAdmitsAndAppliesGuard'), 'storage posture probe must prove the postured factory admits and applies the derived guard when quota posture allows it');
  assert.ok(postureProbe.includes('posturedStoreRejectsPerPutGuardOverrideBeforeMutation') && postureProbe.includes('posturedWebLockFactoryRejectsPerPutGuardOverrideBeforeMutation') && postureProbe.includes('BRT_OPFS_WRITE_BUDGET_OVERRIDE_REJECTED'), 'storage posture probe must prove admitted postured stores reject per-put guard overrides before mutation');
  assert.ok(postureProbe.includes('posturedWebLockFactoryAdmitsAppliesGuardAndSettles'), 'storage posture probe must prove the postured Web-Lock-guarded factory admits, applies the guard, and settles locks');
  assert.ok(postureProbe.includes('posturedGuardedStorageLaneAdapterFactoryAdmitsAppliesGuardAndSettles') && postureProbe.includes('opfsWebLockGuardedStorageLaneAdapterWithPosture'), 'storage posture probe must prove the postured storage-lane adapter factory admits, applies the guard, and settles lanes');
  assert.ok(postureProbe.includes('posturedWebLockFactoryDefaultsBoundedLockWait'), 'storage posture probe must prove the postured Web-Lock-guarded factory installs a bounded lock wait by default');
  assert.ok(postureProbe.includes('posturedWebLockFactoryRejectsUnboundedFactoryTimeoutBeforeStoreCreation') && postureProbe.includes('posturedWebLockFactoryRejectsUnboundedPerOperationTimeoutBeforeMutation') && postureProbe.includes('BRT_OPFS_WEB_LOCK_TIMEOUT_OVERRIDE_REJECTED'), 'storage posture probe must prove postured Web-Lock factories reject unbounded factory/per-operation lock waits before store creation or mutation');
  assert.ok(postureProbe.includes('posturedWebLockContentionRejectsBeforeMutationAndRecovers'), 'storage posture probe must prove postured Web-Lock contention times out before mutation and recovers');
  assert.ok(postureProbe.includes('storage.browserStorageRecoveryGuidance') && postureProbe.includes('shouldQueryLocks'), 'storage posture probe must prove lock-timeout recovery guidance reaches runtime callers');
  assert.ok(postureProbe.includes('BRT_BROWSER_WEB_LOCK_SINGLE_OWNER_FALLBACK_REJECTED') && postureProbe.includes('admitted-single-owner-fallback') && postureProbe.includes('allowUnsafeSingleOwnerFallback'), 'storage posture probe must prove explicit unsafe single-owner fallback gating');
  const managedPostureProbe = await text('tools/browser_storage_posture_managed_probe.mjs');
  assert.ok(abortProductWedge.includes('opfsWebLockGuardedBlockStoreWithPosture'), 'installed browser OPFS abort wedge must use the postured guarded OPFS factory rather than hand-wired raw composition');
  assert.ok(!abortProductWedge.includes('rt.storage.opfsWebLockGuardedBlockStore({'), 'installed browser OPFS abort wedge must not hand-wire raw guarded OPFS construction');
  assert.ok(abortProductWedge.includes('writeBudgetGuardSource') && abortProductWedge.includes('browser-storage-posture-admission-policy') && abortProductWedge.includes('posturedGuardedFactoryUsed'), 'installed browser OPFS abort wedge receipt must prove posture-derived write-budget guard use');
  assert.ok(abortProductWedgeProbe.includes('opfsWebLockGuardedBlockStoreWithPosture') && abortProductWedgeProbe.includes('doesNotMatch') && abortProductWedgeProbe.includes('writeBudgetGuardSource'), 'installed browser OPFS abort package proof must enforce the postured factory migration');
  assert.ok(budgetProductWedge.includes('opfsWebLockGuardedBlockStoreWithPosture'), 'installed browser OPFS budget wedge must use the postured guarded OPFS factory rather than hand-wired raw composition');
  assert.ok(!budgetProductWedge.includes('rt.storage.opfsWebLockGuardedBlockStore({'), 'installed browser OPFS budget wedge must not hand-wire raw guarded OPFS construction');
  assert.ok(budgetProductWedge.includes('posturedGuardedFactoryUsed') && budgetProductWedge.includes('postureGuardPropagated') && budgetProductWedge.includes('writeBudgetGuardSource') && budgetProductWedge.includes('browser-storage-posture-admission-policy'), 'installed browser OPFS budget wedge receipt must prove posture-derived write-budget guard use');
  assert.ok(budgetProductWedgeProbe.includes('opfsWebLockGuardedBlockStoreWithPosture') && budgetProductWedgeProbe.includes('doesNotMatch') && budgetProductWedgeProbe.includes('writeBudgetGuardSource'), 'installed browser OPFS budget package proof must enforce the postured factory migration');
  assert.ok(corruptionProductWedge.includes('opfsWebLockGuardedBlockStoreWithPosture'), 'installed browser OPFS corruption wedge must use the postured guarded OPFS factory rather than hand-wired raw composition');
  assert.ok(!corruptionProductWedge.includes('rt.storage.opfsWebLockGuardedBlockStore({'), 'installed browser OPFS corruption wedge must not hand-wire raw guarded OPFS construction');
  assert.ok(corruptionProductWedge.includes('posturedGuardedFactoryUsed') && corruptionProductWedge.includes('postureGuardPropagatedToRepair') && corruptionProductWedge.includes('budgetPolicySource') && corruptionProductWedge.includes('browser-storage-posture-admission-policy'), 'installed browser OPFS corruption wedge receipt must prove posture-derived write-budget guard use through the corrupt-block repair path');
  assert.ok(corruptionProductWedgeProbe.includes('opfsWebLockGuardedBlockStoreWithPosture') && corruptionProductWedgeProbe.includes('doesNotMatch') && corruptionProductWedgeProbe.includes('repairBudgetSource'), 'installed browser OPFS corruption package proof must enforce the postured factory migration and repair-budget provenance');

  assert.ok(crossTabProductWedge.includes('opfsWebLockGuardedBlockStoreWithPosture'), 'installed browser cross-tab/tab-close OPFS wedge must use the postured guarded OPFS factory rather than hand-wired raw composition');
  assert.ok(!crossTabProductWedge.includes('rt.storage.opfsWebLockGuardedBlockStore({'), 'installed browser cross-tab/tab-close OPFS wedge must not hand-wire raw guarded OPFS construction');
  assert.ok(crossTabProductWedge.includes('posturedGuardedFactoryUsed') && crossTabProductWedge.includes('writeBudgetGuardSource') && crossTabProductWedge.includes('browser-storage-posture-admission-policy'), 'installed browser cross-tab/tab-close OPFS wedge receipt must prove posture-derived write-budget guard use');
  assert.ok(crossTabProductWedgeProbe.includes('opfsWebLockGuardedBlockStoreWithPosture') && crossTabProductWedgeProbe.includes('doesNotMatch') && crossTabProductWedgeProbe.includes('writeBudgetGuardSource'), 'installed browser cross-tab OPFS package proof must enforce the postured factory migration');
  assert.ok(tabCloseProductWedgeProbe.includes('opfsWebLockGuardedBlockStoreWithPosture') && tabCloseProductWedgeProbe.includes('doesNotMatch') && tabCloseProductWedgeProbe.includes('writeBudgetGuardSource'), 'installed browser tab-close OPFS package proof must enforce the postured factory migration');

  assert.ok(reopenProductWedge.includes('opfsWebLockGuardedBlockStoreWithPosture'), 'installed browser reopen/abrupt-kill OPFS wedge must use the postured guarded OPFS factory rather than hand-wired raw composition');
  assert.ok(!reopenProductWedge.includes('rt.storage.opfsWebLockGuardedBlockStore({'), 'installed browser reopen/abrupt-kill OPFS wedge must not hand-wire raw guarded OPFS construction');
  assert.ok(reopenProductWedge.includes('posturedGuardedFactoryUsedAcrossSessions') && reopenProductWedge.includes('posturedGuardedFactoryUsedAcrossProcessRelaunch') && reopenProductWedge.includes('budgetPolicySource') && reopenProductWedge.includes('browser-storage-posture-admission-policy'), 'installed browser reopen/abrupt-kill OPFS wedge receipts must prove postured guarded factory and budget provenance across reload/relaunch');
  assert.ok(reopenProductWedgeProbe.includes('opfsWebLockGuardedBlockStoreWithPosture') && reopenProductWedgeProbe.includes('doesNotMatch') && reopenProductWedgeProbe.includes('budgetPolicySource'), 'installed browser reopen package proof must enforce postured factory migration and budget provenance');
  assert.ok(abruptKillProductWedgeProbe.includes('opfsWebLockGuardedBlockStoreWithPosture') && abruptKillProductWedgeProbe.includes('doesNotMatch') && abruptKillProductWedgeProbe.includes('budgetPolicySource'), 'installed browser abrupt-kill package proof must enforce postured factory migration and repair-budget provenance');
  assert.ok(managedPostureProbe.includes('opfsAsyncBlockStoreWithPosture'), 'managed browser posture proof must exercise the postured OPFS factory in real Chromium');
  assert.ok(managedPostureProbe.includes('opfsWebLockGuardedBlockStoreWithPosture'), 'managed browser posture proof must exercise the postured Web-Lock-guarded OPFS factory in real Chromium');
  assert.ok((pkg.files || []).includes('src/browser-storage-posture.mjs') && !(pkg.files || []).includes('src/*.mjs'), 'package source allowlist must explicitly include browser-storage-posture.mjs without broad src glob');

  const ids = new Set((manifest.tasks || []).map((task) => task.id));
  assert.ok(ids.has('product:browser-storage-posture-proof'), 'manifest must register product storage posture proof');
  assert.ok(ids.has('facility:browser-storage-posture-contract-audit'), 'manifest must register product storage posture contract audit');
  const proofTask = (manifest.tasks || []).find((task) => task.id === 'product:browser-storage-posture-proof');
  const auditTask = (manifest.tasks || []).find((task) => task.id === 'facility:browser-storage-posture-contract-audit');
  assert.ok(proofTask.inputs.includes('src/browser-storage-posture.mjs'), 'storage posture proof must be invalidated by the diagnostic module');
  assert.ok(proofTask.inputs.includes('src/browser-storage-recovery-guidance.mjs'), 'storage posture proof must be invalidated by recovery guidance changes');
  assert.ok(proofTask.outputs.includes(`artifacts/validation/${PFX}-BROWSER-STORAGE-POSTURE-PROBE.json`), 'storage posture proof must emit a current revision artifact');
  assert.ok(auditTask.inputs.includes('src/browser-storage-posture.mjs'), 'storage posture audit must be invalidated by the diagnostic module');
  assert.ok(auditTask.inputs.includes('src/browser-storage-recovery-guidance.mjs'), 'storage posture audit must be invalidated by recovery guidance changes');
  assert.ok(auditTask.outputs.includes(`artifacts/audit/${PFX}-BROWSER-STORAGE-POSTURE-CONTRACT-AUDIT.json`), 'storage posture audit must emit a current revision artifact');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'passed',
    audit_id: `${REVISION}-browser-storage-posture-contract-audit`,
    format: BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT,
    checks: [
      { name: 'public-api-exported', status: 'passed' },
      { name: 'runtime-storage-namespace-exposed', status: 'passed' },
      { name: 'kernel-kit-posture-refactored-through-diagnostic', status: 'passed' },
      { name: 'admission-policy-derived-from-quota-posture', status: 'passed' },
      { name: 'postured-opfs-factory-fails-closed-and-applies-guard', status: 'passed' },
      { name: 'postured-opfs-factory-rejects-guard-override-before-store-creation', status: 'passed' },
      { name: 'postured-web-lock-guarded-opfs-factory-fails-closed-applies-guard-and-settles', status: 'passed' },
      { name: 'postured-web-lock-guarded-default-bounded-lock-wait', status: 'passed' },
      { name: 'postured-web-lock-unbounded-timeout-rejection', status: 'passed' },
      { name: 'postured-web-lock-single-owner-fallback-explicit-unsafe-opt-in', status: 'passed' },
      { name: 'postured-web-lock-contention-timeout-before-mutation', status: 'passed' },
      { name: 'installed-browser-opfs-abort-wedge-migrated-to-postured-factory', status: 'passed' },
      { name: 'installed-browser-opfs-budget-wedge-migrated-to-postured-factory', status: 'passed' },
      { name: 'installed-browser-opfs-corruption-wedge-migrated-to-postured-factory', status: 'passed' },
      { name: 'opfs-write-budget-policy-source-preserved', status: 'passed' },
      { name: 'browser-storage-recovery-guidance-exported-and-typed', status: 'passed' },
      { name: 'service-worker-waituntil-recovery-guidance-classified', status: 'passed' },
      { name: 'derived-transient-write-budget-guard-proven-before-mutation', status: 'passed' },
      { name: 'persist-call-explicitly-gated', status: 'passed' },
      { name: 'best-effort-warning-visible', status: 'passed' },
      { name: 'durability-non-claims-visible', status: 'passed' },
      { name: 'installed-typescript-smoke-covers-namespace', status: 'passed' },
      { name: 'postured-guarded-storage-lane-adapter-factory-admits-applies-guard-and-settles', status: 'passed' },
      { name: 'manifest-registered', status: 'passed' }
    ],
    nonClaims: ['Contract audit only; runtime/browser probes supply environment evidence. No persistent-storage grant, quota reservation, organic eviction, fsync, or cross-browser claim.']
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const report = await runAudit();
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
}
