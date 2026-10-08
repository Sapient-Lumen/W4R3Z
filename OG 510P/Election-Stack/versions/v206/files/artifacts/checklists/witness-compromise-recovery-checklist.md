# Witness compromise recovery checklist

- [ ] Define witness classes and diversity constraints in WitnessCosigningPolicy.
- [ ] Maintain offline-protected witness keys (HSM/secure element) with dual control.
- [ ] On suspected compromise, publish KeyCompromiseEvent quickly with evidence pointers.
- [ ] Execute WitnessSetChange ceremony (rotate/remove witness; update policy) at a checkpoint boundary.
- [ ] Increase monitoring cadence and publish MonitorAttestations during the transition.
- [ ] Provide a safe-shutdown mode (freeze checkpoints; stop ballot intake) if quorum cannot be met.
