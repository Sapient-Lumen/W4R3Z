# Official voter-information search-removal and recrawl checklist

Use this quickcheck when a stale, wrong, superseded, or withdrawn official voter-information page/file is still appearing in general web search.

## Before acting

- Confirm the current official replacement page, help lane, or superseding notice is already live.
- Confirm whether the case is really a moved-current URL, an obsolete result, a file-retirement case, or a product-specific listing issue outside ordinary web search.
- Confirm which URL variants, aliases, and detached file URLs are materially in scope.

## Temporary removal versus durable state

- Use a temporary removal only as a time-buying step when a stale result needs to disappear quickly.
- Pair the temporary action with a durable state change on the page/file itself.
- Do not mark the case complete merely because the temporary request was submitted.

## `noindex`, headers, and crawl visibility

- If using `noindex`, make sure the affected page or resource is still crawlable so Google can actually see the directive.
- Do not rely on `robots.txt` as the primary way to remove a page from search results.
- For non-HTML files such as PDFs, prefer file-appropriate controls such as `X-Robots-Tag` or true removal.
- Re-check CDN, CMS, and static-file rules so the directive appears in the real fetched response.

## Redirect versus removal choice

- Use redirects when the resource truly has a new current location.
- Do not silently treat obsolete or withdrawn content as a moved-current case just to avoid explicit retirement.
- Keep the current official help/replacement path visible while the stale result is being retired.

## Verification and evidence posture

- After the durable state changes, request recrawl for changed URLs or submit updated sitemaps when appropriate.
- Treat recrawl requests as acceleration evidence, not proof that the stale result is already gone.
- Preserve the bounded trace needed to reconstruct affected URL classes, temporary versus permanent state, non-HTML suppression choices, recrawl steps, and verification time.
- Do not retain private webmaster exports, admin tokens, or individualized search telemetry when bounded public-policy reconstruction is sufficient.
