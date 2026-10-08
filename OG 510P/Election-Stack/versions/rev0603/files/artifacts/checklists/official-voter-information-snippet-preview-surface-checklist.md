# Official voter-information snippet and preview checklist

Use this quickcheck when an official voter-information page may be excerpted into search-result snippets, image previews, Discover-like cards, or AI-search answer surfaces.

## Before changing preview controls

- Confirm the visible page is still the right current official destination for the underlying voter question.
- Confirm the current office/help lane remains visible and actionable even if preview text is minimized.
- Confirm the page class is understood: stable evergreen help, volatile deadline notice, office contact page, FAQ, or another bounded category.
- Confirm any structured data on the page was reviewed separately from the visible page text.

## Text-snippet and excerpt-boundary discipline

- Use `nosnippet` when the page should not provide a free-floating text snippet or AI direct-input excerpt.
- Use `max-snippet` when the office wants a bounded text-preview budget rather than open-ended excerpting.
- Use `data-nosnippet` for volatile or decontextualizable page regions instead of assuming a single sitewide setting is enough.
- Keep `data-nosnippet` markup in valid HTML containers and do not rely on late JavaScript mutation to add or remove it.
- Re-check exception-heavy warning blocks, deadline footnotes, and county-specific carve-outs after each content edit.

## Image-preview and Discover discipline

- Allow `max-image-preview:large` only when the page has representative current imagery that helps voters recognize the right current destination.
- Restrict image previews to `standard` or `none` when the available image assets are generic, stale, or likely to mislead.
- Re-check hero images, campaign-season graphics, seals, and rollover artwork after election-cycle changes.

## AI/search boundary discipline

- Treat snippet-eligibility changes as part of the page's AI-feature supporting-link posture.
- Do not assume that hiding visible page text also suppresses overlapping structured-data answer fields.
- Keep the visible current page/help lane trustworthy enough that tighter preview settings still route voters safely after the click.

## Verification and evidence posture

- Preserve only the bounded trace needed to reconstruct page classes, chosen preview states, targeted excerpt-boundary rules, image-preview policy, and verification time.
- Do not retain private webmaster exports, individualized search telemetry, or operator screenshots when bounded public-policy reconstruction is sufficient.
