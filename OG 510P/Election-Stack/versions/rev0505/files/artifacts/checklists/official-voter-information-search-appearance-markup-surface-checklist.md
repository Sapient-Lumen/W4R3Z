# Official voter-information search-appearance markup checklist

Use this quickcheck when an official voter-information page emits breadcrumb or FAQ structured data that may influence how the page is previewed in search results.

## Before publishing or changing markup

- Confirm the visible page is still the right current official destination for the underlying voter question.
- Confirm the current office/help lane is visible on the page even if no breadcrumb or FAQ enhancement appears.
- Confirm the markup describes the same page content a voter can actually see.
- Confirm template or CMS changes did not silently drop or duplicate the emitted markup.

## Breadcrumb discipline

- Make sure breadcrumb markup follows a real user-followable official hierarchy.
- Do not invent a cleaner or shorter hierarchy than the site actually presents.
- Re-check breadcrumb labels after URL moves, hierarchy changes, microsite retirements, or election-cycle rollover.
- Keep duplicate or migrated pages materially consistent until stale copies are retired or redirected.

## FAQ eligibility and visibility discipline

- Use `FAQPage` only on genuine official FAQ/help pages with a single official answer to each question.
- Do not use FAQ markup on pages where users submit alternative answers.
- Make sure the full marked-up question and answer remain visibly accessible on the source page.
- If the same FAQ appears on multiple pages, pick one authoritative instance for markup rather than marking up duplicates everywhere.
- Re-check FAQ markup whenever an answer edition changes or a page is superseded.

## Validation and evidence posture

- Validate changed markup with public-facing testing/inspection tools before or immediately after rollout.
- Treat drops in valid items after template changes as a release signal, not just a search-console curiosity.
- Preserve only the bounded trace needed to reconstruct breadcrumb policy, FAQ eligibility policy, duplicate-page policy, validation posture, and verification time.
- Do not retain private webmaster tokens, admin screenshots, or individualized search telemetry when bounded public-policy reconstruction is sufficient.
