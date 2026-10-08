# Current upstream snapshot notes

Observed through web research on 2026-06-12:

- The project README identifies 3.3.10 as the current stable version and points testers to the 3.3.11 release candidate.
- The release notes for 3.3.11 RC1 include important security/hardening-adjacent changes: maximum uncompressed network message sizes, spoofed-user upload prevention, a peer username fix, and distributed-search fixes.
- TESTING.md identifies 3.3.x as the 3.3.11rc1 test lane and master/default as the 3.4.0.dev1 test lane.
- The 3.3.11 milestone was observed as open and 97% complete, with an open item about safe path joining / path traversal.
- SECURITY.md says only the latest released A.B.x series is supported, currently 3.3.x.

These notes are not a substitute for source checkout. Use the rev0003 source bundle script.
