# 250 — Observation and challenge as evidence surfaces (observer logs, without intimidation)

**Track:** Shared

This spec treats *observation itself* (poll watchers, challengers, nonpartisan observers, and official “public viewing” arrangements)
as a first‑class **evidence surface**: when disputes arise, the question is not “who do we trust?”, but **what did trained observers see,
and can we verify those claims without exposing voters or enabling harassment?**

This is deliberately **non-operational**: it defines safe, publishable artifacts and strict stop-conditions. It does **not** teach tactics for disruption.

## 250.1 External anchors (jurisdiction-specific rules apply)

Observation rules vary by state and local procedure. Use these as *conceptual anchors*, not a substitute for local law:

- EAC overview of poll watchers / election observers (baseline definitions; reminder that rules vary).
- EAC Quick Start Guide: Poll Watchers (official-facing overview + considerations).
- NCSL state-by-state resources on poll watchers/challengers/observers (scope + variance).
- Optional: Bipartisan Policy Center explainer (public-facing framing; non-normative).

## 250.2 Design goals

1. **Non-interference first:** observation must not degrade voter experience or safety.
2. **Privacy by default:** observer evidence must be publishable without exposing voter identity, ballot choices, or vulnerable populations.
3. **Dispute usefulness:** logs must answer “what happened where/when/who said so” with verifiable provenance.
4. **Anti-weaponization:** forbid and block evidence patterns that enable targeting, intimidation, or doxxing.

## 250.3 Roles and scope (terms)

- **Observer / poll watcher:** a person authorized to observe parts of the process, subject to local rules.
- **Challenger:** a person authorized to raise challenges/objections under defined procedures (often bundled with watcher roles).
- **Observation surface:** any setting where the public/authorized parties can view election operations (polling place, ballot processing, tabulation, canvass). (See also `docs/237-...`.)

## 250.4 Minimal evidence objects (publishable, non-PII)

This doc does **not** require new schemas. Prefer reusing existing primitives:
EvidenceEnvelope + existing “note/capture” objects and registries.

### 250.4.1 Observer session note (per shift / location)

**Purpose:** attest that an authorized observer was present, where, and under what constraints.

Minimum fields (conceptual):
- `observer_role` (watcher / challenger / nonpartisan observer / official public liaison)
- `site_id` (stable public identifier)
- `time_window` (start/end, local time)
- `credentialed_by` (category only; *no personally identifying document numbers*)
- `constraints` (distance rules, no-phone rules, etc — descriptive, not adversarial)
- `incident_refs` (pointers to any incident notes filed)

**Publishable proofs:** hash of the session note; optional co-signature by a site official or neutral witness.

### 250.4.2 Observation event note (atomic, bounded)

**Purpose:** record an *observable* event relevant to integrity or access (e.g., “poll opened late”, “accessible machine unavailable”, “signage missing”, “line management issue”, “observer access dispute”, “ballot processing pause”).

Minimum fields (conceptual):
- `event_class` (from a small taxonomy; prefer reusing `docs/234-results-status-taxonomy...` patterns)
- `time` and `site_id`
- `what_was_observed` (plain-language; no speculation)
- `who_was_notified` (role only)
- `resolution_status` (open/mitigated/unresolved)
- `attachments` (rare; see stop-conditions)

**Publishable proofs:** event note hash + optional second-party witness envelope.

### 250.4.3 Challenge/objection record (procedural, not performative)

**Purpose:** capture that a formal challenge was filed, under which procedure, and the disposition.

Minimum fields (conceptual):
- `challenge_basis` (cite the local rule/procedure, not a narrative rant)
- `time`, `site_id`, `process_step`
- `filed_by_role` (not name)
- `decision` (accepted/denied/deferred) + `decision_by_role`
- `appeal_pointer` (if applicable)

**Publishable proofs:** signed envelope + (optional) redacted public release packet.

## 250.5 Evidence minimization rules (hard constraints)

### Always exclude (publishable artifacts)
- Names, faces, license plates, addresses, voter registration numbers, signature images.
- Photographs or video of voters in line, at check-in, or marking ballots.
- “Prove it” media meant to shame individuals.

### Prefer instead
- **Structured notes** + time/location + role-based attestations.
- **Aggregated counts** (e.g., number of accessibility failures) at precinct/site level.
- **Hash commitments** to sensitive attachments held under strict access controls (see `docs/246-...`).

## 250.6 Stop-conditions (do not proceed without program-level review)

Trigger a stop-condition if any proposed artifact:
1. materially increases risk of voter intimidation or targeting,
2. includes operational detail that would help disrupt future voting,
3. requires publishing personally identifying or biometric information,
4. creates an “observer vs voter” dynamic rather than “process vs evidence”.

When a stop-condition triggers: record the gap as an **open question** and route to the Threat Model Ledger (`docs/249-...`) with a “dual-use” tag.

## 250.7 Exercises (safe drills)

- **Non-interference drill:** observers rehearse *reporting to officials*, not confronting voters.
- **Minimal note drill:** can a shift produce session + event notes that would actually help a dispute?
- **Redaction drill:** test that accidental PII is caught and removed (see `artifacts/checklists/public-artifact-redaction-checklist.md`).

## 250.8 Links within the archive

- Canvass/certification/recount as evidence surfaces: `docs/237-canvass-certification-and-recount-as-evidence-surfaces.md`
- Dispute resolution and adjudication: `docs/59-dispute-resolution-and-adjudication.md`
- Court evidence bundle recipes: `docs/211-court-evidence-bundle-recipes.md`
- Assurance-case skeleton & minimization: `docs/246-assurance-case-skeleton-and-evidence-minimization.md`
- Threat Model Ledger & safe red-teaming: `docs/249-threat-model-ledger-and-safe-red-teaming.md`


## Primary anchors

- EAC — Poll Watchers (xref: eac_officials_poll_watchers)
- NCSL — Poll Watchers and Challengers (xref: ncsl_and_campaigns_poll_watchers_and_challengers)
- NCSL — Policies for Election Observers (xref: ncsl_and_campaigns_policies_for_observers)
