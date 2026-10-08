# Successor-Safe Ceremony Receipt — successor-safe-ceremony-receipt-example-cross-device-wallet-presentation

- journey_kind: `presentation`
- schema_version: `1`
- notes: This compact object is meant to replace several paragraphs of ceremony prose while still preserving the decisive replay, display, and topology facts for a future inheritor.

## Authoritative request

- **field one**: request shape and authorized scope: verifier requested an age-over-18 proof plus a pairwise subject identifier for one relying party session.
- **field two**: satisfaction mapping or claim route: request allowed either one mdoc age-attestation credential or one SD-JWT with an age predicate plus a pairwise subject binding.
- **field three**: transaction or presentation binding: the retained receipt names the exact request digest and the wallet-approved claim route so a future session does not infer scope from the returned disclosure alone.

## Verifier targeting

- **field one**: intended verifier and audience: client_id fixed to the verifier callback origin and not reusable for another relying party.
- **field two**: nonce, challenge, or session binding: request nonce and wallet-fetched request object were bound to one live browser session for this presentation.
- **field three**: holder binding and replay window: holder proof and verifier replay policy limited acceptance to one short transaction window rather than generic later reuse.

## Delivery path

- **field one**: request carriage route: browser carried only a request_uri reference while the authoritative request object lived behind a protected fetch path.
- **field two**: response return route: wallet returned the response by direct POST to the verifier callback endpoint instead of a browser URL redirect.
- **field three**: plaintext observer surface: verifier backend and wallet could see plaintext; browser history and URL query surfaces did not carry the full response object.

## Approval surface

- **field one**: trusted renderer and display owner: wallet-native approval sheet rendered the final consent screen rather than merchant-controlled page content.
- **field two**: locale and field-order contract: wallet rendered English labels with issuer-supplied claim names and preserved the wallet's declared field order for the approval view.
- **field three**: user activation and redressing posture: explicit user approval in trusted wallet chrome was required and the receipt records that page-controlled overlays were out of scope at the final approval step.

## Ceremony topology

- **field one**: device split: cross-device journey with the request displayed on a desktop browser and the credential held on a mobile wallet.
- **field two**: invocation route: user scanned a QR code that carried a request_uri handoff rather than a pre-targeted same-device app link.
- **field three**: dispatch assurance and destination binding: wallet choice occurred after scan, so destination binding depended on user wallet selection rather than operating-system claimed-link routing.
- **field four**: proximity or cross-channel participation: human scan linked the browser-displayed request to the responding wallet; no additional BLE-backed co-presence proof was present.

## Linkability and retention

- **field one**: subject identifier scope: pairwise subject identifier intended for one relying party sector rather than a globally stable identifier.
- **field two**: proof linkability and status observers: receipt records whether the chosen proof family and any status checks exposed extra observer or linkage surface beyond the disclosed predicate.
- **field three**: retention and disclosure intent: verifier retained only the compact receipt plus policy snapshot, not the full credential payload, and recorded the declared disclosure minimization posture.

## Retained evidence

- **field one**: authoritative request digest or reference: sha256:request-4f3b plus the retained request_uri reference used for the live ceremony.
- **field two**: approval or response artifact digest or reference: sha256:response-9ab1 plus one compact approval receipt identifier.
- **field three**: policy snapshot and validation material reference: verifier-policy-v7, trust-root-bundle-2026-03-22, and wallet-profile-openid4vp-direct-post-qrcode-cross-device.
