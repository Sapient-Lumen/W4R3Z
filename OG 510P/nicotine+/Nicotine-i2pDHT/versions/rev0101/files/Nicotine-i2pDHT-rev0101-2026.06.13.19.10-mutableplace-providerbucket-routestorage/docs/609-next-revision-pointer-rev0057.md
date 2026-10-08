# Next revision pointer — rev0057

Suggested rev0058 codename: `deadletterstore-retrydrain-reconcilesmoke`.

Suggested focus:

- store dead-letter/retry/reconcile observations in a signed replay lane;
- add retry drain receipts so retry attempts do not loop forever;
- connect effect reconciliation to safe cleanup and chaos budget grants;
- add no-network smoke transcripts for the first future live attempt after reconcile;
- continue reducing fold-registry duplicates without deleting wake-from-amnesia history.
