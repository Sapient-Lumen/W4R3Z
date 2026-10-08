# Key compromise response checklist (IR-KC)

Preparation
- [ ] Key inventory with owners, usage, rotation, and escrow rules.
- [ ] Pre-written public statement templates + proof bundle template.
- [ ] Defined freeze/failover triggers.

Response
- [ ] Publish KeyCompromiseEvent with scope, timing, impact, and containment.
- [ ] Freeze intake/checkpoints if integrity is uncertain.
- [ ] Preserve evidence bundles (logs, hashes, checkpoints, notarizations).
- [ ] Reconstitute keys via ceremony; publish new EPB; enforce KT pinning.
- [ ] Post-incident AAR with remediation plan.
