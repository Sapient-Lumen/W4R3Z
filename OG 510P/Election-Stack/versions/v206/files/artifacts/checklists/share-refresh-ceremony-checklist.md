# Share Refresh Ceremony Checklist (PSS/DPSS)

## Preconditions
- [ ] Committee roster + threshold frozen
- [ ] Refresh protocol selected + implementation validated on test election
- [ ] Secure environment prepared (HSMs, offline machines, observers)

## Execution
- [ ] Record start checkpoint hash
- [ ] Run refresh protocol
- [ ] Validate resulting share commitments / public transcript commitments
- [ ] Record transcript hash and participant signatures

## Publication
- [ ] Publish ShareRefreshTranscript to PBB
- [ ] Anchor transcript hash per NotarizationPolicy (optional)

## Post
- [ ] Rotate operational access and revoke stale credentials
- [ ] Store sealed backups per policy
