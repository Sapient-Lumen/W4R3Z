# Approval rendering, locale, and trusted display are world contracts, not just bound transaction data

Delivery-path receipts, request contracts, verifier targeting, authenticator-assurance notes, and transaction-intent bindings are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **what the human actually saw, in what order and language, under which renderer, and whether that renderer was itself trustworthy**.

- `RS-GR-493` shows that OpenID4VP 1.0 says a Wallet SHOULD NOT return protocol errors before End-User consent when value matching or issuer selection would reveal sensitive facts, and that consent also protects against undetected repeated requests, which means the approval ceremony starts before the final submit button.
- `RS-GR-494` shows that OpenID4VCI 1.0 defines claim-description metadata specifically for how claims are displayed to the End-User, including localized display names, which means raw claim paths are not the full human-facing contract.
- `RS-GR-495` shows that OpenID4VCI 1.0 says the order of claim-description objects determines display order and contradictory render descriptions must abort, which means field order and render consistency can change approval meaning.
- `RS-GR-496` shows that Secure Payment Confirmation is designed to produce cryptographic evidence that the user confirmed transaction details and explicitly carries user-visible instrument, payee, and payment data, which means a trustworthy approval surface is a first-class protocol component.
- `RS-GR-497` shows that Secure Payment Confirmation warns merchant-supplied details shown to the user can diverge from what the backend believes it is authorizing, which means retaining only the backend approval object is not replay-complete.
- `RS-GR-498` shows that NIST SP 800-63B-4 treats explicit per-request user action as a separate authentication-intent requirement and says some biometric capture paths need an additional tap or button, which means “a strong authenticator was involved” still does not tell a future inheritor how approval intent was established.
- `RS-GR-499` shows that RFC 9700 warns authorization interfaces are vulnerable to clickjacking and user-interface redressing that can change granted scope or steal credentials, which means approval meaning depends on whether the renderer was frame-protected and trustworthy.
- `RS-GR-500` shows that Secure Payment Confirmation accepts locale preferences for language negotiation and locale-affected formatting while preserving user-agent control for some visual rendering decisions, which means one machine object can still correspond to materially different human-visible ceremonies.
- Together, these sources warn that a benchmark can look more successor-safe or more Golden-Rule aligned because it changed **claim labels, display order, locale formatting, clickjacking posture, user-agent chrome, or backend-to-render mismatch checking** — not because the underlying cooperative institution improved.

A future benchmark should not treat “the user approved the bound transaction” as replay-complete.

At minimum, it should distinguish between:

1. a world where the approval object is bound cryptographically but rendered inside merchant- or verifier-controlled page content with no preserved field order, label source, or frame protection;
2. a world where the approval object is rendered via wallet-native or user-agent-controlled chrome with explicit locale inputs and stable field order, but without preserved comparison back to the authoritative backend object;
3. a world where the approval surface is both trusted and checked for alignment against the authoritative transaction or authorization object before final acceptance;
4. a world where privacy-sensitive pre-consent processing is suppressed or collapsed so no issuer / value leakage occurs before the user engages;
5. a world where the archive explicitly preserves which user-visible fields were authoritative, decorative, optional, localized, truncated, or omitted.

These are different worlds.
They change whether future inheritors can tell if an apparently improved provenance result came from a better cooperative institution or merely from safer or clearer approval rendering.

So approval rendering, locale, and trusted display belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable authorization, trustworthy consent, or successor-safe presentation should publish at least:

1. the authoritative approval-object handle: digest, signed request object id, transaction-data hash, or another named binding to backend truth;
2. the render field manifest: which fields, labels, ordering, and omissions the human actually saw;
3. the label-source and locale contract: issuer metadata, verifier-provided strings, merchant-supplied descriptions, locale tags, formatting profile, and fallback behavior;
4. the trusted-display surface: user-agent chrome, wallet-native UI, authorization-server page, embedded frame, merchant page, or another named renderer;
5. the anti-redressing posture: framing policy, clickjacking defenses, user-activation or explicit-intent requirement, and any same-error privacy behavior before consent;
6. the render-to-backend comparison rule: whether displayed amount / payee / scope / claim set was checked against the authoritative backend object and what happens on mismatch;
7. the replay exception list: cases where policy intentionally permits weaker rendering provenance, looser locale control, or non-trusted display surfaces.

Without that compact contract, future inheritors can mistake better labels, cleaner locale formatting, stronger clickjacking defenses, or user-agent-controlled transaction dialogs for Golden-Rule progress.
