# Public-record carrier and acquisition protocol

## Purpose

`OQ-0057` route rows used to say that a record was public, replayable, or challengeable. `rev0263` makes that claim executable. The archive now separates:

| Layer | Question | Executable owner |
|---|---|---|
| route denominator | what target, record, quotient, inverse, blocker, and cap does the route claim? | `CANDIDATE-ROUTE-STATE-LEDGER.json` |
| public-record carrier | what artifact actually carries the public record? | `PUBLIC-RECORD-CARRIER-LEDGER.json` |
| acquisition protocol | how is the carrier produced, replayed, calibrated, challenged, or frozen? | `ACQUISITION-PROTOCOL-LEDGER.json` |
| claim binding | which claim language may propagate from the route/carrier/protocol bundle? | `CLAIM-ROUTE-BINDING-LEDGER.json` |

## Publicness levels

The archive deliberately scores publicness below candidate identity:

- `P0` — forecast, proposal, mission design, sensitivity, or intended protocol only.
- `P1` — paper-public or theorem-public: a derivation is inspectable, but no data carrier or challenge route is necessarily replayable.
- `P2` — metadata/protocol-public: the object has enough identifier, provenance, or protocol structure to route a future replay.
- `P3` — public data / benchmark / likelihood / table carrier: a fresh host can attempt a bounded replay.
- `P4` — challengeable laboratory or observational record with custody, calibration, and independent challenge route.
- `P5` — candidate-native public carrier: the candidate itself supplies the record, its public equivalence, and the update/challenge grammar.

No current row reaches `P5`. A `P3` or `P4` carrier can still be only `S2` or bounded `S3` route evidence when the inverse map, target quotient, observed-sector recovery, or candidate-native bridge remains many-to-one.

## Carrier is not closure

The following are now explicitly different:

```text
has DOI / URL / repository pointer
has public metadata
has versioned public data
has fresh-host replay
has independent challenge
has candidate-native public record
identifies the candidate
```

Only the last two are closure-track for candidate-native identifiability, and neither follows from the earlier items by default.

## Acquisition protocol rule

An acquisition protocol must name operations, minimum public artifacts, calibration or metadata, nuisance controls, replay harness, fresh-host requirement, failure effect, and maximum route effect. A protocol can strengthen a route by replacing a vague public-access sentence with a real replay contract, but it cannot move the route above the most restrictive of:

- the route row's `promotion_ceiling`,
- the carrier's `maximum_authority_credit`,
- the protocol's `maximum_route_effect`,
- the decision/forecast row's maximum effect,
- the promotion gate's allowed transition,
- the observed-sector obligation state,
- the residual cap.

## Standards import

The ledger borrows record-custody discipline from FAIR, W3C PROV, and DataCite-style metadata: a public record needs findability, accessibility, interoperability/reuse, provenance lineage, persistent identification, and version/citation discipline where applicable. These standards discipline publicness; they do not identify a physical ontology.

## Failure modes

The linter now treats these as structural failures when the claim needs carrier/protocol support:

- route row lacks carrier or protocol ids;
- carrier references an unknown route or unknown source;
- protocol references an unknown carrier or route;
- forecast/decision row lacks carrier/protocol coverage;
- claim binding references a route, carrier, protocol, claim, open question, or controlling ledger that does not exist;
- generated carrier/acquisition summary drifts from the executable ledgers.
