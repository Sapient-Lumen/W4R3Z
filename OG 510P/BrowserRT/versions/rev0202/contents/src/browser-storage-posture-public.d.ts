export const BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT: 'browserrt.browser-storage-posture.v1';
export const BROWSERRT_BROWSER_STORAGE_ADMISSION_POLICY_FORMAT: 'browserrt.browser-storage-admission-policy.v1';
export const BROWSERRT_BROWSER_STORAGE_POSTURE_RECEIPT_FORMAT: 'browserrt.browser-storage-posture-receipt.v1';
export function buildBrowserStorageAdmissionPolicy(input?: Record<string, unknown>): Readonly<Record<string, unknown>>;
export function diagnoseBrowserStoragePosture(config?: Record<string, unknown>): Promise<Readonly<Record<string, unknown>>>;
