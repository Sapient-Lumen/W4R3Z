# Voter-facing verification story (Track A)

**Track:** A (Deployable core)


This is the **honest** story a voter should be told about verification in a Track A deployment.

Track A is designed so that **independent verification is possible**, but it does not assume
every voter becomes a cryptographer.

Do not accept the adversarial framing: “if you can’t verify the cryptography yourself, you can’t trust the election.”
Track A’s promise is that **enough independent parties can verify**, and that their verification work is itself auditable and comparable.

## What you can personally verify (low effort)

- **Authentic official statements:** check the PublicNotice digest on an official channel and compare with mirrors (`194`, `195`).
- **That a public packet hasn’t been altered:** anyone can run the offline verifier on a packet they received (`observer-kit/`, `177`).
- **That the jurisdiction is meeting its publication promises:** coverage/suppression reports can be checked by many parties (`187`).

## What you usually rely on others to verify (and why that can still be trustworthy)

Some checks (log consistency, witness quorum enforcement, large-scale parity monitoring) are work.
The system’s posture is: **many independent parties do the heavy verification**, and their verification is itself auditable.

You can evaluate those parties by looking for:
- published identities + funding/COI disclosures (witness and monitor governance; `135`, `131`),
- published monitor attestations and verifier reports you can replay (`131`, `193`),
- published witness **liveness+dissent** reports you can compare (kind `hfv.witness.liveness_dissent_report`; `135`),
- disagreement/dissent surfaces (a “perfectly quiet” ecosystem can be a warning sign).
- a pre-election directory of who intends to publish replayable verifier output and where to find it (kind `hfv.verifier.capacity_roster`; `docs/241-verifier-capacity-and-distribution.md`).

## Who verifies on your behalf (representation duty)

If you cannot run a verifier or follow technical disputes, you still have agency: **evaluate the representatives** who verify at scale.
Track A treats monitors/witnesses/civil society/journalists/campaigns as *representatives* whose work must be replayable and whose incentives must be visible.

Look for:
- disclosed identities + funding/COI,
- verifier reports you (or others) can re-run offline,
- a public record of disagreements and corrections,
- evidence that multiple independent groups are checking the same packets.

See also: `PERSONS_PATH.md`.

## If you’re worried something is wrong

- Look for the latest PublicNotice/status surface update and its **next_update_at** commitment (`219`).
- Look for a **packet digest** for any major claim (e.g., “results release”, “suppression report”) and whether multiple mirrors agree (`194`, `211`).
- If official channels disagree or go silent, that *silence* should produce evidence (coverage/suppression reports, liveness beacons; `187`, `210`).

## What Track A does not promise

Track A does not promise that:
- your personal device is uncompromised,
- remote voting in uncontrolled environments is coercion-resistant,
- everyone will check every proof.

## Material floor (when devices or networks fail)

The recovery floor is physical: paper ballot of record + chain of custody + audits/recounts.
Digital evidence is designed to remain mirrorable and verifiable **offline** (observer kit).

Track A promises a narrower but critical thing:
when elections are contested, **there is portable evidence that can be checked by independent parties**,
and missingness or split-views can be proven rather than argued about.

See `docs/167` for boundaries.


## Red flags (how to tell the ecosystem is not doing its job)

- The only response is “trust us” (no signed notice/packet digest exists).
- No independent verifier output shows up (no replayable reports; no dissent; only official narrative).
- All “independent” verifiers share the same funder/provider or publish identical copy.
- Official surfaces change without correction-chain semantics (no links, no effective-state rules).
- Mirrors disagree on bytes/digests and nobody publishes a split-view note.
