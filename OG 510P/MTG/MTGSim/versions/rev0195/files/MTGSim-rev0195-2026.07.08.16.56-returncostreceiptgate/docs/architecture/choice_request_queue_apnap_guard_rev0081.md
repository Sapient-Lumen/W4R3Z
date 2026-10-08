# rev0081 choice request queue APNAP guard

rev0080 made the selected player's `ChoiceRequest` durable, but replay could still miss a global ordering drift: the selected player's local action set might be unchanged while the ordered set of currently exposed choice surfaces had changed. rev0081 adds the smallest executable seam for that risk: an APNAP-ordered `ChoiceRequestQueue`.

The engine now exposes `apnap_ordered_players(...)`, `choice_request_queue(...)`, and `choice_request_queue_hash(...)`. The queue hash uses the current StateCore hash, each non-empty request's APNAP index, chooser, request kind, required flag, action count, and per-request action-set hash. It intentionally does not hash display labels.

`apply_action(...)` samples the queue before mutation and stores `choice_queue_hash`, `choice_queue_index`, and `choice_queue_size` on `ActionReceiptRecord`. `ActionTrace.v1` carries the same fields. During replay, a nonzero expected queue hash is checked before the local choice request hash and before state mutation. Drift is reported as `ChoiceQueueHashMismatch`, while local offered-action drift remains `ChoiceRequestHashMismatch`.

This is not yet a full simultaneous-choice system. It is the replay/audit spine for one: the cube can now prove whether a chosen action came from the same ordered choice surface before it proceeds to more complex APNAP batches, hidden choices, or replacement-order decisions.

Regression coverage:

- `test_apnap_ordered_players_skips_lost_and_starts_with_active`
- `test_choice_request_queue_metadata_roundtrips_and_guards_replay`

Audit hook:

- `audit_choice_request_queue_wiring`
