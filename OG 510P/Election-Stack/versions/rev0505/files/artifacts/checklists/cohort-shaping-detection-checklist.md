# Cohort Shaping Detection Checklist

**Track:** Shared (cross-cutting)


Use this checklist during election week and during any incident that includes claims of selective unreachability.

## Setup (pre-election)
- [ ] Publish a signed `ProbeCohortRotationPlan` and `ProbeCohortPlan` constraints (max ASN share, min ASN/country, path diversity threshold).
- [ ] Enable traceroute collection (best-effort) for all primary targets (PBB submit, receipt verify, evidence portal, OHTTP gateway/relay).
- [ ] Ensure at least two independent probe classes (external platform + operator-controlled probes in independent networks).
- [ ] Publish tool versions and canonicalization/hashing rules used to compute `PathCorrelationReport`.

## During operation
- [ ] For each reporting window, compute `PathCorrelationReport` for each primary target.
- [ ] Check for path collapse:
  - [ ] max ASN share exceeds threshold
  - [ ] ASN entropy below threshold
  - [ ] mean Jaccard similarity above threshold
  - [ ] clustering indicates ≥ N probes share a dominant path
- [ ] If collapse detected:
  - [ ] Emit `CohortShapingAlert` (anchor into ATL + PBB checkpoint).
  - [ ] Rotate cohort immediately; re-run measurements.
  - [ ] Include pre- and post-rotation evidence in the next public evidence bundle.

## Dispute support
- [ ] Provide cohort audit report and selection seed reveal for the disputed window.
- [ ] Provide raw traceroute hashes and tool provenance.
- [ ] Document interference controls used (rate caps, backoff, platform load).

