# ADR 0055 — Garden sentinel is local autocuration, not reputation

Garden nodes can be scored locally from proof and witness evidence. That score must not become a global reputation ledger or truth authority.

Decision: add `gardensentinel.py` as a private evidence-to-salience surface. Semantic lies cost heavily; useful refusal is a small positive; witness contradiction quarantines locally.
