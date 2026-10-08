# Publication receipt channel diversity and duplicate-route firewall

**Track:** Shared

rev0853 hardens publication-receipt quorum semantics. A receipt can no longer satisfy a two-channel quorum merely by minting two channel IDs under one channel type, or by giving the same route two labels.

The verifier records independent channel-type counts, required channel-type counts, duplicate-route counts, and channel-diversity status for the trust-keyset receipt, governance-bundle receipt, status-snapshot receipt, signer-authorization-roster receipt, and verification-policy-lockfile receipt families. Same-type and duplicate-route attempts fail closed in the signature verifier regression harness.

Boundary: this is a synthetic local JSON-receipt guard. It does not fetch publication endpoints, prove real channel independence, prove official control, or replace production publication governance.
