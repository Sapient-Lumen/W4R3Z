# Delivery paths, transport confidentiality, and intermediary visibility are world contracts, not just valid presentations

Portable evidence, request contracts, verifier targeting, transaction-intent bindings, and correlation-scope receipts are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **how the request and the response actually moved, which components saw plaintext, and which parts were deliberately pushed off browser-visible or relay-visible channels**.

- `RS-GR-486` shows that OpenID4VP 1.0 defines `direct_post` and `direct_post.jwt` so the Wallet can send the Authorization Response to a Verifier-controlled `response_uri` via HTTPS POST instead of relying only on redirects, which means response delivery path is an explicit protocol choice rather than a UI afterthought.
- `RS-GR-487` shows that OpenID4VP 1.0 warns plain `direct_post` is susceptible to session-fixation style attacks because the result is sent out-of-band to the Verifier's Response URI, and it says Wallets must ensure Authorization Response data cannot leak through Response URIs, which means cross-device or out-of-band delivery changes both observer surface and replay posture.
- `RS-GR-488` shows that HAIP 1.0 requires signed Authorization Requests via JAR `request_uri` and encrypted responses via `direct_post.jwt`, which means high-assurance ecosystems already treat delivery-path confidentiality as part of the trust contract.
- `RS-GR-489` shows that RFC 9101 defines JAR so authorization requests can be signed and encrypted, attaining integrity, source authentication, and confidentiality, which means the archive should preserve whether the ask traveled as visible URL parameters or as a protected object.
- `RS-GR-490` shows that RFC 9126 defines PAR so the authorization-request payload is pushed directly to the authorization server and only a `request_uri` reference traverses the user agent, which means request transport can intentionally minimize front-channel plaintext.
- `RS-GR-491` shows that RFC 9700 says authorization codes in redirect URLs may end up in browser history and points to form-post as a countermeasure, which means URL-based redirect delivery and body-based delivery are not confidentiality-equivalent.
- `RS-GR-492` shows that RFC 9700 says access tokens can end up in browser history when passed in query parameters and treats some older modes as less secure or insecure, which means “it worked” does not tell a future inheritor whether the transport path was acceptable.
- Together, these sources warn that a benchmark can look more successor-safe or more Golden-Rule aligned because it changed **front-channel versus backchannel request carriage, body delivery versus URL delivery, encrypted versus plaintext response transport, or browser / relay / proxy plaintext visibility** — not because the underlying cooperative institution improved.

A future benchmark should not treat “the verifier got a valid presentation” as replay-complete.

At minimum, it should distinguish between:

1. a world where the full request and response travel in browser-visible URLs or redirect surfaces;
2. a world where the authoritative request is protected or pushed by JAR / PAR, but the response still comes back in plaintext to a Verifier endpoint;
3. a world where the response is body-posted out of band and requires explicit response-code or equivalent correlation to close session-fixation gaps;
4. a world where both the request and the response are protected so only a narrow backend / endpoint set sees plaintext;
5. a world where the archive preserves the intended observer boundary explicitly: browser-visible, frontend-visible, relay-visible, backend-only, encrypted-in-transit-but-plaintext-at-endpoint, or another named delivery scope.

These are different worlds.
They change whether future inheritors can tell if an apparently improved provenance result came from a better cooperative institution or merely from less exposed transport plumbing.

So delivery paths, transport confidentiality, and intermediary visibility belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims privacy-respecting provenance, durable replayability, or successor-safe presentation should publish at least:

1. the request carriage contract: by-value parameters, signed Request Object, encrypted Request Object, `request_uri`, PAR, or another named mode;
2. the response delivery contract: redirect, form-post, `direct_post`, `direct_post.jwt`, platform API return, or another named mode;
3. the plaintext-observer set: browser history, browser referrer surface, frontend, reverse proxy, callback endpoint, wallet, verifier backend, or another named observer set;
4. the response correlation contract for out-of-band delivery: response code, redirect handback, state binding, session transcript linkage, or another named closure mechanism;
5. the response confidentiality posture: plaintext body, signed JWT only, encrypted JWT, endpoint-confidential only, or another named mode;
6. the transport minimization posture: which request / response fields were intentionally kept off URLs, query parameters, and browser-visible surfaces;
7. the replay exception list: cases where policy intentionally permits broader exposure or weaker delivery-path guarantees than the default contract.

Without that compact contract, future inheritors can mistake less exposed transport paths, encrypted-response adoption, or backchannel request carriage for Golden-Rule progress.
