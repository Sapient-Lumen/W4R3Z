# Inspection gossip deployment checklist

- Choose gossip peers across independent orgs and networks.
- Ensure at least one gossip path survives common failures (CDN outage, BGP diversion).
- Emit `PublicInspectionGossipMessage` at a fixed cadence (e.g., every 5 minutes).
- Archive gossip streams (JSONL) and anchor daily digests into the PBB/ATL.
- Run `inspection_gossip_checker.py` continuously; publish inconsistency reports.
