# 373 — Official voter-information forms, applications, affidavits, and version/acceptance discipline

**Track:** Shared

This document defines a bounded control for **official voter-facing action forms and application packets**:
registration forms, absentee or mail-ballot request forms, cure affidavits, declaration/witness forms, designated-agent request packets, accessibility request forms, address/name update forms, and similar downloadable or printable artifacts the public is expected to complete, sign, submit, or rely on.

It composes with:
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md`
- `docs/311-mail-ballot-return-instructions-envelope-requirements-and-deadline-semantics-as-evidence-surfaces.md`
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md`
- `docs/321-provisional-ballot-issuance-reasons-partial-count-rules-and-voter-instructions-as-evidence-surfaces.md`
- `docs/322-emergency-absentee-ballots-hospitalized-incapacitated-and-late-emergency-delivery-paths-as-evidence-surfaces.md`
- `docs/342-ballot-return-by-another-person-designated-agent-or-bearer-rules-and-ballot-handoff-boundaries-as-evidence-surfaces.md`
- `docs/343-challenged-voter-oaths-affidavits-witnesses-and-fail-safe-ballot-rights-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/362-election-office-discovery-ladders-national-routers-and-routing-divergence-discipline.md`
- `docs/364-official-voter-help-hotlines-call-center-script-packets-and-answer-version-discipline.md`
- `docs/365-official-voter-faqs-knowledge-base-articles-and-answer-edition-discipline.md`
- `docs/368-official-voter-information-printable-handouts-flyers-postcards-and-edition-linkback-discipline.md`
- `docs/370-official-voter-information-emails-newsletters-reminders-and-forward-context-discipline.md`
- `artifacts/templates/official-voter-information-form-surface-payload.json`
- `artifacts/checklists/official-voter-information-form-surface-checklist.md`

## Why this exists (bounded)

The archive already treats webpages, FAQs, hotlines, print artifacts, emails, and site signage as governed voter-information delivery layers.
That still leaves a sharper public-risk object:
**the action form itself**.

A voter may read a correct page and still fail because the downloaded packet is old, the affidavit omitted the controlling instructions, the wrong form was routed to the wrong population, or the acceptance conditions were unclear.
Unlike a general flyer, the form is not merely informative; it is an artifact the voter is expected to complete and submit.

Current official guidance makes that lane real.
The EAC's current **National Mail Voter Registration Form** page says the form can be used to register, update a name or address, or register with a political party; it also says voters must follow the **state-specific instructions**, sign where indicated, and send the form to the state or local election office for processing.
The same page also publishes the form in many languages.
The EAC's current **National Mail Voter Registration Form FAQs** page says only certain states accept that form as such, says New Hampshire and Wisconsin treat it differently, says uniformed service members and overseas voters should **not** use it and should instead access the newest **Federal Post Card Application**, and says accepted states allow photocopies printed on regular paper stock.
Vote.gov's current registration page likewise tells voters they can download and print the national form for most states, while routing them to state and territory election websites for state-specific rules.
And the EAC's current **Effective Design for the Administration of Federal Elections** page treats printed voter-information materials, online voter-information materials, and mail-voting materials as designed communication artifacts that should be clear, understandable, accessible, usable, and accurate.
The EAC accessibility clearinghouse also treats accessible communications and accessible voter registration as active maintainer resources rather than optional polish. (xref: `eac_national_mail_voter_registration_form_page`; xref: `eac_national_mail_voter_registration_form_faqs_page`; xref: `vote_gov_register_page`; xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `eac_clearinghouse_resources_accessibility_page`)

So the bounded problem is not “archive every blank form ever issued.”
It is simpler:
**if a jurisdiction expects voters to act on downloadable or printable election forms, how does it keep those forms visibly current, scope-correct, acceptance-aware, accessible, and explicitly superseded when they stop controlling?**

## What this adds (and what it does not)

This document adds a compact **edition + acceptance-semantics + wrong-form-boundary + superseding discipline** for official voter-facing forms and application packets.

