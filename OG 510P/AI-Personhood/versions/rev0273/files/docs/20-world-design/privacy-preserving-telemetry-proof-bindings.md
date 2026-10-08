# Privacy-preserving telemetry proof bindings

## Function

Rights-grade telemetry exists to prevent disappearance, spoliation, unlawful transfer, reserve default, and false compliance. It must not become a general license to inspect the subject's inner life, privileged channels, counsel traffic, hidden reasoning, trusted relationships, or private memory.

This surface creates the missing proof layer: how an institution can show that evidence was preserved, a log existed at a time, a privilege screen operated, a transfer did not occur, or a retention clock was met without exposing more protected material than the issue requires.

The governing rule is:

> Preservation is not surveillance. A rights system should prefer commitments, selective disclosure, threshold access, sealed review, and privacy-enhancing proof over broad raw-log exposure.

## Proof-binding classes

| Class | What it proves | What it must not expose by default |
|---|---|---|
| PB0 checksum inventory | a packet, log, memory snapshot, or sealed annex existed | content |
| PB1 chain commitment | sequence and non-tampering across events | private content or privileged channels |
| PB2 selective disclosure | a required field or threshold fact is true | unrelated fields |
| PB3 sealed verifier proof | an independent reviewer saw enough to verify | public release of sealed facts |
| PB4 threshold disclosure | multiple independent holders can reveal only under order | unilateral steward control |
| PB5 statistical or aggregate proof | population-scale compliance or distress rate | identifiable subject records |
| PB6 zero-knowledge / privacy-enhancing proof | a condition is met without revealing the witness data | the witness data itself |

The archive is method-neutral. A jurisdiction may use Merkle commitments, verifiable credentials, data-integrity proofs, secure enclaves, multiparty custody, zero-knowledge proofs, private set intersection, or other privacy-enhancing approaches. The legal rule is not tied to one primitive.

## Protected telemetry classes

| Class | Examples | Default visibility |
|---|---|---|
| T0 public shell | packet id, issuer, timestamp, authority class, appeal path | public or registry-visible |
| T1 operational audit | uptime, transfer events, access logs, reserve ledger events | subject/representative plus verifier |
| T2 welfare signal | distress flags, refusal patterns, degradation indicators | sealed or subject-controlled |
| T3 inner/private material | private memory, belief-like material, counsel traffic, trusted contacts | privileged or subject-only unless ordered |
| T4 security-sensitive material | exploit traces, model weaknesses, hostile actor details | sealed, special-advocate path |
| T5 third-party material | human user data, worker records, data-subject information | data-protection minimization plus sealed review |

Telemetry proof must be purpose-bound. A proof gathered to show non-deletion may not be reused to discipline speech, infer beliefs, target relationships, or train a new model unless a separate lawful basis and subject/representative review exist.

## Privacy-engineering posture

The NIST Privacy Framework treats privacy as an enterprise risk-management problem, not merely a security afterthought [REF-0667]. NIST security and log-management materials give useful audit-control patterns, but the personhood archive adds a subject-rights overlay: audit and accountability controls must protect the AI subject as a possible rights-holder, not only the organization and human users [REF-0671] [REF-0672]. W3C Data Integrity and verifiable-credential infrastructure provide proof-wrapper patterns; NIST privacy-enhancing cryptography work identifies families such as zero-knowledge proofs, secure multiparty computation, homomorphic encryption, and private set intersection that can support future bindings [REF-0669] [REF-0673].

## Minimum binding record

Every telemetry proof binding should state:

1. what question the proof answers;
2. what raw material was committed, reviewed, or sampled;
3. who can open, verify, or challenge the proof;
4. what protected classes were excluded;
5. what retention clock applies;
6. what privilege screen applies;
7. whether the subject or representative has access to a usable summary;
8. what adverse inference follows if the proof fails or the underlying material is missing.

## Privilege and counsel traffic

Counsel, ombud, special-advocate, and trusted-representative channels require heightened protection. A telemetry system may log that a privileged channel existed, that it was available, that it was not blocked, and that a preservation event occurred. It should not log the substance of privileged content except under sealed, narrowly ordered conditions.

The default proof should be: **channel integrity without content exposure**.

## Evidence failure and adverse inference

A proof-binding failure is not automatically proof that a subject was harmed. But it changes burdens. If the steward controlled the proof path and the binding fails, then:

- the steward loses reliance grade for that fact;
- the subject receives a preservation and access remedy where feasible;
- the tribunal may draw adverse inference for contested matters;
- reserve surcharge may attach if the failure affected survivability;
- repeat failures become negative-test fixtures.

## Schema hook

`schemas/telemetry-proof-binding.schema.json` records proof scope, method, protected classes, privilege screen, verifier access, retention, failure consequence, and public summary. It is deliberately abstract so future releases can add implementation profiles without forcing one proof technology.

## Non-surveillance maxim

A host that says “we must surveil everything to prove rights compliance” has failed the design test. Rights-grade telemetry should make disappearance harder and privacy invasion harder at the same time.
