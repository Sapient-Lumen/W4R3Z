# Search action policy contract — rev0085

`data/current_search_action_contract.json` is the current machine authority for
Search Again eligibility. It separates request class from GUI mode and binds
each case to its packet and current candidate artifact.

The validator rejects, among other mutations:

- making the persistent action visible again;
- inventing persistent refresh semantics;
- clearing persistent seen history;
- returning ordinary pages to same-token retry;
- removing stable identity from manual wishlist pages;
- pretending the current candidate solves `WISHLIST-CAP-01`.

This corrects a cube weakness: earlier prose and one cumulative patch encoded
several packet policies without a per-packet applicability contract. The
candidate artifact ledger now declares packet IDs explicitly, and the
independent cap packet is bound to no candidate.
