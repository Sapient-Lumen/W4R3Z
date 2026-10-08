# rev0986 research notes

Syncthing's Block Exchange Protocol uses fixed blocks and chooses a block size that bounds block-count overhead. Rev0986 adopts the same broad first-generation principle but keeps AnonSync's own protocol authority: canonical power-of-two blocks from 4 MiB to 1 GiB, at most 4,096 hashes, exact whole-file verification, and direct causal-predecessor reuse.

Fixed blocks are deliberately not presented as the final delta design. Insertions can shift every later boundary, and both peers currently hash the complete active source/predecessor before reuse. Durable manifests, multi-level signatures, or content-defined chunks remain necessary for insertion-heavy very large files.

Android remains an experiment rather than a product claim. Android's Storage Access Framework and foreground-service lifecycle do not reproduce the Linux descriptor-rooted namespace and continuously running user-service contract. Selective sync on Linux is the next product slice; an Android adapter should follow only after that metadata-without-payload contract is explicit.

Primary references are recorded in `FIXED_BLOCK_DELTA_AND_MULTI_TERABYTE_CAPACITY_AUDIT_rev0986.md`.
