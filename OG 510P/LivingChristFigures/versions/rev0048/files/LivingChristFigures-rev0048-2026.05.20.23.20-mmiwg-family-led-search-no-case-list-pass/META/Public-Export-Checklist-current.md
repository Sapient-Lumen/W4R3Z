# Public Export Checklist — current

No public reading edition should be produced from the working cube until these gates pass.

## Gate 1 — Live-referral safety

- All public rows preserve `live_referral_safe=false` unless explicitly reclassified in a future, separately reviewed project.
- No shelter location, crisis route, camp location, outreach route, staff pattern, intake instruction, private phone/email, plot number, Medical Examiner number, case-story detail, or precise grave location is exported.

## Gate 2 — Claim/source/capacity separation

- Public language distinguishes existence, current capacity, historical capacity, planning, training, law, interpretation, and evidence debt.
- No law, report, framework, training, or public number is presented as an actual door unless supported by current capacity evidence.

## Gate 3 — Boundary-first reading order

- A public edition begins with method and boundary essays, not a hero list.
- At minimum, the first public table of contents must include: `Burial Is Not Consent`, `Searchable Memory Is Not Return`, and `Outreach Is Not Housing` before or beside any beautiful candidate prose.

## Gate 4 — Dissent and operator-pressure review

- Open `Operator-Dissent-Ledger-current.*` rows are reviewed.
- Any dissent marked closed must show concrete behavior change under `Update-Behavior-Gate-current.md`.

## Gate 5 — Source role review

- Each public claim has a visible source-role limit.
- Self-description, state/public authority, news, critical press, academic, and multilateral sources are not treated as interchangeable.

## Gate 6 — Names and images

- Names are load-bearing or suppressed.
- Images are not exported by default.
- Child, survivor, patient, unsheltered, refugee, undocumented, dead, and family-story details require explicit redaction review.


## rev0030 scanner gate

Before any expanded public export:

- Run `python tools/redaction_scan.py . --write-report --fail-on-high` from the package root.
- Confirm `META/Redaction-Risk-Open-Findings-current.*` reports zero open high-risk configured findings.
- Manually review narrative privacy risks the scanner cannot understand: non-load-bearing names, family stories, child/survivor/patient detail, camp-location inference, and publicity that converts service into spectacle.
- Treat any exact contact or locator detail as excluded unless explicitly exempted in writing.

## rev0031 schema-contract gate

Before any handoff or expanded public export:

- Run `python tools/schema_validate.py . --write-report --fail-on-high` from the package root.
- Confirm `SCHEMA/Schema-Validation-Report-current.*` reports zero high findings.
- Confirm `PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json` revision matches `manifest.json`.
- Confirm `Source-Type-Controlled-Vocabulary-current.*` maps every current source type.
- Treat unmapped or vague source types as evidence-role debt, not mere metadata cleanup.

## Evidence lifecycle gate (rev0032)

Before public export, review `META/Refresh-Priority-Queue-current.*` and rewrite or refresh any claim marked `now_or_before_any_public_claim`. Current-capacity, referral, shelter, visitation, outreach, and implementation claims should not be published as current without a same-pass refresh.


## Negative-case and online-intake gate (rev0033)

Before public export:

- Review `META/Negative-Case-Ledger-current.*` and keep rejected, deferred, demoted, or not-yet-a-door decisions visible near any relevant public claim.
- Review `META/Online-Research-Intake-current.*`; do not treat intake sources as promoted claim evidence unless a later candidate-specific pass moves them into the Source Registry and claim/candidate text.
- Review `META/Operator-Update-Audit-current.*`; do not close `opdist_0001` merely because a receipt exists.
- Keep contact-rich and operational source pages out of public referral language even when they are useful for current-source discovery.

## Gate 9 — Source-promotion veto and public-claim quarantine

- No `ori_*` online-intake source may appear in a public claim unless it first receives a promotion decision other than hold/block in `META/Source-Promotion-Decision-Ledger-current.*`.
- Every row in `META/Public-Claim-Quarantine-current.*` blocks public present-tense capacity, availability, implementation, and referral wording until its preconditions are met.
- A public table of contents may name quarantined candidates only with boundary-first or historical/shape-only wording.

## rev0037 added gate — conflict-zone mutual-aid no-map

Before any public paragraph about Sudan ERRs or a similar conflict-zone mutual-aid network, confirm that the paragraph contains no rooms, routes, kitchen sites, transfer channels, local contacts, volunteer identities, communication patterns, donor-routing instructions, or current access/capacity language. Recognition and awards must be framed as context, not as a service doorway.


## rev0039 Pacific survivor-service export gate

Before any public prose about Pacific crisis centres, confirm that rule 37 is satisfied: no exact contact fields, intake instructions, safe-house/refuge details, live capacity, staff-as-access routes, or referral wording; standards/funding context must be framed as non-referral and non-capacity evidence.

## rev0040 family-search gate
Before any public prose about missing-person search collectives, confirm rule 38 review: no sites, routes, tips, graves, forensic identifiers, registry IDs, images, family contacts, current brigade/protection details, or individual case stories.


## rev0041 law-to-door gate

Before any public use of Nauru/Palau/FSM law-to-door entries, confirm that the prose does not provide legal advice, court/police instructions, protection-order-as-safety, No Drop-as-survivor-choice, reconciliation/compulsory-counselling benefit language, service capacity, shelter/refuge access, enforcement guarantee, referral language, or case/evidence-chain detail. Public prose must begin from the boundary that legal form is not safe access.

## rev0042 child-burial no-case-extraction gate

Before any public prose about Garden of Innocence or adjacent child-burial offices, confirm rule 40: no assigned child names, poems, images, service notices, contact/location cues, case-story fragments, family-status claims, identifiers, or donor/religious narration as consent. No public claim was released in rev0042.

## rev0043 Hart Island / public cemetery no-record-extraction gate

Before any public prose about Hart Island or adjacent public-cemetery/memorial-database offices, confirm rule 41: no individual records, names, plot/section/grave identifiers, permit or Medical Examiner metadata, dates or places of death tied to people, fetal-remains details, family stories, images, maps, contact fields, search instructions, visit/scheduling instructions, or public-tour logistics. No public claim was released in rev0043.

## rev0046 overdose memorial gate

Before any public prose about International Overdose Awareness Day, overdose vigils, fentanyl memorial exhibits, tribute walls, local overdose-awareness events, or overdose-prevention campaigns, confirm rule 44: no tribute names, photos, family text, dates, cause/drug details, event names/locations/times, map markers, organizer contacts, registration paths, landmark details, memorial-exhibit submissions, training/naloxone/supply access paths, current service capacity, medical advice, referral wording, or punishment-framed memorial proof. No public claim was released in rev0046.


- rev0047 public-export gate: no migrant route, coordinate, distress-call, family-search, missing-boat, incident-row, name, image, rescue-capacity, legal-advice, or referral extraction.
