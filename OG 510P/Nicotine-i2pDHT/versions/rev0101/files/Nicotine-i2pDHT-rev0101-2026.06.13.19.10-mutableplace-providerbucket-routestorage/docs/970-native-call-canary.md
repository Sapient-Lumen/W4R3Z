# Native call canary

Native call canary records the Python-oracle result for the exact call vector that rev0092 held. It deliberately does not call the native leaf.

The accepted state is:

```text
canary_ready = true
native_call_allowed = false
native_call_executed = false
python_fallback_executed = true
```

The lane rejects native-result evidence, native execution, wrong Python-result digest, component digest drift, call-vector drift, memory drops, replay, forks, and low diversity.
