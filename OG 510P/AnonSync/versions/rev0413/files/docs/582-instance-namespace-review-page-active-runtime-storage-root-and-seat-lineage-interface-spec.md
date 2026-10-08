# Instance namespace review page — active runtime, storage root, and seat lineage interface spec

## Purpose

Give the operator one reviewed answer to:

- which runtime namespace is active on this host right now
- which storage root, identity world, and control endpoint belong to it
- whether it continues a known seat or represents a sibling runtime
- what evidence still leaves continuity uncertain
- what stronger sentence the product must not let the operator make

This page is the host-local companion to runtime profile, control-surface grade, policy provenance, and spine integrity pages.
It should appear whenever a launch, switch, update, or control entry could plausibly land in more than one namespace.

## Inputs

- host identifier
- runtime identifier / process identifier if known
- executable lane (`app`, `service`, `config-mode`, `cli`, `portable`, `unknown`)
- principal / service account
- storage root path
- config path if any
- control endpoint(s)
- data/listener ports if known
- identity label / seat label if known
- known prior namespaces on this host
- current share roster summary
- lineage verdict (`same-known-namespace`, `sibling-runtime`, `fresh-namespace`, `uncertain`, `collision-risk`)
- strongest safe sentence
- stronger forbidden sentence

## Primary questions this page must answer

1. What runtime namespace am I actually in?
2. Where does its durable state live?
3. Does it continue an earlier seat or fork a sibling runtime?
4. Which control surface belongs to this namespace?
5. What continuity claim remains unsafe?

## Layout

### A. Namespace verdict strip

Fields:

- namespace label
- lineage verdict
- storage-root label
- control-surface label
- strongest safe sentence
- stronger forbidden sentence
- next safest action

Example labels:

- `Known namespace reopened; storage lineage preserved`
- `Sibling runtime active; same host, different storage root`
- `Service-account switch surfaced a different namespace`
- `Namespace unclear; overlap-sensitive work blocked`

### B. Identity and storage card

Fields:

- principal / service account
- storage root
- config root if separate
- identity / seat name if known
- whether shares were carried forward, absent, or unknown
- log / database locus

The operator must be able to answer: **where does this namespace actually live?**

### C. Control and reach card

Fields:

- browser/WebUI endpoint
- whether endpoint is loopback, LAN, or other
- whether endpoint was discovered automatically or chosen explicitly
- whether this endpoint is newly bound relative to prior namespace
- whether the current endpoint could plausibly belong to another sibling runtime

### D. Lineage evidence card

Fields:

- evidence for same-namespace continuity
- evidence for sibling-runtime divergence
- missing evidence
- confidence verdict

Suggested evidence rows:

- same storage root reused
- same principal reused
- same config path reused
- same share roster visible
- same log lineage visible
- different storage root now active
- empty roster with changed principal
- changed ports / changed config / changed launch flags

### E. Safe language block

Three stacked lines:

- **What namespace is currently active**
- **Why the product believes that**
- **What stronger continuity sentence is still forbidden**

Example:

- `You are controlling a sibling runtime on the same host.`
- `The active storage root and principal differ from the prior seat.`
- `The product must not imply that earlier shares or identity are preserved here.`

## Required interactions

- `Open sibling runtime roster`
- `Review overlap admission`
- `Jump to storage root evidence`
- `Export instance namespace receipt`

## Guardrails

- Never let `same host` stand in for `same seat`.
- Never hide the active storage root when continuity is the question.
- Never let a new control tab imply preserved state without lineage evidence.
- Never allow overlap-sensitive mutation while namespace lineage is still `uncertain`.

## Output

A reviewed namespace object that tells the operator which runtime world is active, how it relates to earlier worlds on the same host, and what the product is honestly allowed to claim.
