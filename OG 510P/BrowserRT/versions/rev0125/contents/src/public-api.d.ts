export type { BrowserRTRuntime } from './types.js';
export { VERSION, REVISION, detectCapabilities, availableCapabilityTierNames, boot, createObjectRef, createTransferObjectRef, createTransferObject, createBlockObjectRef, createEnvelope, digestBytesHex, validateBlockStoreLaneAdapterSnapshot, TraceLog } from './types.js';
export const BROWSERRT_PRODUCT_WEDGE_FORMAT: 'browserrt.product-wedge-receipt.v1';
export const BROWSERRT_PUBLIC_API_EXPORTS: readonly string[];
export function createBrowserRtProductWedgeReceipt(input?: { revision?: string; version?: string; observed?: Record<string, unknown>; traceKinds?: string[]; generatedAt?: string; source?: string }): Readonly<Record<string, unknown>>;
export function validateBrowserRtProductWedgeReceipt(receipt: unknown): Readonly<{ ok: boolean; errors: string[]; requiredProof: string[]; proof: Record<string, unknown> }>;
