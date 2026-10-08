# Official voter-information breadcrumb-navigation surface checklist

Use this checklist for official voter-information routes that expose a **breadcrumb trail**, **you-are-here hierarchy**, or other **parent-path navigation** above the answer-bearing content.

## Scope and hierarchy truth

- [ ] Record which official routes expose visible breadcrumb navigation.
- [ ] Record what official hierarchy each breadcrumb is meant to express.
- [ ] Review whether the breadcrumb omits any county, city, state, office, or section level that changes which authority controls the route.
- [ ] Review whether hierarchy changes, migrations, or election-cycle rollovers have left stale breadcrumb labels or parent links behind.

## Current item and alignment

- [ ] Review whether only one breadcrumb item is marked as the current page.
- [ ] Review whether the current-item wording aligns with the page title and visible heading closely enough that the route tells one coherent story.
- [ ] Review whether breadcrumb links remain ordinary parent-path navigation rather than styling several items as if they are current.
- [ ] Review whether the breadcrumb still helps users who arrive from search, chat, QR codes, or forwarded links instead of relying on browser-history luck.

## Compact/mobile and accessibility

- [ ] Review compact/mobile behavior so truncation, collapsing, or wrapping does not erase the parent-path meaning.
- [ ] Review whether tap targets remain usable on small widths.
- [ ] Review whether the breadcrumb appears in a labeled navigation region and exposes the current page with `aria-current="page"` when appropriate.
- [ ] Review keyboard, zoom, and screen-reader behavior in the implemented route, not only in isolated component previews.

## Evidence discipline

- [ ] Preserve a small public digest of the intended hierarchy, current-item marking posture, compact/mobile behavior, and verification time.
- [ ] Do not retain person-level click trails, referrer logs, browser-history dumps, session replay, or other navigation telemetry merely to prove the breadcrumb existed.
