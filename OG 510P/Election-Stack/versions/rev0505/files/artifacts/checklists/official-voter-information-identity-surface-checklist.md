# Official voter-information identity surface checklist

Use this quickcheck when an official voter-information site changes its public source identity cues: site name, organization markup, logo, favicon, hostname scope, or the off-site identity mappings that help external systems recognize the source.

## Before publishing or changing identity cues

- Confirm which domain or subdomain is supposed to carry the voter-information identity.
- Confirm the visible home-page identity matches the responsible election office or official government shell.
- Confirm the current office/help lane remains legible in both visible page content and emitted organization/contact metadata.
- Confirm any new microsite, subdomain, or emergency replacement page has a deliberate identity plan before launch.

## Site names, host scope, and duplicate home pages

- Put `WebSite` site-name markup on the supported home page of the domain or subdomain that is meant to carry the identity.
- Do not assume a subdirectory can have its own independent site-name or favicon scope.
- Keep duplicate home pages materially consistent during HTTPS / www / non-www / subdomain transitions.
- Re-check home-page identity markup whenever the canonical home page changes.

## Organization, contact, logo, and sameAs alignment

- Make sure organization name, alternate name, URL, logo, and contact details identify the same official source the page visibly presents.
- Keep election-help contact metadata aligned with the current authoritative help lane.
- Use only representative, current logo/icon assets.
- Limit `sameAs` mappings to the same organization on clearly attributable external platforms.
- Do not let vendor shells, stale legacy pages, or unrelated departments inherit the election office identity by accident.

## Truthfulness and migration discipline

- Do not emit structured data that contradicts visible page content.
- Treat rebrands, office-renames, mergers, and emergency replacements as identity-change events that require review.
- Re-check emitted identity cues after template swaps, CMS migrations, or domain/subdomain moves.
- Preserve a bounded trace of preferred name, host scope, organization/contact policy, and verification time.
- Do not retain private webmaster tokens, admin screenshots, or individualized search analytics when bounded public-policy reconstruction is sufficient.
