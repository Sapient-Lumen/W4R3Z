# Official voter-information address-entry surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes workable when the public must enter, choose, or confirm an address before the current answer appears.

## Inventory and review scope

- Identify the critical public-answer routes that depend on address entry: polling-place lookup, ballot-style lookup, residence confirmation, drop-box or vote-center lookup, and similar address-gated help paths.
- Distinguish this from generic field-entry review, map/geolocation review, date-entry review, and special-case address-policy docs.
- Re-check routes whose success depends on autocomplete, typeahead, geocoder suggestions, or repeated residential-vs-mailing address groups.

## Address role and suggestion posture

- Confirm that each critical route states which address role it needs before suggestions begin.
- Do not rely on placeholder-only hints or suggestion text to explain whether the field expects a residence address, mailing address, temporary address, or other location.
- Treat autocomplete or geocoder suggestions as helpers, not hidden commitments.
- Do not auto-submit, auto-reroute, or silently lock a guessed address merely because a suggestion is highlighted.

## Manual entry, secondary detail, and repeated address groups

- Keep a workable typed/manual path available before and after suggestions appear.
- Confirm that voters can reject or edit a suggestion without restarting the route.
- Re-check that apartment, suite, building, lot, urbanization, military-post, rural-route, or other relevant secondary detail is preserved when needed.
- When collecting more than one address context, keep residential and mailing groups visibly and programmatically distinct and verify any same-as helper does not overwrite the wrong group.

## Recovery and evidence posture

- If the route cannot confidently normalize an address, keep a bounded retry/help lane available instead of a generic invalid-address dead end.
- Confirm that typed, pasted, suggested, and manually corrected address variants resolve to the same authoritative answer for the same location.
- Preserve only route labels, reviewed address paths, address-role review state, suggestion-behavior review state, secondary-detail review state, recovery review state, and last review time.
- Do not preserve raw residential addresses, unit identifiers from real users, full geocoder request logs, or exhaustive session replay when bounded policy reconstruction is sufficient.
