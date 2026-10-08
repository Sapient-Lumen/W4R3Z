# 424 — Official voter-information address entry, autocomplete suggestions, unit details, and manual-override fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that depend on a public address before the voter can reveal the current answer/help lane**:
polling-place lookups,
ballot-style lookups,
registration-status routes that confirm residence context,
drop-box or vote-center finders,
and similar public routes where the difference between a current answer and a dead end is often an address-entry detail rather than the underlying rule.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `292`, which governs polling-place directory and change-notice semantics,
- `293`, which governs ballot-style lookups and sample-ballot surfaces,
- `374`, which governs routers and decision selectors,
- `376`, which governs maps, geolocation, and directions,
- `403`, which governs progressive enhancement and degraded-client recovery,
- `416`, which governs reflow, text scaling, and small-viewport survivability,
- `417`, which governs keyboard navigation and logical focus order,
- `418`, which governs nonvisual structure and announced state,
- `421`, which governs touch targets, hover boundaries, and coarse-pointer operability,
- `422`, which governs generic field purpose, autofill, and error recovery,
- `423`, which governs date-entry and picker fallback when the route specifically depends on a date,
- or `478`, which governs browser/device text-assistance mutation and composition posture before the typed value even reaches address-suggestion review or manual override.

It adds one narrow rule:
**if an official voter-information route asks the public for an address before revealing the current answer, the office should keep address purpose, autocomplete suggestion behavior, unit/secondary-detail handling, and manual editing/override clear enough that the current official answer does not depend on accepting a brittle geocoder guess.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clear, understandable, and accessible communications. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible, authoritative, user-centered, and mobile-first. USWDS’s current address pattern guidance says address entry should accommodate rural areas, U.S. territories, military posts, temporary or unhoused situations, distinguish physical from mailing address when that matters, and consider browser autocomplete support on address inputs. The same guidance also says not to auto-advance focus between address fields. USWDS’s current combo-box guidance says option strings should use familiar spellings, dependent choices should be avoided, auto-submission should be avoided, and labels remain required; it also warns that these controls can be confusing and should be tested carefully. W3C’s current understanding guidance for **Identify Input Purpose** says programmatically declared field purpose helps user agents and assistive technologies present more consistent help when completing forms. MDN’s current `autocomplete` reference documents address-specific tokens such as `street-address`, `address-line1`, `address-level1`, `address-level2`, and `postal-code`, and explains `section-*` grouping for repeated address sets. WAI’s current editable-combobox example specifically illustrates **manual selection** behavior: typed text may remain the value if the user leaves the field without choosing a suggestion, while WAI separately warns that production implementations require careful testing across browser and assistive-technology combinations, especially on mobile/touch devices. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_address_pattern_page`; xref: `uswds_combo_box_component_page`; xref: `w3c_wcag21_identify_input_purpose_page`; xref: `mdn_autocomplete_attribute_page`; xref: `w3c_wai_aria_apg_editable_combobox_manual_selection_example_page`)

That is enough to justify a compact control here.
A route can be current, searchable, keyboard reachable, legible on a phone, and generally pass `422`, yet still fail first contact because the voter cannot tell whether the form wants a residence address or a mailing address, an autocomplete popup drops the apartment number, the route forces acceptance of a “best match” that is wrong, a state/county selector auto-submits before the street is finished, or the official answer disappears when the geocoder cannot confidently normalize an otherwise understandable address.

## This is not the same thing as generic field-entry review, map review, or special-case address policy

`422` asks whether the voter can generally tell what to type, recover from an error, and preserve entered values.

`376` asks whether a map, geolocation, or directions layer remains subordinate to the answer lane.

`324`, `328`, `336`, and `337` govern special-case address semantics such as no fixed address, student residence choice, tribal/community addressing, and displacement.

`478` asks whether browser/device text assistance and composition can silently change the typed address or locality value before the voter ever reaches suggestion review or manual override.

`424` asks a different question:
**once an official route specifically depends on address entry, can the voter tell which address is being requested, review or reject suggestions, preserve unit/secondary detail, and reach the same authoritative answer without handing control to an opaque autocomplete or geocoder?**

A route may pass `422` and still fail `424` if:
- the form says “Address” without clarifying residence vs mailing vs temporary location,
- the only workable path is an autocomplete suggestion list with no practical manual-edit path,
- apartment, unit, building, lot, or other secondary detail is lost when a suggestion is accepted,
- the route auto-submits or reroutes when a suggestion is highlighted rather than intentionally chosen,
- unmatched or nonstandard addresses drop straight into a dead end instead of a bounded retry/help lane,
- or typed, pasted, suggested, and manually corrected address variants resolve to different official answers for the same location.

## Address purpose should be explicit before suggestions begin

The practical rule here is simple:
- say whether the route needs a residential voting address, a mailing address, a temporary location, or another specific address role,
- keep that role visible near the active field,
- and do not rely on placeholder-only hints or an autocomplete popup to explain what kind of address the voter is being asked to provide.

This does **not** require a long tutorial.
It requires enough task-specific clarity that a voter can predict whether a dorm, shelter, reservation address, rural route, military post, apartment, or temporary mailing location belongs in the field before the system starts guessing.

## Suggestions should help, not silently decide

Autocomplete, typeahead, and geocoder suggestions can be useful.
But for this archive, they are helpers, not authorities.
That means:
- suggestions should be reviewable before acceptance,
- highlighting a suggestion should not itself commit the value,
- a voter should be able to continue typing or editing after a suggestion appears,
- and the route should not turn a probabilistic “best match” into an invisible jurisdictional decision.

The core rule is not “never suggest.”
It is “do not make the current official answer depend on the voter accepting a brittle guess they cannot inspect or correct.”

## Unit, secondary-detail, and nonstandard-address handling should preserve the answer lane

Apartment numbers, suites, building identifiers, lot numbers, urbanization fields, military posts, rural routes, plus codes, and temporary-location details can all matter.
Sometimes they matter to delivery.
Sometimes they matter to district or polling-place resolution.
Sometimes they are needed only for later correspondence.

`424` does **not** require every route to collect every possible address detail.
It requires offices to keep the answer lane clear about:
- whether the detail is needed for this route,
- where it belongs if it is needed,
- whether accepting a suggestion preserves or discards it,
- and what the voter should do when the official route cannot confidently normalize a real-world but nonstandard address.

A common failure here is subtle:
a route appears to work for ordinary addresses but silently drops apartment/unit data, collapses Puerto Rico or military-post distinctions into a generic state picker, or treats nonstandard addressing as invalid with no visible explanation or fallback.

## Manual entry and correction should remain available after suggestions appear

USWDS’s combo-box guidance and WAI’s combobox example both point toward the same practical posture:
manual typed entry still matters.
For this archive, that means an autocomplete-enabled address route should preserve a manual-edit path before and after suggestions appear.
The voter should not have to start over just because the system surfaced a suggestion or guessed the wrong street suffix, city, or ZIP.

This composes directly with `417`, `421`, and `422`.
`424` simply adds the address-specific rule that suggestion interaction should not become its own hidden decision engine.

## Repeated address groups and physical-vs-mailing duplication should stay unambiguous

Some routes legitimately ask for more than one address context.
A voter may need to give a residential voting address plus a mailing address, or confirm that two addresses are the same.
When that happens, the route should keep those groups clearly distinct both visibly and programmatically.
The point is not standards theater.
The point is to prevent browser autofill, assistive technology, or hurried mobile entry from filling the wrong address set and quietly changing the official answer path.

## The same authoritative answer should survive address-entry variants

Different voters may:
- type the entire address manually,
- paste an address,
- accept a suggestion,
- edit a suggestion,
- use separate street/city/state/ZIP fields,
- or rely on a “same as physical address” duplication helper.

Those interaction differences should **not** silently change the underlying authoritative answer, warning, district assignment explanation, or office-help fallback for the same location.
If the route resolves the same real-world address, it should resolve to the same official answer lane.

## Minimal address-entry-state taxonomy

A small taxonomy is enough:

1. **Address purpose clarity state** — the route says which address role it needs.
2. **Suggestion-helper state** — autocomplete or geocoder suggestions are reviewable helpers, not silent commitments.
3. **Manual edit/override state** — typed entry and post-suggestion correction remain available.
4. **Secondary-detail preservation state** — unit/apartment/secondary detail is preserved when relevant instead of being silently dropped.
5. **Repeated-address disambiguation state** — residential vs mailing and repeated address groups remain visibly and programmatically distinct.
6. **Unmatched-address recovery state** — nonstandard or unrecognized addresses still lead to a bounded retry/help lane.
7. **Same-answer-across-address-variants state** — typed, pasted, suggested, and manually corrected variants resolve to the same authoritative answer for the same location.
8. **Address-entry answer lane available** — the current official answer/help route remains materially reachable after ordinary address-entry mistakes.

## Preserve bounded reconstruction, not address exhaust

What matters here is bounded reconstruction of the office’s address-entry posture:
- which critical address-dependent routes were reviewed,
- whether address role was explicit,
- whether suggestions acted as helpers or hidden commitments,
- whether unit/secondary detail survived suggestion acceptance,
- whether repeated address groups were kept distinct,
- whether unmatched-address recovery remained available,
- and when the route was last reviewed.

Do **not** preserve raw residential addresses, full submitted address books, apartment/unit identifiers from real users, exact geocoder request logs, or exhaustive session replay when bounded public-answer reconstruction is sufficient.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `address_entry_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_address_paths[]`
- `address_role_clarity_note`
- `residence_vs_mailing_distinction_note`
- `autocomplete_and_typeahead_behavior_note`
- `manual_entry_and_post_suggestion_edit_note`
- `unit_secondary_and_nonstandard_address_note`
- `programmatic_address_tokens_and_grouping_note`
- `suggestion_acceptance_and_no_autosubmit_note`
- `unmatched_address_recovery_note`
- `same_answer_across_address_variants_note`
- `address_entry_state_classes[]`
- `address_trace_policy{}`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- `supersedes`
- `superseded_by`

## Verification prompts that fit this surface

- Can a voter tell which address the route is asking for before suggestions or validation begin?
- If suggestions appear, can the voter review, reject, or edit them without auto-submission or hidden commitment to a guessed match?
- When apartment/unit/secondary detail matters, does the route preserve it rather than discarding it when a suggestion is accepted?
- If the office asks for more than one address context, are those groups clearly distinct both visibly and programmatically so autofill or hurried mobile entry does not swap them?
- If the main lookup path cannot confidently normalize an address, is there still a plainly visible first-party retry/help fallback instead of a dead end?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-address-entry-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-address-entry-surface-checklist.md`

## Sources to keep pinned

Keep the lockfile entries for:
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: Requirements for delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- USWDS: Address pattern guidance (xref: `uswds_address_pattern_page`)
- USWDS: Combo box component guidance (xref: `uswds_combo_box_component_page`)
- W3C WAI: Understanding SC 1.3.5 Identify Input Purpose (xref: `w3c_wcag21_identify_input_purpose_page`)
- MDN: `autocomplete` attribute reference (xref: `mdn_autocomplete_attribute_page`)
- W3C WAI: Editable combobox with list autocomplete example (manual selection) (xref: `w3c_wai_aria_apg_editable_combobox_manual_selection_example_page`)
