# Channel Surface Contract Kit fixtures

This fixture pack freezes a first artifact vocabulary for **P-0529 Channel Surface Contract Kit**.

Artifacts:
- `capacity-posture.receipt.schema.json`
- `overflow-policy.receipt.schema.json`
- `delivery-obligation.report.schema.json`
- `shutdown-drain.receipt.schema.json`

Scenario families:
- `tokio_bounded_backpressure_clean_shutdown/`
- `tokio_broadcast_lagged_receivers/`
- `tokio_watch_latest_state_only/`
- `crossbeam_zero_capacity_rendezvous/`
- `embassy_priority_channel_reorders_delivery/`
- `drop_oldest_ring_channel_is_not_backpressure/`
