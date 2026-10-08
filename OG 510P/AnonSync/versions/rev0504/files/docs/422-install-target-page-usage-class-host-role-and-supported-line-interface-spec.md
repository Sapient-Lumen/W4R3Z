# Install target page — usage class, host role, and supported line interface spec

## Purpose

The archive already had release-channel, execution-seat, and host-authority guidance.
What it still lacked was one ordinary page for the simpler question:

> may this seat on this host role, under this usage class, actually run this release line, and what exact support boundary or redirect applies if not?

Current official Resilio docs make this seam concrete.
They still say Sync v3 is for personal non-commercial use, that Sync Business stays on v2, that v3 is not supported on Windows Server, and that platform/architecture support differs by line.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Install target** page for every seat candidate and every already-installed seat.

The page exists to answer five things in one place:

1. what host role and usage class this seat currently claims
2. which release lines are actually eligible for that claim
3. what support boundary blocks ineligible lines
4. whether a redirect target exists
5. which next action is least misleading

## Fixed page order

1. **Current eligibility verdict**
2. **Host and usage claims**
3. **Supported line matrix**
4. **Block / redirect explanation**
5. **Safe next actions**

### 1) Current eligibility verdict

Show:

- `install_target_page_id`
- target seat or planned seat scope
- current `eligibility_verdict` (`eligible`, `eligible-with-review`, `ineligible-by-host-role`, `ineligible-by-usage-class`, `ineligible-by-architecture`, `mixed-claims`, `unknown`)
- strongest honest summary
- last verification time

The operator must be able to answer:

> may this seat honestly run this line here right now?

### 2) Host and usage claims

Show rows for:

- host platform
- host role (`workstation`, `server`, `nas`, `mobile`, `container`, `other`)
- architecture
- usage class (`personal`, `family`, `commercial`, `mixed`, `unknown`)
- current installed line, if any

Each row must show provenance and confidence.
The page must not let package filename or current binary presence impersonate truthful eligibility.

### 3) Supported line matrix

Show one row per release line or product family:

- line name
- host-role support verdict
- usage-class support verdict
- architecture support verdict
- notes on special constraints
- consequence if crossed anyway

This matrix must keep `supported`, `unsupported`, and `unsupported-but-bytes-may-survive` visibly different.

### 4) Block / redirect explanation

If the current target is not eligible, show:

- exact blocking rule
- whether a different line is the supported destination
- whether the issue is hard-unsupported, unsupported-but-detectable, or policy-only
- whether linked peers or local state make the block stricter

The page must answer:

> why exactly is this line wrong for this host or usage claim?

### 5) Safe next actions

Actions may include:

- `Confirm usage class`
- `Review supported line`
- `Open upgrade gate`
- `Open package lane`
- `Keep current line`
- `Do not install here`

Each action must preview consequences and non-effects.

## Public object

### Install target page

Fields:

- `install_target_page_id`
- `seat_ref` nullable
- `planned_target_ref` nullable
- `host_claim`
- `usage_claim`
- `installed_line` nullable
- `eligibility_verdict`
- `supported_line_rows[]`
- `blocking_rules[]`
- `redirect_options[]`
- `safe_next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. target
2. host role / usage class
3. current line
4. eligibility verdict
5. next least-misleading action

Example:

```text
lab-nas-03     nas / commercial     v2-business     eligible-with-review     Open package lane
```

## Non-goals

This page does **not** replace channel updates, linked-cohort skew review, or schema migration planning.
It proves only **whether this seat belongs on this release line at all**.
