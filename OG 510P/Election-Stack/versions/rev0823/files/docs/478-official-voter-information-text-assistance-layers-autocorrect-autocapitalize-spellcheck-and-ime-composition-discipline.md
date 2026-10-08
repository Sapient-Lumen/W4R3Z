# 478 — Official voter-information text-assistance layers, autocorrect/autocapitalize, spellcheck, and IME composition discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes where browser, OS, or input-method text assistance can mutate or delay the entered value before the voter reveals, commits, or submits the current official answer/help lane**:
registration-status lookups,
address- or jurisdiction-based routing fields,
contact-target entry before code delivery,
problem-report and request forms,
searchable official pickers,
and similar public routes where the governing difference between “right value” and “wrong lane” may turn not on the office’s rule text, but on what the browser/device quietly did to the text while the voter was entering it.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `418`, which governs nonvisual semantics, announced state, and screen-reader structure more broadly,
- `422`, which governs field purpose, keyboard/input hints, autofill, and ordinary error recovery more broadly,
- `424`, which governs address-entry autocomplete suggestions, unit details, and manual override,
- `427`, which governs phone/email targets, delivery channels, and verification-code recovery,
- or `453`, which governs combobox suggestion popups and explicit commit when the route chooses from a bounded official set.
- or `481`, which governs browser-native constraint-validation blocking and validation-message posture once the failure state has moved from value mutation/composition into the user-agent’s ordinary `required` / type / pattern / range gate.

It adds one narrow rule:
**if an official voter-information route depends on entered text to reveal, route, verify, or submit the current official answer, the office should keep browser/device text-assistance layers subordinate to the controlling value, distinguish composing text from committed text, and avoid silent correction or capitalization behavior that changes decisive entered values without an obvious review/correction path.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, accessibility, usability, and accuracy. The current HTML Standard matters because `autocapitalize` and `autocorrect` are explicit browser hints, can inherit from a `form`, and must not be relied on for validation; the standard also says `autocapitalize` / `autocorrect` never turn on for `email`, `url`, or `password` inputs. MDN’s current `spellcheck` guidance matters because spellcheck is only a browser hint, browsers are not required to perform it, and spellchecking can have security/privacy consequences. MDN’s current `beforeinput` guidance matters because not every user modification reaches that hook: accepted spellchecker corrections, autocomplete, password-manager autofill, and IME-driven changes may vary by browser/OS and may require `input`-level recovery too. MDN’s current composition-event and `InputEvent.isComposing` guidance matters because composition is its own state between `compositionstart` and `compositionend`, not the same thing as ordinary committed text. MDN’s current `writingsuggestions` guidance matters because browser-provided sentence-completion assistance can be enabled by default where supported and should be reviewed explicitly on decisive fields. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `whatwg_html_autocapitalize_autocorrect_section`; xref: `mdn_autocapitalize_global_attribute_page`; xref: `mdn_autocorrect_global_attribute_page`; xref: `mdn_spellcheck_global_attribute_page`; xref: `mdn_beforeinput_event_page`; xref: `mdn_compositionstart_event_page`; xref: `mdn_inputevent_interface_page`; xref: `mdn_inputevent_iscomposing_property_page`; xref: `mdn_writingsuggestions_global_attribute_page`; xref: `w3c_uievents_algorithms_composition_section`)

That is enough to justify a compact control here.
A route may pass `422`, `424`, `427`, and `453` yet still fail the public because:
- an address or office name is silently corrected to a nearby but wrong term before lookup fires,
- a browser/device capitalizes or rewrites a contact target that should have stayed exact,
- an IME composition session is treated as though the voter had already finished typing,
- the route auto-submits, live-reroutes, or chooses a suggestion while the visible text is still provisional,
- spellcheck or browser writing help appears on a sensitive or exact-value field where the office never reviewed that exposure,
- or a team handles only `beforeinput` and misses later browser/device mutations that arrive through `input` or composition completion.

## This is not the same thing as field labels, address autocomplete, or combobox commit

