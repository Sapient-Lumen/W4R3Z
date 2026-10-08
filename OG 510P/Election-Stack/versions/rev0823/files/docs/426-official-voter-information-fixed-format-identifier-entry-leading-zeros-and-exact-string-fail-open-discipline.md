# 426 — Official voter-information fixed-format identifier entry, leading zeros, and exact-string fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that depend on a fixed-format, exact-character, or mixed-format public identifier before the current answer/help lane can appear**:
voter-registration lookup keys,
mail-ballot or provisional-ballot tracking numbers,
case or confirmation numbers,
partial driver-license or state-ID tokens,
PIN-like lookup fragments,
and similar public keys where the difference between a current official answer and a dead end can hinge on whether the office treats the token as an exact string rather than as a normal “number” field.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `294`, which governs registration-status lookups and correction notices,
- `295`, which governs mail-ballot status lookups and cure notices,
- `296`, which governs provisional-ballot status lookups and reason notices,
- `305`, which governs the authoritative office/help lane,
- `316`, which governs voter-history and participation-record lookups,
- `403`, which governs progressive enhancement and degraded-client recovery,
- `416`, which governs reflow, text scaling, and small-viewport survivability,
- `417`, which governs keyboard navigation and logical focus order,
- `418`, which governs nonvisual structure and announced state,
- `421`, which governs touch targets, hover boundaries, and coarse-pointer operability,
- `422`, which governs generic field purpose, autofill, and error recovery,
- `423`, which governs date-entry and picker fallback when the route specifically depends on a date,
- `424`, which governs address-entry and suggestion behavior when the route specifically depends on an address,
- or `425`, which governs personal-name structure and match recovery when the route specifically depends on a name.
- or `478`, which governs browser/device text-assistance mutation, silent correction or capitalization, and IME-composition commit posture once the entered identifier itself may be changed or still provisional before the route should treat it as exact.

