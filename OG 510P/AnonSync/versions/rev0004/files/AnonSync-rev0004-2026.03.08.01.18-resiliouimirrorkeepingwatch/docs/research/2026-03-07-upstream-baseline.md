# Upstream baseline — 2026-03-07

This note records a minimal external baseline used while creating the initial archive skeleton.

## I2P / i2pd
- SAM remains the key integration seam for non-Java application designs.
- `i2pd` is a viable bundled runtime target for a no-Java posture.

## Tor
- The Tor Project distributes expert bundles for developers bundling tor with applications.
- Arti remains strategically important, but is not the current implementation target for this archive.

## Resilio Sync
- The product analogy is folder-centric peer-to-peer sync between user devices.
- Selective sync, placeholders, and mobile-friendly defaults are strong UX references.
- Resilio documents both filesystem notifications and periodic rescans, which is a key operational lesson.

## Impact on this repo
- choose bundled `i2pd` + SAM as the first I2P posture
- choose bundled tor daemon as the first Tor posture
- preserve provider boundaries so transport implementations can evolve later
- treat Resilio as a serious product and operational reference, not just a superficial UX analogy
