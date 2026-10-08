# Official voter-information browser-chrome identity surface checklist

Use this quickcheck when an election office needs official voter-information routes to stay distinguishable as browser tabs, history entries, or other chrome-level labels.

## Inventory and scope

- Identify routes people are likely to revisit through tabs, history, task switchers, or assistive-technology title announcements.
- Distinguish this from URL portability, return-state freshness, and reader-mode extraction.
- Re-check routes where multiple official pages can otherwise collapse into the same generic browser title.

## Title uniqueness and task clarity

- Make every reviewed route title unique and descriptive enough to communicate the page's purpose.
- Put the actual task or answer first, then retain enough office/jurisdiction context to disambiguate the route.
- Do not rely on a generic shell title such as “Elections,” “Portal,” or “Voter Information” when materially different routes share the same chrome-level label.

## Dynamic route and state changes

- Check whether client-side navigation updates the document title when the effective route changes.
- Distinguish materially different route states such as entry, result, review, confirmation, pending, or needs-action states when those differences change the next step.
- Do not let the browser chrome keep advertising the old page state after the live content changed.

## Alignment with on-page identity

- Verify that page title, visible heading, breadcrumb, and official-site identity cues tell the same truth about the route and its owner.
- Keep enough office/jurisdiction context that county, city, and state election routes are not flattened into one ambiguous title pattern.
- Do not assume the in-page banner or header rescues a stale or overly generic browser title.

## Minimization and evidence posture

- Distinguish route states without exposing unnecessary personal details, long identifiers, or secret-bearing values in the title.
- Preserve reviewed route labels, intended title patterns, must-distinguish states, title-update posture, alignment checks, and last review time.
- Do not preserve named-user browsing histories, individualized tab telemetry, or raw browser-history exhaust when bounded policy reconstruction is sufficient.
