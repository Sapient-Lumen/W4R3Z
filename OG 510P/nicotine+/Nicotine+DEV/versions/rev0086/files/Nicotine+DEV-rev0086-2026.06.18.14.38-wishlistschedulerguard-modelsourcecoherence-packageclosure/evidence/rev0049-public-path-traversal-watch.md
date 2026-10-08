# rev0049 public path traversal watch evidence

Observed 2026-06-15.

## Sources checked

- `https://nicotine-plus.org/`
- `https://nicotine-plus.org/NEWS.html`
- `https://github.com/nicotine-plus/nicotine-plus/milestone/15`
- `https://github.com/nicotine-plus/nicotine-plus/pull/3781`
- `https://github.com/nicotine-plus/nicotine-plus/pull/3723`

## Observed facts used inside the cube

- Homepage: stable version 3.3.10 remains listed, with 3.3.11 release candidate testing advertised.
- NEWS: 3.3.11 Release Candidate 1 is the current release-note section observed, with broad correction language overlapping network caps, upload spoofing, username identity, distributed search, and room-search crash behavior.
- Milestone 3.3.11: observed at 97% complete with one open item for safe path joining/path traversal.
- PR #3781: observed open; public text describes adding `safe_path_join()` to remove illegal characters/path traversal components and ensure the final path remains within the base path.
- PR #3723: observed closed; public discussion covers earlier `clean_path()`/download destination path traversal handling.

## Decision

These are public-context inputs, not new private cube findings. The strict/front packet set remains unchanged.
