# Rev0951 audit summary

Rev0950's deterministic bounded prefix guaranteed progress only while earlier
applied values remained stable. Repeated successors at an early canonical path
could consume every remote effect frontier and starve a later path. Rev0951
moves every remote file/tombstone effect into one cyclic planner and persists the
last successfully selected canonical path in catalog schema v4. Complete hard
projection admission still precedes all effects.

A second crash-order audit found that the first cyclic planner still required a
present predecessor to be hashed by the current local scan invocation. An
incomplete scan journal survives restart, but a completed epoch resets its seen
rows. Therefore journal membership could not prevent an epoch-long delay after
completion, restart, or a remote frontier.

The retained design lets the durable catalog predecessor nominate work only
after fresh rooted descriptor metadata reproduces its source-snapshot digest.
That metadata is scheduling evidence, not byte authority. The exact apply owner
reopens and fully hashes the local file, reloads the predecessor, and re-proves
the remote successor immediately before publication. A stale or racing local
edit fails closed. The authenticated scan journal remains traversal continuation
and absence authority only.

The audit also found an avoidable N× payload-namespace cost: each selected remote
file took its own complete verified payload snapshot. One frozen inventory now
serves all readiness checks and applies in a pass, with at most one refresh after
local insertion. A missing payload is deferred scheduling work and does not
block a ready cyclic suffix. Settlement and JSON diagnostics carry that
remainder explicitly.

Schema-v4 migration retains the v3 authenticated scan journal in place, and a
shared modern catalog loader removes repeated v2/v3/v4 row proof code. Idle
classification now re-proves the mutable scan journal. The structural audit has
70 lexical ownership checks; it is not semantic proof.

Principal remaining costs are complete remote projection reconstruction, rooted
prefix replay, complete immediate-directory buffering/sorting, restart-cold
payload inventory, non-atomic cross-owner cutpoints, and unbounded retained
history. See
`DURABLE_CYCLIC_REMOTE_APPLY_CURSOR_AND_MODERN_CATALOG_PROOF_AUDIT_rev0951.md`.
