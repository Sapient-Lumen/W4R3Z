# 311. Mail-ballot return instructions, envelope requirements, and deadline semantics as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I already have my mail ballot; exactly how do I return it, what has to be on or in the envelope, which deadline semantics control, and what changed?”** as an **evidence surface**.
The goal is not to publish per-voter ballot-return events, signature images, internal acceptance heuristics, or chain-of-custody internals. The goal is to make six things hard to fake after the fact:

1. **Which public return path the jurisdiction identified as authoritative** for election scope `E`,
2. **Which return methods the public surface said were allowed**,
3. **Which envelope, declaration, witness, notary, or postage instructions the public surface said applied**,
4. **What return deadline semantics the public surface said controlled each method**,
5. **When a return instruction, envelope requirement, or deadline basis changed**, and
6. **Whether official channels stayed consistent, accessible, and explicit about the change**.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/271-vote-by-mail-distribution-tracking-and-dropboxes-as-evidence-surfaces.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/295-mail-ballot-status-lookups-and-cure-notices-as-evidence-surfaces.md`
- `docs/298-ballot-drop-box-directories-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md`
- `docs/306-military-and-overseas-voting-paths-fpca-fwab-and-change-notices-as-evidence-surfaces.md`
- `docs/308-election-calendars-key-dates-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

Many voters do not fail at the **request** step. They fail in the narrow window after the ballot is in hand, when the practical question becomes **“how do I return this correctly, by which official route, and what exact deadline basis now controls?”** Current official guidance makes that a distinct public-information problem rather than just a footnote to request or status pages. EAC’s current **How do I vote by mail?** page tells voters to review the deadline to return the ballot in time to be counted, carefully read the instructions on how and when to return it, complete the return envelope, and note that some states require a notary or witness signature. The same page also distinguishes return by mail from in-person or drop-box return and reminds voters to include enough postage where needed. EAC’s current **How do drop boxes work?** page reinforces that return instructions remain method-specific even after ballot issuance: place the ballot in the return envelope, complete the required envelope information, use a clearly marked official drop box, and, when using that method, return the ballot no later than the close of polls on Election Day. NASS’s current **Absentee & Early Voting** page likewise says state laws vary greatly and directs voters to the information provided by election officials or the local election office, while **Can I Vote** frames the service as routing directly to state election websites and trusted resources rather than compressing return rules into one generic national answer. (source: `eac_how_do_i_vote_by_mail_page`, `eac_how_do_drop_boxes_work_page`, `nass_absentee_early_voting_page`; xref: `nass_can_i_vote_page`)

That is why this surface should be separate from adjacent ones. `docs/304` answers whether and how the voter must **request** a ballot. `docs/295` answers what the official **status/cure** surface later said happened to the returned ballot. `docs/298` answers where official **drop boxes** exist and when those locations are available. `docs/308` synthesizes calendar-level deadlines across the broader election. None of those, by themselves, fully preserve the bounded public facts that control the return act itself: whether the voter was told to sign the envelope, obtain a witness or notary, use a secrecy sleeve, add postage, deliver by receipt deadline, rely on a postmark rule, deposit by close of polls, or use an in-person counter return instead of a mail route. Those are precisely the facts that become contested after a late correction, court-order shift, packet redesign, or stale PDF remains online.

