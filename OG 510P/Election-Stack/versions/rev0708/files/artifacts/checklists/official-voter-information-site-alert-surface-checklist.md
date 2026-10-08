# Official voter-information site-alert surface checklist

- Inventory each official sitewide alert, emergency/status bar, page-scoped alert block, homepage notice module, and interruptive modal/interstitial that voters may encounter.
- Make the prominence role explicit: the alert makes urgent current-state information visible; it does not replace the current official destination or help route by itself.
- Distinguish sitewide urgent alerts from page-scoped alerts and from rare blocking interstitials.
- Use sitewide treatment for truly cross-site urgent information and keep narrower messages page-scoped.
- Avoid stacking multiple sitewide alerts when one bounded alert with supporting links can carry the information.
- Use blocking pop-ups, modals, overlays, and interstitials only when necessary to the design of the experience rather than as generic friction.
- Keep publication dates and, when relevant, effective/expiration dates visible on action-changing alerts.
- Clear or explicitly supersede alerts that no longer control; do not leave stale banners visibly active.
- Keep the current official destination or help route recoverable from the alert itself.
- Test the alert treatment in the context of the implemented site for heading clarity, consistent meaning, zoom/reflow, and assistive-technology announcements.
- Do not rely on color alone to convey meaning or severity.
- Preserve a bounded alert trace for action-changing states, including policy version, alert class, timing fields, placement class, target/help route, and timestamp.
- Do not retain detailed user-level alert-dismissal or modal-interaction telemetry longer than the published policy requires.
- Re-check alert behavior after election-cycle changes, deadline changes, moved locations, outage workarounds, redesigns, or superseding notices.
- When material alert behavior changes, publish an explicit updated state instead of relying only on silent UI edits.
