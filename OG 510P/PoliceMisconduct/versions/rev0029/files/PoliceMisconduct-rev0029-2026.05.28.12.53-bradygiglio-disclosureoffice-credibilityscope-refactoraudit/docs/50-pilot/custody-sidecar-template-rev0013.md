# Custody sidecar templates — rev0013

A source without sidecars is not reproducible evidence.

Rev0013 defines seven sidecar shapes: HTTP transaction, redirect chain, fixity digest, WARC/WACZ archive metadata, privacy preflight, claim review, and source mutation. These are templates only. No live sidecar instance contains payload hashes in this revision.

The sidecar design lets future revisions preserve exact transport conditions while keeping raw payloads outside the public release path until privacy and display review are complete.

