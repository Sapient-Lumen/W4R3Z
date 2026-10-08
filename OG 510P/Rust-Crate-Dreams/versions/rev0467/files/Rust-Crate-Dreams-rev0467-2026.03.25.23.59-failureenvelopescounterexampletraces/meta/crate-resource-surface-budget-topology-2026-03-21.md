# P-0521 — Crate Resource Surface Pack Kit: budget-topology refinement (2026-03-21)

## Why this lane deserves another pass

The March 19 planning pass made **admission path**, **backlog ownership**, **capacity shrink**, and **acquire fate** explicit.
That was a real upgrade, but one practical support question still slips through too easily:

> “Does this limit apply per clone, per client/pool/channel family, per connection, per host, per runtime, or to the whole process?”

That question now looks unusually buildable because current Rust substrate already publishes enough facts to prove the distinction matters:

- `reqwest::Client` documents that the client holds a connection pool internally, should be reused, and already uses an `Arc` internally; its builder also documents that `pool_max_idle_per_host` defaults to `usize::MAX`.
- `sqlx::Pool` documents that cloning is cheap because it is just a reference-counted handle to the inner pool state.
- Deadpool documents the same basic shape: `Pool` is cloneable and uses reference counting for internal state.
- Tokio `mpsc::Sender` documents that cloning is essentially a reference-count increment.
- Moka documents that cloning a shared cache is cheap because it clones reference-counted pointers to shared internal data structures.
- Tonic documents `concurrency_limit_per_connection`, which means a visible limit can still multiply with the number of live connections.
- Tower documents that layer ordering changes the total number of in-flight requests.

So the sharper missing value is no longer just “what is the bound?”
It is also **where that bound lives and along which replication axis total retained state multiplies**.

## Main judgment

A worthy next pass for **P-0521** should treat four more review objects as first-class:

1. **budget topology** — whether a resource budget is per-handle, shared across clones, per-connection, per-host, per-runtime, process-global, or external;
2. **sharing scope** — whether cloning/forking/constructing another handle shares the same waiting room or creates another one;
3. **multiplication axis** — which dimension increases total retained state: clone families, hosts, connections, runtimes, shards, or external tenants;
4. **aggregate-bound honesty** — whether the crate can honestly state an end-to-end aggregate bound or must mark it `manual_review_required` because the bound depends on topology outside the crate.

These objects sit above boundedness and saturation rather than replacing them.
They stop a common support lie:

- “max 32” sounding process-wide when it is really **per connection**,
- “bounded queue” sounding singular when each service clone gets its own queue,
- or “shared client” sounding expensive-to-replicate when clones actually share one pool.

## What the crate should provide other people

For downstream integrators and maintainers, the crate should provide:

1. **budget-topology truth**
   - whether each bound is scoped per instance, clone family, host, peer, connection, worker, runtime, process, or external service;
2. **clone-sharing truth**
   - whether another clone shares the same budget or silently multiplies it;
3. **multiplication-risk truth**
   - which deployment/runtime/topology choices multiply retained state even when each local bound is individually honest;
4. **aggregate-bound caveats**
   - whether “max 10” really means `10 total`, `10 per host`, `10 per connection`, or “unknown without deployment topology”;
5. **summary text another team can actually use**
   - one compact explanation of what scales with clones, with connections, and with hosts.

## Recommended `0.1` artifact additions

Promote at least one new first-class file into the bundle:

- `budget-topology.receipt.json`

Recommended fields:

- `resource_name`
- `scope_class`: `per_instance` | `shared_clone_family` | `per_connection` | `per_host` | `per_runtime` | `process_global` | `external_service_scoped` | `manual_review_required`
- `sharing_behavior`: `clone_shares_state` | `clone_multiplies_budget` | `constructor_multiplies_budget` | `mixed` | `manual_review_required`
- `multiplication_axes`: list such as `connections`, `hosts`, `runtimes`, `service_instances`, `workers`, `tenants`
- `aggregate_bound_posture`: `exact_total_known` | `per_scope_only` | `topology_dependent` | `manual_review_required`
- `notes`

The existing bundle should then read more honestly alongside:

- `resource-budget.report.json`
- `admission-path.report.json`
- `backlog-ownership.receipt.json`
- `saturation-behavior.report.json`
- `resource.summary.md`

## Suggested command behavior

### `cargo resource-surface check`

Should fail or warn when a maintainer publishes a bound without any topology answer.
Examples:

- `per_host_pool_bound_without_scope_class`
- `cloneable_handle_without_sharing_behavior`
- `per_connection_limit_presented_as_global`
- `aggregate_bound_claim_without_topology`

### `cargo resource-surface doctor`

Should render human-first warnings such as:

- `clone_shares_state_but_summary_says_each_client_has_its_own_pool`
- `constructor_multiplies_budget_but_summary_only_lists_local_bound`
- `per_connection_limit_can_multiply_with_live_connections`
- `per_host_pool_bound_can_multiply_with_host_fanout`
- `aggregate_total_unknown`

### `cargo resource-surface summary`

Should answer, in plain language:

- whether clones share or multiply the budget,
- whether the visible bound is per host or per connection,
- and whether total retained state depends on deployment topology outside the crate.

## Scenario families that should anchor this pass

1. **Reqwest client clones share one pool**
   - one client family,
   - clone is cheap,
   - pool budget is shared,
   - but `pool_max_idle_per_host` is still per-host rather than process-total.

2. **SQLx/Deadpool clone handles share inner pool state**
   - clone does not multiply the pool,
   - but multiple independently constructed pools still do.

3. **Tokio sender clones share one bounded channel**
   - many senders,
   - one channel budget.

4. **Tonic concurrency limit is per connection**
   - a truthful local limit,
   - but aggregate in-flight requests still multiply with connection count.

5. **Tower layer ordering changes total in-flight**
   - topology of the stack affects the aggregate budget,
   - not just the visible local numeric limits.

6. **Shared caches versus duplicated caches**
   - a cache clone may share internal state,
   - a newly constructed cache may create an independent budget island.

## What to keep separate

Do **not** let future revisions collapse these:

- **resource budget** — the numeric or symbolic local limit,
- **budget topology** — where that limit lives,
- **sharing behavior** — whether clones share it,
- **aggregate deployment bound** — what happens when hosts, connections, runtimes, or independently created instances multiply.

The archive should not let “bounded” quietly imply “bounded for the whole process” when the real answer is “bounded per host” or “bounded per connection”.

## Bottom line

The sharper next move for **P-0521** is not another cache/queue/pool crate.
It is one compact way to tell another team:

- which budget is shared,
- which budget multiplies,
- what dimension it multiplies along,
- and when an honest aggregate total is impossible without deployment topology.
