# Official voter-information installed web-app surface checklist

Use this quickcheck when an election office supports or encourages Add-to-Home-Screen, Add-to-Dock, installable-PWA, or similar installed-web-app use for public voter-information routes.

## Inventory and scope

- Identify official routes that may be installed or relaunched as web apps from the operating system.
- Distinguish installable web-app posture from native app-store posture, generic embedded-browser behavior, generic cache freshness, or generic copy/share controls.
- Re-check routes whose launch entry, scope, or standalone display may materially affect first contact with the current official answer.

## Optionality and truthfulness

- Treat installed-web-app use as an optional convenience, not the only way to reach the official answer/help lane.
- Do not promise that an install prompt will appear on every browser or platform.
- Hide or suppress custom install UI where the current browser does not support the reviewed install flow.
- Keep the ordinary browser path fully usable when install is unavailable, declined, or later removed.

## Identity and recovery in standalone mode

- Verify that the route still exposes enough office, jurisdiction, task, or help identity when ordinary browser UI is reduced or absent.
- Keep an open-in-browser, copy official URL, or equivalent re-anchoring path visible when needed.
- Do not treat the operating-system icon, app name, or shell alone as sufficient proof of official authority.
- Review whether out-of-scope or browser-reveal transitions remain understandable rather than looking like a suspicious context break.

## Launch entry and scope posture

- Review the effective launch entry (`start_url` or likely installation page fallback) for stale-election, secret-bearing, or brittle deep-link risk.
- Prefer safe public launch routes over personalized or highly stateful reopen points.
- Check whether scope boundaries, redirects, and help routes behave predictably when the installed shell leaves its app-like region.
- Verify that install/relaunch does not strand the voter on an obsolete or overly narrow entry page.

## Shell drift and privacy

- Account for the fact that user devices may allow changing the installed shell’s name, icon, URL, or visible controls.
- Keep in-route official identity strong enough that shell drift does not destroy source legibility.
- Preserve only reviewed install surfaces, launch-entry posture, identity/recovery posture, and last review time.
- Do not preserve individualized install logs, per-device launch histories, or hidden launch identifiers when bounded policy reconstruction is sufficient.
