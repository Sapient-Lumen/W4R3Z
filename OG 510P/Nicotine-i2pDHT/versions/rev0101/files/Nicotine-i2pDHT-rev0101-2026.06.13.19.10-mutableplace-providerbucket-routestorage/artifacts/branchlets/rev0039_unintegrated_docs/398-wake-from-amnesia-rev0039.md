# Wake from amnesia — rev0039

You are looking at the I2P DHT baby cube.  The current revision is rev0039.
The cube is still intentionally not a live I2P/SAM implementation.

Recent path:

- rev0036: service catalog / load sheath / profile GC
- rev0037: service tickets / receipts / announcements / ingress
- rev0038: joined service continuity across folded service branchlets
- rev0039: service leases and repeated-window session ledger

The design stance remains:

```text
Garden nodes give capacity, not truth.
A single valid report is not enough to authorize repeated side effects.
```

Start with `docs/393-rev0039-servicelease-sessionledger-fold.md`, then inspect
`servicelease.py`, `sessionledger.py`, and the rev0039 tests.
