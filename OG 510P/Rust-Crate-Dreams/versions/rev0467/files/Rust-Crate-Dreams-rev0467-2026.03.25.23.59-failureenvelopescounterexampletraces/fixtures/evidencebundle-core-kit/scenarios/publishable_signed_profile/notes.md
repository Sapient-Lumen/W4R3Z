# Scenario — publishable signed profile

A domain profile wants a bundle that can be handed off locally *and* later published through an external system.

The core bundle owns:

- deterministic packing,
- manifest vocabulary,
- profile declaration,
- and explainable verification.

The domain profile imports DSSE and Sigstore-related material without requiring the core crate to become a transparency service.
