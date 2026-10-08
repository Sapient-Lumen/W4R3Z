import { claudeAdapter } from './claude';
import { labAdapter } from './lab';
export const adapters = [claudeAdapter, labAdapter];
export function detectAdapter(url, document) {
    for (const adapter of adapters) {
        if (adapter.matches(url, document))
            return adapter;
    }
    return null;
}
export function supportedOrigins() {
    return adapters.flatMap((adapter) => adapter.origin_patterns);
}
export function supportedMatchPatterns() {
    return Array.from(new Set(supportedOrigins().map((origin) => `${origin}*`)));
}
export function adapterDescriptors() {
    return adapters.map((adapter) => ({
        name: adapter.name,
        origin_patterns: adapter.origin_patterns,
        capabilities: adapter.capabilities,
    }));
}
