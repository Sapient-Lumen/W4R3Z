import type { AdapterCapabilities, PageAdapter } from './base';
import { chatgptAdapter } from './chatgpt';

export const adapters: PageAdapter[] = [chatgptAdapter];

export interface AdapterDescriptor {
  name: string;
  origin_patterns: string[];
  capabilities: AdapterCapabilities;
}

export function detectAdapter(url: string, document: Document): PageAdapter | null {
  for (const adapter of adapters) {
    if (adapter.matches(url, document)) return adapter;
  }
  return null;
}

export function supportedOrigins(): string[] {
  return adapters.flatMap((adapter) => adapter.origin_patterns);
}

export function supportedMatchPatterns(): string[] {
  return Array.from(new Set(supportedOrigins().map((origin) => `${origin}*`)));
}

export function adapterDescriptors(): AdapterDescriptor[] {
  return adapters.map((adapter) => ({
    name: adapter.name,
    origin_patterns: adapter.origin_patterns,
    capabilities: adapter.capabilities,
  }));
}
