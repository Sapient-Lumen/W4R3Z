# Windowed metric page — metric family, time window, and claim ceiling interface spec

## Purpose

The archive already has presence, freshness, and activity metrics work.
What it still lacked was one ordinary page for the simpler question:

> what kind of metric is this, what window is it speaking about, and what sentence is still honest because of it?

Current official Resilio docs make this seam concrete.
They still distinguish connected peers from historically known peers, mobile `last synced date` from other row facts, and `Last transferred` from live presence.
That should compile to one stable product page.

## Core decision

AnonSync must expose one first-class **Windowed metric** page for every counter, badge, or timestamp that can be mistaken for present-tense status proof.

The page exists to answer six things in one place:

1. what metric family this is
2. what time window it speaks about
3. what subject scope it covers
4. what freshness basis produced it
5. what strongest safe sentence it earns
6. what stronger forbidden sentence must stay adjacent

## Fixed page order

1. **Metric identity**
2. **Window and scope**
3. **Evidence freshness**
4. **Safe language and forbidden upgrade**
5. **Jump pages and alternatives**

### 1) Metric identity

Show:

- `windowed_metric_page_id`
- display label
- metric family (`live-presence`, `historical-membership`, `last-change`, `last-landed`, `last-seen`, `rolling-activity`, `threshold-clock`, `mixed`, `unknown`)
- current rendered value
- strongest honest one-line summary

### 2) Window and scope

Show:

- `window_class` (`instant`, `connected-now`, `ever-known`, `rolling-window`, `event-time`, `threshold-based`, `mixed`, `unknown`)
- subject scope (`row`, `subject`, `bind`, `peer set`, `seat`, `history slice`)
- whether the value excludes hidden/offline/aged members
- whether the value is filtered by current route or connection state

The operator must be able to answer:

> what exact window is this metric speaking about?

### 3) Evidence freshness

Show:

- last recompute time
- freshness basis
- whether the metric is live-updating, periodic, restart-bound, or stale until refresh
- known reasons the display may lag the world

### 4) Safe language and forbidden upgrade

Show side by side:

- strongest safe sentence
- stronger forbidden sentence
- the residue or missing proof that blocks the upgrade

Example:

- safe: `synced with all connected peers`
- forbidden: `synced with every known peer`

### 5) Jump pages and alternatives

Primary actions may include:

- `Open status row proof`
- `Open peer presence review`
- `Open change publication`
- `Open freshness basis`
- `Copy safe sentence`

## Public object

### Windowed metric page

Fields:

- `windowed_metric_page_id`
- `metric_ref`
- `metric_family`
- `window_class`
- `subject_scope`
- `rendered_value`
- `freshness_basis_ref` nullable
- `recomputed_at`
- `strongest_safe_sentence`
- `stronger_forbidden_sentence`
- `blocking_residue_rows[]`
- `jump_actions[]`
- `generated_at`
