# Delivery repair after missing ACK

Delivery repair treats missing delivery acknowledgements as explicit protocol state.  It does not assume the send failed, and it does not assume the send succeeded.  It accepts only scoped repair probes bound to:

- the live-send gate digest,
- the delivery-witness digest,
- the send-fence digest,
- the original idempotency key,
- the exact profile / service / scope / request / payload boundary.

The pressure cases are replay, same-sequence fork, previous-link mismatch, component digest drift, delivered-already state, low family diversity, low path-family diversity, and hard-negative pressure.

needle: delivery repair
