# Proof obligation — rev0047

Current proof obligation:

```text
Show that a public bridge publication cannot be treated as locally safe merely because a bridge ledger passed; watched evidence, publication replay memory, and quench pressure must bind to the same profile/service/scope/request boundary.
```

Evidence:

- `witnessappealmesh.py`
- `publicationledger.py`
- `bridgequenchlane.py`
- `appealpublicationfold.py`
- `tests/test_rev0047_appeal_publication_quench.py`

Open obligation:

- Live I2P/SAM publication is still shadowed.
- Real validator roots remain future design.
- Quench and redress semantics remain local and subjective.
