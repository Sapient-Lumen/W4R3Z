# Risk register — rev0058

Open risks:

- Finality is local, not consensus.
- Retry escrow is toy algebra, not a real scheduler.
- Prune guard has no production database behind it.
- Family/path diversity in tests is lab metadata, not a solved independence oracle.
- No live I2P/SAM transport exists in this cube.

The new risk reduced in rev0058 is accidental local laundering: unresolved dead-letter memory can no longer quietly become terminal, retry, or pruned state without an exact-boundary report.
