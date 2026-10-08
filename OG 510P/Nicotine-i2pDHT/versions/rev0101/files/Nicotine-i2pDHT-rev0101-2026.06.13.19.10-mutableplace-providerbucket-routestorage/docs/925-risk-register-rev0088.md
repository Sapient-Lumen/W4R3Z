# Risk register — rev0088

Risks under test:

- native code remains loaded after a wrong result or crash;
- sandbox language creates false confidence before real isolation exists;
- crash-ledger GC erases quarantine/fallback memory;
- performance evidence launders native back into service;
- unload/GC state diverges after restart or same-sequence fork.

Mitigation guess: keep unload, sandbox stub, and crash-GC as exact-boundary reports with Python fallback memory mandatory.
