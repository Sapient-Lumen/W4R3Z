# Official voter-information combobox surface checklist

Use this checklist for official voter-information routes that use a **combobox**, **typeahead**, **searchable select**, or other **suggestion popup** to choose from a bounded official set before revealing or changing the answer lane.

## Scope and route inventory

- [ ] Record which official routes use combobox/typeahead/searchable-select controls.
- [ ] Record what official set each control chooses from (county, office, polling location subset, FAQ/article, language, other).
- [ ] Record whether the control is editable, select-only, or otherwise specialized.

## Commit boundary and recovery

- [ ] Review whether the route makes clear what action actually commits a suggestion.
- [ ] Review whether merely typing or highlighting a suggestion leaves the prior state recoverable instead of silently changing the answer lane.
- [ ] Review whether the voter can revise text, dismiss the popup, or back out of an explored suggestion without restarting the route.
- [ ] Review whether clearing the field also clears any hidden active selection when that selection controls the visible answer lane.

## Labels, disambiguation, and dynamic updates

- [ ] Review whether each combobox has a clear label and instructions that identify the official set it controls.
- [ ] Review whether multiple comboboxes on the same page remain distinguishable in visible and assistive-technology use.
- [ ] Review whether the route avoids auto-submission or immediate rerouting on input unless that behavior is explicit and well-bounded.
- [ ] Review whether committed answer-lane changes are announced in bounded form without treating the announcement itself as silent consent.

## Compact/mobile and evidence discipline

- [ ] Review compact/mobile behavior so popup overlays, collapsed labels, or auto-scroll do not erase the commit boundary.
- [ ] Preserve a small public digest of the controlled set, commit boundary, recovery posture, update-announcement posture, and review time.
- [ ] Do not retain individualized typing logs, keystroke timing, session replay, or person-level suggestion telemetry merely to prove the control existed.
