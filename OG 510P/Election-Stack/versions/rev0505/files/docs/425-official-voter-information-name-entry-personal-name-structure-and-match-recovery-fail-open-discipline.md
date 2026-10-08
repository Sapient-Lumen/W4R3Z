# 425 — Official voter-information name entry, personal-name structure, and match-recovery fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that depend on a public personal name before the current answer/help lane can appear**:
registration-status lookups,
mail-ballot status lookups,
provisional-ballot status lookups,
voter-history or correction routes,
and similar public paths where the difference between a current answer and a dead end can hinge on how the office asks for, parses, or retries a person's name rather than on the underlying rule.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `294`, which governs registration-status lookups and correction notices,
- `295`, which governs mail-ballot status lookups and cure notices,
- `296`, which governs provisional-ballot status lookups and reason notices,
- `316`, which governs voter-history and participation-record lookups,
- `318`, which governs registration updates involving name changes,
- `403`, which governs progressive enhancement and degraded-client recovery,
- `416`, which governs reflow, text scaling, and small-viewport survivability,
- `417`, which governs keyboard navigation and logical focus order,
- `418`, which governs nonvisual structure and announced state,
- `421`, which governs touch targets, hover boundaries, and coarse-pointer operability,
- `422`, which governs generic field purpose, autofill, and error recovery,
- `423`, which governs date-entry and picker fallback when the route specifically depends on a date,
- or `424`, which governs address-entry, autocomplete suggestions, and manual override when the route specifically depends on an address.

