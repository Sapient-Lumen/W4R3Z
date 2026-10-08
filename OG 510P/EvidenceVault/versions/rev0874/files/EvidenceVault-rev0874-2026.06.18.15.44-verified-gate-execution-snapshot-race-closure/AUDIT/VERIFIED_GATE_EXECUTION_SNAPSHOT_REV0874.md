# Verified gate execution snapshot audit — rev0874

## The severe defect

The exact rev0873 `scripts/overlay_gate.py` could pass its integrity preflight, execute substituted validator bytes, restore the original file, pass postflight, and report success. The deterministic fixture used an integrity command that hashed the legitimate target at both boundaries. Between them, the exact parent gate launched the target again by mutable source-tree pathname. The substituted program wrote an execution marker, the original bytes were restored, and all three parent executions still passed.

Parent gate SHA-256: `0cd99969c9bf47938af37b23649dcb3a91aeffaa83d73f3c8dc9c6e6bfb8245d`.

This is a demonstrated local correctness defect, not a claim that an outside party altered a prior archive.

## The correction

rev0874 makes the gate bootstrap self-contained and re-executes under Python `-I -S` before ordinary imports. It descriptor-anchors the source root, verifies the exact manifest sidecar, canonical path set, sizes, and hashes, then copies every inventoried byte into one private execution tree. Coverage and every configured check run from that verified tree in isolated interpreters; they do not execute source-tree script paths.

Before success, both the execution snapshot and the retained source tree are independently re-enumerated and rehashed against the captured inventory. Results explicitly record `verified_private_snapshot`, `source_postflight=pass`, and `snapshot_postflight=pass`.

The regression repeats the source-path substitution after preflight. rev0874 executes the legitimate captured target, never the substituted source file, and still verifies both trees afterward. Separate probes show that a hostile `PYTHONPATH` module and an in-bundle `hashlib.py` shadow are not imported.

## Recovery work, bounded by evidence

All 12 retained sibling ZIPs from rev0862 through rev0873 were swept against canonical path, exact size, and full SHA-256. Across 7,305 file members, 919 exact occurrences represented 113 unique canonical paths; all 113 were already available in the current tree or recovery state. No new bytes were admitted, and this lane should not be repeated unless a genuinely new archive or candidate arrives.

Coverage remains **109 / 4,586 exact current-path files**, **125 files / 4,973,641 bytes rehydratable**, and **4,461 files / 101,448,349 bytes unavailable**.

## Honest boundary

The private read-only snapshot closes source-tree substitution during an ordinary gate run. It is not a sandbox against a hostile process with the same operating-system identity, and it does not authenticate the gate bootstrap itself. External digest/signature verification is still needed for that trust boundary.

Rights closure, all 17 selected StreamFold payloads, canonical `README.md`, and the broader unavailable corpus remain unresolved.
