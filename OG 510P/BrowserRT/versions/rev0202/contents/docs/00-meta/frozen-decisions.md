# Frozen decisions for the baby cube

These decisions are intentionally early. Changing them requires a future revision
receipt that names the reason and migration path.

1. The release filename shape is `BrowserRT-rev####-YYYY.MM.DD.HH.MM-slug.zip`.
2. BrowserRT is a runtime substrate, not an app framework.
3. BrowserRT is not merely a worker-pool or RPC library.
4. The hot path separates control-plane envelopes from data-plane bytes.
5. No unbounded queues are permitted in the design contract.
6. Capability tiers are first-class; advanced features are progressive, not mandatory.
7. Every persistent storage path needs recovery semantics.
8. Every GPU path needs a CPU fallback or an explicit non-availability result.
9. Cloudtainer evidence is not real-device performance evidence.
10. New recurring surfaces require validation.
