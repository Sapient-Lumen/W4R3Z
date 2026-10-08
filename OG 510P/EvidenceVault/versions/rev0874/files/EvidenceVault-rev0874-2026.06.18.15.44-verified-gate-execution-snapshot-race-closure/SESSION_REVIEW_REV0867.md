# Session review — rev0867

The session stayed on byte preservation and operational truth rather than adding
another registry. Sixteen exact canonical versions (88,101 bytes) that had
survived only as intermediate reverse-patch states are now durable,
content-addressed recovery objects. A safe materializer can place them into a
separate canonical tree without overwriting newer bytes or traversing symlinks.

The coverage model was refactored into two deliberately separate facts:

- 100 files are exact at their indexed paths;
- 16 additional exact versions are protected as recovery objects;
- 116 files can be rehydrated, while 4,470 remain unavailable.

The audit also corrected an operator-risk issue: rev0826 release, SPDX, hash,
dedupe, and Makefile surfaces are historical canonical-tree evidence, not live
inventories or commands for this partial overlay. The primary gate now verifies
both current-path coverage and recovery availability from actual bytes.

No rights decision or payload was invented. Publication remains blocked; the
indexed README version and all 17 selected StreamFold payloads remain missing.
