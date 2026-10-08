# rev0043 — controlintent-bridgefirewall-foldtrim

rev0043 continues the DHT-over-I2P cube in the shared control plane.  The risky boundary is now the moment when local operator, router, cooldown, service, announcement, and hard-negative facts try to combine into a profile-level side effect.

Strong sentence:

> A public bridge is not open, closed, or safe to resume because one component says so; profile control and public exposure must join at the same service, scope, request, and evidence boundary.

New active surfaces:

- `src/i2p_dht_lab/controlintent.py`
- `src/i2p_dht_lab/bridgefirewall.py`
- `src/i2p_dht_lab/foldtrim.py`
- `tests/test_rev0043_controlintent_bridgefirewall_foldtrim.py`

The revision keeps live I2P/SAM closed.  This is no-network pressure testing before public bridge and garden-service side effects exist.
