# Egress meter metadata budget

Provider proof, repair, route gossip, witness publication, STORE, and SAM sends all spend something.  Sometimes they spend bytes.  Sometimes they spend stream slots.  Sometimes they spend metadata by exposing a content key or making an interest visible to a provider family.

`egressmeter.py` makes that spend explicit.  It checks freshness, byte budget, stream budget, raw-key exposure ceiling, destination-family caps, risky-egress diversity, real/decoy provider-probe ratio, and replayed egress events.

The point is not a privacy proof.  The point is to prevent a local success from creating unbounded outbound work.
