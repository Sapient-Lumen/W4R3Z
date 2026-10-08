# rev0019: store mesh tombstone repair

Store-mesh rounds join sibling-store acknowledgements across mutable heads, tombstones, immutable/provider records, and useful refusals. Mutable heads that depend on a tombstone repair should not be treated as durably stored until the tombstone round has been accepted.

The mesh is not consensus. It is local evidence that exact-digest storage, refusal pressure, and resurrection pressure are typed separately.
