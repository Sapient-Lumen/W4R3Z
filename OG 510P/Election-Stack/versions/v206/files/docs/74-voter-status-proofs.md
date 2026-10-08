# Privacy-preserving voter status proofs

**Track:** A (Deployable core)


Goal: enable voters (and authorized pollbooks) to verify **registration status + ballot style assignment** while minimizing surveillance and targeted suppression.

## Design principles
- Do **not** leak “this IP queried registration status” to the same entity that knows the query contents.
- Do **not** bind a long-term citizen credential to public logs.
- Make censorship/dropping **provable** (intake receipt → inclusion proof with deadline).

## Building blocks
- **Oblivious HTTP (OHTTP)** for privacy-partitioned status queries (RFC 9458).
- **Oblivious DNS over HTTPS (ODoH)** for private endpoint resolution when DNS is in scope (RFC 9230).
- **Anonymous rate limiting** via Privacy Pass tokens for DoS resilience without IP discrimination (RFC 9577).
- **Canonical JSON** for signed objects (JCS / RFC 8785).

## Protocol (one workable variant)
### Actors
- Client (voter/pollbook)
- Relay (sees IP, not content)
- Status Gateway (sees content, not IP)
- Registration Authority (RA) signer
- VR Witness quorum

### Objects
- `VoterStatusRequest` (encrypted for gateway via OHTTP)
- `IntakeReceipt` (signed, with deadline)
- `VoterStatusProof` (signed by RA; includes snapshot/log references)
- `InclusionProof` (Merkle proof into VRDBChangeLog / Snapshot log)

### Flow
1. Client resolves service via ODoH (optional).
2. Client sends `VoterStatusRequest` through OHTTP relay.
3. Gateway returns `IntakeReceipt` with `must_include_by`.
4. Gateway/RA appends a status-proof entry to VRDB log and returns `VoterStatusProof` + `InclusionProof`.
5. Client verifies:
   - RA signature
   - log inclusion + witness cosignature checkpoint
   - ballot style hash matches ElectionParameterBundle/BDI pipeline.

### Status fields (minimum)
- `registered: bool`
- `jurisdiction_id`
- `ballot_style_id`
- `ballot_style_hash`
- `effective_date`
- `challenge_window` (how to contest)

## Offline election-day mode
- Pollbooks operate on **signed snapshots** plus **signed delta packs** up to a cutover checkpoint.
- Any mismatch triggers:
  - provisional ballot workflow
  - logged exception record
  - public evidence bundle for later audit.

## Abuse resistance & equity
- Tokens throttle abusive automated querying without IP-based throttles.
- Rate limits must be published and tested to avoid disproportionate impact.