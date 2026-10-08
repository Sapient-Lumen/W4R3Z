# Revalidation seal for prior native lanes

`revalidationseal.py` prevents rev0092 from trusting stale old native evidence. Before a load-gate re-entry request becomes useful, the cube now requires fresh digest evidence from the prior native safety lanes:

- parity;
- ABI guard;
- fallback seal;
- runtime stamp;
- native selection;
- build provenance;
- differential corpus;
- native budget.

The seal expires. It rejects stale/expired evidence, missing required lanes, replay, rollback, same-sequence forks, previous-link mismatch, digest drift, low diversity, and memory drops.

It still does not allow native load or dispatch.
