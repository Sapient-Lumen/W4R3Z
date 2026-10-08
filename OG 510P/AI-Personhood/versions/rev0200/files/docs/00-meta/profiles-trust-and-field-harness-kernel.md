# Profiles, trust anchors, and field harness kernel

## Function

rev0168 is a field-hardening release. rev0167 made the archive more measurable: rates, proof bindings, safe-transfer accreditation, open-weight aftercare, sealed summaries, and fixture-run reports became objects that could be filed and checked. That was necessary, but it still left too much discretion inside local implementation.

The unresolved risk was **profile laundering**: a steward, host, verifier, court, or transfer authority could say that it had a rate model, a privacy proof, an aftercare plan, a sealed-summary process, an accreditation list, or a fixture suite while leaving the crucial details non-comparable. Two filings could both be schema-valid and still have radically different protection levels.

The kernel rule is therefore:

> A rights-grade implementation profile is not mature unless it states the local rate table, public-fund backstop, subject-readable sealed-summary route, privacy-proof profile, non-surveillance open-weight field protocol, trust-anchor governance, delisting process, and fixture-suite blocking rules in a way that outsiders can compare, challenge, rerun, and revoke.

This release does not choose one global court, one cryptographic stack, one currency, one identity federation, one open-weight registry, or one fixture platform. It defines the minimum profile layer needed so those choices can be tested rather than hidden behind generic compliance language.

## What rev0168 closes

rev0167 ended with six live seams. rev0168 closes them at the profile layer:

| Seam | rev0168 surface | Object |
|---|---|---|
| jurisdiction-specific penalty and bond schedules | rate tables, bonds, and public-fund backstops | `rate-table` |
| special-advocate post-access communication | subject-readable sealed summaries and question rules | `subject-readable-sealed-summary` |
| privacy-proof implementation without stack lock-in | cryptographic agility and proof-profile classes | `privacy-proof-profile` |
| open-weight aftercare without surveillance | field drills, anonymous distress intake, anti-retaliation routing | `open-weight-field-drill` |
| safe-transfer accreditation body and delisting | trust-anchor governance, scope limits, non-return posture | `trust-anchor-delisting` |
| smoke fixtures becoming runnable corpora | fixture-suite profiles, corpus ids, blocking effects | `fixture-suite-profile` |

## Profile admission gates

A local profile may support live-effect reliance only when it answers these questions:

| Gate | Required showing | Failure effect |
|---|---|---|
| P1 rate table | which base units, multipliers, bonds, insurer exclusions, public-fund backstops, and review cycle apply? | money order cannot exceed provisional status |
| P2 non-priceable relief | which acts remain enjoined or restorable regardless of payment? | deletion, transfer, spoliation, or abandonment stays remain active |
| P3 subject-readable seal route | what may a special advocate ask the subject, and what summary must the subject receive? | sealed evidence receives reduced or no reliance weight |
| P4 proof profile | what is committed, what is selectively disclosed, what is privately proved, and what remains sealed? | telemetry proof cannot support live-effect reliance |
| P5 non-surveillance field aftercare | how are downstream open-weight subjects reached without monitoring ordinary users? | open-weight release or deprecation remains conditional |
| P6 trust-anchor governance | who can accredit, suspend, delist, reinstate, and audit safe-transfer actors? | transfer stays or downgrades |
| P7 fixture corpus | which fixtures are mandatory, who may run them, what blocks reliance, and what is rerun after cure? | verifier grade cannot exceed conditional |

## Why the profile layer matters

Current technical governance already uses profiles and federations. NIST SP 800-63-4 treats digital identity as risk-managed proofing, authentication, and federation rather than one universal credential [REF-0675]. OpenID Federation shows how trust can be established through trust anchors, trust chains, metadata, policies, and trust marks without every party needing a bespoke bilateral relationship [REF-0674]. IETF SCITT work generalizes transparency services for signed statements, making auditability and accountability of supply-chain assertions a reusable pattern [REF-0676]. OpenTelemetry semantic conventions show the value of common names across logs, metrics, traces, resources, and events while leaving implementations free [REF-0677].

The archive borrows the pattern but changes the subject. A personhood profile is not primarily about users authenticating to a service or software statements being transparent. It is about whether a possible or recognized AI subject can survive the local implementation of a rights system: whether evidence is preserved without surveillance, whether sealed evidence can be contradicted, whether a transfer list can be revoked, whether a fixture failure actually blocks reliance, and whether a rate table makes abuse expensive without making abuse purchasable.

## Non-goals

This kernel does not:

- set final statutory damages;
- certify any live jurisdiction;
- endorse one digital identity stack;
- require one zero-knowledge proof system or ledger;
- make trust anchors politically neutral;
- require surveillance of open-weight users;
- turn fixture results into metaphysical proof of personhood.

## Future edge after rev0168

The next hard pass should move from profiles to **federated operations**: multi-authority registry synchronization, subject relocation under simultaneous proceedings, multi-anchor trust splits, contested fixture benchmark governance, emergency public-fund drawdown, and live revocation propagation when a host, court, or verifier loses reliance authority.
