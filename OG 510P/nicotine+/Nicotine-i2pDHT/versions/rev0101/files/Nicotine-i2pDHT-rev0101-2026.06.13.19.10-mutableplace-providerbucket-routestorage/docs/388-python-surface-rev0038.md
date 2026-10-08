# Python surface — rev0038

Primary new API:

```python
ServiceContinuitySignal
ServiceContinuityPolicy
ServiceContinuityReport
assess_service_continuity(...)
audit_servicecontinuity_fold(...)
```

Folded APIs now active:

```python
CatalogWirePayload / validate_catalog_wire_capsule
ServiceProbePlan / assess_probe_plan / assess_probe_receipt
ServiceWithdrawalNotice / assess_service_withdrawal
ServiceRelayObservation / assess_service_relay
ServiceUseIntent / assess_service_use_gate
ServiceWorkIntent / assess_service_handoff
ContributionReceipt / assess_receipt_window
ProfileGcJoinReport / join_profile_gc_to_restart_memory
CatalogSuccessionReport / assess_catalog_succession
```

All of this remains toy Python design code. It is meant to make risky joins executable before live I2P transport and before a production DHT exists.
