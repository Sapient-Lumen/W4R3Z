# Verifier targeting, session binding, and replay scope are world contracts, not just valid presentations

Portable evidence, disclosure receipts, request contracts, and satisfaction mappings are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **why a proof was admissible for this verifier, this origin, this endpoint, and this session rather than merely being cryptographically valid somewhere**.

- `RS-GR-441` shows that OpenID4VP 1.0 uses `client_id` to detect replay of Verifiable Presentations to a party other than the intended one and uses `nonce` to bind a presentation to a specific authentication transaction, which means a future inheritor must preserve verifier-target and transaction-binding semantics rather than treating a valid presentation as globally reusable.
- `RS-GR-442` shows that OpenID4VP 1.0 requires a Wallet that supplied a `wallet_nonce` during Request URI retrieval to reject a Request Object that does not carry the same `wallet_nonce`, and requires the Wallet to use only the parameters from the Request Object, which means request retrieval itself can be session-bound and exact-object-bound rather than a loose fetch step.
- `RS-GR-443` shows that OpenID4VP 1.0 requires `expected_origins` for signed DC API requests and says the Wallet must compare them to the Verifier's Origin to detect replay from a malicious Verifier, which means origin-binding belongs in the replay contract rather than being hidden as browser plumbing.
- `RS-GR-444` shows that OpenID4VP 1.0 defines ISO mdoc `DeviceResponse` processing so the signed or MACed `SessionTranscript` includes an OpenID4VP-specific handover with `clientId`, `nonce`, `jwkThumbprint`, and `responseUri`, which means transport / response-channel details can be part of the authenticated session contract rather than extrinsic metadata.
- `RS-GR-445` shows that RFC 9901 makes SD-JWT Key Binding explicit: the Holder signs a Key Binding JWT over the selected-disclosure package hash plus `nonce` and `aud`, and the Verifier must validate `iat`, `nonce`, `aud`, and `sd_hash`, which means holder proof is also verifier-target and transaction-bound rather than only possession-of-key evidence.
- `RS-GR-446` shows that VC Data Integrity 1.0 defines `domain` as the security domain in which a proof is meant to be used and says `challenge` should be used once for a particular domain and time window to mitigate replay, which means proof options can carry first-class anti-misbinding and anti-replay semantics.
- `RS-GR-447` shows that RFC 9449 binds proof-of-possession not only to a key but also to request method, URI, optional nonce, time window, and optionally the access token value itself, and says these checks are all still necessary for replay resistance, which means future inheritors may need to preserve endpoint / method / token-binding scope rather than only the signed proof blob.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **who a proof was targeted at, which origin or endpoint counted, how long replay was tolerated, or what exact session transcript had to match**, not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat “the presentation signature verified” as self-explanatory.

At minimum, it should distinguish between:

1. a world where the same disclosed payload is valid only for one named verifier or origin;
2. a world where that payload becomes invalid outside one authentication session because nonce, wallet nonce, or handover fields changed;
3. a world where the same holder key proves possession but only when the proof is bound to the selected disclosures and intended audience;
4. a world where browser / API origin checks and response-channel binding are part of the security contract rather than incidental transport detail;
5. a world where request-method or endpoint binding is required, making a captured proof unusable on a different route even with the same verifier;
6. a world where future inheritors can replay not only what was shown, but why replay to another party, origin, endpoint, or session should have failed.

These are different worlds.
They change whether future inheritors can detect verifier swapping, session confusion, stale-proof reuse, or route misbinding instead of mistaking those hardening layers for moral improvement.

So verifier targeting, session binding, and replay scope belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, privacy-respecting replay, or successor-safe authenticity should publish at least:

1. the intended verifier identity and scope: `client_id`, audience, relying-party lane, origin, or equivalent target identifier;
2. the session freshness material: nonce, wallet nonce, issuance / creation time window, and exact stale-or-missing handling;
3. the response-channel or route binding: response URI, endpoint / method constraints, expected origins, and any token hash or channel-binding inputs;
4. the holder-binding rule: whether proof of possession or key binding was required, optional, or waived by policy;
5. the transcript-binding object and its authenticated fields: handover contents, request-object hash, `sd_hash`, proof-option `domain` / `challenge`, or another named transcript surface;
6. whether replay outside the original verifier, origin, route, or session is rejected, degraded, logged, or tolerated by policy.

Without that compact contract, future inheritors can mistake replay hardening, verifier-target narrowing, or session-binding drift for Golden-Rule progress.
