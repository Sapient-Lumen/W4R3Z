# Official voter-information request-context variance checklist

Use this quickcheck when an election office needs a bounded way to keep the same official voter-information URL from drifting by cookie state, inferred location, experiment bucket, or other hidden request context.

## Variant inventory

- Identify which dimensions can change the page at all.
- Separate visible user-choice dimensions from ambient dimensions such as cookie state, inferred geography, experiment bucket, or user-agent class.
- Re-check the inventory after CDN, consent, localization, experimentation, or routing changes.

## Critical-answer boundaries

- Keep deadline text, routing instructions, election-scope labels, and office/help recovery lanes out of A/B testing and personalization systems.
- Do not let cookie state or experiment assignment quietly choose between materially different authoritative answers.
- Keep the no-cookie / first-visit path authoritative for critical public answers.

## Locale and region posture

- Use explicit boundaries when language or region materially changes the answer.
- Prefer visible selectors, stable locale paths, or clear fallback over hidden guessing.
- Confirm explicit user choices are not silently overridden by fresh ambient inference.

## Cache and diagnosis posture

- If request headers influence the response, record which dimensions are in play and confirm variance is declared consistently enough for cache and diagnosis purposes.
- Spot-check that the same variance posture is used on default and `304` responses where applicable.
- Preserve bounded `req[...]` / `vary[...]` notes when investigating divergence instead of raw targeting data.

## Evidence posture

- Preserve only dimension labels, explicit-vs-ambient classification, critical-answer experiment-boundary state, no-cookie/first-visit state, variance-declaration state, help-lane visibility state, and last review time.
- Do not preserve raw cookies, user identifiers, experiment-assignment logs, audience-targeting segments, full analytics exports, or giant edge-debug dumps when bounded policy reconstruction is sufficient.
