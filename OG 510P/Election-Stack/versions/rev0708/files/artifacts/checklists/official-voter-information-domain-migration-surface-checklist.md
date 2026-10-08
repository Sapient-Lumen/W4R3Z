# Official voter-information domain-migration checklist

Use this quickcheck when an election office moves current voter information from one domain or subdomain to another, adopts `.gov`, or must stand up an emergency replacement host without confusing the public about which host is actually current.

## Before changing the host

- Confirm which host will be the clearly current primary official source for the covered voter-information scope.
- Confirm whether the change is an ordinary domain move, a `.gov` transition, or an emergency replacement host.
- Confirm whether the timing collides with deadlines, voting windows, or other high-volatility periods that make parallel ambiguity especially dangerous.
- Prepare a bounded URL-mapping policy that distinguishes one-to-one moves, consolidations, tombstones, and office/help fallbacks.

## Legacy-host containment and redirect discipline

- Keep the prior host under trusted control; do not let the old domain fall into the wrong hands.
- Keep TLS current on the legacy host while redirects or transition notices remain in use.
- Prefer server-side permanent redirects once the move is live; use temporary redirects for testing only.
- Do not collapse many old URLs into an irrelevant homepage when that would destroy scope or election-cycle context.
- Provide an explicit recovery/tombstone path when content does not safely map one-to-one.

## Search/discovery move support

- Verify both old and new hosts where search-side move tooling requires it.
- Submit Change of Address signaling when applicable for domain/subdomain moves.
- Publish and review the new sitemap set on the current host.
- Re-check canonical annotations so the new host names itself as current.
- Re-check alternate-language declarations so translated equivalents move with the host.

## Communications, email, and offline overlap

- Preserve safe delivery or explicit retirement for legacy email addresses during the transition.
- Update partner directories, community relays, and official listings so they stop teaching the superseded host as current.
- Review QR paths, printed materials, signage, and other offline branding on a migration timeline.
- Publish a visible transition notice when the public is likely to know the office by the old host.
- Keep the ordinary office/help lane visible from both the old and new host states.

## Emergency replacement-host honesty and evidence posture

- If a temporary replacement host is used, label it explicitly as temporary current state rather than letting it masquerade as an unexplained parallel authority.
- Keep one clearly named current host at a time; do not let multiple shells appear equally authoritative without explanation.
- Preserve only the bounded trace needed to reconstruct old/new host labels, migration class, redirect policy, retention state, search-move review, and verification time.
- Do not retain private registrar credentials, full Search Console exports, or internal DNS tickets when bounded public-policy reconstruction is sufficient.
