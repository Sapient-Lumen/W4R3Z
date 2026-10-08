# Structurally valid successor-safe ceremony receipts should also ship a fail-closed assessment report

The archive already has three good successor-safe ceremony primitives:

- one compact receipt that captures the decisive ceremony facts,
- one content-addressed locator that lets later notes cite the receipt without re-copying it,
- and, in the most recent pass, a delta-friendly way to talk about narrow receipt changes.

That solves structure and citation.
It still does not solve **receipt adequacy drift**.
A receipt can be JSON-valid yet still leave the inheritor guessing about the exact anti-phishing or anti-replay contract that made the ceremony safe.

Three source facts justify one tighter move:

- `RS-GR-511` says OpenID4VP `direct_post` without redirect-based protection leaves the verifier without session context to detect fixation attempts, so the flow needs explicit strengthening material.
- `RS-GR-512` says phishing resistance requires cryptographic binding to the authenticated verifier and session, via channel binding or verifier name binding.
- `RS-GR-513` says PAR exists to make the authoritative authorization request confidential and integrity-protected before user interaction begins.

So the archive should not stop at structural schema validity.
It should also ship one **tiny fail-closed assessment report** beside each durable successor-safe ceremony receipt.

That report should say, in machine-checkable form, whether the receipt still contains placeholder language and whether it explicitly names at least the following:

1. the intended verifier or audience binding;
2. the live session, nonce, challenge, or replay window;
3. the request-integrity regime when the authoritative ask traveled by `request_uri` or another by-reference path;
4. the verifier-side session-mapping material when `direct_post` or another out-of-band response route was used;
5. the claimant-participation or proximity evidence for any cross-device ceremony;
6. the dispatch-assurance posture when invocation depended on a custom scheme rather than a claimed HTTPS app link;
7. the trusted approval renderer;
8. digest-bearing retained-evidence references.

This is the right kind of archive growth.
It adds one tiny assessment object, but it prevents a more expensive future failure: inheritors mistaking “schema-valid” for “replay-safe and phishing-legible.”
