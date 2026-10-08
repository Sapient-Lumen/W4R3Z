# Official voter-information QR / shortlink surface checklist

- Inventory each official QR code, short URL, vanity path, and resolver-backed public handoff token that voters may encounter in print, signs, mailers, videos, social posts, or downloadable files.
- Make the bridge role explicit: the handoff token helps a voter reach the current official destination; it does not become the rule source by itself.
- Do not make a QR code the only public path to action-changing voting information when a readable URL, office/help route, or other fallback can be provided.
- Keep public handoff tokens inside recognizable official government domains where possible.
- Prefer concise, memorable official paths over opaque third-party shorteners when a trusted official resolver is available.
- Label the destination class clearly so voters can tell what scanning or typing will do before acting.
- Provide accessible text alternatives for digital QR images and readable fallback URLs or help routes for printed QR artifacts.
- Keep adequate print size, contrast, and placement so the code can be scanned under ordinary real-world conditions.
- Do not use QR or shortlink handoffs as the primary path to force a download, app install, text message, or other surprise action.
- Resolve short URLs directly to the most relevant current official destination when possible rather than to a generic homepage.
- Preserve stale recovery: old handoff tokens should redirect safely to the current destination or to a help-rich tombstone/replacement page.
- Do not let an old QR or short URL silently resolve to the wrong election, wrong jurisdiction, or stale PDF.
- Minimize analytics: use shared public tokens and bounded aggregate metrics by default rather than individualized voter-tracking links.
- Preserve a bounded handoff trace for action-changing states, including policy version, carrier class, visible fallback value, resolver mapping version, destination ref, supersession state, and timestamp.
- Re-check handoff tokens after deadline changes, moved locations, election resets, redesigned destinations, or any resolver/service migration.
