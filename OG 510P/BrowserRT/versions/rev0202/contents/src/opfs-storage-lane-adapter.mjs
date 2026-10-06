import { createCrossLaneScheduler } from './cross-lane-scheduler.mjs';
import { createOpfsAsyncBlockStore } from './opfs-block-store.mjs';
import { BlockStoreLaneAdapter, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot, BLOCK_STORE_LANE_ADAPTER_OPS } from './block-store-lane-adapter.mjs';
export class OpfsBlockStoreStorageLaneAdapter extends BlockStoreLaneAdapter {
  constructor(config = {}) {
    const label = config.label || 'opfs-storage-lane-adapter';
    const trace = config.trace || null;
    const ownsStore = config.ownStore === undefined ? !config.store : config.ownStore !== false;
    const store = config.store || createOpfsAsyncBlockStore({
      name: `${label}:store`,
      prefix: config.prefix || `browserrt/opfs-storage-lane-adapter/${label}`,
      trace,
      ...(config.storeConfig || {})
    });
    const scheduler = config.scheduler || createCrossLaneScheduler({
      label: `${label}:scheduler`,
      trace,
      lanes: config.lanes || [
        { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 512 },
        { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
      ],
      ...(config.schedulerConfig || {})
    });
    super({ ...config, label, store, scheduler, trace, lane: config.lane || 'storage', ownStore: ownsStore });
  }
}
export class OpfsStorageLaneAdapter extends OpfsBlockStoreStorageLaneAdapter {}
export function createOpfsBlockStoreStorageLaneAdapter(config = {}) { return new OpfsBlockStoreStorageLaneAdapter(config); }
export function createOpfsStorageLaneAdapter(config = {}) { return new OpfsBlockStoreStorageLaneAdapter(config); }
export function validateOpfsStorageLaneAdapterSnapshot(snapshot) { return validateBlockStoreLaneAdapterSnapshot(snapshot); }
export const OPFS_STORAGE_LANE_ADAPTER_SUPPORTED_OPS = BLOCK_STORE_LANE_ADAPTER_OPS;
export { createBlockStoreLaneAdapter };
