# Voter status proof service checklist

**Track:** Shared (cross-cutting)


- [ ] OHTTP relay/gateway separation deployed and audited (no shared logs that recombine IP+content)
- [ ] Optional ODoH for endpoint resolution
- [ ] Privacy Pass token policy documented and tested for equity impacts
- [ ] Intake receipts include `must_include_by` and are logged
- [ ] Status proofs reference snapshot roots + log inclusion + witness checkpoints
- [ ] Rate limiting does not depend on IP/geo in ways that disenfranchise
