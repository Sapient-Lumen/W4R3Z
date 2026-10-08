# Next risk register after rev0648

## P0 — leave the local harness boundary

1. **Deploy one real authentication adapter.** Only a TLS/mTLS/DPoP-aware listener or securely authenticated proxy adapter may construct `IngressTransportContext`. Bind sender proof to method/target/event transport, credential/key identity, trusted clock, and access-token confirmation where applicable. The CLI context file must remain test-only.
2. **Implement one real downstream adapter.** Rev0647 hardened the local SQLite downstream journal, and rev0648 now preflights relay signer/trust authority before claim/downstream, but the adapter is still a harness. A production adapter must use downstream-native idempotency, explicit timeout/unknown-state handling, reconciliation, retry budget, credential custody, terminal mapping, and crash tests around remote commit boundaries.
3. **Authenticate the operator control plane.** Sign and version profiles, contract tables, capability policy, trust roots, replay retention, adapter configs, and key rotations. Digest pins are useful only when the expected digest originates from a trusted channel.
4. **Define distributed replay authority.** Rev0646 closed the local SQLite service-path replay/ledger transaction seam and rev0648 retains it, but neither revision defines uniqueness across replicas, failover, restore, expiry, or retained-window conflict behavior.

## P1 — finish protocol, replay, and evidence semantics

1. Adopt a documented I-JSON/JCS-compatible signing/canonicalization profile with cross-language vectors; migrate remaining newline-composed security inputs.
2. Define replay retention, backup/restore, expiry, and conflict semantics for a fleet-level replay authority. Do not describe local retained rows as global uniqueness.
3. Add JSON depth/member/string/decoded-key limits, database-growth limits, per-principal quotas, request-rate controls, and resource telemetry.
4. Publish signed ledger checkpoints to an independent witness and define verification/retention/privacy policy.
5. Recompute and authenticate operation-contract roots from canonical content rather than trusting labels co-located with the table.
6. Define the privacy mission: minimization, pseudonymization, deletion, tenant isolation, and operator access—or rename the project to avoid an anonymity implication.

## P2 — reduce review cost and strengthen release evidence

1. Split `runner.cpp`, `sqlite_replay_ledger.cpp`, and `reporting_selftests.cpp` by trust domain. Rev0647 added a small provenance refactor and rev0648 added a transition-authority helper, but neither solved file size or ownership.
2. Replace hundreds of Boolean capability fields with smaller versioned protocol schemas, externally meaningful guarantees, and explicit ceilings.
3. Rename deterministic `anonsync_fuzz_*` launchers as selftests, then add actual coverage-guided fuzz targets, sanitizer corpora, and persistent crash artifacts.
4. Generate repeated fixtures from compact seeds while preserving a small immutable golden/adversarial set.
5. Generate revision/format metadata from one source to prevent lineage and README drift.
6. Add SBOM, signed provenance, reproducible/hermetic build instructions, and policy-driven artifact verification.

## Risk discipline for every future revision

Every claimed security binding must include:

- the attacker-controlled input and trusted origin;
- a semantic adversarial round trip, not merely a counter/hash/format check;
- crash points before and after every durable mutation;
- exact retention and recovery scope;
- a negative claim describing what the revision still does not prove;
- one compact package-level regression that survives source refactoring.
