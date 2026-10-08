# Probe cohort selection checklist

- [ ] Define `ProbeCohortPlan` constraints (geo/ASN caps, minimum diversity)
- [ ] Choose selection method (quota / topology-diverse / hybrid)
- [ ] Record input dataset hash + as-of timestamp
- [ ] Generate selected probe list and compute plan hash
- [ ] Sign plan and anchor hash into EPB (pre-polls)
- [ ] Publish plan summary (human-readable)
- [ ] Define change-control policy (what constitutes an “incident”)
