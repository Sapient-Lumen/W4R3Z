# Risk register — rev0041

New risk surfaces:

- Router stop can accidentally destroy persistence, cover, or bridge continuity.
- Resume can relaunch service exposure after stale or partial recovery.
- Restart memory can erase hard negatives and make old danger look safe.
- Service/session/router identifiers can drift at the exact moment a local operator believes they are doing cleanup.
- Useful public bridge disablement can still leak through stale announcements or relay tickets if not joined later.

Still unsolved:

- real SAM/i2pd behavior;
- durable database format;
- production cryptographic key policy;
- private retrieval;
- global Sybil resistance;
- mutable-head consensus.
