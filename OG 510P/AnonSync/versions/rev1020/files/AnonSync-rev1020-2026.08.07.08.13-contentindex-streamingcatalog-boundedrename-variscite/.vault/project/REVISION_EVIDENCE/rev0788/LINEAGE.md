# rev0788 lineage

## Last archived parent

`AnonSync-rev0786-2026.07.14.14.41-observed-sqlite-mutex-generation-capabilityfenceforge.zip`

The ZIP exists locally, passes the release-package verifier, and has SHA-256
`d5f2589c1fceef0fe8fe55fd70b9f6d5266f816c548f2dcaa63e214ebe333a40`.
Its active implementation projection is
`df1819e5187fbda3976eb63b94851b85ef1dba594a8d33143084a167c6eb95ec`.

## Recovered intermediate source

The intended rev0787 ZIP named in the prior handoff is absent. Source was
recovered from `/mnt/data/_rev0787_final/AnonSync`, copied into an isolated
worktree, and committed as baseline
`923d302edc572e0db04ba607b50bc40612d7c954`. Its active implementation
projection is
`d465a8de5e6fdecbce8b8e3cf46d6d41be02584bf4b4baf092fdd10111521b25`.
The recovered evidence includes an audit traceback and `passed: false`; this is
therefore a candidate source snapshot, not a verified release parent.

## rev0788 projection

The tested active implementation projection is
`27155873c3eca548628a73a8da230ba98f1c7e3b54e9bd0f1da25dc13f9ebf29`.
Exactly six active files differ from the recovered baseline:

- `CMakeLists.txt`
- `src/persistence/peer_ingress_connection_profile.cpp`
- `src/persistence/peer_ingress_connection_profile.hpp`
- `src/sync_domain.cpp`
- `tests/persistence/peer_ingress_connection_profile_test.cpp`
- `tools/audit_peer_ingress_connection_profile.py`

Package verification re-computes this projection after ZIP extraction before
publication.
