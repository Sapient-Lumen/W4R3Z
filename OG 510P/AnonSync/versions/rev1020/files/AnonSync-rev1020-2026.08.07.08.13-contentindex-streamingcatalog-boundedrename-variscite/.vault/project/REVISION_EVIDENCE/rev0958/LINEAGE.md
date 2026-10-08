# Rev0958 lineage

Parent: `AnonSync-rev0957-2026.07.31.11.56-exacthandoff-cutpointfreshness-evidencepair-sapphire.zip`

Parent SHA-256: `6ed3a2a71082c17059eac55bac8875293448a4a0b6e33af322f8f8ffa88feb94`

Package: `AnonSync-rev0958-2026.07.31.13.24-writeaheadintent-restartfence-exactwitness-rhodolite.zip`

Rev0958 is reconstructed from the exact sealed rev0957 sapphire parent and the
recorded binary-aware active-source patch. The patch reconstructs
7/7 changed active files byte-for-byte and by executable mode.
The active projection contains 567 files,
25208824 bytes, and SHA-256 `d2efac72d8381cda1c910438915d4b86ef0231ae3410e7b33ef482ab4c2b533e`.

The slice retains one C++ synchronization spine. It publishes durable scrub
intent before the first read, makes active intent revoke fresh-process restart
acceleration until current bytes are re-proved, and centralizes exact publication
reconciliation without making scrub metadata authoritative.
