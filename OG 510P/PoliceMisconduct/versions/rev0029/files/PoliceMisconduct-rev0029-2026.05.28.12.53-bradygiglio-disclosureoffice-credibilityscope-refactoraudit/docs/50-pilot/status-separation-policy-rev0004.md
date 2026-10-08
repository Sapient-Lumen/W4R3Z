# Status separation policy — rev0004

The cube now separates status into four lanes.

## 1. Source-page status label

This is what the carrier page says. It is source-scoped and time-scoped.

Allowed display:

> Source-page status label: Enforcement, observed on DOJ SLS page at [timestamp]. Not independently reverified as current court status.

## 2. Document-chain status signal

This is a weak signal from document labels such as `Joint Motion to Terminate`, `Order Dismissing Case`, `Closing Letter`, or `Sustainment Plan`.

Allowed display:

> Document chain includes a 2025 dismissal order label. Current status requires review.

## 3. Court-order status

This requires actual review of an order, docket reconciliation, effective date, and scope. This lane is closed in rev0004 except as an open design target.

## 4. Current-status candidate

This is internal synthesis and must not be public.

## Rollback rule

No status gets overwritten. Every new status observation becomes an event. Public display should show history and uncertainty rather than a single brittle label.
