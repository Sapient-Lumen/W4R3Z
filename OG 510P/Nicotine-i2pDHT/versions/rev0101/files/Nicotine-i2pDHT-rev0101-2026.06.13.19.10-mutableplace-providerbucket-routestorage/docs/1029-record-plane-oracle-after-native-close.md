# Record-plane oracle after native close

`recordplaneoracle.py` converts the rev0098 native branch close into a positive DHT rule: record-plane truth remains Python-owned.

It accepts only when:

```text
native branch close accepted
native policy is shadow-only
record validators are Python-owned
mutable-head latestness is Python-owned
provider semantic proof is Python-owned
untrusted-byte parsing is Python-owned
signature/crypto semantics are Python-owned
transport/session lifecycle is Python-owned
persistence/finality is Python-owned
native record/parser/provider/transport/persistence permission is absent
negative memory survives
```

It rejects native record validation, native mutable truth, native provider truth, native parser ownership, digest drift, memory drops, replay, rollback, forks, previous-link mismatch, and low family/path diversity.
