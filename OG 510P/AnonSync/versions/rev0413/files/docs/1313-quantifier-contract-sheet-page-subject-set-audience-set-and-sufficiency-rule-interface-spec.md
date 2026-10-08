## Quantifier contract sheet

### Purpose
Make the product say **who exactly a sentence ranges over and what threshold makes it true** before it says `shared`, `approved`, `available`, `synced`, `removed`, or `restored`.

### The contract object
Each serious multi-counterpart sentence renders these fields together:

- **Claim family**: approval, reachability, fetchability, sync completeness, removal, revocation, redundancy, or another typed claim.
- **Subject set**: one named peer, any source peer, all currently connected peers, all linked-device seats, all known remote peers, all ever-approved authorities, self-only derived branch, or unknown.
- **Audience set**: the people or seats to whom the sentence is meant to matter.
- **Sufficiency rule**: any one, at least one source with needed bytes, all currently connected, all linked seats, all known holders, no known holders, or unknown.
- **Horizon**: now, until refresh, until approval-memory expiry, historical only, or unknown.
- **Evidence basis**: live witness, remembered roster, certificate memory, source-byte proof, or mixed / unknown.
- **Exclusion basis**: who is intentionally not covered by this sentence.
- **Blocked stronger sentence**: the next stronger quantifier claim the product refuses to make.

### Default language rules
- `peer online` is intentionally weaker than `source peer with the needed bytes online`.
- `all devices` is intentionally weaker than `all linked devices` until the product proves broader coverage.
- `approved before` is intentionally weaker than `approved under this folder's current approval rule`.
- `removed` is intentionally weaker than `removed from every remote holder`.
- `in sync with connected peers` is intentionally weaker than `safe against offline-return divergence`.

### Required persistent receipts
Any serious availability, approval, removal, or count sentence stores one durable receipt preserving claim family, subject set, audience set, sufficiency rule, horizon, evidence basis, and the blocked stronger sentence.
