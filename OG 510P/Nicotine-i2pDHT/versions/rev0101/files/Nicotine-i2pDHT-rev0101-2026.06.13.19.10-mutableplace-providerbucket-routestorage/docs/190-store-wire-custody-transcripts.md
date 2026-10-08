# STORE/custody wire transcripts

`wirecanon.py` made signed transport-neutral frames.  `storewire.py` binds those frames to exact STORE/custody objects:

- `STORE_REQUEST` wraps a `StoreContractRequest` hash and body;
- `STORE_RECEIPT` wraps a signed exact-digest store receipt;
- `CUSTODY_CHALLENGE` wraps a challenge hash and body;
- `CUSTODY_PROOF` wraps a signed challenge-bound custody proof.

The key pressure is role binding: a custody proof payload carried as a store request, or a store request carried as a custody proof, is a semantic mismatch even if the outer frame is signed.

The module still does not define a network protocol.  It gives deterministic transcript fixtures for future SAM/I2P tests.