It adds one narrow rule:
**if an official voter-information route asks the public for a fixed-format identifier before revealing the current answer, the office should keep exact-character expectations, visible format/length cues, leading-zero and separator handling, appropriate keyboard hints, and retry guidance clear enough that the current official answer does not depend on guessing whether the token is a number, an exact string, or a masked value that cannot be safely corrected.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, accessibility, usability, and audience-aware structure. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible, authoritative, user-centered, and mobile-first. USWDS’s current **Text input** guidance says text inputs support letters, numbers, or symbols, that mobile context matters, and that validation should wait until a user has interacted with the field. USWDS’s current **Input mask** guidance says masks can support valid values but has known accessibility issues and requires project-level accessibility testing. W3C’s current understanding guidance for **Labels or Instructions**, **Error Identification**, and **Error Suggestion** says fields should expose what input is expected, identify detected errors in text, and offer known safe corrections. MDN’s current `inputmode` reference says virtual-keyboard hints can be used to present an appropriate keyboard, while MDN’s current `input type="number"` reference says numeric-only strings that are not truly numbers are often better served by another input type plus `inputmode` instead of a number control. Section508.gov’s current accessible-web guidance separately says labels, instructions, and error suggestions should be easy to find. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_text_input_component_page`; xref: `uswds_input_mask_component_page`; xref: `w3c_wcag21_labels_or_instructions_page`; xref: `w3c_wcag21_error_identification_page`; xref: `w3c_wcag21_error_suggestion_page`; xref: `mdn_inputmode_attribute_page`; xref: `mdn_input_type_number_element_page`; xref: `section508_guide_accessible_web_design_development_page`)

That is enough to justify a compact control here.
A route can be current, mobile-usable, keyboard reachable, and generally pass `422`, `423`, `424`, and `425`, yet still fail first contact because a public identifier with leading zeros is treated like an incrementable number, punctuation or spacing rules are hidden until rejection, an input mask blocks paste or correction, or the page shows a masked review state that leaves the voter unable to tell which exact token the office expects.

## This is not the same thing as generic field-entry review, date review, address review, or name review

`422` asks whether the voter can generally tell what to type, recover from an error, and preserve entered values.

`423` asks whether date-gated routes survive pickers, segmented date fields, and visible date-window limits.

`424` asks whether address-gated routes survive autocomplete, unit detail, repeated address groups, and manual override after suggestion behavior begins.

`425` asks whether name-gated routes survive personal-name structure, punctuation, optional parts, and record-matching cues.

`426` asks a different question:
**once an official route specifically depends on a fixed-format or mixed-format identifier, can the voter tell whether the token is an exact string, enter it without losing meaningful characters, and reach a bounded retry/help lane when a format helper or parser is brittle?**

A route may pass `422` and still fail `426` if:
- the route uses a number input for a value whose exact digits, leading zeros, or separator pattern matter,
- the visible label says “ID number” but never says whether spaces, hyphens, prefixes, or letters are allowed,
- a mask or segmented-entry helper blocks paste, correction, or screen-reader review,
- the route silently strips characters or uppercases/lowercases a mixed-format token in a way that changes the lookup outcome,
- browser or device text assistance silently corrects, capitalizes, or commits the identifier before the voter has a clear review boundary,
- or a rejected identifier clears the value or gives no clue whether the office expected a voter ID, license fragment, case number, or another bounded alternate token.

Text-assistance mutation is a separate question from identifier format. `426` asks whether the route explains the expected token and preserves its meaningful characters; `478` asks whether browser/device writing assistance or active IME composition can rewrite or prematurely finalize that token before the route should trust it.


## Treat the identifier as the exact public token it is, not as a generic number

Many public lookup keys contain only digits.
That does **not** make them “numbers” in the UI sense.
They are often **exact strings**:
- leading zeros may matter,
- a fixed length may matter,
- letters or prefixes may matter,
- and displayed separators may be part of how the public was instructed to read the token.

The practical rule here is simple:
- if the route needs an exact public token, design and review it as an exact token,
- do not assume the semantics of an incrementable numeric control,
- and do not let browser stepper, rounding, or normalization behavior quietly rewrite the lookup key.

`426` does **not** ban numeric keyboards.
It requires the office to separate “show an appropriate keyboard” from “pretend the token is a mathematical number.”

## Visible format and length cues should exist before the voter fails

W3C and Section508 guidance point the same way: the field should expose what input is expected before the system rejects it. (xref: `w3c_wcag21_labels_or_instructions_page`; xref: `section508_guide_accessible_web_design_development_page`)

For this archive, that means the route should make clear, near the field:
- which identifier the office wants,
- whether the token may contain letters, spaces, or hyphens,
- whether the token has a fixed or typical length,
- whether the voter should copy it exactly as shown or type digits only,
- and whether a bounded alternate token or help path exists if the expected identifier is unavailable.

This does **not** require a long tutorial.
It requires enough task-specific clarity that the voter can tell whether to enter a voter ID, ballot-tracking code, confirmation number, or license fragment **before** a generic “invalid ID” error turns the route into guesswork.

## Leading zeros, separators, and mixed-format characters must survive ordinary use

A common failure here is subtle rather than dramatic:
the field appears to work, but the route silently removes leading zeros, strips letters or separators, or reformats a pasted token into something the backend does not actually match.

For this archive, `426` should explicitly review whether:
- leading zeros survive typing, paste, review, and retry,
- inserted spaces or hyphens are optional helpers rather than hidden requirements,
- mixed-format tokens keep their meaningful letters or prefixes,
- separator removal, trimming, or uppercasing/lowercasing is either harmless and explained or avoided,
- and displayed review text stays close enough to the source token that the voter can tell what the system is actually matching.

The rule is not “never normalize.”
It is “do not silently normalize the public token in a way that changes the answer or hides why the route failed.”

## Masks and segmented entry should help without trapping paste, review, or correction

USWDS’s current input-mask guidance is useful precisely because it is cautious: masks can support common patterns, but the component has known accessibility issues and requires project-level testing. (xref: `uswds_input_mask_component_page`)

That is enough for a compact rule here:
- a mask may help display a familiar pattern,
- but the mask should not be the only workable input path,
- and the route should stay usable when a voter pastes the token, edits the middle of the token, or revisits the field after an error.

`426` does **not** require every office to remove masks.
It requires masks to remain subordinate to the answer lane.
If the mask becomes the reason a voter cannot submit, review, or correct the exact token, the mask has become a first-contact integrity failure.

## Keyboard hints should help mobile entry without forcing the wrong field semantics

MDN’s current inputmode reference makes the practical implementation point: virtual-keyboard hints can improve the keyboard posture on mobile devices. MDN’s current number-input reference adds the caution that a number control is for true numeric values, not every digit-only string. (xref: `mdn_inputmode_attribute_page`; xref: `mdn_input_type_number_element_page`)

So the compact archive posture is:
- choose a field posture that preserves the exact token,
- use keyboard hints to reduce friction where appropriate,
- and avoid field types whose semantics imply stepwise numbers when the route really needs an exact identifier string.

This is especially important for tokens that may be copied from paper notices, mail pieces, SMS/email notices, or screenshots, where ordinary public behavior is often paste-first rather than digit-by-digit entry.

## Error recovery should preserve the token and explain the next bounded step

W3C’s error-identification and error-suggestion guidance is direct: if the system detects an input error, identify it in text, and if a safe correction is known, say what correction is possible. (xref: `w3c_wcag21_error_identification_page`; xref: `w3c_wcag21_error_suggestion_page`)

For this archive, that means:
- do not clear the identifier after a failed attempt,
- say whether the issue is length, character set, wrong identifier type, or no matching record,
- keep any alternate-token hint bounded and explicit,
- and preserve a visible office/help lane when automated matching remains brittle.

A route should not tell the voter merely “invalid number” when the real issue is that the office wanted a different public token or exact character posture.

## Preserve review state, not raw identifier corpora

This control is about public-answer integrity, not building a sensitive identifier archive.
The evidence posture should therefore preserve:
- which identifier families the route claims to accept,
- whether exact-string semantics, leading-zero handling, mask behavior, and retry posture were reviewed,
- which public routes were checked,
- and when the review last occurred.

It should **not** require preserving raw voter IDs, full tracking-number corpora, rejected lookup-attempt logs tied to real voters, or exhaustive session replay when bounded policy reconstruction is sufficient.

## What to test

- Can a voter tell which identifier is wanted before typing anything?
- If the identifier includes leading zeros, do they survive typing, paste, review, and retry?
- If the token contains letters or separators, does the route explain whether they are allowed, optional, or required?
- Does a mask or segmented helper still allow paste, mid-string correction, and screen-reader review?
- Does mobile entry present a sensible keyboard without turning the token into an incrementable number field?
- If entry fails, does the route preserve the value, explain the problem in text, and keep a first-party help lane visible?
- Do semantically equivalent entry variants resolve to the same authoritative answer or the same explainable recovery posture?

## Minimal companion artifacts

- Template payload: `artifacts/templates/official-voter-information-fixed-format-identifier-entry-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-fixed-format-identifier-entry-surface-checklist.md`
