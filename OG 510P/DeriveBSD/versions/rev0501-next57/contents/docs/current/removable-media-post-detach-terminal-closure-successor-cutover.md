# Current removable-media post-detach terminal-closure successor cutover

r533 defines the activation fence for post-closure successor authority. r531 denies old authority, r532 allows new successor authority only from fresh authority, and r533 proves that the successor is not live until successor-index cutover, checkpoint, and reader admission have all been observed.

The current contract is `removable.media.local.post_detach.terminal.closure.successor.cutover.receipt`.

Required posture:

- the r532 successor-authority receipt is bound by computed digest;
- successor-index cutover observed before activation;
- old handles are terminal and no dual-active window is accepted;
- checkpoint observed before broker use;
- reader admission bound before use;
- activation ledger expected root equals prior root and new root advances;
- terminal closure remains terminal;
- support remains digest-only and does not claim offline erasure.

Red fixtures live under `spec/examples/invalid/removable-media/post-detach-terminal-closure-successor-cutover-receipt/`.

Last updated: 2026-05-30r533
