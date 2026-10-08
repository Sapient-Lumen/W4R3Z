# Official voter-information unobscured-target surface checklist

Use this checklist for official voter-information routes that rely on fragment jumps, in-page navigation, or scripted scroll/reveal behavior while sticky headers, fixed banners, or other persistent chrome remain on screen.

## Scope and target inventory

- [ ] The route(s) reviewed are official voter-information routes where jump links, fragments, or reveal actions are expected to land the voter on an answer-bearing section.
- [ ] The review identifies the critical target headings, first controlling lines, or reveal controls that must remain visible after landing.
- [ ] The review records the persistent UI that can obscure the target (site header, sticky in-page navigation, alert bar, cookie banner, etc.).

## Landing visibility

- [ ] Browser-native fragment jumps land with the target heading visibly above persistent chrome.
- [ ] Same-page navigation links and scripted `scrollIntoView()` / jump-to-section behavior land in a meaningfully visible place, not merely a technically resolved target.
- [ ] If the target is inside a disclosure or accordion, the panel opens and the first answer-bearing lines remain visible above persistent chrome.
- [ ] The route does not leave the voter staring at a blank seam where the correct heading is hidden underneath a fixed or sticky interface.

## Variant checks

- [ ] Mobile or narrow-screen layouts were checked.
- [ ] 200% zoom or equivalent enlarged-text conditions were checked where header height changes.
- [ ] Temporary banners or election alerts were included if they can appear during the live route.
- [ ] Embedded or constrained-container variants were reviewed if the route is commonly reached in those contexts.

## Evidence discipline

- [ ] The review records the critical targets, chrome inventory, and landing-visibility findings.
- [ ] The review records when the check occurred and which route/version was observed.
- [ ] The archive does not retain named-user scroll telemetry, individualized viewport recordings, or unnecessary replay exhaust for this bounded surface.
