# Proof obligation rev0039

The rev0039 proof obligation is to show that ongoing service has its own local
boundary after service continuity:

```text
continuity accepted
  -> lease accepted / renewed
    -> repeated session windows accepted
      -> sticky service-session memory may advance
```

Evidence:

- `tests/test_rev0039_servicelease_sessionledger_fold.py`
- `servicelease.py`
- `sessionledger.py`
- `sessionfold.py`
- `foldmap.py` rev0039 entries
- `foldregistry.py` rev0039 entries
- `surfaceledger.py` rev0039 entries

Nonproofs:

- no production protocol
- no live network behavior
- no anonymity/Sybil guarantee
- no global trust semantics
