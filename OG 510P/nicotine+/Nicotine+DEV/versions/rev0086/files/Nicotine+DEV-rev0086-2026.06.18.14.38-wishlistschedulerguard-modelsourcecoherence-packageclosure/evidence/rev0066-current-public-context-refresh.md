# rev0066 current public context refresh

Checked on 2026-06-16 while preparing rev0066.

- Nicotine+ homepage still lists 3.3.10 as the current stable release and points testers to the 3.3.11 release candidate.
- Nicotine+ NEWS still lists Version 3.3.11 Release Candidate 1 with broad correction language for uncompressed network-message limits, upload spoofing, username identity, distributed search, and empty-room search behavior.
- GitHub milestone 3.3.11 was observed at 97% complete with one open item: PR #3781, “Implement safe path joining to prevent path traversal.”
- PR #3781 remains public/open and describes adding safe_path_join() to remove illegal/path-traversal components while keeping the final path within the base path.

Boundary retained: these public items are context only. They are not folded into the seven private strict/front packet claims, and rev0066 does not open any new private packet.