`422` asks whether the voter can tell what to type, get a sensible keyboard/input posture, preserve entered values, and recover from ordinary entry errors.

`424` asks whether address suggestions, unit details, and geocoder matches stay reviewable and manually overridable.

`427` asks whether contact-target and verification-code lanes keep channel requirements and recovery routes clear.

`453` asks whether suggestion popups and comboboxes keep highlight/exploration distinct from explicit user commitment.

`478` asks a different question:
**once browser/device text assistance itself starts capitalizing, correcting, underlining, suggesting, or composition-buffering the value, can the voter still tell what is provisional, what is exact, what actually committed, and how to fix a mutated value before the office route treats it as authoritative?**

A route may pass the earlier controls and still fail `478` if:
- labels and format hints are fine, but autocorrection still rewrites the decisive value,
- address suggestion review is fine, but the typed street or locality was altered before suggestion review even began,
- the contact-target lane is clear, but the browser capitalizes or “helps” an email or case token at the wrong moment,
- or combobox commit is explicit, yet IME composition text is mistaken for a finished search term and triggers the popup or reroute too early.

## Browser and OS text assistance is a real mutation layer, not just decoration

The current HTML Standard and MDN guidance are explicit that `autocapitalize`, `autocorrect`, and related text-assistance controls are browser hints, not guarantees, and support varies across engines. The standard also allows `autocapitalize` and `autocorrect` to be set at the `form` level, which means one forgotten default can quietly affect several fields at once. (xref: `whatwg_html_autocapitalize_autocorrect_section`; xref: `mdn_autocapitalize_global_attribute_page`; xref: `mdn_autocorrect_global_attribute_page`)

For this archive, that means maintainers should review text-assistance posture as its **own** public-answer layer:
- which decisive fields inherit assistance from the containing `form`,
- which fields need exact-value entry rather than “helpful” correction,
- which fields can tolerate assistance only if review remains visible before lookup/submit,
- and which fields should never let sentence completion or correction masquerade as the voter’s final intended value.

The rule is not “turn off every assistance feature everywhere.”
It is “do not let browser/device assistance quietly become the policy that chooses the controlling public answer lane.”

## Exact identifiers, contact handles, URLs, and similar values need a stricter posture

The current HTML Standard says `autocapitalize` never enables for `email`, `url`, or `password` inputs, and the current MDN `autocorrect` guidance says those input types always have autocorrection off. That is a useful floor, not a complete design recipe. Many official voter-information routes also depend on other effectively exact values: case numbers, voter IDs, confirmation codes, apartment/unit fragments, precinct codes, county abbreviations, and other strings where “helpful” rewriting is not neutral. (xref: `whatwg_html_autocapitalize_autocorrect_section`; xref: `mdn_autocorrect_global_attribute_page`)

For `478`, a route should review whether exact-value fields keep a bounded assistance posture such as:
- no sentence-case or word-case transformation,
- no spelling correction,
- no browser sentence-completion or writing-suggestion layer where supported,
- no auto-submit or reroute on a silently mutated value,
- and a visible correction path before the route treats the value as authoritative.

What fails `478` is not merely “the browser offered help.”
What fails `478` is letting an exact field inherit a writing-assistance posture that can change the decisive meaning of the value while the page behaves as though nothing material happened.

## Names, addresses, and jurisdiction labels may benefit from assistance, but still need explicit review

Not every important field is an exact token.
Names, street names, city names, tribal place names, or office labels may benefit from spelling help or composition-aware entry on some devices.
But these fields still become dangerous when the route:
- fires a lookup on the first browser-corrected version without review,
- replaces the voter’s typed form with a normalized form that hides what changed,
- or collapses “browser suggested a nearby spelling” into “the office has now chosen the answer-bearing route.”

That is why `478` composes with `424` and `453` instead of replacing them.
The office may allow assistance on address or place-name entry, but it should still keep a visible review/correction boundary before that mutated text decides a polling-place answer, a county routing lane, or an office contact destination.

