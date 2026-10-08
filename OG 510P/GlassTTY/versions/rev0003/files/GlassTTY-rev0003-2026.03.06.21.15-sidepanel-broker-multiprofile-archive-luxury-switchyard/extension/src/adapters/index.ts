import type { PageAdapter } from './base';
import { claudeAdapter } from './claude';

export const adapters: PageAdapter[] = [claudeAdapter];

export function detectAdapter(url: string, document: Document): PageAdapter | null {
  for (const adapter of adapters) {
    if (adapter.matches(url, document)) return adapter;
  }
  return null;
}

export function supportedOrigins(): string[] {
  return ['https://claude.ai/'];
}
