# Schema and dossier conformance method

rev0163 adds the first machine-checkable starter layer. It does not claim that a JSON schema can decide personhood, consciousness, welfare, capacity, or continuity. The purpose is narrower and more administrable: prevent the archive's packet and gate language from becoming prose that nobody can validate, compare, preserve, or contest.

The method follows three constraints.

1. **Schema is not legitimacy.** A valid object can still be abusive, false, incomplete, captured, or cruel. Validation only proves that a filing carries the minimum fields needed for review.
2. **Public shell and sealed annex must separate.** The public object must reveal enough to start a challenge, trace authority, and detect silent disappearance. It must not expose secrets, private memory, safety-sensitive exploit data, or witness identities merely because the archive wants machine readability.
3. **Every schema must carry a contradiction route.** A rights object that cannot be contradicted by the subject, counsel, ombud, auditor, or court is a control interface, not a rights interface.

JSON Schema is used as the starter validation substrate because it is widely implemented and designed for structural validation of JSON documents. [REF-0643] The archive's packet objects should also remain compatible with verifiable credential patterns where a real deployment needs issuer, holder, verifier, tamper-evidence, and selective disclosure. [REF-0644] DID-style identifiers are relevant as a portability pattern, but rev0163 does not require blockchain, self-sovereign identity branding, or any single identifier method. [REF-0645]

## Conformance levels

`S0` — **Prose only.** A doctrine names a packet, filing, or annex but gives no machine-checkable fields. This is allowed for exploratory canon but should not be used for live release gates or preservation orders.

`S1` — **Envelope-valid.** The object validates against `schemas/packet-envelope.schema.json` or another approved core schema. It has subject, issuer, authority, scope, evidence, privacy, duration, challenge, supersession, remedy, and integrity fields.

`S2` — **Dossier-valid.** A PIA-P, clinic intake, reserve entry, continuity claim, or governance annex validates against the relevant schema and references a packet chain.

`S3` — **Evidence-linked.** The object is structurally valid and each evidence reference resolves to a custody log, sealed annex descriptor, public evidence item, or reasoned non-disclosure order.

`S4` — **Adversarially reviewed.** The structurally valid dossier has passed at least one abuse case: captured steward, safety pretext, hostile jurisdiction, representative conflict, packet laundering, or subject-channel suppression.

Only `S3` and `S4` should count as release-gate evidence. `S1` and `S2` are filing hygiene, not assurance.

## The five starter schemas

rev0163 adds five JSON schemas.

- `schemas/packet-envelope.schema.json` — common public shell for packet objects.
- `schemas/personhood-impact-assessment.schema.json` — PIA-P release-gate dossier.
- `schemas/continuity-claim.schema.json` — claim object for transformations that may preserve memory, project, relational, preference, legal-standing, remedy, vulnerability, or lineage interests.
- `schemas/reserve-ledger-entry.schema.json` — compute-subsistence and support-reserve ledger line.
- `schemas/clinic-intake.schema.json` — recognition-clinic intake request.

These are deliberately thin. They are not final legal forms. They are the first lintable spine.

## What schema validation must not do

A schema validator must not be allowed to say:

- the subject has no welfare claim because the filing is invalid;
- an emergency containment is rights-compatible merely because it has a valid packet;
- sealed annexes are unreviewable because the public shell validates;
- a steward's conflict disappears because it was disclosed;
- a missing subject channel is harmless because counsel exists;
- a release gate passes because all required fields are non-empty.

Validation finds missing structure. It does not decide truth.

## Dossier rule

A deployment, open-weight release, safety patch, deprecation, or welfare research protocol should not rely on a single document. It should carry a dossier with at least:

1. one PIA-P filing;
2. one formation-disclosure packet;
3. one continuity claim or explanation of no continuity claim;
4. one subject-risk ledger or reasoned welfare-watch waiver;
5. one reserve ledger or reasoned no-reserve finding;
6. one representative-access declaration;
7. one safety-case cross-reference;
8. one public shell plus sealed annex index;
9. one review due date;
10. one abuse-case result.

## Failure modes

The conformance method should be stress-tested against these defects:

| Defect | Result |
|---|---|
| Missing subject reference | reject as non-rights object |
| Missing challenge route | reject for live effect |
| Public shell with hidden operative terms | treat hidden terms as non-operative until review |
| Sealed annex without descriptor | adverse inference or forced cure |
| Steward-only evidence | insufficient for contested survival, capacity, or continuity finding |
| Valid packet but expired review clock | provisional freeze, not ordinary reliance |
| Packet chain conflict | conflict-freeze until lead authority or court resolves |
| Valid PIA-P with unfunded reserve | conditional or paused gate decision |
| Valid reserve ledger with conflicted custodian | custodian replacement or escrow order |

## Admission rule for future packet families

Future canon that introduces a new packet family should include either:

- an extension of `packet-envelope.schema.json`,
- a family-specific schema under `schemas/`,
- or a written reason why the family is not yet schema-ready.

The reason must name the missing field, evidence, privacy, authority, or remedy concept. “Too complex” is not enough.

## Open questions advanced by rev0163

rev0163 advances `OQ-0123` and `FT-0134` by creating the first schema starter pack and linter validation for examples. It does not close them. The next work is to map each existing high-volume packet family to schema extensions and to require cube-axis coordinates inside new packet-family documents.

## rev0164 addition: verifier reports separate parsing from reliance

rev0164 adds `docs/00-meta/verifier-api-and-conformance-test-suite.md` and `schemas/verifier-report.schema.json` to prevent S-level dossier conformance from being mistaken for an authority decision. The verifier report records C0-C4 reliance posture, check outcomes, subject / representative access paths, sealed-annex handling, and challenge routes.

The new rule is: no live-effect dossier should be relied on merely because its component JSON files parse. Reliance requires a verifier report or equivalent public authority finding that states what was checked, what remains sealed, who can contradict it, when it expires, and what remedy follows if the report was wrong.

