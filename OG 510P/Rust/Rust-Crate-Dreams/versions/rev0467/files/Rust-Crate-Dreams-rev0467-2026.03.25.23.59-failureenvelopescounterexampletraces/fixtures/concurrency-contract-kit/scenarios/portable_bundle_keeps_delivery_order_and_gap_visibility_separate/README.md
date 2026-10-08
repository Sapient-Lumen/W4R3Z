# portable_bundle_keeps_delivery_order_and_gap_visibility_separate

A portable concurrency-support bundle should be able to say:

- what sequence class a surface exports, and
- what the receiver can know about missed or collapsed units,

without flattening those into generic “channel ordering.”
