# SAM canary before live send

`samcanary.py` adds a no-network canary lane after outbox drain but before any live SAM/I2P send exists.

The canary binds:

```text
profile/service
session id
I2P destination string
scope/request/payload
outbox drain report digest
SAM trace report digest
egress report digest
idempotency key
canonical frame digest
canary effect digest
sequence/previous digest
family/path-family hints
signature
```

The canary deliberately rejects public label leakage. A diagnostic label that carries raw or recognizable public payload fragments is treated as a metadata leak, not harmless operator detail.

The canary does not open a router socket. It is a shadow boundary for future transport side effects.
