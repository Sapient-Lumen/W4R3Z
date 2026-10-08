# Official voter-information search-result presentation checklist

- Inventory the public search-result entrypoints most likely to bring voters to official pages for action-changing topics.
- Make the routing role explicit: search-result presentation helps voters recognize the current official destination, but it does not become the legal rule source by itself.
- Ensure title links identify the page purpose and jurisdiction or office clearly enough that a voter can tell whether the result is likely relevant before clicking.
- Add election/date scope in titles or snippets when omission would make a stale or generic result look current.
- Avoid vague result framing such as generic “election info” or “updates” labels when a more specific official description is available.
- Keep site-name and favicon posture recognizable so the official source is easy to distinguish from stale microsites, retired subdomains, or unofficial copies.
- Keep current authoritative pages canonically favored over superseded pages for action-changing topics.
- Recover stale indexed pages into the current destination or a help-rich current-state landing page when direct one-to-one replacement would mislead.
- Do not rely on a rich result to communicate core action-changing information; the ordinary title/snippet/page path must still work.
- Validate structured data after template changes and fix invalid or dropped markup that would make the result presentation drift.
- Re-check result presentation after JavaScript, template, localization, URL-structure, or emergency-homepage changes.
- Preserve a bounded presentation trace for important state changes, including template version, title/description policy version, canonical policy version, destination ref, supersession state, and timestamp.
- Minimize telemetry: do not turn public search-result arrival into individualized clickstream surveillance when bounded policy reconstruction is sufficient.
- Re-test stale-result recovery whenever deadlines, polling locations, form editions, or election scopes roll over.
