# Witness appeal mesh

Watch is not a comment.  In the public bridge path, watch can come from subjective policy, moderation, redress, egress, or shadow-fire.  rev0047 gives watch pressure a typed lane before public exposure proceeds.

`witnessappealmesh.py` stores signed observations such as:

```text
policy_watch
bridge_ledger_watch
redress_privacy_scan
hard_negative_scan
stale_public_scan
operator_context
```

The mesh accepts only when the observations bind to the exact profile, service, bridge-ledger digest, moderation digest, optional redress digest, scope digest, request digest, action, family surface, and path surface.  It rejects replay, bad signatures, sequence forks, drift, live hard negatives, missing required observation kinds, low family diversity, and low path diversity.

The intent is not witness quorum.  A witness appeal is local evidence that keeps proof debt visible when a node proceeds under watch.
