# Multi-Log Notarization Checklist

**Track:** Shared (cross-cutting)


## Inputs
- [ ] Artifact hash (sha256)
- [ ] Artifact type and election_id
- [ ] NotarizationPolicy from EPB (targets + timing)

## For each log target
- [ ] Submit artifact hash + metadata
- [ ] Retrieve log entry id
- [ ] Retrieve inclusion proof
- [ ] Retrieve current log checkpoint / tree head
- [ ] Validate inclusion proof locally
- [ ] Store NotarizationRecord

## Publish
- [ ] Post NotarizationRecord to PBB
- [ ] Include NotarizationRecord in EvidenceBundle

## Monitor
- [ ] Monitor log consistency over time (checkpoint changes)
- [ ] Alert on anomalies or missing entries
