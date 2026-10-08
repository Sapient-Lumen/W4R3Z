# Candidate-to-packet binding refactor — rev0085

The candidate artifact contract previously named one current cumulative patch
without saying which packets it implemented or intentionally did not solve.
That ambiguity became material once persistent wishlist action policy and
scheduler capacity were separated.

Rev0085 advances `data/current_candidate_artifact_contract.json` to version 2:

- every candidate declares immutable `packet_ids`;
- `required_packet_bindings` maps each current packet to an artifact or `null`;
- the current artifact's declared packet set must exactly match its bindings;
- historical rev0084 evidence now binds the formerly-current artifact by path
  and digest;
- a negative control rejects falsely binding `WISHLIST-CAP-01` to the current
  Search Again candidate.

This prevents a cumulative patch from silently acquiring credit for a newly
split problem it does not address.
