# Exposure and Liability Lifecycle

rev0188 refactors the cube's exposure, liability, insurance, indemnity, reserve, warranty, and risk-transfer layer.

The archive already had many sharp pieces: replay-grade clearance logs as insurance evidence, source-object identity warranties, source-snapshot escrow, fault-class scoreboards, extension-frequency penalties, bond-release evidence, liability surfaces created by readable/structured divergence, supported-version windows as quiet exclusion regimes, and custody-break certificates. But those dossiers used `liability`, `insurance`, `underwriting`, `warranty`, `indemnity`, `capital release`, `reserve`, `fault`, and `risk transfer` as if they were one thing.

They are not one thing. The central object is now:

> **A proof object becomes financially decisive when it changes who bears loss, which policy responds, whether a defense is funded, whether a limit erodes, whether an exclusion applies, whether a reserve is released, whether an indemnity chain activates, and whether a later recovery action is preserved.**

This model treats exposure as a state machine rather than a vague cost cloud.

## Why this needed a refactor

The cube has already normalized four adjacent families:

- **freshness** — whether a proof is current enough;
- **remedy** — how a challenged proof is contested, stayed, corrected, and closed;
- **authority** — who is allowed to act, bind, disclose, waive, receive, or appeal;
- **lineage** — whether source, custody, transformation, resolver, redaction, and replay paths are visible enough.

Exposure kept leaking through all four. A stale proof can void a warranty. A remedy clock can trigger a notification duty. A lineage gap can shift a claim from covered to reserved-rights. An unauthorized agent can bind a firm to an indemnity. A certificate can be technically valid but financially useless if the relevant policy excludes the loss class.

rev0188 makes the reusable object explicit: **exposure state**.

## Canonical lifecycle

| Stage | Question | Typical artifact | Failure if missing |
|---|---|---|---|
| `identify` | What loss class, asset, transaction, party, product, incident, or tail is being exposed? | exposure inventory, covered-product list, insured-location schedule, claim taxonomy | unknown accumulation; orphan risk |
| `allocate` | Who initially bears the loss: owner, buyer, seller, broker, supplier, insurer, platform, public fund, or residual claimant? | contract allocation, limitation-of-liability clause, holdback, indemnity schedule | uninsured or double-counted exposure |
| `attach` | What policy, warranty, bond, guarantee, reserve, escrow, or fund could respond? | policy schedule, certificate of insurance, bond, reserve memo, warranty register | false assurance; nonresponsive protection |
| `condition` | What conditions must be satisfied before protection applies? | notice clause, cooperation duty, security warranty, maintenance obligation, update requirement, preservation hold | condition-precedent failure |
| `trigger` | Which event starts a reporting, defense, payment, disclosure, reserve, or stay clock? | incident report, adverse-action notice, defect notice, demand letter, regulator notice | late notice; wrong trigger class |
| `classify` | Which coverage / warranty / exclusion / fault class applies? | coverage position, exclusion label, fault code, materiality analysis | mispriced claim; wrong defense path |
| `notify` | Which counterparties, carriers, reinsurers, regulators, investors, boards, trustees, or affected parties must be told? | notice packet, broker notice, 8-K, CIRCIA report, supplemental report | lost rights; duplicated reports; silent accumulation |
| `defend` | Who controls defense, settlement, remediation, ransom, recall, repair, cure, or replacement? | defense tender, reservation-of-rights letter, panel-counsel assignment, response playbook | conflict over control; unrecoverable spend |
| `reserve` | What capital, accounting reserve, holdback, deductible, SIR, or bond amount must remain locked? | reserve schedule, loss run, impairment memo, escrow release schedule | under-reserving; premature release |
| `pay` | What actually pays: indemnity, expense reimbursement, bond draw, trust release, escrow, parametric trigger, warranty credit, public fund? | claim payment, draw certificate, reimbursement ledger | leakage; unjustified denial |
| `erode` | Does the payment erode limits, aggregates, retentions, warranties, or future capacity? | limit ledger, aggregate consumption, retention ledger, loss history | hidden capacity exhaustion |
| `subrogate` | Can the paying party recover from a vendor, attacker, seller, installer, delegate, certifier, or maintainer? | subrogation hold, evidence packet, assignment, recovery claim | destroyed recovery rights |
| `renew` | Does the loss history, control failure, or evidence quality alter renewal, exclusions, pricing, or market access? | renewal submission, loss-run normalization, underwriting response | sudden withdrawal; uninsurable class |
| `close` | Is the exposure closed, tail-open, released, excluded, litigated, reserved, or archive-only? | closure memo, release, non-reliance label, tail schedule, archive packet | ambiguous afterlife |

