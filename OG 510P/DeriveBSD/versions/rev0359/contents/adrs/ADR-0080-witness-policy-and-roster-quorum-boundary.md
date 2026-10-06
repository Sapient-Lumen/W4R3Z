# ADR-0080: Witness policy and roster/quorum boundary

- Status: Accepted
- Date: 2026-03-07

## Context

DeriveBSD already had the main transparency evidence objects:

- `release.transparency.entry`,
- `log.checkpoint.receipt`,
- `transparency.monitor.policy`,
- `transparency.monitor.snapshot`,
- and `release.authority.policy` / `release.publish.receipt` for the real publish gate.

The archive had already decided that transparency evidence is not publication authority.
What remained too soft was **witness trust itself**.

The docs still risked implying that witness trust came from one of three accidental places:

- inline quorum integers on whichever policy object happened to mention them,
- the witness ids that happened to appear in a receipt,
- or external service/community discovery tables.

That is too ambiguous for all four product shapes:

- **A / fleet host** and **D / appliance factory / regulatory** need offline-verifiable witness trust that can be mirrored and audited without dynamic service lookups.
- **B / workstation** needs witness shortfalls to be explainable rather than backend folklore.
- **C / general-purpose OS** needs optional/community witness lanes without letting monitor config quietly become the source of truth.

Current transparency practice points the same way:

- Sigsum makes trust policy an explicit verification input.
- Witness networks are coordination surfaces, not a substitute for local trust policy.
- Witnessed checkpoints are portable evidence, but they only mean something relative to a chosen witness policy.

## Decision

DeriveBSD will treat witness trust as a **digest-bound policy artifact**.

1. `witness.policy` becomes the authoritative object for:
   - which logs it applies to,
   - which witnesses count,
   - operator-diversity grouping,
   - quorum thresholds,
   - and shortfall behavior.

2. `log.checkpoint.receipt` remains **checkpoint evidence only**, but it must bind:
   - `witness_policy_digest`
   - `quorum_verdict`

3. `transparency.monitor.policy` may reference `witness_policy_digest`, but it does not get to silently define witness trust with ad-hoc quorum integers.

4. `release.authority.policy` may require a specific `witness_policy_digest` for publication review whenever transparency is required.

5. `release.publish.receipt.transparency_verification` may summarize the witness-policy result at publish time, but publication authority still terminates in the threshold-signed publish receipt.

6. Witness network discovery surfaces remain useful for coordination and operator diversity, but they are **not** the authoritative trust root for a given DeriveBSD channel.

## Consequences

### Positive

- The archive now has one compact answer to “which witnesses count?”
- Witness shortfalls become explainable and reviewable instead of ambient backend behavior.
- A/D can mirror witness evidence offline without smuggling in trust changes.
- B/C can consume public/community witness ecosystems while still pinning local policy.

### Trade-offs

- One more typed artifact enters the transparency lane.
- Authority and monitor examples must now carry another digest join.
- Operators must express roster rotation and shortfall handling explicitly instead of assuming whatever the backend currently advertises.

## Follow-up

This ADR does **not** settle:

- the final default witness-policy values by product shape,
- witness-policy distribution/rotation transport,
- or whether certain channels should require monitor diversity in addition to witness diversity.

Those remain implementation and posture questions.

## Why this is coherent with the rest of the archive

This follows the same boundary discipline now used elsewhere:

- release transparency is evidence, not authority,
- publisher identity evidence is supplemental,
- workflow verification is supplemental,
- and witness trust should likewise be explicit policy rather than inferred service state.
