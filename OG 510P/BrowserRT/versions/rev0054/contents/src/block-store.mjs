// BrowserRT rev0025 block-store compatibility surface.
// The implementation lives in src/browserrt.mjs for the current baby cube so the
// tiny runtime can stay small while storage providers graduate into separate modules. This file gives future
// provider work a stable path without introducing a second implementation.
export {
  JournaledMemoryBlockStore,
  MemoryBlockStore,
  createBlockObjectRef,
  createJournaledMemoryBlockStore,
  createMemoryBlockStore,
  digestBytesHex,
  recoverJournaledMemoryBlockStore,
  OpfsAsyncBlockStore,
  createOpfsAsyncBlockStore
} from './browserrt.mjs';