## State vocabulary introduced here

The corresponding state vocabulary is in `33-exposure-state-vocabulary.md`. The short form:

- `unallocated-exposure`
- `allocated-by-contract`
- `coverage-attached`
- `certificate-evidence-accepted`
- `endorsement-required`
- `condition-precedent-pending`
- `warranty-breached`
- `notice-clock-running`
- `materiality-determination-pending`
- `coverage-position-reserved`
- `defense-under-reservation`
- `exclusion-flagged`
- `deductible-unmet`
- `sir-open`
- `limit-eroding`
- `aggregate-approaching`
- `indemnity-chain-mapped`
- `subrogation-preserved`
- `reserve-held`
- `reserve-release-pending`
- `loss-run-sensitive`
- `renewal-restricted`
- `tail-open`
- `claim-closed`
- `nonresponsive-protection`

## Design rule for future dossiers

A new exposure/liability dossier should not merely say that a proof creates risk or that insurance will care. It must identify at least one of the following:

1. a new **allocation problem**;
2. a new **coverage/warranty trigger**;
3. a new **condition-precedent or notice clock**;
4. a new **fault/exclusion classification surface**;
5. a new **reserve, retention, holdback, or capital-release state**;
6. a new **limit erosion or aggregate-accumulation problem**;
7. a new **subrogation or recovery evidence requirement**;
8. a new **renewal / withdrawal / market-access consequence**.

If it does not do one of those, it should probably be a state inside this lifecycle rather than a standalone dossier.

## Relationship to other refactors

### Freshness

Freshness determines whether a proof is current enough. Exposure determines whether its age changes coverage, reserve, indemnity, or price. A stale proof is sometimes harmless; sometimes it is a warranty breach.

### Remedy

Remedy determines how a contested decision is reviewed. Exposure determines who pays while review is pending, whether a stay preserves coverage, and whether delay creates a notification or mitigation failure.

### Authority

Authority determines who can tender, settle, waive, sign, or bind. Exposure determines whether that act changes loss allocation. A representative may be authorized to report an incident but not to settle or waive subrogation.

### Lineage

Lineage determines whether evidence can be trusted. Exposure determines whether a lineage gap is an ordinary caveat, a reserve hold, a coverage reservation, a deductible dispute, or a subrogation killer.

## Minimal exposure packet

A reliance-grade exposure packet should include:

- exposure subject and loss class;
- parties, roles, insureds, additional insureds, beneficiaries, and residual bearers;
- policy, bond, warranty, guarantee, escrow, reserve, or fund references;
- coverage / warranty / indemnity trigger grammar;
- required notices and clocks;
- conditions precedent and cooperation duties;
- exclusions and exceptions;
- defense / settlement / remediation control rules;
- deductible, SIR, limit, aggregate, and erosion state;
- reserve or holdback schedule;
- subrogation preservation requirements;
- loss-run treatment;
- renewal consequences;
- dispute and appeal path;
- closure and tail state.

## Falsifiers

This family weakens if insurers, lenders, buyers, auditors, and regulators continue treating proof-object quality as a generic due-diligence note rather than a priced exposure variable; if exclusions and warranties remain too bespoke to generalize into state labels; if incident-report clocks stay disconnected from coverage and reserve workflows; or if counterparties keep accepting certificates of insurance and warranty language without asking whether the underlying protection actually responds to the new proof failures.
