# Epic proposal: Cryptography Productization Stack

## Thesis
Rust needs a **portable, boring crypto-product boundary** above primitives, providers, and secret-handling helpers.
The problem is no longer “can Rust do serious cryptography?”
The problem is that algorithm-family scope, provider/backend choice, key-material posture, randomness posture, compliance/runtime validation, and support/docs truth are still too often implicit.

## Why this would count as worthy
This contribution would help multiple major Rust lanes at once:
- protocol and TLS products;
- identity and credential products;
- service-side cryptography and secure configuration;
- client/web/mobile products that ship keys or rely on system/external stores;
- compliance-sensitive and enterprise deployments;
- policy, support, and release teams that need something better than README prose.

It would be boring in the right way:
- reviewable;
- importable by other tools;
- provider-aware instead of provider-denying;
- honest about randomness, key sources, and runtime validation;
- useful to support, policy, and release review, not only primitive-crate authors.

## Deliverables
- `design/cryptography-productization-stack.md`
- `design/cryptography-productization-pilot-program.md`
- `gaps/crypto-products-keys-providers-compliance-and-support-contracts.md`
- `crypto-surface/v0` family refinements
- comparison pilots across `rustls` / `aws-lc-rs` / `ring` / RustCrypto trait lanes / secret-handling helpers
- protocol/identity/support import examples

## First proof bar
A first serious proof should show that one Rust project can publish a `crypto-pack/v0`-style bundle that keeps:
- crypto surface identity,
- provider/backend profile,
- key-material profile,
- randomness posture,
- compliance/runtime-validation posture,
- and checked support/docs evidence

all distinct while still being reusable by protocol, identity, service, policy, and support consumers.

## Non-goals
- universal cryptography abstraction;
- universal compliance badge;
- replacing protocol or identity design with crypto-only metadata;
- flattening provider, randomness, key-source, and support truth into one fake “secure” verdict.
