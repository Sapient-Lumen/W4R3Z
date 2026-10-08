# rev0044 — compartmentfirewall-controlreceipt-foldbridge

rev0044 folds the alternate rev0043 control-intent / bridge-firewall branchlet into the canonical key-compartment line.  The new risk surface is not another isolated gate; it is the join between role-separated keys, authority split, control intent, bridge firewall, and signed local receipt memory.

New active surfaces:

- `src/i2p_dht_lab/controlintent.py`
- `src/i2p_dht_lab/bridgefirewall.py`
- `src/i2p_dht_lab/compartmentfirewall.py`
- `src/i2p_dht_lab/controlreceipt.py`
- `src/i2p_dht_lab/foldbridge.py`
- `tests/test_rev0044_compartmentfirewall_controlreceipt_foldbridge.py`

The strongest rule is: a valid key compartment, a valid control intent, and a valid bridge firewall are still not one permission until they bind to the same profile, service, scope, request, mode, action, and hard-negative state.
