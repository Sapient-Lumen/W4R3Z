export {
  VERSION,
  REVISION,
  detectCapabilities,
  availableCapabilityTierNames,
  createObjectRef,
  createTransferObjectRef,
  createTransferObject,
  createBlockObjectRef,
  createEnvelope,
  digestBytesHex,
  diagnoseBrowserStoragePosture,
  createBrowserStorageRecoveryGuidance,
  BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT,
  BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT,
  TraceLog
} from './runtime-core-public.mjs';

export { validateBlockStoreLaneAdapterSnapshot } from './block-store-lane-adapter.mjs';
export {
  BROWSERRT_PRODUCT_WEDGE_FORMAT,
  BROWSERRT_PUBLIC_API_EXPORTS,
  createBrowserRtProductWedgeReceipt,
  validateBrowserRtProductWedgeReceipt
} from './product-wedge.mjs';
export async function boot(options = {}) {
  const { boot: bootBrowserRt } = await import('./browserrt.mjs');
  return bootBrowserRt(options);
}
