# Monitor accountability checklist

## Minimum
- [ ] At least 2 independent monitor implementations exist for: PBB, ATL, EPB pinning, ResultsReleasePackage verification.
- [ ] Monitors publish signed MonitorAttestation objects on a fixed cadence.
- [ ] MonitorAttestations are anchored (PBB/ATL inclusion) and mirrored.
- [ ] Coverage summaries are published (who monitored what, and when).

## Public inspection
- [ ] A process exists for stakeholders to issue inspection challenges.
- [ ] Monitor responses are signed and replayable.

## Failure handling
- [ ] “No alerts” is never treated as “safe” in UX/docs.
- [ ] If monitoring coverage drops below threshold, publish a coverage incident and trigger mitigation.
