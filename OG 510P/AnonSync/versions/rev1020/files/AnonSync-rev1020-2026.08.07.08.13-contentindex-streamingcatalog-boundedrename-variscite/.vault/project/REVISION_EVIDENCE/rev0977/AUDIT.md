# Rev0977 audit handoff

## Scope

Rev0977 composes two deletion-free payload-lifetime proofs without claiming a collector: an exact bounded same-owner live-capability registry and a cooperative current-reader fence carried by opened payload descriptors.

## Primary correction

Retention mark v3 now binds snapshots, targeted accessors, mutation batches, and exact opened descriptors issued by the retained store owner. Registration IDs prevent same-count replacement aliases, while a fail-closed non-wrapping activity generation detects complete create-and-destroy activity between equal set observations. Snapshot and targeted payload byte access re-enter the current shared store-identity fence and transfer a shared exact-inode payload-use lease through final close. Existing quarantine rename and release unlink take the global store lease exclusively before the candidate inode lease exclusively.

## Adjacent audit and cloudtainer correction

The merge restored sealed-parent modes after divergent unsealed branches had marked ordinary C++, Markdown, and Python files executable. Release-source NUL and UTF-8 hygiene is now checked. Duplicate and stale build launchers against shared Ninja trees were excluded; final authority comes from one exact-source GCC tree and one isolated Clang ASan/UBSan tree. The binary patch reconstructed all 18 changed active files and the complete projection byte-for-byte and by mode.

## Authority boundary

The result remains deletion-free. It does not bind independently opened owners, a process that has not yet opened a payload, already copied outbound buffers, noncooperating writers, policy, durable collection intent, collection quarantine, restart reobservation, reclaim, or unlink authority.
