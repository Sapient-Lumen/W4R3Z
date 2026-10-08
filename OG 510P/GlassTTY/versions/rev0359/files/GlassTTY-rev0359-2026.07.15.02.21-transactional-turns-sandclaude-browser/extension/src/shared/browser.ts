import { supportedOrigins } from '../adapters';

export async function getActiveTab(): Promise<chrome.tabs.Tab | undefined> {
  const tabs = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
  return tabs[0];
}

export async function getTabById(tabId?: number): Promise<chrome.tabs.Tab | undefined> {
  if (!tabId) return undefined;
  try {
    return await chrome.tabs.get(tabId);
  } catch {
    return undefined;
  }
}

export function isSupportedUrl(url?: string): boolean {
  if (!url) return false;
  return supportedOrigins().some((origin) => url.startsWith(origin));
}
