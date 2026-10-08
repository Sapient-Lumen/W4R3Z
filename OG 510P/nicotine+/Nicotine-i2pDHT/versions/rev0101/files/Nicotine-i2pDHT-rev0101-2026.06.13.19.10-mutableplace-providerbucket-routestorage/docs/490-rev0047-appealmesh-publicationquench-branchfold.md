# rev0047 — appealmesh-publicationquench-branchfold

rev0047 follows the public-bridge governance line one step past rev0046.  rev0046 made subjective moderation, redress, and bridge-ledger joins explicit.  This revision asks what happens after that local ledger says a future public bridge side effect is permissible.

The risk-first answer is: do not let a valid bridge ledger publish sticky public entrance records by itself.  It must pass through a witness-appeal mesh when watch pressure exists, then through a publication ledger, then through a quench/cooldown lane that can stop repeated stale public exposure.

The strongest design sentence is:

```text
A local bridge side effect is still not a public bridge publication; watched evidence, publication replay memory, and quench pressure must bind to the same scope/request boundary.
```

New active surfaces:

- `src/i2p_dht_lab/witnessappealmesh.py`
- `src/i2p_dht_lab/publicationledger.py`
- `src/i2p_dht_lab/bridgequenchlane.py`
- `src/i2p_dht_lab/appealpublicationfold.py`
- `tests/test_rev0047_appeal_publication_quench.py`

The audit/refactor lane folds sibling rev0046 branchlets into visible historical evidence under `artifacts/branchlets/rev0046_public_bridge_branchlets/`.  The folded branchlets explored witness appeal, bridge chaos, bridge publish, bridge quench, and validator-root boundaries.  rev0047 does not copy those branchlets blindly; it extracts the active seam and pins the rest as wake-from-amnesia history.

Current nonclaims remain: no live I2P/SAM transport, no production DHT, no production public bridge publication protocol, no global ban list, no global reputation, no mutable-head consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
