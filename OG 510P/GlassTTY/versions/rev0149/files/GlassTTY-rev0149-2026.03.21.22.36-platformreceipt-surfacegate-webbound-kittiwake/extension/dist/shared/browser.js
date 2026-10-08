import { supportedOrigins } from '../adapters';
export async function getActiveTab() {
    const tabs = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
    return tabs[0];
}
export async function getTabById(tabId) {
    if (!tabId)
        return undefined;
    try {
        return await chrome.tabs.get(tabId);
    }
    catch {
        return undefined;
    }
}
export function isSupportedUrl(url) {
    if (!url)
        return false;
    return supportedOrigins().some((origin) => url.startsWith(origin));
}
