# Rev0982 authority incidents

1. The first unsealed extracted worktree disappeared during a cloudtainer filesystem remount. The sealed rev0981 ZIP remained intact; rev0982 was reconstructed from that parent, and pre-remount observations were not used as final release authority.
2. A foreground product replay was terminated by the tool execution boundary after 26/41 passing tests. It was rerun as a detached immutable lane and reached a terminal 41/41 pass; the interrupted run is excluded.
3. The first source-reconstruction record covered 15 active files and predated the final stop-socket lifecycle fix plus revision-specific inventory hardening. Final sealing discarded it, froze a new source authority, regenerated the binary patch, and proved the actual 17-file delta and full projection.
4. Build trees whose configured source roots were older or divergent were not used for final package authority. The final GCC registry was rerun against the current source path; the Clang ASan/UBSan product graph was configured and built from the frozen authority path.
