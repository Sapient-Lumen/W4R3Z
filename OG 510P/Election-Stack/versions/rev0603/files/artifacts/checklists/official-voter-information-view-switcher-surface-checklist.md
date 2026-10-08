# Official voter-information view-switcher surface checklist

Use this checklist for official voter-information routes that expose **the same answer-bearing official set through multiple views or presentation modes** such as list/map, list/calendar, card/table, or similar labeled toggles.

## View identity and control posture

- [ ] Record which official routes expose multiple views onto the same answer-bearing set.
- [ ] Review whether the active view is obvious, stably named, and visually distinguishable from alternate views.
- [ ] Review whether view labels are short and descriptive enough that voters can predict what will change before switching.
- [ ] Review whether the control relationship is conveyed clearly and whether the implementation uses real buttons or a true tab interface as appropriate.
- [ ] Review whether the route avoids ambiguous mixtures of “current,” “selected,” “pressed,” or “active” state language.

## Activation and cross-view continuity

- [ ] Review whether changing views requires explicit user action rather than silently switching on focus or exploration.
- [ ] Review whether the route makes clear whether alternate views are presentation-equivalent or materially different.
- [ ] Review whether search terms, filters, date ranges, jurisdiction scope, and sort state carry across views or reset with a visible explanation.
- [ ] Review whether the currently selected item remains re-findable after switching views.
- [ ] Review whether the route preserves an easy return to the more reviewable overview mode.

## Compact/mobile and accessibility review

- [ ] Review whether compact/mobile layouts keep the active-view cue intelligible and avoid hiding current-state meaning behind wrapping, clipping, or abbreviation.
- [ ] Review whether keyboard users can inspect all available views and activate the intended one deliberately.
- [ ] Review whether screen-reader users hear the current mode and its relationship to the alternate modes clearly enough to understand what is displayed.
- [ ] Review whether any slow-loading or map-recentering behavior after a view change stays bounded and legible.
- [ ] Review whether the route preserves a truthful fallback when one view cannot safely present the full official set.

## Evidence discipline

- [ ] Preserve a small public digest of the available views, default-view posture, active-state cues, and cross-view carryover behavior.
- [ ] Preserve bounded review evidence showing whether compact/mobile, keyboard, and assistive-technology paths can still understand and recover the active view.
- [ ] Do not retain per-user mode-switch histories, individualized pan/zoom traces, session replay, or other exploration exhaust merely to prove that another view existed.
