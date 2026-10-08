# 408 — Procurement clauses for exit, escrow, and public continuity

## One-line thesis

Public procurement should treat **continuity at supplier exit** as a design requirement from day one, with contract clauses, tested handovers, and fallback assets that make the public service survivable.

## Why this matters

Governments often talk about avoiding lock-in while signing contracts that make switching, insourcing, audit, or emergency takeover practically impossible. The real test is not whether a tender mentions open standards, but whether the public authority can still run the service when:

- the vendor fails,
- the relationship breaks down,
- prices spike,
- a security event hits,
- policy changes,
- the state needs to move to a successor supplier or public operator.

The archive should therefore move from generic anti-lock-in sentiment to concrete **continuity clauses**.

## Design rule

For critical digital public services, every major contract should include an active continuity package covering:

- exit planning,
- data return rights,
- knowledge transfer,
- key-person continuity,
- dependency mapping,
- escrow or protected access where appropriate,
- rehearsal of handover under realistic conditions.

## Pattern pack

### 1. Live exit plan, not end-of-contract panic

Require an exit plan from the start and review it regularly. It should cover:

- activities and milestones,
- roles and accountabilities,
- joint risk register,
- interfaces and dependencies,
- asset and data transfer,
- staffing and knowledge transfer,
- continuity standards during transition.

### 2. Data return as an operational right

The buyer should have enforceable rights to receive:

- complete records,
- documentation for schemas and APIs,
- audit logs,
- configuration state,
- metadata and business rules needed for continuity,
- export in open or documented formats.

Data return that arrives without context is a theatrical right.

### 3. Knowledge transfer duty

A successor needs more than raw files. Contracts should require:

- runbooks,
- architecture diagrams,
- dependency inventories,
- service desk history,
- known defects list,
- incident history,
- training and shadowing periods.

### 4. Escrow where failure would strand the public

For especially critical or brittle dependencies, require a continuity instrument such as:

- source escrow,
- build artifact escrow,
- key-material recovery arrangements,
- mirrored documentation,
- independent copies of critical configuration and records.

Escrow is not for every commodity service; it is for places where collapse would otherwise hand the public no viable bridge.

### 5. Step-in and degrade gracefully

The buyer should define step-in rights for emergencies and degraded modes of operation:

- temporary operational control,
- priority support obligations,
- transition assistance,
- capped charges for mandatory handover work,
- minimum service continuation during dispute.

### 6. Open boundary inventory

A contract should identify which boundaries must stay portable:

- identity,
- event streams,
- reporting,
- case records,
- messaging,
- payment interfaces,
- moderation logs,
- model inputs and outputs where relevant.

If those seams are not named, they usually harden into proprietary dependency.

### 7. Exit rehearsal

Run at least one real handover drill or partial migration exercise before renewal. Test:

- export completeness,
- re-hosting assumptions,
- credential rotation,
- replacement of modules,
- documentation quality,
- continuity of records and auditability.

The point is to discover what the contract only pretends to guarantee.

## Guardrails

- Continuity clauses should match service criticality; do not overburden trivial procurements.
- Anti-lock-in must not become anti-innovation; some lock-in can be a conscious trade if the off-ramp is explicit and priced.
- Intellectual property strategy should preserve re-competition and public continuity even when suppliers retain some ownership.
- Exit planning should be linked to security, records retention, and business continuity rather than left to commercial teams alone.

## Failure modes

- **paper portability**: the contract promises export but not usable transfer.
- **key-person trap**: only supplier staff know how the system actually runs.
- **escrow fiction**: escrow exists but is outdated, inaccessible, or legally unusable.
- **renewal extortion**: the cost of leaving becomes the incumbent’s main bargaining chip.
- **boundary blur**: data, code, and operations are so entangled that no partial transition is possible.

## Practical tests

A public service passes the continuity test when a buyer can answer yes to all of the following:

1. Could we identify the assets, people, and interfaces needed to transfer the service within a defined timeframe?
2. Would exported records remain intelligible to a successor without the incumbent interpreting them?
3. Do we have a legally and technically real path to continue operations during supplier failure or dispute?
4. Have we tested at least one meaningful part of the exit plan before contract end?
5. Would a re-compete preserve public records, auditability, and service continuity?

## Compression rule for the archive

Whenever procurement language sounds reassuring, ask:

**Could we still operate the service ninety days after a hostile or chaotic supplier exit?**

If not, continuity has not really been bought.
