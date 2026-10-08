# Live-window card gate audit rev0280

## Question

Did rev0280 change the live-window card gate or allow a local card to authorize
service-record edits, lifecycle promotion, public language, custody, acceptance,
or closure?

## Finding

No. Rev0280 leaves the live-window card mechanics intact and works upstream of
that gate, at the first-contact packet/router execution seam. The card still
only becomes readout-ready after a terminal/readout-ready state: `paused`,
`rolled_back`, `completed_no_closure`, or `quarantined`.

## Boundary preserved

A current-version packet, field-next docket, send log, contact clock, intake,
workbench seed, workbench review, first-packet decision, post-decision ticket,
live-window card, readout note, or audit surface cannot mutate service records,
upgrade lifecycle state, support public claims, create custody, accept evidence,
or close `FT-0181`.

## Watch point

When the first real packet arrives, the temptation will be to skip from a clean
workbench route to service change. Do not. Use the decision, ticket, card, and
readout path exactly as routed.
