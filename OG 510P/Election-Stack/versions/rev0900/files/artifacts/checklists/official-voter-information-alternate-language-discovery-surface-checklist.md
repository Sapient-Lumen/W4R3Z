# Official voter-information alternate-language discovery checklist

Use this quickcheck when current official voter-information pages exist in more than one language and the office needs search to land users on the right current language variant instead of a generic or hidden locale shell.

## Before changing alternate-language discovery

- Confirm which language paths are truly current full equivalents, which are selected-content routes, and which are help-only fallbacks.
- Confirm the office/help fallback remains visible and actionable for languages without a full equivalent current page.
- Confirm whether the multilingual surface includes non-HTML files such as translated PDFs that may need header- or sitemap-based alternate declarations.
- Confirm whether any locale-adaptive behavior is present by IP, geolocation, or browser-language detection.

## Locale-URL and declaration discipline

- Prefer stable locale-specific URLs for full equivalent current translations instead of relying only on adaptive delivery.
- Use one maintained alternate-language declaration method well: HTML, HTTP headers, or sitemap.
- Keep the chosen declaration method current during election windows; do not let HTML, headers, and sitemap drift against one another.
- Re-check translated PDFs and other non-HTML files if the office expects search discovery beyond an HTML wrapper.

## Reciprocity and fallback discipline

- Ensure each page lists itself and its alternate language versions.
- Ensure alternate-language declarations are reciprocal enough to avoid being ignored.
- When a new language variant launches, at minimum link it bidirectionally with the dominant/current official language lane.
- Provide a safe generic-language or `x-default` fallback page for unmatched users when region-specific or selector patterns are in play.
- Do not let fallback pages collapse into empty splash pages, stale selectors, or decorative shells.

## Partial-translation and locale-adaptive honesty

- Do not advertise template-only or selected-content routes as full equivalent current translations.
- Keep `hreflang` clusters aligned with what the office has actually translated and reviewed.
- If locale-adaptive delivery exists, do not assume it alone is enough for crawl, index, or routing of translated voter information.
- Avoid silent language steering that hides stable locale URLs from crawlers or users.

## Markup, robots, and evidence posture

- Keep HTML `lang` attributes and language-link annotations in place for accessibility and markup clarity.
- Re-check robots consistency across locale variants so translated equivalents are not accidentally harder to crawl.
- Preserve only the bounded trace needed to reconstruct locale URL sets, declaration method, reciprocity status, fallback class, adaptive-delivery review, and verification time.
- Do not retain private search-engine dashboards, raw `Accept-Language` logs, or individualized search telemetry when bounded public-policy reconstruction is sufficient.
