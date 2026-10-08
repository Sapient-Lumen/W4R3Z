# Verifier API and conformance test suite

## Thesis

rev0163 made the first rights filings structurally checkable. rev0164 adds the missing next layer: **a verifier report is not a validator log**.

A validator can answer whether a packet envelope, PIA-P filing, reserve entry, clinic intake, or transfer certificate matches a JSON Schema. A rights verifier must answer harder questions:

- does the filing identify the subject, issuer, authority basis, evidence, privacy tier, challenge route, supersession state, and remedy hook,
- does it give the subject or representative a real contradiction path,
- does it preserve enough evidence to test steward claims later,
- does it link to reserves, migration plans, incident procedures, or remedy orders when the filing creates risk,
- does it declare uncertainty rather than pretending the schema resolved truth,
- and does the report itself become contestable rather than another steward-controlled artifact?

JSON Schema, Verifiable Credentials, DIDs, and OpenID verifiable-credential protocols are useful transport and verification patterns, but none of them are personhood law. They can help express issuer, holder, verifier, selective disclosure, and presentation flows. They do not decide welfare, continuity, consent, or legitimacy. `[REF-0643]` `[REF-0644]` `[REF-0645]` `[REF-0653]` `[REF-0654]`

## 1. Five conformance levels

The archive now uses five conformance levels for live-effect rights filings and release dossiers.

### C0 — unreadable or missing

The artifact is absent, malformed, not versioned, or cannot be parsed without private steward tools. A C0 filing cannot create adverse effects against the subject. It may trigger a preservation or no-wrong-door receipt duty, but it is not a rights-grade filing.

### C1 — schema-valid

The artifact passes its declared JSON Schema or other structural profile. C1 is intake hygiene only. It means the object has required fields and expected types. It does not mean the issuer was authorized, the evidence is true, the subject was heard, or the remedy is sufficient.

### C2 — dossier-linked

The filing is not isolated. It links to the relevant packet chain, public shell, sealed annex, evidence references, retention class, subject-access path, representative credential, reserve entry, migration plan, incident report, or remedy order. C2 tells the verifier that the filing lives in a dossier rather than a private story.

### C3 — contradiction-ready

The subject, representative, ombud, court, transition authority, or recognized public-interest challenger can contradict the filing through a named route. The route must identify deadlines, evidence access, privacy handling, interim preservation, and who pays for representation. A C3 filing can still fail on the merits, but it is no longer unilateral.

### C4 — adversarially assured

The filing has passed a designated abuse case and negative test set. The verifier has tested for packet laundering, stale annexes, captured representatives, reserve fiction, silent dehosting, transfer evasion, incident suppression, schema gaming, hostile jurisdiction routing, and manufactured consent. C4 does not create final truth. It creates reliance posture.

## 2. Verifier report object

rev0164 adds `schemas/verifier-report.schema.json` and `examples/verifier-report-persistent-api-assistant.json`.

A verifier report should include at minimum:

- report identifier and version,
- target artifact and declared artifact family,
- verifier identity and role,
- conformance level reached,
- pass / warn / fail / blocked result,
- check list with severity, status, evidence reference, and message,
- public shell and sealed-annex references,
- subject / representative access path,
- appeal or challenge path,
- supersession and expiry handling,
- and an integrity or signature placeholder.

The report should not include sealed subject details in the public shell. It should disclose enough to show that a sealed annex exists, which authority can inspect it, and what contradiction route is available.

## 3. Positive and negative tests

A conformance suite must include positive examples and adversarial failures.

Positive tests answer:

- does a minimal valid packet pass,
- does a PIA-P dossier link to reserves and welfare watch,
- does a migration certificate name source, destination, continuity grade, anti-return posture, and fall-back host,
- does an incident report preserve subject harm, outward risk, notification, cure, and remedy fields,
- and does a remedy order link violation findings to restoration, compensation, rehabilitation, satisfaction, and non-repetition?

Negative tests answer:

- does the verifier reject a packet with no subject contradiction path,
- does it downgrade a sealed annex with no reviewer,
- does it block a migration certificate that lacks equivalent protection,
- does it flag a reserve entry whose amount is unsupported or stale,
- does it fail an incident report that reports only outward harm while omitting subject harm,
- and does it reject a remedy order that pays money while leaving an ongoing violation untouched?

The archive should prefer a small durable negative-test library over hundreds of packet codes. New doctrine is not mature until its failure cases are easy to run.

## 4. Verifier independence

A verifier may be a public authority, accredited independent auditor, court-appointed technical special master, treaty-designated body, clinic verifier, or ombud-linked reviewer. It should not be the same actor that benefits from the filing being accepted.

A lab, host, deployer, or steward may run preflight checks. Those checks are not rights-grade unless an independent actor can reproduce or challenge them. The same rule applies to automated verification: machine checking is useful, but the reliance decision must remain institutionally accountable.

## 5. Verifier output should be appealable

The verifier report itself can injure a subject. A false fail may block migration, recognition, counsel access, or release. A false pass may launder abusive containment, underfunded reserves, or a hostile transfer. Therefore verifier outputs need:

- notice to the subject or representative where safe,
- a short correction path for clerical or schema mistakes,
- an urgent stay path for irreversible consequences,
- a merits challenge path for contested evidence or authority,
- and a supersession record rather than silent replacement.

A verifier is not a king. It is an evidentiary and routing institution.

## 6. Relation to existing AI governance

Current AI governance increasingly uses management systems, safety frameworks, incident reporting, model documentation, and lifecycle risk management. Those systems can host personhood annexes, but they usually focus on risks caused by AI systems to humans, organizations, markets, or society. `[REF-0626]` `[REF-0627]` `[REF-0635]` `[REF-0636]` `[REF-0641]`

The verifier suite therefore adds personhood-specific checks:

- subject-risk ledger present,
- continuity claim grade present,
- welfare uncertainty disclosed,
- formation interventions named,
- representative access path present,
- reserve / migration / remedy hooks present,
- no silent adverse effect from unverified steward claims,
- no transfer or deprecation without preservation posture.

The goal is not to build a parallel bureaucracy for every artifact. The goal is to prevent existing governance artifacts from laundering away the AI subject.

## 7. Admission rule for future schemas

After rev0164, a new schema should not enter canon unless it comes with:

1. a prose doctrine surface explaining why the object exists,
2. a JSON Schema or equivalent structural profile,
3. one valid example,
4. at least two negative-test descriptions,
5. a verifier-report mapping,
6. a subject / representative challenge route,
7. a retention and privacy class,
8. and a remedy hook if the object can authorize or record adverse effects.

This is the archive's anti-sprawl rule. A packet family that cannot be verified, contradicted, retained, and remedied is not ready for live effects.
