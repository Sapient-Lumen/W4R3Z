# rev0059 current public context refresh

Public context was refreshed before freezing rev0059. This is boundary context only and does not promote or retire any strict/front packet.

Observed public state:

```text
Nicotine+ homepage: current stable version listed as 3.3.10; testers are pointed to the 3.3.11 release candidate.
NEWS page: Version 3.3.11 Release Candidate 1 remains listed with broad correction language around uncompressed network-message size limits, upload spoofing, username identity, distributed search, and empty-room search crash behavior.
GitHub 3.3.11 milestone: observed as open, 97% complete, with PR #3781 as the single open item.
PR #3781: public/open path traversal safe_path_join() work; retained as public-watch-only context.
```

Boundary: rev0059 does not open a private path traversal packet and does not treat broad release-note language as an exact duplicate of the seven strict/front packets.
