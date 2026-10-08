# Transaction-intent binding, approval surfaces, and consent continuity are world contracts, not just authenticated sessions

Portable evidence, request contracts, verifier targeting, chosen capability profiles, and authenticator-assurance receipts are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **what exact transaction, document, or authorization the user actually approved, what subset was granted, and whether that approval object was integrity-protected end to end**.

- `RS-GR-471` shows that OpenID4VP 1.0 defines a `transaction_data` mechanism that binds the user's identification / authentication to the user's authorization — for example, completing a payment or signing specific documents — using the same user-controlled key that proves possession of the presented credential, which means a valid presentation can carry either generic identity proof or transaction-specific approval semantics.
- `RS-GR-472` shows that OpenID4VP 1.0 defines `transaction_data_hashes` so each hash ensures the integrity of and maps to a specific transaction-data object, and says those hashes must be included in the proof-of-possession mechanism, which means the archive can preserve exact approval-object linkage rather than only a loose narrative about what the session was for.
- `RS-GR-473` shows that RFC 9396 defines `authorization_details` for fine-grained authorization data and says the authorization server asks the user for consent to the requested access permissions and that the user may grant a subset, which means a future inheritor may need to know the granted subset rather than only the original ask.
- `RS-GR-474` shows that RFC 9396 says there is no standardized simple mechanism to compare arbitrary `authorization_details` objects and that authorization servers should not rely on naive object comparison, which means approval semantics depend on type-specific interpretation rather than bytewise similarity alone.
- `RS-GR-475` shows that RFC 9101 lets authorization requests travel as signed and optionally encrypted Request Objects so integrity, source authentication, and confidentiality of the request are protected, which means the archive should preserve whether the approval object itself was integrity-protected or merely reconstructed after the fact.
- `RS-GR-476` shows that RFC 9126 lets clients push the authorization request payload directly to the authorization server and notes that front-channel query parameters otherwise lack cryptographic integrity and can even let an attacker swap payment context, which means a future inheritor may need to know whether the approved object was back-channel pinned or browser-malleable.
- `RS-GR-477` shows that the current NIST SP 800-63B guidance defines authentication intent as requiring the claimant to respond explicitly to each authentication or reauthentication request, which means a preserved proof of user action is still weaker than a preserved proof of **what that user action authorized**.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **transaction-specific binding, approval-object integrity, granted-subset semantics, or request-tamper resistance** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat “the right user, with the right authenticator, approved the request” as replay-complete.

At minimum, it should distinguish between:

1. a world where the user proved identity in a live session but no transaction- or document-specific approval object was bound to the proof;
2. a world where the verifier requested specific structured authorization details but the archive retained only the original ask, not the granted subset or enriched result;
3. a world where transaction data existed but only in front-channel or unverifiable form, so later inheritors cannot tell whether the approved object was tampered with in transit;
4. a world where the exact transaction or document set was hashed, bound into proof-of-possession, and preserved as the approved object;
5. a world where the same authenticator gesture could satisfy either a generic login or a transaction-specific authorization, depending on whether signed request-object / pushed-request / transaction-hash continuity was required.

These are different worlds.
They change whether future inheritors can tell if an apparently improved provenance result came from a better cooperative institution or merely from stronger transaction-intent binding and approval-object preservation.

So transaction-intent binding, approval surfaces, and consent continuity belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, replayable presentation / authorization, or successor-safe approval should publish at least:

1. the exact approval object that mattered: `authorization_details`, `transaction_data`, requested document set, payment context, or another named transaction-intent structure;
2. the request-protection path: whether the approval object traveled unsigned in the front channel, as a signed Request Object, by pushed request reference, or under another integrity / confidentiality regime;
3. the grant result: full approval, reduced subset, enriched server decision, denied request, or another named outcome;
4. the binding witness: transaction-data hashes, credential-proof linkage, request-object signature, pushed request URI, or another compact witness that ties the approval object to the user-controlled proof;
5. the semantic comparison rule for later replay: how “same approval,” “reduced approval,” or “materially different approval” was interpreted for that transaction type;
6. the archived human-facing approval summary, when policy-relevant, so inheritors do not have to infer what the user was being asked to approve from machine structures alone.

Without that compact contract, future inheritors can mistake tighter transaction binding, stronger request integrity, or narrower granted subsets for Golden-Rule progress.
