# Gap: crypto products, keys/providers, compliance, and support contracts

Rust already has real cryptography substrate pieces, but it still lacks a **portable product boundary above them**.

Today, a serious Rust crypto-facing product often has to combine:
- algorithm-family crates or RustCrypto trait families,
- a concrete provider or backend choice,
- secret-handling wrappers,
- runtime provider selection or process-global installation,
- compliance-sensitive features and version pinning,
- password-hash or key-format interchange,
- remote-signer / HSM / KMS adapters,
- and support/docs language for what is actually promised.

The ecosystem has strong ingredients, but the product boundary is still too often hidden inside feature flags, init code, README caveats, and security-team lore:
- `rustls` now has a first-class `CryptoProvider` seam with two built-in provider lanes (`aws-lc-rs` by default and optional `ring`), supports process-global provider installation, and even documents custom key-loading/provider overrides with HSM-style examples.
- `rustls`’s FIPS guidance is explicit that users must enable the `fips` feature, use the FIPS provider, and validate `ClientConfig`/`ServerConfig` at run time. That is already a productization story, not just an implementation detail.
- `aws-lc-rs` is explicit that it is `ring`-compatible, FFI-backed, and that FIPS builds have materially different build requirements than non-FIPS builds. It is also explicit that teams needing a previous validated module version should pin `aws-lc-rs` accordingly.
- RustCrypto’s `crypto` facade crate exists specifically to provide one place for compatible trait versions across `aead`, `cipher`, `digest`, `elliptic-curve`, `password-hash`, `signature`, and related crates. That is evidence that cross-trait compatibility is already a coordination problem worth making legible.
- `secrecy`, `zeroize`, and `subtle` already make important but different promises: wrapper/exposure posture, wipe-on-drop posture, and best-effort constant-time utilities. Those are not interchangeable claims.
- the `signature` crate is explicit that errors are deliberately opaque to reduce side-channel leakage, while also allowing `std`-feature source errors for remote signers such as HSM/KMS integrations.
- `password-hash` already gives Rust a real interchange lane via PHC strings, including algorithm identifiers, versions, parameters, salt, and hash payloads.

That means the missing contribution is no longer another primitive crate, another provider wrapper, or another “safe crypto” badge.
The missing contribution is a **Cryptography Productization Stack** that keeps these truths separate but composable:
- algorithm-family and provider/backend truth,
- randomness and secret-material posture,
- runtime/provider/feature/key-source activation,
- compliance/audit/support truth,
- and downstream attachment truth for protocols, identity products, services, and clients.

Sources:
- https://docs.rs/rustls/latest/rustls/crypto/struct.CryptoProvider.html
- https://docs.rs/rustls/latest/rustls/manual/_06_fips/index.html
- https://docs.rs/aws-lc-rs/latest/aws_lc_rs/
- https://docs.rs/crate/aws-lc-rs/latest
- https://docs.rs/crate/crypto/latest
- https://docs.rs/secrecy/latest/secrecy/
- https://docs.rs/zeroize/latest/zeroize/
- https://docs.rs/subtle/latest/subtle/
- https://docs.rs/signature/latest/signature/struct.Error.html
- https://docs.rs/password-hash/latest/password_hash/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
