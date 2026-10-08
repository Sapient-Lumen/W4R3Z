# abi_stable prefix-module additive evolution

This scenario captures the case where an `abi_stable` root/prefix module adds an optional field.
The important truth is that this is **additive surface evolution**, not an automatic breaking change.

What the receipt should prove:

- the authoritative surface is an `abi_stable` prefix module,
- the load-check basis comes from `abi_stable` root-module checks,
- the extensibility posture is `prefix_additive`,
- and compatibility witnesses can stay green while the optional field is absent on older loaders.
