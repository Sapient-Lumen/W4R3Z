# Chaos budget after post-effect recovery

`chaosbudget.py` models budget grants for expensive post-effect work: restart replay, effect recovery, safe cleanup, fuzz shrink, retry probes, dead-letter handling, and future SAM canary rehearsal.

The point is not to make testing weaker. It is to keep safety testing from becoming a metadata, CPU, or raw-key leak after a public edge has nearly gone live. The budget lane binds effect seal, recovery mesh, safe cleanup, restart chaos, and fuzz shrink to one action/profile/service/scope/request/payload/idempotency boundary.

Budget rejection is local evidence. It is not payment, reputation, or consensus.
