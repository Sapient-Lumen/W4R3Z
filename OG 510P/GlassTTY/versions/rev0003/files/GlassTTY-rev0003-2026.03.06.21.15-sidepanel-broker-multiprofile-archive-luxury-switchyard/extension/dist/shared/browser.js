import { supportedOrigins } from '../adapters';
export async function getActiveTab() {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    return tabs[0];
}
export function isSupportedUrl(url) {
    if (!url)
        return false;
    return supportedOrigins().some((origin) => url.startsWith(origin));
}