## Composition is not commitment

MDN’s current composition-event guidance says `compositionstart` begins a composition session for IME-driven input, and `InputEvent.isComposing` indicates whether the event fired after `compositionstart` and before `compositionend`. The current UI Events draft also treats active composition as its own state rather than ordinary finished key input. (xref: `mdn_compositionstart_event_page`; xref: `mdn_inputevent_interface_page`; xref: `mdn_inputevent_iscomposing_property_page`; xref: `w3c_uievents_algorithms_composition_section`)

For this archive, that means a route should not quietly treat these as equivalent:
- text currently being composed,
- text that has only just been accepted from composition,
- text that the voter has actually reviewed and committed for lookup or submit,
- and text that a browser/device then further corrected or completed.

A route fails `478` if it:
- auto-submits on Enter while the IME composition is still active,
- opens or commits a suggestion popup as if partially composed text were final,
- live-routes to a county, office, or record on the basis of provisional composition text,
- or gives no way to tell whether the visible value is still composing, just-corrected, or truly committed.

## `beforeinput` is useful, but it is not a complete interception boundary

MDN’s current `beforeinput` guidance is especially important here: not every user modification results in `beforeinput`, and some modifications may be non-cancelable or vary by browser/OS, including accepted spellchecker corrections, autocomplete, password-manager autofill, and IME-related changes. (xref: `mdn_beforeinput_event_page`)

That means an office route should not rely on one optimistic frontend assumption like:
- “we intercept all value changes in `beforeinput`, so silent mutation cannot happen,”
- or “if the browser changed something, we would have blocked it already.”

For `478`, maintainers should review the full consequence path:
- what happens before the browser mutates text,
- what happens after `input`,
- what happens when composition ends,
- and whether any consequential lookup, reroute, auto-submit, or validation story still assumes a value the voter never clearly reviewed.

## Spellcheck and writing suggestions can also be privacy and authority boundaries

MDN’s current `spellcheck` guidance says spellchecking is only a browser hint and notes explicit security/privacy concerns because spellchecking may involve third parties; MDN also says authors should consider `spellcheck="false"` for fields that may contain sensitive information. MDN’s current `writingsuggestions` guidance says browser-provided writing suggestions may be enabled by default where supported and can be disabled for editable fields. (xref: `mdn_spellcheck_global_attribute_page`; xref: `mdn_writingsuggestions_global_attribute_page`)

For this archive, that means a voter-information route should review at least two separate questions:
1. **privacy question:** should this field expose its contents to browser spellcheck or writing-help layers at all?
2. **authority question:** if browser/device writing help appears, could it change a decisive value in a way the office never intended to bless as the controlling lookup or submit text?

Free-text feedback or question boxes may reasonably allow more assistance.
Exact identifiers, private notes, case narratives, or structured values that drive routing should receive a stricter posture.

## Minimal text-assistance state taxonomy

A compact taxonomy is enough here:

1. **Composing state** — IME or other composition is active; visible text is not yet treated as committed.
2. **Mutated-but-reviewable state** — browser/device assistance changed, suggested, or completed text, but the route has not yet treated that value as authoritative.
3. **Committed value state** — the voter has a clear moment of review/commit and the route may now use the value for lookup, routing, or submit.
4. **Free-text assistance-allowed state** — assistance is allowed because the field is advisory/free-text rather than an exact routing/identifier value.

What this archive wants to avoid is collapsing all four into one ambiguous “the field has text in it, therefore the route may now act” story.

## Evidence and privacy posture

The evidence posture here is about reconstructing whether text-assistance and composition boundaries were reviewed.
Preserve:
- which decisive field classes were reviewed,
- what assistance posture each class received,
- whether composition-sensitive routing/submit controls were tested,
- whether exact/sensitive fields disabled or constrained spellcheck / correction / writing suggestions,
- and the last review time.

