# Discovery bootstrap, catalog outage, and fallback-authority interface spec

## Purpose

The archive already has discovery disclosure, route exposure, and route-narrowing residue language.
What it still lacked was one explicit contract for a narrower but very real dependency seam:

> before a node can even apply its declared discovery posture, **who tells it where discovery infrastructure exists at all**, what happens when that bootstrap authority is missing or stale, and which fallback scope is still honest?

Current official Resilio docs make this seam unusually explicit.
They still say Sync learns tracker and relay addresses from `https://config.resilio.com/sync.conf`, that `Cannot get the list of trackers` means the app cannot fetch that configuration file, and that the troubleshooting path is to check browser reachability to that URL, firewall rules, and port access.
A companion connectivity page still says an unreachable catalog blocks tracker/relay learning before the product ever gets to ordinary peer matching.

That is not just networking trivia.
It is a control-plane dependency.

AnonSync should therefore treat discovery bootstrap as one first-class authority object with health, scope, fallback, and receipts.

## Core decision

Every seat must have one explicit **discovery bootstrap authority** record that answers four questions together:

1. where discovery and rendezvous endpoint knowledge came from
2. whether that knowledge is still fresh enough to trust
3. what reduced connectivity envelope remains if bootstrap is unavailable
4. what receipt proves a bootstrap source changed, narrowed, or failed over

The product must never compress this into generic states like `tracker unavailable` or `trying to connect`.
If the node does not currently know where to find discovery infrastructure, that is a different truth from `knows but cannot reach`, and both are different from `intentionally not using centralized discovery at all`.

## Why this matters

Current official Resilio docs still expose four seams AnonSync should not inherit:

- central catalog availability decides whether tracker/relay addresses are known at all
- outage diagnosis begins outside the app, with browser or `wget` checks against the catalog URL
- tracker failure and tracker-list failure are distinct, but easy to collapse into one `cannot connect` story
- manual/predefined-host fallback is documented as a separate troubleshooting move instead of one bounded fallback envelope rendered from the current node state

AnonSync should therefore keep one harder rule:

> bootstrap authority is part of route truth, not a hidden prerequisite that only support pages mention.

## Fixed review order

Every non-trivial discovery-bootstrap surface should render the same sections in the same order:

1. **Bootstrap authority now**
2. **Fetch and freshness health**
3. **Fallback connectivity envelope**
4. **Dependency-change receipt**

### 1) Bootstrap authority now

This section should show:

- source class (`embedded-default`, `fetched-catalog`, `pinned-private-catalog`, `manual-static`, `none`)
- source identifier
- who approved that source
- what endpoint classes it may define (`tracker`, `relay`, `directory`, `rendezvous`, `other`)
- current effective authority rank

The operator must be able to answer: **who currently tells this node where discovery infrastructure exists?**

### 2) Fetch and freshness health

This section should show:

- last successful refresh
- last failed refresh
- whether the current catalog is fresh, stale-but-usable, expired, or absent
- whether transport reachability, TLS validation, signature validation, or content parsing failed
- which currently active endpoints were learned from this authority versus preserved from earlier state

The operator must be able to answer: **is the problem that the catalog is missing, stale, unreachable, or no longer trusted?**

### 3) Fallback connectivity envelope

This section should show one honest answer for what still works if bootstrap authority is degraded:

- `no ambient discovery remains`
- `known-peer direct only`
- `local discovery only`
- `cached private infra only`
- `manual artifact claims only`
- `full discovery envelope retained`

The operator must also see what facts are now uncertain:

- new tracker learning blocked
- relay pool growth blocked
- old cached endpoints may still dial
- peer discovery narrowed to pinned/manual knowledge
- connectivity may remain for existing peers while new joins fail

The operator must be able to answer: **what exact connectivity envelope remains right now, and what did we lose?**

### 4) Dependency-change receipt

This section should show:

- previous bootstrap authority
- resulting bootstrap authority
- freshness before/after
- effective fallback envelope before/after
- any residual endpoint cache that survived the change

The operator must be able to answer: **what later proves whether we changed, lost, or intentionally narrowed discovery bootstrap?**

## Public objects

### `discovery_bootstrap_authority`

Fields:

- `discovery_bootstrap_authority_id`
- `seat_ref`
- `source_class`
- `source_locator`
- `authority_rank`
- `declared_endpoint_classes[]`
- `signature_posture`
- `freshness_state`
- `last_success_at` nullable
- `last_failure_at` nullable
- `active_failure_class` nullable
- `fallback_envelope`
- `created_at`
- `updated_at`

### `discovery_bootstrap_report`

Fields:

- `discovery_bootstrap_report_id`
- `seat_ref`
- `effective_authority_ref` nullable
- `candidate_authority_refs[]`
- `catalog_health_findings[]`
- `fallback_envelope`
- `residual_cached_endpoint_findings[]`
- `next_actions[]`
- `generated_at`

### `discovery_bootstrap_receipt`

Fields:

- `discovery_bootstrap_receipt_id`
- `seat_ref`
- `action` (`fetch-refresh`, `failover`, `pin-private-authority`, `disable-authority`, `clear-cached-bootstrap-state`)
- `before_summary`
- `after_summary`
- `fallback_delta_summary`
- `created_at`

## Main surface

A compact row should read like one of these, not just `tracker unreachable`:

- `bootstrap authority healthy · fetched catalog · refreshed 4m ago`
- `bootstrap catalog stale · cached rendezvous only`
- `bootstrap absent by policy · manual/pinned discovery only`
- `catalog unreachable · new public discovery blocked`

## CLI shape

```text
anonsync discovery bootstrap show
anonsync discovery bootstrap refresh
anonsync discovery bootstrap pin --source private-catalog
anonsync discovery bootstrap explain
anonsync discovery bootstrap receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- a node can lose catalog reachability and still only show `peers aren't connecting`
- the operator must test the catalog URL in a browser just to know whether endpoint authority exists
- cached endpoint reuse survives a bootstrap outage without being visible in route/disclosure reports
- a manual or pinned fallback behaves like an implementation accident instead of a rendered fallback envelope

## Non-clone reason

Resilio's current docs still make discovery bootstrap feel like support lore around one remote `sync.conf` fetch and later tracker troubleshooting.
AnonSync should instead publish discovery bootstrap authority, freshness, fallback envelope, and receipts as first-class state.