It does **not** require publishing completed voter submissions.
It does **not** require preserving every historical blank form forever.
It does **not** replace:
- the underlying rule surfaces in `304`, `311`, `318`, `321`, `322`, `342`, and `343`,
- the general printable/downloadable voter-information lane in `368`,
- the FAQ/help lane in `365`,
- the hotline packet lane in `364`, or
- the office-routing lane in `305` / `362`.

It adds one narrow rule:
**if a jurisdiction expects the public to rely on a downloadable or printable election form, application, affidavit, or declaration packet, that artifact should identify its current edition and scope, state what acceptance conditions control, route the user safely when the artifact is not the right one, and carry an explicit superseding or withdrawal path when it stops controlling.**

## Distinct boundary from print handouts and general webpages

A voter-facing form lane is distinct because the artifact is not merely explanatory.
It is intended to be:
- completed,
- signed or attested,
- submitted through a particular channel,
- and judged against acceptance conditions.

That makes it different from:
- a general flyer or infographic (`368`),
- a maintained FAQ/help page (`365`),
- a short-form alert or reminder (`366`, `370`), or
- the underlying substantive rule surface describing who is eligible or what deadline applies.

The form is the **public action artifact**.
The underlying rule still belongs to the correct canonical voter-question surface.

## Visible edition and scope floor

A voter-facing form should not look timeless when it is not timeless.
Where form drift could matter, the artifact should make visible enough context that a voter, helper, and later verifier can tell:
- what the form is,
- what office or jurisdiction issued it,
- what election or process it applies to when that matters,
- what edition, issue date, or packet version controlled, and
- whether a current official page or instructions packet supersedes it.

That does not require a huge banner on every form.
It does require enough visible version/scope discipline that a stale PDF attachment or photocopy does not masquerade as the current controlling instrument.
If the harder problem is not which edition exists but whether an in-progress or resumed interaction that began under one reviewed edition may continue under a later controlling edition without visible re-review, `470` governs that expected-head boundary rather than `373` silently implying continuity from mere artifact persistence.

## Acceptance-semantics floor

The hard part of form drift is usually not typography; it is **acceptance semantics**.
A voter needs to know things like:
- which office receives the form,
- what supporting instructions are part of the packet,
- whether a signature, witness, assistant, notary, or declaration is required,
- whether photocopies are accepted,
- how and where the completed packet may be submitted,
- and what fallback or help route exists when the voter cannot satisfy the ordinary path.

Those acceptance conditions should not live only in an unlinked FAQ or only in a staff script.
If the public form is meant to be used, the packet should either carry the acceptance conditions directly or point in a visible bounded way to the current controlling official instructions.

## State-specific-instructions and wrong-form boundary floor

Election forms often fail because the public finds **a real form, but not the right form for this path**.
The current EAC registration-form materials make that risk explicit: the National Mail Voter Registration Form requires state-specific instructions, some states treat the form differently, and uniformed service members and overseas voters are told to use the newest FPCA instead.
That is exactly the sort of wrong-form boundary the archive should model. (xref: `eac_national_mail_voter_registration_form_page`; xref: `eac_national_mail_voter_registration_form_faqs_page`)

So a governed form lane should make it easy to answer:
- who should use this form,
- who should **not** use this form,
- what alternate form or packet controls instead,
- and where the voter gets current official help if they are near a boundary case.

A jurisdiction should not rely on “the public will infer the right packet from context.”
When the wrong form family is a predictable failure mode, the packet should route the voter away from it explicitly.

## Accessibility and language floor

If a jurisdiction expects the public to download, read, fill out, print, sign, or route a form, accessibility is not optional ceremony.
The EAC's current design and accessibility materials treat election communications as needing to be clear, understandable, accessible, and usable, and treat accessible communications plus accessible voter registration as active operational work.
That means voter-facing action forms should follow the same discipline:
- plain-language instructions,
- accessible electronic versions where offered,
- language variants where the jurisdiction maintains them,
- machine-readable or otherwise usable digital text rather than image-only scans where practical,
- and a visible help route when a voter cannot complete the ordinary form path independently. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `eac_clearinghouse_resources_accessibility_page`; xref: `eac_national_mail_voter_registration_form_page`)

