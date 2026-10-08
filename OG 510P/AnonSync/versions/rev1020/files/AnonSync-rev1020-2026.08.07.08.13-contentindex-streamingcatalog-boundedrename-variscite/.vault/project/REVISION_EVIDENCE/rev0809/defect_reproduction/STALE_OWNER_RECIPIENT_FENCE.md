# Stale owner recipient-fence reproduction

## Parent hazard

The rev0807 control plane had a daemon owner row but no recipient-verifiable
fencing generation. Its epoch came from caller state, and downstream mutations
did not carry or check the exact current owner row in their own write
transactions.

A valid harmful schedule was:

1. daemon A acquires the row;
2. A pauses;
3. A's row expires;
4. daemon B replaces the row;
5. A resumes;
6. A reaches a mutation transaction; and
7. the mutation succeeds because the recipient never compares A's authority
   with B's durable generation.

SQLite's one-writer rule serializes step 4 and step 6 but cannot decide which
writer is authorized.

## Rev0809 regression

`tests/sync_checkpoint_owner_fence_sqlite_test.cpp` exercises the focused
recipient with a guarded effect table:

- generation one is minted from an absent row;
- a live takeover is refused;
- generation one is exactly released;
- generation two is minted from durable generation one;
- stale generation one cannot release generation two;
- stale generation one cannot authorize a guarded effect in an immediate
  transaction; and
- generation two can authorize the same recipient transition.

The focused result is **23/23**. The pure state policy separately passes
**28/28** malformed, overflow, expiry, generation, and capability checks.

## Scope

This proves the local recipient behavior of the focused C++/SQLite boundary.
It assumes checkpoint actors use the same database/VFS and enter the guarded
API. It does not cover an independent remote storage recipient or an actor with
unrestricted database rewrite authority.
