# Python surface — rev0043

Current active additions:

```text
src/i2p_dht_lab/keycompartment.py
src/i2p_dht_lab/authoritysplit.py
src/i2p_dht_lab/compartmentfold.py
tests/test_rev0043_keycompartment_authoritysplit.py
```

The tests are deterministic and no-network. They exercise role reuse, replay, rollback, previous-link mismatch, same-sequence forks, request drift, actor-key reuse, component failure, watch holds, and current-fold visibility.
