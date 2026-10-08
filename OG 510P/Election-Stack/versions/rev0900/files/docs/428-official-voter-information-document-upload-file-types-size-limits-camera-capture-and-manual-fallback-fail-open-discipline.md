# 428 — Official voter-information document upload, file types, size limits, camera capture, and manual-fallback fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that ask the public to attach a file, image, scan, or photo-captured document before the current answer/help lane can appear or the next official step can continue**:
registration or update routes that ask for supporting documents,
mail-ballot request, cure, or signature-update routes that ask for an ID or affidavit image,
status/problem routes that ask for a screenshot or document upload before help continues,
and similar public answer/help paths where upload success becomes part of whether a voter can reach the current official route.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `300`, which governs the actual ID / alternative-document rules,
- `304`, which governs mail-ballot request methods and deadlines,
- `305`, which governs the authoritative office/help lane,
- `307`, which governs problem reporting and civil-rights escalation,
- `317`, which governs replacement / nonreceipt / surrender fallback paths,
- `339`, which governs signature alternatives and cure,
- `373`, which governs official forms/applications/affidavits more broadly,
- `378`, which governs file delivery and document-download surfaces,
- `412`, which governs browser/device permission prompts,
- `421`, which governs pointer-operability,
- `422`, which governs generic field purpose, autofill, and error recovery,
- or `427`, which governs phone/email targets and verification-code gates.

