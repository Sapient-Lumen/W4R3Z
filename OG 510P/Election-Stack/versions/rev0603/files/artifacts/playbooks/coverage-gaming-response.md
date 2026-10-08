# Coverage Gaming / Selective Blindness Response Playbook

**Track:** Shared (cross-cutting)


## When to use
Use when coverage accounting suggests monitors/watchers are:
- failing quotas repeatedly,
- deviating from deterministic challenge schedules,
- suppressing bad news,
- or coordinating to avoid hard targets.

This is an ecosystem integrity incident, not a “PR issue”.

## Immediate steps (0–24h)
1. **Preserve evidence**
   - snapshot: challenge schedules, coverage reports, suppression reports, gossip digests
   - create an evidence packet using `tools/evidence_packager.py` (see `docs/173`)
2. **Recompute independently**
   - run `tools/coverage_accounting.py` on raw logs
   - compare to published coverage claims
3. **Publicly timestamp discrepancies**
   - publish a signed discrepancy note with digests of the inputs

## Escalation (24–72h)
4. **Force re-randomization**
   - re-run deterministic sampling using published randomness seeds (`docs/168`)
5. **Increase perspective diversity**
   - recruit additional independent watchers (different orgs / networks / incentives)
6. **Trigger 'watchers inspecting monitors'**
   - publish: (a) what *should* have been challenged, (b) what *was* challenged, (c) what was missed

## Recovery
7. **Re-baseline trust**
   - mark compromised watchers as untrusted for coverage weighting
   - require additional confirmations for critical artifacts

## Long-term fixes
- revise `ChallengeQuotaPolicy` and monitoring incentives
- add automated alarms for quota misses and sampling deviations
