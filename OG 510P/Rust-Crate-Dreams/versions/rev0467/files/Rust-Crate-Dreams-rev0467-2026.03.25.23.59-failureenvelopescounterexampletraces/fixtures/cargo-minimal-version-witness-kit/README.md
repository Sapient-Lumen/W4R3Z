# Cargo Minimal-Version Witness Kit fixtures

Fixture ideas:
- crate whose stated direct dependency floor is correct under `direct-minimal-versions`
- crate that accidentally relies on a newer dependency feature than its manifest floor implies
- workspace with a direct-minimal solver conflict caused by feature/version interaction
- fixture with one temporary lower-bound waiver and expiry metadata
