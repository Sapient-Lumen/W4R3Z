# ADR 0101 — evidence GC normalizes cross-surface negative pressure

Decision: custody audits, tombstone mesh reports, witness-cache summaries, and revocation verdicts are normalized into typed evidence before GC.

Reason: if GC only sees soft convenience evidence, stale provider/latest observations can bury tombstones, revocations, forks, and false custody proofs.

Consequence: `custodygc.py` synthesizes local `EvidenceItem` records and then reuses the ordinary GC pass.
