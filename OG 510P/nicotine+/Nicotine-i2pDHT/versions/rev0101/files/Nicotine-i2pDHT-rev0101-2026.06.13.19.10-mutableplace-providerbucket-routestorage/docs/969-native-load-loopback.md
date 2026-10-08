# Native load loopback

Native load loopback is not native load permission. It is the typed observation that rev0092's load re-entry, revalidation seal, and call-hold evidence all still agree at one exact boundary.

The accepted state is:

```text
loopback_ready = true
native_load_allowed = false
native_dispatch_allowed = false
python_fallback_active = true
```

The lane rejects replay, rollback, same-sequence forks, previous-link mismatch, low diversity, digest drift, memory drops, and any attempt to smuggle load or dispatch through the loopback marker.
