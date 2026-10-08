# Evidence synthesis contract sheet page: target question, packet set, and weighted basis interface spec

## Purpose

Once several packets or witness planes exist for the same live question, the operator still needs one page that answers:

> what exactly are we trying to say, which packets are in the synthesis set, and on what basis are we allowed to merge them into one sentence at all?

## Core decision

AnonSync must expose one first-class **Evidence synthesis contract sheet** whenever two or more evidence packets, witness panes, or support artifacts are being interpreted as one basis for a decision, verdict, escalation, certification, or doctrine move.

## Fixed page order

1. **Synthesis header**
2. **Target-question card**
3. **Packet-set card**
4. **Relation-map card**
5. **Weighting-basis card**
6. **Open-conflict card**
7. **Decision sentence**

### 1) Synthesis header

Show:

- synthesis sheet id
- target case or decision id
- synthesis owner
- current synthesis posture
- source packet count
- independent-support count
- contradiction count
- current strongest safe integrated sentence
- strongest blocked sentence

Supported `synthesis_posture` values:

- `packet-set-opened`
- `relation-mapping-in-progress`
- `weighted-basis-drafted`
- `conflict-blocked`
- `bounded-integrated-claim-ready`
- `integrated-claim-ready-with-reservations`
- `superseded-or-stale`

Hard rule:

The header may not describe a synthesis as `ready` until at least one explicit relation judgment exists for every packet included in the active set.

### 2) Target-question card

Required rows:

- target question or decision
- candidate stronger sentence sought
- currently safe weaker sentence
- governing world assumptions
- governing scope
- excluded questions

Supported `synthesis_target_class` values:

- `diagnosis`
- `control-trust`
- `rollout-health`
- `dispute-verdict`
- `fulfillment-acceptance`
- `precedent-application`
- `certification`
- `external-escalation`

Hard rule:

One synthesis object answers one named target question.
It may support adjacent questions, but it cannot claim to answer them implicitly.

### 3) Packet-set card

Render one row per packet or witness source.
Required fields:

- source id
- source type
- source world or lane
- capture or observation window
- freshness posture
- fit posture for this question
- current participation status

Supported `source_type` values:

- `debug-log-packet`
- `dump-or-crash-packet`
- `network-test-packet`
- `ui-history-witness`
- `ui-graph-witness`
- `peer-state-witness`
- `queue-or-status-witness`
- `operator-note`
- `external-support-note`

Supported `participation_status` values:

- `active-basis`
- `context-only`
- `discounted`
- `superseded`
- `held-out-for-conflict`
- `rejected-wrong-world`

Hard rule:

A packet may not silently disappear from the set once it has influenced synthesis.
It must become `discounted`, `superseded`, or `rejected` explicitly.

### 4) Relation-map card

For each material source pair, require a relation judgment.
Supported `relation_class` values:

- `independent-corroboration`
- `duplicate-observation`
- `downstream-restatement`
- `partial-overlap`
- `not-comparable`
- `soft-conflict`
- `hard-conflict`
- `unknown-relation`

Hard rule:

The interface must not count `duplicate-observation` toward independent corroboration.

### 5) Weighting-basis card

Required rows:

- weighting policy used
- highest-weight sources
- discounted sources and reasons
- stale-but-still-used sources and reasons
- missing source classes that still matter
- open synthesis gap

Supported `weighting_policy` values:

- `source-rank-first`
- `freshness-first`
- `world-fit-first`
- `conflict-sensitive`
- `question-specific-custom`

Hard rule:

Any custom weighting policy must still publish why a lower-count result can outrank a higher-count result.

### 6) Open-conflict card

Required rows:

- unresolved conflict id
- conflicting source ids
- conflict description
- what sentence it blocks
- cheapest resolution path
- safe fallback sentence if unresolved

Supported `conflict_severity` values:

- `cosmetic`
- `bounded`
- `claim-capping`
- `route-reversing`
- `world-invalidating`

Hard rule:

A `claim-capping` or stronger conflict must appear above the final decision sentence, not below it.

### 7) Decision sentence

Render exactly two lines:

- **Strongest safe integrated sentence**
- **Strongest blocked sentence and why**

Hard rule:

If any active source remains `unknown-relation`, the decision sentence must mention the unresolved synthesis relation explicitly.
