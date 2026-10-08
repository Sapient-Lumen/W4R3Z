# Ceremony topology, device split, and invocation routes are world contracts, not just app-launch plumbing

Delivery-path receipts, approval-rendering notes, verifier targeting, and authenticator-assurance contracts are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **which device showed the ask, which device held the keys or credentials, how the wallet or authenticator was invoked, and what proved that the responding device was actually the one meant to participate**.

- `RS-GR-501` shows that OpenID4VP 1.0 explicitly supports passing Authorization Requests across devices as QR codes and recommends `request_uri` plus `direct_post` for that case, which means cross-device ceremony shape is part of the protocol contract.
- `RS-GR-502` shows that SIOPv2 distinguishes same-device from cross-device models and says cross-device flows cannot rely on user-agent redirects, which means device split changes response topology rather than only user experience.
- `RS-GR-503` shows that SIOPv2 says an RP often cannot robustly know which wallet URI to target on first interaction, so some ceremonies are intentionally untargeted and rely on user choice or scanning, which means manual wallet selection versus pre-targeted invocation is part of the world.
- `RS-GR-504` shows that SIOPv2 allows either custom URL schemes or claimed HTTPS links for wallet invocation, which means not every “wallet open” event has the same dispatch identity guarantees.
- `RS-GR-505` shows that RFC 8252 prefers app-claimed HTTPS routes because the operating system guarantees the destination app, while private-use URI schemes can suffer collision or interception risk, which means invocation route can materially change trust in the ceremony without changing any disclosed claim.
- `RS-GR-506` shows that CTAP 2.2 hybrid transport separates message carriage from physical-proximity proof by combining a tunnel service with BLE evidence, which means “cross-device” alone is too coarse: co-presence proof is another world variable.
- `RS-GR-507` shows that CTAP 2.2 QR-initiated hybrid flows require a BLE-backed proof of proximity to resist attacks, which means a QR start plus explicit co-presence proof is a different world from a QR start plus human scan only.
- `RS-GR-508` shows that NIST SP 800-63B-4 treats out-of-band channels as distinct only when the device does not silently leak between channels and when claimant participation transfers the secret or request, which means cross-channel participation semantics are part of assurance rather than ceremony ornament.
- Together, these sources warn that a benchmark can look more successor-safe or more Golden-Rule aligned because it changed **same-device versus cross-device split, targeted app launch versus untargeted scan, claimed-HTTPS versus custom-scheme dispatch, or explicit proximity / participation proof** — not because the underlying cooperative institution improved.

A future benchmark should not treat “the wallet answered the request” as replay-complete.

At minimum, it should distinguish between:

1. a same-device world where a known wallet is invoked through a claimed HTTPS link with operating-system-backed destination binding;
2. a same-device world where invocation uses a private custom URI scheme that may collide with other apps on the device;
3. a cross-device world where the request is carried by QR code and the user manually opens or selects a wallet without strong pre-targeting;
4. a cross-device hybrid world where QR initiation is paired with explicit proximity evidence or cross-channel secret transfer;
5. a world where the archive explicitly preserves which device rendered, which device approved, which device signed, and how those devices were correlated.

These are different worlds.
They change whether future inheritors can tell if an apparently improved provenance result came from a better cooperative institution or merely from safer or more tightly bound ceremony topology.

So ceremony topology, device split, and invocation routes belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable consent, trustworthy authentication, or successor-safe presentation should publish at least:

1. the device-split map: same-device, cross-device, hybrid, or another named topology, including which device rendered the ask, held keys or credentials, and returned the result;
2. the invocation route: QR code, deep link, claimed HTTPS link, private-use URI scheme, loopback callback, browser redirect, or another named path;
3. the invocation-targeting posture: untargeted manual scan, pre-targeted `authorization_endpoint`, static registration, dynamic discovery, or another named mechanism;
4. the app-identity assurance posture: operating-system-guaranteed claimed link, custom-scheme collision risk, loopback-only receiver, or another named dispatch guarantee;
5. the request and response handoff contract: `request_uri`, by-value request, direct POST, redirect callback, tunnel service, response code, or another named closure path;
6. the proximity or participation proof: BLE advert, transferred secret, user-entered code, manual camera scan only, or another named co-presence rule;
7. the topology exception list: any cases where policy intentionally permits weaker dispatch assurance, weaker co-presence evidence, or looser device-correlation semantics.

Without that compact contract, future inheritors can mistake cleaner app dispatch, stronger device binding, or proximity-proven hybrid handoff for Golden-Rule progress.
