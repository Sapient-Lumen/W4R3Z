# crates.io enrichments and TP mode do not transfer to an alternate registry

This scenario freezes a common overclaim:

> “Because crates.io exposes `pubtime`, Trusted Publishing Only mode, and other publish-side enrichments, our alternate registry lane must expose the same review surface.”

The point is to keep **registry capability** separate from:

- Cargo's generic ability to publish to an alternate registry,
- publish identity for one workflow,
- and crates.io-specific operational enrichments.
