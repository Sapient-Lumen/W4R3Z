# Official voter-information public-read access checklist

Use this quickcheck when an election office needs a bounded way to keep general official voter-information pages publicly readable while separating genuinely private or customized account routes.

## Route classification

- Identify a small set of critical public-answer routes that should remain anonymously readable.
- Classify genuinely customized or private routes separately from those public-read routes.
- Re-check the classification after CMS, SSO, vendor, redesign, election-crunch, or account-first front-end changes.

## Public-read boundary

- Keep ordinary read-only public-answer routes accessible without sign-in.
- Do not require account creation just to read general deadlines, office/help information, current notices, or other ordinary official guidance.
- If a route truly requires authentication, explain what private or customized function it unlocks.
- Keep the ordinary official help/contact lane visible without authentication.

## Session expiry and re-authentication

- Give advance notice before automatic sign-out and offer a clear way to request more time when feasible.
- Re-authentication should preserve current task context or return the user to the same task when feasible.
- Do not let an expired-session shell silently replace a public-answer route.
- Re-check timeout and re-authentication behavior with keyboard-only and assistive-technology flows.

## Discovery and evidence posture

- Keep public-read routes accessible to crawlers and anonymous users; keep private routes intentionally separate.
- Distinguish sign-in/account walls from anti-bot challenge posture and overload posture.
- Preserve only route labels, public-vs-auth classification, sign-in rationale, anonymous help/explanation state, timeout/reauth policy, crawler-visibility boundary, and last review time.
- Do not preserve credentials, auth tokens, session IDs, identity-provider traces, or detailed per-user login analytics when bounded policy reconstruction is sufficient.
