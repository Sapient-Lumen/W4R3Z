import { claudeAdapter } from './claude';
export const adapters = [claudeAdapter];
export function detectAdapter(url, document) {
    for (const adapter of adapters) {
        if (adapter.matches(url, document))
            return adapter;
    }
    return null;
}
export function supportedOrigins() {
    return ['https://claude.ai/'];
}
