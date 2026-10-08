# Cube deep audit rev0233: first-packet decision gap and execution-path refactor

## Audit finding

Rev0232 made the first owner packet easier to receive. The remaining risk is that a received packet
could still fail to change anything because the operator has a landing workbench but not a compact
first-decision board. The cube could therefore stay trapped in the pattern the user warned about:
more readiness, more registry hygiene, and no decision about authority, evidence, construct, public
claims, or lifecycle.

Rev0233 treats that as the riskiest unfinished work. It adds a board that converts the owner packet
into five decision slices: authority, evidence, construct, public summary, and lifecycle. The board
also defines what to do when the packet is overbroad, protected, security-sensitive, weak evidence,
fallback-only, or decision-neutral.

## What changed

The main new operational surface is
[`ft0181-first-packet-decision-board.md`](../30-operations/ft0181-first-packet-decision-board.md).
It sits after the owner packet workbench and before acceptance, lifecycle decision, public summary,
closeout, and closure checklist updates.

The substantive shift is from "can this packet land?" to "what is this packet allowed to change?"
A landed packet must now produce a before/after statement for the five slices or remain a blocked,
fallback, trim, or re-request event.

## Risk reduced

| Risk | Rev0233 response |
|---|---|
| first packet lands but produces vague acceptance | decision board requires before/after rows before lifecycle or public claim changes |
| weak usage or satisfaction signal becomes learning proof | evidence slice forces claim-family downgrade or suppression |
| raw learner/protected/security facts drive hidden decisions | board routes protected and security facts to local-only or quarantine dispositions |
| schema expands because an export contains fields | schema restraint rule requires `DD2-DD6` decision effect |
| operator keeps asking for decision-neutral fields | `NO-CHANGE-TRIM` becomes a valid outcome and future request-reduction path |

## Audit/refactor: active-question and startup drag

The active open-question pressure is still `OQ-0103`, not the older branch-history family. Rev0233
keeps the long registry resolvable but updates the active followthrough index so the current question
is now the decision effect of the first owner packet, not generic field survival. It also fixes a
small duplicate legacy-alias line in the compact open-question registry.

The context path remains capped and execution-first. The new board replaces startup reliance on
release/toolchain registries; those registries remain in extended indexes for maintainers who are
changing schemas, validators, or canonical metadata.

## What not to do next

Do not add another schema or validator before a real packet arrives unless a lint failure proves the
current artifacts can accept a false closure or prohibited transfer. The highest-value next move is
still operational: use the owner packet workbench, then fill the decision board.

## Best next concrete move

The next operator should ask for exactly one minimized packet and be ready to record one of these
outcomes within the same session:

1. `PROCEED-STAGED` with five decision slices filled;
2. `FALLBACK-SERVICE` to `AIEDU-SR-003` because hint-tutor evidence needs raw learner traces;
3. `BLOCK-*` with a single re-request question; or
4. `NO-CHANGE-TRIM` with fields removed from future requests.

Any of those is forward motion. Another control-plane pass without a packet decision is not.

## Boundary

Rev0233 does not import real `SRC2+` evidence and does not close `FT-0181`. It improves decision
readiness only. It does not prove learning, safety, access, compliance, workload reduction, or
service effectiveness.
