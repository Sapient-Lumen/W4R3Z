# Witnessed checkpoints, split-view resistance, and cross-perspective consistency are world contracts, not just append-only logs

Recent transparency-log work adds one more missing layer beneath append-only publication and monitor plurality for any successor-facing archive or provenance lane.

- `RS-GR-341` shows that a witness only cosigns a new checkpoint after verifying a consistency proof from previously observed state, so witnessed checkpoints change the security contract from "the log says it is append-only" to "independent parties attest that this checkpoint extends prior history."
- `RS-GR-342` shows that witnessing is specifically about preventing split-view attacks and that diverse custodianship of witness devices matters, so anti-equivocation is partly a topology question rather than only a proof-format question.
- `RS-GR-343` shows that witness presence is not enough by itself because a trust policy still needs an explicit quorum rule saying how many witnesses must agree before the log is trusted.
- `RS-GR-344` shows that multi-witness security also depends on sustainable discovery and onboarding of logs and witnesses, so configuration governance is part of the world contract rather than deployment trivia.
- `RS-GR-345` shows that client devices can verify inclusion and consistency themselves, cross-check state across a user's own devices, and gossip hashes to detect split views, so anti-equivocation can live in user-facing verification paths as well as in third-party monitors.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **checkpoint witnessing, witness quorum, cross-perspective consistency, or split-view detection architecture** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat one append-only log as a complete provenance design.

At minimum, it should distinguish between:

1. a world with an append-only log but no witnesses and no client cross-checking;
2. a world with one or more witnesses but no explicit quorum rule;
3. a world with a declared witness quorum but fragile or ad hoc witness onboarding;
4. a world with witness quorum plus client-side consistency checks across devices or peers;
5. a world with witness quorum, client cross-checking or gossip, and declared escalation when equivocation evidence appears.

These are different worlds.
They change whether the archive merely publishes history, makes split views expensive, gives successors durable quorum evidence, or lets end users and inheritors detect that they are being shown a different reality.

So witnessed checkpoints and cross-perspective consistency belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, successor-safe authenticity, or anti-equivocation resilience should publish at least:

1. which witnesses are trusted, how they are discovered / onboarded, and whether witness trust is pinned, TOFU, or externally governed;
2. the witness quorum rule and whether checkpoints remain useful if some witnesses are unavailable;
3. whether clients, monitors, or both verify consistency proofs, and whether users can validate bundled / self-contained checkpoint evidence offline;
4. whether the system cross-checks state across a user's own devices, between peers, or through gossip / witness networks;
5. what happens when equivocation evidence appears: reject, warn, fall back, re-register elsewhere, freeze use, or escalate to a repair / incident path.

Without that compact contract, future inheritors can mistake witnessed checkpoints or gossip-backed consistency for Golden-Rule progress.
