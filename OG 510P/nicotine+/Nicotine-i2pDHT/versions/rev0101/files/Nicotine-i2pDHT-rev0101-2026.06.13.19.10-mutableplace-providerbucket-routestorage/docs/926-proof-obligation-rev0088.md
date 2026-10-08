# Proof obligation — rev0088

Before native code grows beyond the XOR-distance leaf, the cube must prove:

- faults force fallback/quarantine;
- sandbox claims remain nonproduction and no-network;
- parser/crypto/secret-key surfaces stay Python-owned;
- crash-ledger GC never drops active fault memory;
- fallback remains available at every native boundary.

The current proof is local and toy: deterministic Python tests plus fold/audit surfaces. It is not a production security proof.