Do **not** preserve by default:
- raw keystroke logs,
- full IME composition traces,
- per-user accepted-correction histories,
- spellcheck dictionaries or third-party suggestion telemetry,
- or individualized recordings of every mutated input event.

## Claims this control should support

1. **Field-class posture claim:** decisive fields were classified by exactness/sensitivity rather than given one undifferentiated browser-text-assistance policy.
2. **Exact-value protection claim:** exact identifiers, contact handles, URLs, and similar values do not silently inherit misleading capitalization/correction behavior.
3. **Composition-boundary claim:** routes that react to typed text distinguish composition from final commitment before consequential lookup/reroute/submit behavior.
4. **Mutation-review claim:** browser/device text mutations remain reviewable before the route treats the value as authoritative.
5. **Privacy-minimization claim:** spellcheck/writing-assistance posture for sensitive fields was reviewed rather than left to accidental browser defaults.
6. **Recovery claim:** when assistance changes the text or the user rejects the suggestion, the route preserves an ordinary correction path instead of forcing re-entry or silent commitment.

## Canonical digest artifacts

Publish **small digests of reviewed text-assistance posture**, not keystroke telemetry.

- **Text Assistance Surface Digest (TASD):** digest of reviewed field classes, assistance posture, and browser-variance notes.
- **Composition Commit Boundary Digest (CCBD):** optional digest proving that composition-sensitive routes do not auto-commit while text is still provisional.
- **Sensitive Field Assistance Posture Digest (SFAPD):** optional digest for spellcheck / writing-suggestion / exact-value review on sensitive or exact fields.

## What belongs in the public text-assistance payload

Keep the payload **small, route-aware, and field-class focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `text_assistance_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_text_entry_routes[]`
- `field_class_policies[]`
- `form_level_inheritance_note`
- `autocapitalize_policy_note`
- `autocorrect_policy_note`
- `spellcheck_policy_note`
- `writing_suggestions_policy_note`
- `ime_composition_commit_note`
- `mutation_review_boundary_note`
- `sensitive_field_exposure_note`
- `browser_variance_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw composition or keystroke traces,
- user-specific corrected values,
- suggestion-provider telemetry,
- or screenshots of private entered text merely to prove the control was reviewed.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which reviewed routes depended on entered text before revealing or submitting the official answer?
- Which decisive fields were treated as exact/sensitive rather than as ordinary free text?
- Could browser/device assistance silently capitalize, correct, or complete a value that changed routing or submission meaning?
- Did the route distinguish IME composition from final commit before it ran lookup, reroute, or auto-submit logic?
- Was any spellcheck or writing-suggestion posture for sensitive/exact fields reviewed explicitly?
- If browser/device assistance changed the text, could the voter see and correct that value before the office route treated it as authoritative?

## How this fits the family map

`478` belongs in the voter-facing public-answer-surfaces family because browser/device text assistance is itself a public delivery layer for entered values.
The underlying voter question still belongs to another family surface.
What changes here is whether the office let browser or OS help quietly decide what value counted.
It stays small by refusing to become a generic internationalization handbook, IME tutorial, or mobile-typing style guide.
The archive only cares about the subset of text-assistance behavior that can silently change the truthfulness, routing, privacy posture, or commitment boundary of official voter-information delivery.

## Minimal artifacts in this archive

- `artifacts/templates/official-voter-information-text-assistance-surface-payload.json`
- `artifacts/checklists/official-voter-information-text-assistance-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- `eac_effective_design_for_the_administration_of_federal_elections_page`
- `whatwg_html_autocapitalize_autocorrect_section`
- `mdn_autocapitalize_global_attribute_page`
- `mdn_autocorrect_global_attribute_page`
- `mdn_spellcheck_global_attribute_page`
- `mdn_beforeinput_event_page`
- `mdn_compositionstart_event_page`
- `mdn_inputevent_interface_page`
- `mdn_inputevent_iscomposing_property_page`
- `mdn_writingsuggestions_global_attribute_page`
- `w3c_uievents_algorithms_composition_section`
