# Official voter-information browser find-in-page surface checklist

Use this checklist for long official voter-information routes that people may realistically search inside with browser/app **Find in page** behavior such as `Ctrl+F`, `Cmd+F`, or mobile “Find on page”.

## Route inventory and keyword scope

- [ ] Record which important routes are long enough that ordinary users are likely to re-find the answer by browser keyword search instead of by maintained section anchors alone.
- [ ] Identify the high-stakes keyword classes most likely to change what the voter does next (deadline, ID, signature cure, drop box, student, military/overseas, provisional, accessibility help, etc.).
- [ ] Re-check heavily edited or densely structured pages where duplicated keywords can drift away from the controlling section.

## First-match integrity review

- [ ] Review whether the first realistic matches for high-stakes keyword classes land on the governing section, an honest subordinate summary, or misleading secondary text.
- [ ] Review whether repeated navigation, banner, summary-box, footer, related-content, or archived-notice language quietly outranks the controlling answer during manual on-page search.
- [ ] Review compact/mobile layouts so a highlighted match still leaves enough heading, scope, freshness, and help context visible.

## Hidden-state and fail-open review

- [ ] Review whether any route is relying on `hidden="until-found"` or another hidden/collapsed pattern to make decisive content discoverable by browser search.
- [ ] Do not assume browser search will reveal every hidden, collapsed, or injected answer region; keep an ordinary visible path to decisive content.
- [ ] Review what happens when browser search lands on a secondary match first or does not reveal hidden content at all.
- [ ] Review whether those cases fail open through visible headings, section structure, and official help routing instead of leaving a decontextualized phrase to pose as the full answer.

## Evidence and minimization review

- [ ] Preserve a small public digest of reviewed route classes, keyword classes, first-match posture, hidden-state posture, and last review time.
- [ ] Do not retain individualized find-in-page strings, keypress logs, or session-replay exhaust merely to prove that users searched within a page.
