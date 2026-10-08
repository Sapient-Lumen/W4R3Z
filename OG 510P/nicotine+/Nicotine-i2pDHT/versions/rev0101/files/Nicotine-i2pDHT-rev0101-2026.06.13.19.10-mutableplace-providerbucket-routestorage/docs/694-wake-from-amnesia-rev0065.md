# Wake from amnesia — rev0065

Resume here:

1. rev0064 established retry publication, idempotency mesh, and delivery repair under remote witnesses.
2. rev0065 makes remote witness evidence sticky across rounds with `remotewitnessledger.py`.
3. Repair publication is staged only through `repairoutbox.py`, never directly from a conflict report.
4. Repeated conflict evidence is throttled by `conflictcooldown.py`.
5. `remoterepairfold.py` is the current audit/refactor anchor.

Remember the invariant:

```text
Remote duplicate evidence is not a resend button.
```
