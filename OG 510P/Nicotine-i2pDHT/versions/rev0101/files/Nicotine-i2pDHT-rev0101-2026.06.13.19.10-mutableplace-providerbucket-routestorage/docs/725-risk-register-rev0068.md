# Risk register — rev0068

Known risks intentionally left open:

- Toy signatures and digest-only component binding are not production cryptography.
- Restart generations are local counters, not distributed time.
- Family/path diversity labels are lab hints, not a Sybil solution.
- Closure audit is local evidence, not consensus.
- No live I2P/SAM transport is present.

The main risk attacked in rev0068 is **cleanup laundering**: a soft prune or archive replay accidentally becoming permission to forget contradiction memory.
