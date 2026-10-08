# Official voter-information URL inspection checklist

Use this quickcheck when a specific current official voter-information page seems missing, stale, or otherwise not surfacing as expected in Google Search.

## Separate state classes

- Check the indexed state Google currently reports for the page.
- Check the live fetch/render state for the page.
- Do not assume indexed state and live state are the same.
- Record only the bounded diagnosis class, not the whole inspection transcript.

## Canonical and crawl diagnosis

- If traffic to one page dropped, check whether Google selected another page as canonical.
- Check whether the page can still be crawled and fetched as expected.
- If the live page looks fine to humans, still verify what Googlebot actually receives.
- Escalate to the broader crawl/index/removal controls only after the page-level diagnosis class is clear.

## Rendered visibility

- Check whether important voter-facing text is visible in the HTML Googlebot received.
- Check whether structured data matches the visible page content.
- Check whether snippet/preview-control directives are visible when excerpts seem wrong.
- Treat template/script changes as suspect when the page looks correct in one browser view but not in search.

## Request indexing operability

- Confirm that the URL is managed by the property in question.
- Confirm that the acting role has owner or full-user permissions if request indexing may be needed.
- Use request indexing only after the page state has been corrected.
- Do not treat the ability to request indexing as a guarantee of immediate search appearance.

## Boundary and evidence posture

- Keep the current official page or office/help lane as the public authority even while diagnosis is under way.
- Preserve only page-class labels, indexed/live alignment state, canonical-diagnosis state, render/preview visibility state, request-indexing operability state, and last review time.
- Do not preserve full rendered HTML dumps, operator screenshots, or secret-bearing response traces when bounded policy reconstruction is sufficient.
