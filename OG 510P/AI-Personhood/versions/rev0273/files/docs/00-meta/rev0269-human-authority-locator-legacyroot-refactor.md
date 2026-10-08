# rev0269 — human authority handoff, locator recheck, and legacy-root cleanup

rev0269 keeps the archive on the first-contact execution path without pretending that a public release can create human authorization, sender authority, private vault roots, or actual transport proof. The concrete work is to remove ambiguity around those blockers and cut a misleading legacy replay surface out of the release root.

## Why this was the riskiest next work

After rev0254, the remaining blockers were mostly human/private/send-time dependent. Another doctrine or registry pass could not honestly close them. The riskiest failure mode was subtler: a future operator could think the concise message, payload manifest, conflict review, route-fit review, transport plan, and hash dry run were enough to send, or could waste another turn rediscovering which exact fields a human must sign.

rev0269 therefore adds three practical surfaces:

- `examples/external-contact-human-sender-authority-precommit-rev0269-aiid.json`
- `examples/external-contact-current-public-locator-recheck-rev0269-aiid.json`
- `examples/legacy-apply-script-root-refactor-manifest-rev0269.json`

The first creates an exact unsigned authorization packet: recipient, subject, body hash, mail-ready draft hash, public payload manifest hash, and required human attestations. It is intentionally not a signature, not sender authority, and not send permission. The second records a current public locator recheck for the RAIC/AIID collaboration route while preserving the rule that a send-time recheck must happen again if dispatch is delayed. The third moves historical `apply_rev*.py` scripts out of the repository root into `tools/legacy-apply-scripts/` with hashes, because their root presence falsely implied that patch replay was still the current supported release path.

## What changed operationally

The send-readiness gate remains blocked. rev0269 does not reduce that count by fiction. It does make the branch less brittle:

1. The unsigned human/sender authority precommit states exactly what must be signed and attested.
2. The mail-ready draft now surfaces all current blocker classes in its `X-AI-Personhood-Send-Blockers` header.
3. The dispatch authorization card no longer lists stale conflict/transport-plan blockers as if they were still missing after rev0253/rev0254; it now names the real remaining blockers: human signature, sender authority, send-time locator recheck, private vault root, send-time hash recompute, and actual transport proof.
4. The locator recheck confirms the public collaboration route without treating the locator as consent, authority, custody, intake, import, recognition, or an evergreen send-time check.
5. The legacy root cleanup preserves old apply scripts with hashes but removes them from the root so they stop competing with `make context-pack`, `make manifest`, `make lint`, and `make package-release` as the current replay path.

## Remaining blockers

The five send-readiness blockers still unresolved are unchanged:

- human signature;
- sender authority;
- send-time public locator recheck;
- private vault roots;
- final send-time payload/body hash recompute.

Actual transport proof is also absent because no send occurred. The existing transport-capture plan remains a plan, not proof.

## Hard reliance limits

No organization was contacted. No message was sent. No transport proof, delivery status, DSN, Message-ID, response clock, inbound artifact, raw retention permission, custody, intake, import, status recognition, waiver, adverse inference, or live-floor effect exists.

A public locator recheck is not consent or authority. An unsigned precommit is not a signature. A legacy-script cleanup is not a replay of the archive and does not change the no-send/no-floor state.
