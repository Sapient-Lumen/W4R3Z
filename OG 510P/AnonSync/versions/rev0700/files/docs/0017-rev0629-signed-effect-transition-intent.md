# rev0629 — signed terminal effect-transition intents

rev0628 anchored terminal SQLite/WAL transitions to the prepared ledger row sequence and entry hash from a verified pending-effect recovery report. That prevented a copied effect idempotency key from closing unrelated work, but the public CLI could still close an effect using raw parameters.

rev0629 makes the public transition path intent-driven:

- raw public CLI transition parameters now fail closed;
- the transition command requires a signed intent and a digest-pinned transition trust profile;
- the intent payload uses format `anonsync-effect-transition-intent-payload-v1` and the envelope uses `anonsync-effect-transition-intent-v1`;
- the trust profile uses `anonsync-effect-transition-trust-profile-v1`;
- signatures are RS256 over a typed signing input;
- the signed payload binds the effect key, prepared sequence/hash, terminal state, result digest, reason, prepared ledger head, and transition-chain head.

SQLite/WAL advances to schema v7. `effect_transitions` now stores `transition_intent_id`, `transition_intent_signer_kid`, and `transition_intent_sha256`; those fields are included in the transition hash chain and verified by the read-only snapshot verifier.

This is deliberately smaller than a full outbox worker. It gives a future reconciler a safer local handoff point, but it still does not prove that a downstream system applied the effect, nor does it claim HSM custody, multi-node consensus, or distributed exactly-once semantics.
