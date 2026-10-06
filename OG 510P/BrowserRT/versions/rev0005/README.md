# rev0005: Test Observatory Scaffold

Archive label: **rev0005**. Packaged version: **0.0.5**. Filename date: **2026-05-24**. Preserved extracted files: **98**.

[Original ZIP](BrowserRT-rev0005-2026.05.24.02.50-test-observatory-scaffold.zip) · [Original README](contents/README.md) · [Start here](contents/START_HERE.md) · [Revision receipt](contents/REVISION-RECEIPT.json) · [Project index](../../README.md)

## Why this snapshot matters

The original README calls this a “baby cube” and explicitly says rev0005 adds no browser, GPU, or storage features. Its contribution is the testing scaffold: manifest-driven slices, changed-file routing, a surface inventory, quarantine policy, timing history, and a process-start policy that does not depend on a daemon surviving between sessions.

The [runtime scaffold](contents/src/browserrt.mjs) contains capability detection, object references, channels, and worker supervision. The [phase-zero proof record](contents/artifacts/proof/REV0005-PROOF-RUN.json) reports a Node environment, bounded-channel overflow, an ArrayBuffer transfer, and recovery after one forced worker failure. Those are carried observations, not checks rerun for this showcase. The listed capability tiers also describe intended future surfaces.

## Useful reading

- [Test-facility architecture](contents/docs/40-validation/test-facility-architecture.md)
- [Affected selection and timing](contents/docs/40-validation/affected-selection-and-timing.md)
- [Manifest](contents/test/manifest.json) and [impact map](contents/test/impact-map.json)
- [Phase-zero proof description](contents/docs/60-proof/phase-zero-executable-proof.md)

The receipt explicitly withholds production readiness, performance proof, browser conformance, a browser/CDP harness, and OPFS/SAB/WebGPU implementation. This snapshot has no CUBE-META.json; its receipt and package metadata are the relevant identity records.

The ZIP is preserved separately from its extracted contents. Historical instructions remain inert archival material. No license is added by this guide.
