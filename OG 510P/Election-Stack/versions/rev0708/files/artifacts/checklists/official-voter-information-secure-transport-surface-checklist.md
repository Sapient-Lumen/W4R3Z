# Official voter-information secure-transport checklist

Use this quickcheck when an election office needs a bounded way to keep current official voter-information pages reachable without certificate warnings, mixed-content breakage, or unsafe-page first contact.

## Route scope

- Identify a small set of critical public-answer routes that should be HTTPS-only.
- Include the ordinary help/contact recovery lane in that critical set.
- Re-check the set after host moves, redesigns, emergency replacement pages, or major vendor changes.

## HTTPS and warning posture

- Confirm ordinary HTTP entry URLs redirect cleanly to HTTPS for public entry routes.
- Review certificate validity/renewal posture for official public-answer hosts.
- Review HSTS posture intentionally; do not assume users can bypass future certificate warnings.
- Do not publish recovery instructions that tell users to click through certificate or unsafe-site warnings.

## Mixed content and dependencies

- Check critical routes for mixed content or mixed downloads.
- Confirm blocked insecure subresources do not hide the answer, form, map, or file handoff.
- Inventory load-bearing third-party scripts, embeds, and download paths on critical routes.
- Keep a disable/replace path for third-party components that trigger deceptive behavior, redirect chains, or browser warnings.

## Unsafe-page recovery

- Review Search Console Security Issues or equivalent warning checks when trust or traffic changes abruptly.
- Treat browser/Google unsafe warnings as first-contact answer failures, not just SEO noise.
- Keep a still-trusted official recovery/help lane and current notice visible on an unaffected official channel while the page is under repair.
- Re-check official social/profile/listing surfaces if they are being used as the emergency recovery lane.

## Evidence posture

- Preserve only route labels, HTTPS-only boundary state, redirect posture, HSTS/certificate review state, mixed-content review state, third-party dependency boundary state, warning-monitoring state, recovery-lane state, and last review time.
- Do not preserve private TLS keys, raw malware samples, giant vulnerability-scanner exports, or incident-forensics dumps when bounded policy reconstruction is sufficient.
