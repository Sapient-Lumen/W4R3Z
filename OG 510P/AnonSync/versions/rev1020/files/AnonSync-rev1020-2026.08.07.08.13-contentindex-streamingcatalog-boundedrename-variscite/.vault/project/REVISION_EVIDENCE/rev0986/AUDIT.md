# rev0986 audit

Rev0986 moves the shipping reconciliation protocol to generation 3 and adds bounded fixed-block predecessor reuse to the existing crash-safe contiguous payload prefix. One active file retains at most 4,096 SHA-256 block digests. The receiver reuses only an exact retained direct causal predecessor for the same canonical path, copies verified blocks through bounded ranges, and admits metadata only after the reconstructed whole-file digest is durable.

The adjacent capacity audit found two product contradictions: the deployment manifest rejected files above 4 GiB, and the production payload store rejected aggregate retained bytes above 64 GiB. New deployments now default to 64 GiB per file, may select up to the exact 4 TiB manifest frontier, and use an 8-PiB-minus-one exact aggregate comparison frontier without preallocation. Wire ranges remain 4 MiB and one response page remains bounded.

Executable proof includes a 12 MiB one-byte edit that transfers 4 MiB and reuses 8 MiB, plus a two-page successor that hashes source and predecessor manifests once. Supporting source audits pass 42/42 fixed-block/multi-terabyte, 41/41 database-replacement, and 412/412 payload-store authority checks. These lexical audits support, but do not replace, compiler, sanitizer, runtime, and package proof.
