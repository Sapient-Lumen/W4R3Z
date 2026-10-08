# Namespace registry and mutable validator policy

`namespaceregistry.py` starts answering a design debt in a generic DHT: how can future applications define record validation without letting payloads self-authorize?

A `NamespacePolicy` binds:

```text
namespace
authority_public_key
sequence
validity window
allowed wire kind -> payload roles
max body bytes
max TTL
required flags by role
optional scope prefixes
signature
```

A local node chooses which namespace policies to load. This is local dispatch safety, not global governance.

Pressure tests cover:

- unknown namespace refusal;
- policy signature tamper;
- expired policy;
- rollback against local monotonic memory;
- same-sequence policy fork quarantine;
- wire-kind/payload-role mismatch;
- TTL/size excess;
- scope-prefix mismatch;
- missing required frame flags via validator wall.

The important split:

```text
identity routes and signs
namespace policy declares local validation
validator wall checks frame/body semantics
admission wall decides whether work is worth doing now
```
