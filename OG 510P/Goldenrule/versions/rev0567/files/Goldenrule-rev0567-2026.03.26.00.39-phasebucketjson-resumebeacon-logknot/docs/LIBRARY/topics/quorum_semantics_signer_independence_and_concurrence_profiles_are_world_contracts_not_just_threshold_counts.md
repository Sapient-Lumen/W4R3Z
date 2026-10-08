# Quorum semantics, signer independence, and concurrence profiles are world contracts, not just threshold counts

Verified issuers, preserved standing rules, and replayable policy snapshots are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **how many distinct actors had to concur, what counted as distinct, and whether a satisfied threshold actually represented independent judgment or only duplicated signatures inside one control plane**.

- `RS-GR-394` shows that NIST key-management guidance expects some keying material to be distributed as key components with dual control and split knowledge required, so “more than one person” can be part of the security contract rather than an implementation flourish.
- `RS-GR-395` shows that the current TUF specification makes every role depend on one or more keys plus a signature threshold, requires threshold counting over the role's keys, and warns that the root threshold should make compromise of all offline keys extremely unlikely, so a threshold is about surviving partial compromise and not just collecting redundant signatures.
- `RS-GR-396` shows that the current in-toto specification says a step threshold is the number of link metadata pieces required for verification and is intended for higher-trust steps where multiple functionaries perform the operation and report the same results, so concurrence semantics can be part of the claim itself and not just of key ceremony.
- `RS-GR-397` shows that Sigsum trust policy can require that at least a declared witness quorum verify append-only behavior before a log is trusted, so transparency trust can depend on explicit witness concurrence and not only on one log signature.
- `RS-GR-398` shows that the current SCITT architecture allows the same statement to be registered in multiple transparency services to produce multiple independent receipts and says relying parties decide which issuers and transparency services to trust, so multi-service concurrence is a first-class policy dimension and not merely extra paperwork.
- `RS-GR-399` shows that the current TUF specification forbids counting multiple signatures with the same keyid toward a threshold, which makes the archive's distinctness problem explicit: numeric threshold claims only mean something when the unit of distinctness is published.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **threshold rules, distinctness class, separation-of-duty assumptions, witness quorum, or multi-service concurrence policy** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat “it reached threshold” as the end of the story.

At minimum, it should distinguish between:

1. a world where any single authorized signer or service may decide alone;
2. a world with nominal threshold counts, but where the counted signatures still come from one operator, one HSM boundary, one CI system, or one organization;
3. a world where distinct keys are required, but the archive does not preserve whether those keys represented distinct people, roles, services, or compromise domains;
4. a world where independent witnesses, issuers, or transparency services concur, but the precise quorum rule, fail-open behavior, or veto semantics remain local folklore;
5. a world where future inheritors can replay the full concurrence profile — unit of distinctness, threshold or quorum, control-domain assumptions, required witness / service diversity, and emergency-degraded behavior — and see why one claim counted as collectively endorsed while another merely collected duplicate assent.

These are different worlds.
They change whether future inheritors can merely count signatures, reconstruct whether a threshold represented real separation of duty, or detect that a later replay silently collapsed multi-party assurance into one administrative domain.

So quorum semantics, signer independence, and concurrence profiles belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, successor-safe authenticity, or replayable long-horizon verification should publish at least:

1. the exact concurrence rule for each critical action: issuance, approval, transparency registration, supersession, recovery, or revocation;
2. what unit counts as distinct for threshold purposes: key, functionary, human approver, workload, organization, transparency service, witness, or administrative domain;
3. which independence assumptions are required for success: separate operators, separate hardware boundaries, separate parent identities, separate organizations, or separate policy domains;
4. whether the system fails closed or degrades gracefully when quorum is missing, witnesses disagree, or only same-domain signers are available;
5. whether different actions require different concurrence profiles, such as ordinary issuance versus emergency recovery or root rotation;
6. how concurrence profiles are rotated, audited, or re-established after compromise, staffing loss, or witness / service churn.

Without that compact contract, future inheritors can mistake duplicated assent, cheap threshold inflation, or collapsed independence classes for Golden-Rule progress.