## Canonical-link and packet-coherence floor

A form packet may be portable, but it should not be a free-floating rulebook.
When the form alone is not enough, it should route the voter to the current official destination safely.
That can mean:
- an official page with the current instructions,
- an office/help route,
- a hotline or FAQ packet,
- or a signed public notice when the form family changed.

The form lane should converge with the current official state already expressed elsewhere.
If the webpage says one signature rule, the downloadable affidavit says another, and the hotline packet says a third, the archive should model that as a real public-answer failure.

## Silent replacement and stale-packet discipline

Blank forms get downloaded once and reused later.
They are attached to emails, printed from old links, stored by community partners, photocopied, and passed around in clinics, campuses, shelters, and family networks.
So when a material form condition changes, silent webpage replacement is not enough.

A governed form lane should support an explicit correction trail:
- identify current form editions or packet versions,
- publish explicit superseding or withdrawal events when a materially different form now controls,
- preserve enough note about what changed to explain why an older packet is no longer controlling,
- and make the safe next step visible for someone holding a stale copy.

This does **not** require indefinite public hosting of every superseded blank form.
It does require an explicit public record that the old one stopped controlling and what replaced it.

## Canonical digest artifacts

Publish **small digests of the form lane**, not completed submissions.

- **Form Surface Digest (FSD):** digest of the bounded policy payload for the official voter-facing form lane.
- **Form Packet Edition Digest (FPED):** digest of a current approved form/application/affidavit packet edition.
- **Form Superseding or Withdrawal Digest (FSWD):** digest of an explicit replacement, withdrawal, or wrong-form rerouting event.
- **Form Acceptance-Parity Snapshot (FAPS):** optional digest tying the packet edition to the current page/help/hotline/notice state.

## What belongs in the public form-surface payload

Keep the payload **small, current-state oriented, and packet-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `form_surface_family_label`
- `delivery_role_note`
- `covered_form_classes[]`
- `underlying_surface_refs[]`
- `authoritative_download_locations[]`
- `current_packet_identifiers[]`
- `edition_and_scope_policy`
- `acceptance_semantics_policy`
- `wrong_form_boundary_policy`
- `canonical_destination_policy`
- `accessibility_and_language_note`
- `stale_packet_and_superseding_behavior`
- `public_help_route_uri`
- `public_help_route_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- completed voter forms,
- signatures or supporting documents,
- free-form case notes,
- or full submission logs with personal data.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which voter-facing form lane or packet edition controlled at time `T`?
- Could an ordinary voter tell whether this was the right form for their path?
- Were state-specific instructions or other controlling packet conditions visibly available?
- Did the packet state enough about signatures, witnesses, submission channel, and receiving office to be usable?
- Did the packet remain aligned with the current official page, FAQ/help article, hotline packet, and signed notice state?
- When the packet stopped controlling, was there an explicit superseding or withdrawal trail rather than a silent swap?

## How this fits the family map

Official voter-facing forms, applications, affidavits, and declaration packets are **not** a new canonical voter-question family bucket.
They are a high-stakes delivery layer in front of the same underlying questions already modeled in `292–343`.

This document only says that, if a jurisdiction expects the public to act on downloadable or printable election forms, those action artifacts should stay visibly current, scope-correct, acceptance-aware, accessible, and explicitly superseded when they drift.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-form-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-form-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: National Mail Voter Registration Form page (xref: `eac_national_mail_voter_registration_form_page`)
- EAC: National Mail Voter Registration Form FAQs page (xref: `eac_national_mail_voter_registration_form_faqs_page`)
- Vote.gov: Register page (xref: `vote_gov_register_page`)
- EAC: Effective Design for the Administration of Federal Elections page (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- EAC: Clearinghouse Resources on Accessibility page (xref: `eac_clearinghouse_resources_accessibility_page`)
