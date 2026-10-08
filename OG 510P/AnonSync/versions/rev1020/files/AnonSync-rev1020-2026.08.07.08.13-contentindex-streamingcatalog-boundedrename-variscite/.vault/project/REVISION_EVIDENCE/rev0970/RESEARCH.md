# Research notes — rev0970

The product distinction in this revision is between causal metadata and current byte availability. Syncthing documents a durable index database containing file metadata and hashes, while its block exchange model separately requests missing file blocks. That supports the architectural value of allowing cheap metadata reasoning without pretending that metadata alone proves current retained bytes.

Resilio exposes file version recovery as a normal user-facing Archive feature with configurable retention. That reinforces AnonSync's next product obligation: metadata browsing is only a substrate. A replacement product still needs explicit pins, understandable ordering, bytes/count/age limits, safe reachability and collection, conflict behavior, and ordinary restore UX.

Official references consulted on 2026-08-01:

- https://docs.syncthing.net/users/config.html
- https://docs.syncthing.net/specs/bep-v1.html
- https://docs.syncthing.net/users/syncing.html
- https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

The references are precedent, not authority for AnonSync's semantics. AnonSync retains its own authenticated causal model, rooted filesystem boundary, and fail-closed route behavior.
