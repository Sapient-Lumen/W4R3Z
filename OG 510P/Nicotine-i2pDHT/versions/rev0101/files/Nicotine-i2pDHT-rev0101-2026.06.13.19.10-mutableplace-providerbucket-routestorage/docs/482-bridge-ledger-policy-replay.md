# Bridge ledger policy replay

`bridgeledger.py` joins public bridge refresh/withdraw signals with current policy, bridge epoch, announcement digest, moderation quarantine, redress receipts, stale-announcement scans, and hard-negative scans.

The risky bug class is simple: a public bridge can look valid while replaying an old policy or ignoring a fresh abuse quarantine. The bridge ledger catches stale policy digests, epoch drift, signal forks, replay, unresolved quarantine, missing redress, watch-policy pressure, and hard negatives before a future refresh/withdraw side effect is allowed.

The ledger permits two broad outcomes: fresh public refresh, or withdrawal/repair. It does not create global moderation truth.
