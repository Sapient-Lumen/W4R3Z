# 422 — Official voter-information field-entry hints, autofill, and input-error recovery fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that depend on typed, pasted, autofilled, or otherwise entered public input before the voter can reveal the current answer/help lane**:
registration-status lookups,
polling-place searches,
ballot-status searches,
address checkers,
contact/help forms,
and similar public routes where the difference between a current answer and a dead end is often a field-entry detail rather than the underlying rule.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `373`, which governs downloadable or printable forms/applications/affidavits,
- `374`, which governs routers and state/decision selectors,
- `403`, which governs progressive enhancement and degraded-client recovery,
- `416`, which governs reflow, text scaling, and small-viewport survivability,
- `417`, which governs keyboard navigation and logical focus order,
- `418`, which governs nonvisual structure and announced state,
- or `421`, which governs touch targets, hover boundaries, and coarse-pointer operability.

It adds one narrow rule:
**if an official voter-information route asks the public to enter data before revealing the current answer, the office should keep field purpose, keyboard/input hints, format expectations, paste/autofill behavior, and correction/retry paths clear enough that the current official answer does not depend on guesswork about how to type the query.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clear, understandable, and accessible communications. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible to people of diverse abilities. USWDS’s current text-input guidance says text inputs are often easier than alternative controls for things like birthdays, that pasted content matters, that mobile context matters, and that validation should wait until a user has interacted with the field. USWDS’s current input-mask guidance says masks can help with common restricted formats and mobile entry, but also flags that component for project-level accessibility testing and notes known issues. W3C’s current understanding guidance for **Labels or Instructions** says users should know what information to enter and any needed format expectations. W3C’s current understanding guidance for **Error Identification** and **Error Suggestion** says automatically detected input errors should be identified in text and, when known, correction suggestions should be provided. W3C’s current understanding guidance for **Identify Input Purpose** says programmatically declared field purpose helps user agents and assistive technologies present more consistent help for filling forms. MDN’s current `inputmode` reference says the attribute hints the virtual keyboard a device should show but does not itself enforce validity, and MDN’s current `autocomplete` reference says user agents can use field tokens to prefill or assist repeated data entry. Section508.gov’s current accessible-web guide adds concrete implementation guidance: identify errors in text, associate error descriptions with fields, make fixes visible, and provide labels or instructions where input is required. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_text_input_component_page`; xref: `uswds_input_mask_component_page`; xref: `w3c_wcag21_labels_or_instructions_page`; xref: `w3c_wcag21_error_identification_page`; xref: `w3c_wcag21_error_suggestion_page`; xref: `w3c_wcag21_identify_input_purpose_page`; xref: `mdn_inputmode_attribute_page`; xref: `mdn_autocomplete_attribute_page`; xref: `section508_guide_accessible_web_design_development_page`)

That is enough to justify a compact control here.
A route can be current, searchable, keyboard reachable, screen-reader intelligible, and easy to tap, yet still fail first contact because a ZIP code field summons the wrong keyboard, a date field demands an unexplained format, a mask rejects pasted input, a registration-lookup field silently drops spaces or punctuation, autofill lands in the wrong field, or an error is announced only as a red outline with no practical correction path.

## This is not the same thing as generic form accessibility or downloadable form control

`373` governs **public action artifacts** such as downloadable forms, applications, affidavits, and acceptance packets.

`421` asks whether the voter can hit, reveal, or dismiss the route with ordinary pointer input.

`418` asks whether the route still makes sense when read nonvisually.

`422` asks a different question:
**once the voter reaches the active field-entry lane, can they tell what to enter, enter it with an appropriate keyboard/help posture, preserve what they typed or pasted, and recover from an error without turning the official answer into guesswork?**

A route may pass `418` and `421` and still fail `422` if:
- a date, ZIP, address, or ID field gives no usable format cue,
- the wrong on-screen keyboard appears for the expected value,
- a mask or formatter traps deletion, blocks paste, or silently rewrites the input,
- autofill or remembered values land in the wrong field because purpose is underspecified,
- an error state is shown only by color or icon with no useful text,
- or the form clears the voter’s query after a failed lookup, forcing re-entry from scratch.

## Input purpose and visible instructions should narrow guesswork before validation fires

The practical rule here is simple:
- label fields according to the task the voter is actually performing,
- make required format cues visible when they are not obvious,
- keep visible instructions aligned with programmatic field purpose,
- and avoid using placeholder-only hints as the sole explanation of what belongs in a field.

This does **not** require long lectures above every input.
It requires enough task-specific clarity that a voter can predict whether a field expects a full address, a ZIP code, a birth date, a county name, a case number, a voter ID, or a free-form question.

## Keyboard and input hints should help entry without pretending to validate

Many public routes are first used on phones.
That means `422` should explicitly review whether the route presents a sensible entry posture for the kind of value being requested:
- numeric entry should not unnecessarily summon a full text keyboard,
- free-form fields should not be squeezed into brittle numeric or masked entry,
- and the route should not confuse keyboard hints with actual validation logic.

The important distinction is the one MDN makes explicit:
input hints can help the user agent present a better keyboard,
but they do **not** by themselves guarantee valid input.
So this control asks offices to align field hints with expected data **and** keep correction logic clear when the hint is not enough.

## Paste, autofill, and constrained-format helpers should preserve the voter’s path to the answer

Official voter-information routes often benefit from autofill, remembered addresses, stored contact information, copied ZIP codes, pasted ballot IDs, or pasted confirmation numbers.
They also sometimes use masks or constrained formatting for dates, phone numbers, and similar patterns.

That can help — but only if the helper remains subordinate to the answer lane.
For this archive, that means:
- do not make ordinary paste behavior a casualty of formatting,
- do not let masks or inline normalizers silently destroy or obscure the value the voter entered,
- do not let autofill collide fields whose purposes are actually different,
- and keep the post-entry correction path easier than re-entering the whole query from memory.

The rule is not “never constrain input.”
It is “do not make the current answer depend on a brittle entry gadget that treats common pasted or autofilled input as hostile noise.”

## Errors should identify what is wrong, how to fix it, and preserve the entered value where possible

A voter who enters the wrong format or an unmatched value should not be left with a generic “invalid input” banner, a red border, or a cleared form.
For this archive, `422` should explicitly review:
- whether errors identify the field or step that failed,
- whether the text describes what was wrong in plain language,
- whether known fixes or examples are surfaced when safe,
- whether focus/announcement behavior makes the problem discoverable,
- and whether the route preserves already-entered values when retrying is appropriate.

This matters because the public task is rarely “submit a form correctly for its own sake.”
The real task is to reach the current authoritative answer.
A field-entry route fails `422` when the error-recovery loop is so lossy or opaque that voters abandon the lookup instead.

## The same authoritative answer should survive input-assistance variants

Different devices or browsers MAY show different keyboards, autofill options, remembered values, or formatting assistance.
They should **not** silently change the underlying authoritative answer or hide warnings, deadlines, or office-routing instructions that only appear for one input-assistance path.

This composes directly with `406`.
Different entry modalities may justify different interaction cues.
They do **not** justify answer drift.

## Minimal field-entry-state taxonomy

A small taxonomy is enough:

1. **Field purpose clarity state** — each critical input exposes a clear task label and any needed format cue.
2. **Input hint alignment state** — keyboard/input hints align with expected data without pretending to be the whole validation story.
3. **Paste/autofill survivability state** — common pasted and autofilled values can be reviewed and corrected without brittle failure.
4. **Constrained-format helper state** — masks, patterning, or inline formatting do not block ordinary correction or turn entry into a trap.
5. **Error identification and suggestion state** — failures are described in text and known corrections are offered when safe.
6. **Value-preserving retry state** — the route preserves enough entered information that the voter can recover without retyping the whole query.
7. **Field-entry answer lane available** — the current official answer/help route remains materially reachable after ordinary entry mistakes.

## Preserve bounded reconstruction, not public-input exhaust

What matters here is bounded reconstruction of the office’s input-entry posture:
- which critical routes were reviewed,
- which field classes were present,
- whether input purpose and hints were aligned,
- whether paste/autofill and formatting helpers survived ordinary use,
- whether errors were identifiable and correctable,
- whether values were preserved on retry,
- and when the route was last reviewed.

Do **not** preserve raw public-entered values, copied IDs, full address strings, browser autofill contents, keystroke logs, or exhaustive session replay when bounded public-answer reconstruction is sufficient.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `field_entry_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_input_paths[]`
- `field_purpose_and_label_note`
- `format_expectation_note`
- `keyboard_hint_and_inputmode_note`
- `autocomplete_and_input_purpose_note`
- `paste_and_copy_entry_note`
- `input_mask_and_inline_formatting_note`
- `error_identification_note`
- `error_suggestion_note`
- `value_preservation_and_retry_note`
- `same_answer_across_input_variants_note`
- `field_entry_state_classes[]`
- `input_trace_policy{}`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- `supersedes`
- `superseded_by`

## Verification prompts that fit this surface

- Can a voter tell what each critical field expects before validation fires, including any unusual date/address/ID format requirement?
- Do keyboard/input hints and autofill cues help the device present the right entry posture without becoming the only validation rule?
- Can ordinary pasted or autofilled values survive review and correction instead of being trapped by masks or silent reformatting?
- When entry fails, does the route identify the problem in text, suggest the safe fix when known, and preserve enough of the prior entry to make retry reasonable?
- If the main lookup path remains brittle, is there still a plainly visible first-party office/help fallback?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-field-entry-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-field-entry-surface-checklist.md`

## Sources to keep pinned

Keep the lockfile entries for:
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: Requirements for delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- USWDS: Text input component guidance (xref: `uswds_text_input_component_page`)
- USWDS: Input mask component guidance (xref: `uswds_input_mask_component_page`)
- W3C WAI: Understanding SC 3.3.2 Labels or Instructions (xref: `w3c_wcag21_labels_or_instructions_page`)
- W3C WAI: Understanding SC 3.3.1 Error Identification (xref: `w3c_wcag21_error_identification_page`)
- W3C WAI: Understanding SC 3.3.3 Error Suggestion (xref: `w3c_wcag21_error_suggestion_page`)
- W3C WAI: Understanding SC 1.3.5 Identify Input Purpose (xref: `w3c_wcag21_identify_input_purpose_page`)
- MDN: `inputmode` attribute reference (xref: `mdn_inputmode_attribute_page`)
- MDN: `autocomplete` attribute reference (xref: `mdn_autocomplete_attribute_page`)
- Section508.gov: Guide to Accessible Web Design & Development (xref: `section508_guide_accessible_web_design_development_page`)
