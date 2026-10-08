# Official voter-information screen-reader surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes understandable through screen readers, braille displays, semantic structure, usable labels, and announced answer-state changes rather than visual layout alone.

## Inventory and review scope

- Identify the critical public-answer routes most likely to be used nonvisually: landing pages, lookup forms, results regions, warning banners, and office-help fallbacks.
- Distinguish this from keyboard-only review, small-viewport review, degraded-script review, and first-load overlay review.
- Re-check routes whose meaning depends heavily on visual grouping, unlabeled controls, dynamic result panes, or styling-only required-field cues.

## Structure, landmarks, and headings

- Confirm that the main answer/help lane is exposed through semantic sections or appropriately labeled landmarks rather than only by visual placement.
- Re-check that headings and section labels are descriptive enough to let a nonvisual user predict where the answer, warning, or fallback path lives.
- Avoid making the current official answer depend on a visual grouping that disappears when the page is linearized.

## Controls, instructions, and relationships

- Confirm that critical lookup, submit, filter, correction, and help controls expose usable names and role/state information.
- Re-check that grouped options, required-field cues, and helper text remain programmatically connected or explicitly textual rather than implied only by styling or proximity.
- Keep visible labels and programmatic names aligned closely enough that the control is recognizable across visual and nonvisual use.

## Dynamic updates and fallback

- Make sure lookup results, warnings, status notices, and validation/correction states become nonvisually apparent when they matter to the answer lane.
- Do not rely on silent partial-page swaps that update the answer only on screen.
- Preserve a visible and announceable first-party help/contact fallback when the main route becomes ambiguous in nonvisual use.

## Evidence posture

- Preserve only route labels, reviewed nonvisual paths, landmark/heading state, control naming state, relationship/instruction state, live-update announcement state, and last review time.
- Do not preserve screen-reader audio captures, braille traces, assistive-technology fingerprints, or other detailed accessibility-session exhaust when bounded policy reconstruction is sufficient.