It adds one narrow rule:
**if an official voter-information route asks the public for a personal name before revealing the current answer, the office should keep full-name-vs-split-field choice, character and length support, optional-name-part handling, and match-recovery cues clear enough that the current official answer does not depend on a Western-only name model or a brittle exact-match parser.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, accessibility, usability, and audience-aware structure. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible, authoritative, user-centered, and mobile-first. USWDS’s current **Name** pattern says people have a wide variety of names and that forms should support long names, single-character names, diacritics, accents, multiple names in a field, hyphens, apostrophes, spaces, and optional middle/family-name structure when needed. USWDS’s current **Name form** guidance says agencies should only split names into separate data elements when they actually need to, avoid select menus for title/suffix, and not restrict the characters people can enter. W3C’s current **Personal names around the world** guidance says designers should ask whether separate given/family-name fields are necessary at all, avoid assuming everyone has a family name, allow punctuation and spaces, and preserve the case users enter. W3C’s current understanding guidance for **Identify Input Purpose** says name purpose can be programmatically identified through technologies such as HTML `autocomplete` tokens, and MDN’s current `autocomplete` reference says `name` is generally preferred over splitting the name into components unless the application really needs the parts. Section508.gov’s current accessible-web guidance separately says labels, instructions, and known error suggestions should be easy to find. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_name_pattern_page`; xref: `uswds_name_form_template_page`; xref: `w3c_personal_names_around_world_page`; xref: `w3c_wcag21_identify_input_purpose_page`; xref: `mdn_autocomplete_attribute_page`; xref: `section508_guide_accessible_web_design_development_page`)

That is enough to justify a compact control here.
A route can be current, mobile-usable, keyboard reachable, and generally pass `422`, yet still fail first contact because it requires “first name / last name” for someone whose registration record does not fit that structure, rejects diacritics or apostrophes, trims a suffix or space-separated family name, forces a title from a narrow menu, or returns a generic “not found” error without telling the voter whether to use a previous name, registration-record name, or another bounded retry path.

## This is not the same thing as generic field-entry review, date review, or address review

`422` asks whether the voter can generally tell what to type, recover from an error, and preserve entered values.

`423` asks whether date-gated routes survive pickers, segmented date fields, and visible date-window limits.

`424` asks whether address-gated routes survive autocomplete, unit detail, repeated address groups, and manual override after suggestion behavior begins.

`425` asks a different question:
**once an official route specifically depends on a personal name, can the voter tell how much structure the office really requires, enter the name they actually have, preserve punctuation/spacing/case where meaningful, and reach a bounded retry/help lane when the registration record or lookup matcher expects a different presentation?**

A route may pass `422` and still fail `425` if:
- the form requires both a first and last name when the voter has only one name,
- the route strips apostrophes, hyphens, diacritics, or spaces and changes the lookup behavior without warning,
- a title or suffix is forced through a narrow select menu even though the route does not materially need it,
- the office really needs the registration-record name or a previous name but never says so before failure,
- or ordinary name-presentation variants collapse into a generic “record not found” state with no bounded retry/help lane.

## Prefer full-name entry when the route does not truly need separate parts

MDN and W3C point in the same practical direction: if the route does not genuinely need separate name parts, a full-name field is often safer.
That avoids forcing every voter into a given-name/family-name model when the real operational need is just “the name on the relevant record.”

`425` does **not** require every office to use a single full-name field.
It requires the office to justify split fields by actual task need rather than habit.
If the route really must distinguish parts of a name, the route should still avoid pretending the split is culturally universal.

## Characters, spacing, case, and length should survive ordinary public use

The point here is not to create an abstract internationalization manifesto.
It is to keep the answer lane reachable.
That means name fields should not quietly break on:
- diacritics or accented characters,
- hyphens and apostrophes,
- spaces inside given names, family names, or suffix-bearing names,
- very short names,
- long names,
- or user-entered casing that matters for readability and review.

A common failure is subtle rather than spectacular:
the page accepts the keystrokes, but silently normalizes, truncates, uppercases, or splits the value in a way that changes the lookup result and leaves the voter with no explanation of what happened.

## Optional parts should stay optional unless the route materially needs them

USWDS’s current name guidance is explicit that not every person has a middle name or a family name, and not every one-character entry is an initial.
For this archive, that means official name-gated routes should avoid turning optional name parts into mandatory blockers unless the route can clearly justify the requirement.

The goal is not to outlaw structure.
The goal is to avoid invented structure that only exists because a form designer assumed everyone has the same name anatomy.

## Title, suffix, and previous-name cues should help rather than trap

When a route asks for a title, suffix, preferred name, or previous name, it should be clear why that field exists and whether it matters to the lookup outcome.
If the route does not materially need a title or suffix, it should not force one.
If the route does need a previous name because the authoritative record may still be under that value, it should say so before the voter burns a retry.

A strong practical rule here is:
**do not make the voter infer record-matching policy from a failed lookup.**
If the office wants “name as registered,” “previous name,” or “exact name on the ballot request,” say that plainly near the active field and keep the help fallback visible.

## Programmatic purpose and repeated name groups should stay unambiguous

Some routes legitimately ask for more than one name context.
A voter may need to provide the current name plus a previous name, or the voter name plus a witness or assistant name.
When that happens, the route should keep those groups visibly and programmatically distinct.
This is not metadata theater.
It reduces autofill collisions, assistive-technology ambiguity, and hurried mobile entry mistakes.

## Match recovery should be bounded and explainable

Not every authoritative record system will accept every ordinary variant of a person’s name.
`425` does **not** require perfect fuzzy matching.
It requires bounded recovery when the first attempt fails.
That means:
- explain whether the office expects the current legal name, registration-record name, or previous name,
- preserve the entered value across retries,
- avoid clearing the whole form after a mismatch,
- and keep a plainly visible first-party help path available when the automated lookup remains brittle.

The public failure mode should be “here is the next bounded retry or help step,” not “the record does not exist and good luck.”

## The same authoritative answer should survive ordinary name-entry variants when the underlying record is the same

Different voters may:
- type a full name in one field,
- use split given/family-name fields,
- include or omit punctuation,
- include or omit a suffix,
- paste the value from another source,
- or rely on browser autofill.

Those interaction differences should **not** silently change the authoritative answer or fallback lane for the same person unless the office clearly explains that the route depends on a narrower record-specific naming rule.
Where normalization or exact matching remains unavoidable, the recovery path should say what changed and what to try next.

## Minimal name-entry-state taxonomy

A small taxonomy is enough:

1. **Name-structure clarity state** — the route makes clear whether full name or separate parts are actually required.
2. **Character/length acceptance state** — ordinary punctuation, spacing, case, short names, and long names are handled without brittle rejection.
3. **Optional-part posture state** — middle, family, title, and suffix fields are optional unless materially needed.
4. **Registration-record cue state** — the route says when the lookup expects a prior or record-specific name rather than leaving the voter to guess.
5. **Programmatic name-purpose state** — repeated or distinct name groups stay visibly and programmatically distinct.
6. **Variant/match recovery state** — mismatches preserve entered values and expose a bounded retry/help lane.
7. **Same-answer-across-name-entry-variants state** — ordinary name-entry variants do not silently change the authoritative answer for the same person.
8. **Name-entry answer lane available** — the current official answer/help route remains materially reachable after ordinary name-entry mistakes.

## Preserve bounded reconstruction, not identity exhaust

What matters here is bounded reconstruction of the office’s name-entry posture:
- which critical name-dependent routes were reviewed,
- whether full-name or split-field structure was justified,
- whether punctuation/spacing/length/case support was reviewed,
- whether optional name parts were actually optional,
- whether the route explained registration-record naming expectations,
- whether mismatch recovery preserved values and visible help fallback,
- and when the route was last reviewed.

Do **not** preserve raw personal-name corpora, rejected-name logs from real voters, complete lookup attempts tied to identities, exhaustive session replay, or freeform matcher telemetry when bounded public-answer reconstruction is sufficient.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `name_entry_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_name_paths[]`
- `full_name_vs_split_fields_note`
- `registration_record_name_scope_note`
- `punctuation_diacritics_case_and_length_support_note`
- `single_name_and_optional_parts_note`
- `title_suffix_and_previous_name_note`
- `autofill_and_programmatic_name_tokens_note`
- `name_variant_and_match_recovery_note`
- `no_hidden_normalization_or_context_change_note`
- `same_answer_across_name_entry_variants_note`
- `name_entry_state_classes[]`
- `name_trace_policy{}`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- `supersedes`
- `superseded_by`

## Verification prompts that fit this surface

- Can a voter tell whether the route really needs a full name, split name parts, a previous name, or the exact registration-record name before failure occurs?
- Does the route accept ordinary punctuation, spaces, diacritics, short names, and long names without silently changing the lookup behavior or coercing the displayed name?
- If title, suffix, preferred-name, or previous-name fields are present, is it clear whether they are optional and whether they matter to the lookup outcome?
- When the first lookup misses, does the route preserve the entered value and point to a bounded retry/help path rather than clearing the form or collapsing into a generic “not found” message?
- Do full-name, split-field, pasted, and autofilled entry paths converge on the same authoritative answer or at least the same explainable recovery posture for the same person?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-name-entry-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-name-entry-surface-checklist.md`

## Sources to keep pinned

Keep the lockfile entries for:
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: Requirements for delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- USWDS: Name pattern guidance (xref: `uswds_name_pattern_page`)
- USWDS: Name form template guidance (xref: `uswds_name_form_template_page`)
- W3C Internationalization: Personal names around the world (xref: `w3c_personal_names_around_world_page`)
- W3C WAI: Understanding SC 1.3.5 Identify Input Purpose (xref: `w3c_wcag21_identify_input_purpose_page`)
- MDN: `autocomplete` attribute reference (xref: `mdn_autocomplete_attribute_page`)
- Section508.gov: Guide to Accessible Web Design & Development (xref: `section508_guide_accessible_web_design_development_page`)