This surface also needs a narrow lane for specialized return paths without swallowing them whole. UOCAVA voters may have different return options or backup-ballot paths, but the ordinary domestic return surface should still clearly point to the specialized official path when that distinction matters rather than pretending all returned ballots follow identical rules. Pair this document with `docs/306`; do not collapse the two surfaces. (xref: `fvap_mailing_ballots_election_updates_page`; xref: `nass_can_i_vote_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative return-path claim:** for election scope `E`, the jurisdiction identified one authoritative public path for mail-ballot return instructions and one authoritative help path.
2. **Return-method claim:** the public surface stated which return methods were officially allowed (for example postal return, in-person counter return, official drop box, or other state-specific method).
3. **Envelope/declaration claim:** the public surface stated which return-envelope fields, declarations, signatures, witness/notary steps, or packaging steps were required.
4. **Deadline-semantics claim:** each return method carried explicit deadline semantics rather than a vague “return as soon as possible” sentence.
5. **Change-log claim:** changes to return methods, envelope requirements, postage guidance, or deadline basis were published as explicit superseding events rather than silent edits.
6. **Parity/accessibility claim:** ballot-packet instructions, website, downloadable PDF instructions, hotline/help script packet, and signed notices converged on the same effective public state in accessible and, where required, language-appropriate forms.

## Canonical digest artifacts

Publish **digests of the public mail-ballot return surface**, not per-voter return events.

- **Mail Ballot Return Surface Digest (MBRSD):** digest of the authoritative public return-instructions payload for a scope.
- **Mail Ballot Return Change Notice Digest (MBRCND):** per-event digest for changed return methods, envelope requirements, postage rules, or deadline semantics.
- **Mail Ballot Return Deadline Advisory Digest (MBRDAD):** optional digest for late-breaking deadline-basis clarifications, court-order changes, or emergency operational advisories.
- **Mail Ballot Return Surface Parity Snapshot (MBRSPS):** optional snapshot binding the effective return-instructions surface across declared official channels.
- **Mail Ballot Return Help Path Digest (MBRHPD):** optional digest of the fallback help path when the voter cannot safely use the primary return method or cannot tell which deadline basis applies.

## What belongs in the public mail-ballot return payload

Keep the payload **small, action-relevant, and method-specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_return_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the most recent signed correction or maintenance notice

Recommended return-specific fields:
- `public_terms_in_use` (for example `mail_ballot`, `absentee_ballot`)
- `return_methods`
- `envelope_requirements`
- `packet_requirement_notes`
- `special_population_refs`
- `status_tracking_uri` or `status_surface_ref`
- `language_set`
- accessibility-format indicators

Recommended per-return-method fields:
- stable `method_id`
- `method_type` (`mail`, `drop_box`, `in_person_counter`, `election_day_site_where_lawful`, `special_population`)
- `availability_ref` or bounded location/reference pointer
- `return_deadline`
- `deadline_basis`
- `plain_language`
- `fallback_if_unavailable`
- optional `detail_surface_ref`

Recommended envelope/declaration fields:
- `return_envelope_required`
- `voter_signature_required`
- optional `witness_signature_required`
- optional `notary_required`
- optional `secrecy_envelope_required`
- `postage_policy`
- bounded `plain_language`

Do **not** publish by default:
- per-voter barcode scans, intake events, or individualized ballot-return telemetry
- signature images, witness identities, or notary details
- internal acceptance thresholds, signature-matching heuristics, or exception queues
- copied state statutes or county manuals when a bounded summary plus pointer will do
- location-by-location drop-box inventories inside this payload when `docs/298` already owns that directory surface

## Return semantics and anti-retcon rules

The return surface should fail **loudly** when voter actionability changes.

Rules:
- A change that affects how a voter may return a ballot SHOULD produce a new change notice digest.
- A change that affects envelope/declaration steps, signature expectations, witness/notary requirements, secrecy-envelope use, or postage expectations SHOULD produce a new change notice digest.
- The public surface SHOULD distinguish **request deadline** from **return deadline**.
- The public surface SHOULD distinguish **received by**, **postmarked by**, **deposited by close of polls**, and **hand-delivered by office close** semantics.
- If drop-box return is allowed, the return surface SHOULD point to the current official drop-box directory rather than collapsing directory data into this payload.
- If a specialized military/overseas or other legally distinct return path applies, the return surface SHOULD point to that official path rather than burying it in generic instructions.
- Silent mutation of packet inserts, downloadable instructions, return-envelope text, or website deadline language without a superseding event SHOULD be treated as a governance failure.
- If different audiences are sent to different return instructions, publish a parity snapshot (`201`) and follow it with a signed correction notice.

## Accessibility, language access, and packet parity

Return instructions often live in more than one place at once: on the packet insert, on the return envelope, on the website, in a downloadable PDF, and in help-center scripts.

Minimum publishable facts:
- which official return methods are allowed,
- what packaging or envelope steps are required,
- which signature, witness, notary, or secrecy-envelope steps apply,
- which deadline semantics control each method,
- where the detailed official help path lives,
- which signed notice superseded the prior answer,
- which languages and accessible formats cover the answer surface.

If the ballot packet says one thing, the website says another, and the help line is reading from an older script, the public answer surface is not trustworthy. Treat packet parity and deadline-language precision as integrity controls, not editorial polish.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public return-instructions surface at time `T`?
- Can we reconstruct which return methods the public was told were lawful and available?
- Did the public surface say what had to be signed, witnessed, notarized, or enclosed?
- Were deadline semantics specific enough to distinguish receipt, postmark, drop-box, and office-close cutoffs?
- Did ballot packets, websites, PDFs, help scripts, and signed notices converge on the same effective public instructions?
- Were late corrections explicit, or quietly edited into mutable pages after disputes arose?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/mail-ballot-return-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/mail-ballot-return-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: How do I vote by mail? (source: `eac_how_do_i_vote_by_mail_page`)
- EAC: How do drop boxes work? (source: `eac_how_do_drop_boxes_work_page`)
- EAC: Voting by Mail / Absentee Voting resources (source: `eac_voting_by_mail_absentee_voting_resources_page`)
- EAC: Be Election Ready — Voting by Mail guide script (source: `eac_voting_by_mail_video_guide_2024_pdf`)
- NASS: Absentee & Early Voting (source: `nass_absentee_early_voting_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- FVAP: Mailing Ballots and Election Date Updates (xref: `fvap_mailing_ballots_election_updates_page`)
