# Interest mixing before provider proof probes

Provider proof handshakes are useful because provider records are claims, not content truth. They are also dangerous because each probe reveals timing, family/path shape, and sometimes the raw content key.

`interestmix.py` makes that cost explicit. It models:

- real interest targets,
- cover targets,
- commitment-first private-provider probes,
- raw-key exposure limits,
- local repeat-window memory,
- probe-family diversity pressure,
- witness payloads that carry commitments rather than raw content keys.

The aim is not private retrieval. The aim is to keep proof and privacy budgets coupled so that a future implementation cannot accidentally normalize naked provider probing as a default fast path.

Important rule:

```text
Semantic confirmation has a metadata budget.
```
