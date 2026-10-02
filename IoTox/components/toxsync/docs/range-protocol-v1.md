# toxsync range protocol v1

The wire types are fixed-size transport payloads. They do not select a transport and do not
grant authorization.

```text
MutableHead       236 bytes (first 172 bytes are canonical signing body)
RangeCapabilities  32 bytes
RangeRequest       64 bytes
RangeOffer        104 bytes
RangeCancel        24 bytes
RangeResult        64 bytes
```

A request binds a nonzero request ID, immutable artifact SHA-256, exact offset, exact length,
and policy flags. An accepted offer repeats those values and adds an application-defined
32-byte Tox file ID. The receiver correlates the later paused Tox file offer by peer, file ID,
and exact size before accepting it.

All decoders reject wrong lengths, wrong magic/version, nonzero reserved bits, unknown enum
values, zero request IDs, arithmetic overflow, and policy limits. Capabilities are advisory
until an embedding application binds them to an authenticated peer; IoTox additionally uses
them to reject unsupported local requests before transmission.

`MutableHead::signature` is opaque. Toxsync provides deterministic signing bytes but no
identity or trust policy. An unverified HEAD must never select filesystem state.
