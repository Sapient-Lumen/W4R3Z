# Evidence acquisition topology, challenge binding, and observation scope are world contracts, not just retained evidence

Portable evidence packets, policy snapshots, replay diagnostics, and baseline corpora are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **how the evidence was acquired, what freshness / handle contract bound it, which claims were actually collected, and which intermediaries or observation surfaces stood between the subject and the verdict**.

- `RS-GR-421` shows that RFC 9334 defines Evidence as Attester-produced information appraised by a Verifier and distinguishes the Passport and Background-Check topological patterns, which means the same trust claim can reach a relying party through materially different evidence-routing contracts.
- `RS-GR-422` shows that the current RATS reference-interaction draft makes the Handle and optional Claim Selection part of the evidence-request contract, cryptographically binds Claims, Handle, and Attester identity information to the Evidence signature, distinguishes passport versus background-check flows, allows unsolicited uni-directional pushes, and defines streaming / brokered collection patterns, which means acquisition topology and requested claim scope are part of what a future inheritor must replay.
- `RS-GR-423` shows that RFC 9711 says all EAT use MUST provide a freshness mechanism, that the EAT nonce supports multistage consumption, and that the nonce MUST have at least 64 bits of entropy, which means freshness-binding quality is part of evidence admissibility and not an afterthought.
- `RS-GR-424` shows that the current nonce-based freshness draft for attestation-bearing CSRs reiterates the 64-bit-entropy and privacy-preserving-randomness requirements for nonces, which means even when attestation is embedded inside another workflow, freshness provenance remains a first-class acquisition contract.
- `RS-GR-425` shows that `in-toto-run` records materials, products, executed command, return value, stdout, and stderr into signed link metadata, and even allows a `--no-command` signed-off-by step, which means “evidence” already depends on what observation fields a collection tool chose to capture.
- `RS-GR-426` shows that `in-toto-verify` requires evidence to exist as step link metadata, checks thresholded link presence, authorized functionary signatures, step artifact rules, layout expiry, and keeps verification isolated from external key metadata, which means admissible evidence depends on concrete capture form and local verification boundary rather than on an abstract story about what happened.
- `RS-GR-427` shows that the `in_toto_record_start` / `in_toto_record_stop` API can preserve preliminary and final link metadata, command/byproducts, and environment information for steps that cannot be captured as one wrapped command, which means capture staging and environment scope can change what future inheritors are actually able to inspect.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **evidence-collection topology, request / handle freshness, claim-selection scope, relay / broker trust, captured observation fields, or capture staging** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat “we retained the evidence blob” as proof that replay conditions are complete.

At minimum, it should distinguish between:

1. a world where evidence survives only as a final blob, but no one can tell whether it was direct challenge/response, cached passport-style reuse, relayed background-check, or unsolicited / streaming collection;
2. a world where freshness exists, but the archive cannot tell who generated the nonce / handle, whether it was verifier-specific, or whether it was stale by the time the verdict was rendered;
3. a world where the archive preserves the evidence bytes but not which claims, event logs, attestation-key ids, or environment fields were requested versus omitted;
4. a world where intermediaries such as relying-party relays, brokers, handle distributors, or call-home trigger paths were trusted in practice but not recorded as part of the evidence path;
5. a world where future inheritors can compare the same subject under multiple acquisition contracts and tell whether a verdict changed because the cooperative problem changed or because the observation contract changed.

These are different worlds.
They change whether future inheritors can merely re-read a retained payload, replay the same acquisition boundary, or separate institutional improvement from evidence-collection drift.

So evidence acquisition topology, challenge binding, and observation scope belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, successor-safe authenticity, or replayable long-horizon verification should publish at least:

1. the exact evidence-acquisition model for each material verdict: direct challenge/response, cached passport-style result, background-check relay, uni-directional push, streaming subscription, brokered distribution, or another explicitly named pattern;
2. who generated the freshness handle / nonce / trusted timestamp, what entropy or secure-time assumptions applied, how that freshness token was bound to the evidence, and how verifier-specific or replay-resistant it was;
3. what claim-selection, subject-selection, event-log, attestation-key-id, or environment-capture scope was requested, and whether omitted fields mean absent, unknown, intentionally filtered, or not collected;
4. any intermediary roles that participated in evidence handling — relying-party relay, broker, handle distributor, cache, call-home trigger, or mirror — plus the trust and audit assumptions placed on them;
5. what concrete observation fields were captured locally: materials, products, command, byproducts, stdout / stderr, environment, workdir, timestamps, and any staged start/stop capture boundary for multi-step evidence;
6. what the verifier did when evidence was stale, partially collected, claim-filtered, relay-corrupted, or missing required capture fields.

Without that compact contract, future inheritors can mistake evidence-collection drift for Golden-Rule progress.