It adds one narrow rule:
**if an official voter-information route depends on a voter successfully attaching a document, image, or photo-captured file before the current answer/help lane can continue, the office should keep the allowed file kinds, count and size limits, camera-vs-file posture, upload-progress/retry behavior, and bounded non-upload fallback clear enough that the answer does not depend on guessing whether the route wanted a PDF, a phone photo, front-and-back images, a live camera capture, or a full restart after an ordinary upload failure.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, accessibility, usability, and audience-aware structure. Digital.gov’s current digital-first public-experience guidance says public digital services should be accessible, authoritative, user-centered, and mobile-first. USWDS’s current **File input** component says file input allows users to attach one or multiple files, and its current accessibility-test guidance says teams need to test the component in their own context, provide instructions for file type and use, verify mobile behavior, and review keyboard and screen-reader behavior. MDN’s current `input type="file"`, `accept`, and `capture` references explain that file inputs can limit file-type choices by hint, that `accept` does not itself validate selected files, that `image/*` often allows camera capture on mobile devices, and that `capture` is limited-availability rather than a baseline guarantee. W3C’s current form-instruction and labels/instructions guidance says forms should tell users what data, format, and other requirements apply before the user is forced to guess. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_file_input_component_page`; xref: `uswds_file_input_accessibility_tests_page`; xref: `mdn_input_type_file_element_page`; xref: `mdn_accept_attribute_page`; xref: `mdn_capture_attribute_page`; xref: `w3c_wai_forms_instructions_page`; xref: `w3c_wcag21_labels_or_instructions_page`)

That is enough to justify a compact control here.
A route can be current, generally accessible, and even pass `422` or `427`, yet still fail first contact because:
- the page never says whether it wants a PDF, image, or either one,
- the voter discovers a file-size or count limit only after selection,
- the route requires front/back or multi-page evidence but never says so before rejection,
- the mobile route silently expects live camera capture,
- the route offers camera capture only, even though `capture` is not a baseline behavior,
- upload failure clears all entered context and forces a full restart,
- or the page says only “upload failed” without distinguishing wrong type, too large, too many files, permission denial, interrupted transfer, or server rejection.

## This is not the same thing as generic field-entry review, file delivery, or verification-code review

`422` asks whether the voter can generally tell what to type, preserve values, and recover from ordinary field errors.

`378` asks whether official files and downloads can be received and opened.

`427` asks whether the voter can use a phone/email target and code-entry step.

`428` asks a different question:
**once the route depends on attaching a file or photo before the answer/help lane can continue, can the voter tell what artifact is required, choose or capture it in an ordinary way, survive ordinary upload errors, and reach a bounded alternate/help lane if upload itself is the weak link?**

A route may pass `422`, `378`, and `427` and still fail `428` if:
- it labels the control “Upload” without saying what file kinds are accepted,
- it exposes a camera path but not an existing-file path,
- it silently rejects a perfectly legible image because of a hidden size or count rule,
- it starts upload on file selection with no clear retry/help posture,
- or it clears the chosen files and the rest of the form after an intermittent network error.

## Say what evidence the route wants before the voter touches the picker

W3C’s current form-instructions guidance says forms should indicate relevant input requirements, formats, and timing limits before the user has to discover them through failure. Its labels/instructions guidance says users should know what information is expected. USWDS’s current file-input guidance also reinforces explicit instructions for file type and use. (xref: `w3c_wai_forms_instructions_page`; xref: `w3c_wcag21_labels_or_instructions_page`; xref: `uswds_file_input_accessibility_tests_page`)

For this archive, that means the route should say near the control:
- whether the office wants a PDF, image, or another specific file type,
- whether one file or multiple files are allowed,
- whether the route expects front and back images, multiple pages, or a combined document,
- whether there is a practical file-size limit,
- and whether a bounded alternate/help lane exists if the voter cannot upload right now.

The rule is not “document every implementation detail.”
It is “do not make the voter guess what kind of artifact the official route needed before continuing.”

## Treat `accept` as a hint, not a complete rule system

MDN’s current `accept` guidance is precise and useful here: `accept` provides hints that guide browsers toward the right files, but it does not itself validate the selected files. MDN’s current file-input reference similarly says file inputs can suggest specific file types or categories such as `image/*`. (xref: `mdn_accept_attribute_page`; xref: `mdn_input_type_file_element_page`)

For `428`, that means:
- the page should expose human-readable file-type expectations instead of relying on the picker alone,
- server-side or route-level validation should still produce useful public-facing error states,
- and the route should not treat a browser chooser hint as if it had already explained the requirement to the voter.

## Do not make live camera capture the only workable posture

MDN’s current `capture` guidance says camera capture on file inputs is limited-availability and depends on the `accept` type. MDN also notes that `image/*` on many mobile devices may let the user take a picture with the camera. That combination is useful precisely because it warns against over-committing to one capture behavior. (xref: `mdn_capture_attribute_page`; xref: `mdn_input_type_file_element_page`)

For this archive, that means:
- a route may offer camera capture,
- but it should also preserve an ordinary existing-file path when practical,
- it should not assume all browsers expose the same camera behavior,
- and it should not make permission success, camera availability, or lens choice the hidden prerequisite for reaching the answer/help lane.

This does **not** forbid camera capture.
It forbids pretending that “open the camera and take a photo right now” is a universal baseline interaction.

## Error states should distinguish the ordinary reasons uploads fail

USWDS’s current file-input examples and accessibility tests explicitly include helpful incorrect-file-type errors, instructions for file type/use, and project-context testing for accessibility. W3C’s current error-identification guidance says errors should be described to the user, and its on-input guidance warns against surprise context changes. (xref: `uswds_file_input_component_page`; xref: `uswds_file_input_accessibility_tests_page`; xref: `w3c_wcag21_error_identification_page`; xref: `w3c_wcag21_on_input_page`)

For `428`, that means the public route should separate at least:
- wrong file type,
- too many files,
- file too large,
- unreadable/corrupt upload,
- permission/camera denial where capture was attempted,
- interrupted or timed-out transfer,
- and server-side rejection that still leaves a help lane.

This surface is not satisfied if the office merely says “upload failed” while clearing the selected files and hiding what the voter should do next.

## Preserve bounded review state across retry when safe

A public voter-information route should preserve safely preservable state across ordinary upload retry: previously entered text fields, chosen upload mode, and, where the platform allows, visible reference to the selected file name or the need to reselect only the failed artifact rather than redoing the whole route.

The goal is not to preserve sensitive documents forever.
The goal is to avoid the common first-contact failure where a network hiccup or picker mismatch turns a nearly complete official route into a full restart.

## Test the upload lane on mobile, keyboard, zoom, and screen-reader paths

USWDS’s current file-input accessibility tests are unusually valuable here because they are concrete: teams should test file input in project context, on mobile, at zoom, with keyboard navigation, and with screen readers. The same page notes real edge cases, including focus-model quirks and a screen-reader exception where invalid-file-type errors may not announce as expected. (xref: `uswds_file_input_accessibility_tests_page`)

That means `428` should review whether:
- upload remains visible and functional on mobile,
- instructions remain visible at 200% zoom and ordinary reflow,
- keyboard users can reach and operate the control predictably,
- screen readers announce the control, related instructions, and upload errors meaningfully,
- and drag-heavy affordances still leave a non-drag path.

## Preserve bounded review evidence, not the documents themselves

This control is about public-answer integrity, not building a retention archive of voter-submitted documents.
The evidence posture should therefore preserve:
- which public routes depend on document upload or camera capture,
- the stated file-type / count / size / front-back rules,
- whether camera capture is optional or required,
- whether upload errors and retry/help behavior were reviewed,
- and when the review last occurred.

It should **not** require preserving real voter documents, scans, IDs, affidavit images, signature images, camera captures, EXIF metadata, full upload logs tied to named voters, or exhaustive session replay when bounded policy reconstruction is sufficient.

## What to test

- Can a voter tell what file types the route accepts before opening the picker?
- If the route expects one file, multiple files, front/back images, or a combined PDF, is that explicit before failure?
- Are practical size/count limits visible before the route rejects the upload?
- If camera capture is offered, does an ordinary existing-file path still remain available when practical?
- Do upload errors distinguish wrong type, too-large, too-many, permission denial, interrupted transfer, and server-side rejection?
- After an ordinary upload failure, does the route preserve safely preservable state instead of forcing a full restart?
- Does a visible first-party help or alternate recovery lane remain available when upload itself is the weak link?

## Minimal companion artifacts

- Template payload: `artifacts/templates/official-voter-information-document-upload-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-document-upload-surface-checklist.md`
