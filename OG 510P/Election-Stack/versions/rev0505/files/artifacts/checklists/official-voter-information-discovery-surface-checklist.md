# Official voter-information discovery surface checklist

Use this quickcheck when official voter-information pages are expected to be found through web search, AI retrieval, voice assistants, or other public-web discovery paths.

## Before publishing or changing a public voter-information page family

- Confirm which URL is intended to be the current authoritative public destination.
- Confirm the page is reachable through ordinary crawlable links from current official navigation or landing pages.
- Confirm the current office/help route remains visible even if the page is not immediately surfaced in search.
- Confirm stale cycle pages, retired microsites, and alternate-format copies have an explicit recovery plan.

## Discovery and sitemap posture

- Include the current authoritative page in the sitemap when a sitemap is part of the site's discovery posture.
- Do not let superseded or stale election pages remain equally favored discovery targets without an explicit reason.
- Re-check sitemap entries when election scope, deadlines, page ownership, or localized variants change.
- Treat sitemap timestamps and alternate-language declarations as public-discovery signals, not decorative metadata.

## Canonical, duplicate, and alternate-format handling

- Pick the canonical URL deliberately for current voter-information pages.
- Link internally to the canonical URL consistently.
- Align HTML, PDF, and other alternate-format artifacts around the intended representative page.
- Re-check canonical behavior after template changes, URL migrations, outage failovers, or emergency replacement pages.
- Do not let a duplicate page, staging-like path, or stale microsite look like an equally current public answer anchor.

## Locale variants and retirement behavior

- Declare supported language/locale variants coherently when the office actually maintains them.
- Keep localized and primary-language pages aligned on current-state and help-routing cues.
- Use index-control changes carefully when retiring stale pages that voters may still reach from bookmarks, previews, or shared links.
- Pair retirement/de-indexing work with redirects, current notices, or help-rich recovery pages.

## Rendering and evidence posture

- Verify that JavaScript/template changes do not remove canonical/current-state/help cues from the discoverable page.
- Do not depend on fragile client execution for the page's basic discoverability or representative identity.
- Preserve a bounded trace of discovery policy, canonical policy, locale-variant declarations, retirement/recovery policy, and verification time.
- Do not retain crawler logs, individualized search analytics, or other private telemetry when bounded public-policy reconstruction is sufficient.
