# Ciphertext custody page: plaintext ceiling, onward share, and default read-only guardrails interface spec

## Purpose

This page answers:

> what can this opaque node actually do right now, what hard ceilings are always true here, and which guardrails are forced rather than optional?

The page exists because `encrypted copy exists` is not enough truth.
Ciphertext custody is a role with its own capability floor and its own hard ceilings.

## Core rule

Every encrypted-custody subject on every seat must compile to one first-class **Ciphertext custody** page.
That page owns:

- custody role
- plaintext ceiling
- fixed guardrails
- onward-share ceiling
- performance cost note
- receipt

## Primary layout

The page always renders the same regions:

1. custody verdict
2. capability card
3. forced-guardrails card
4. onward-share / seeding card
5. receipt and next ladder

### 1) Custody verdict

Show:

- custody class: `ciphertext-only`, `mixed/uncertain`, `plaintext-capable elsewhere`, `blocked`
- strongest one-line answer
- current seat and target path
- whether a decrypt-capable peer is currently visible elsewhere
- safest next action

The operator must be able to answer: **what role is this node serving now?**

### 2) Capability card

Show explicit answers for:

- can store ciphertext: yes/no
- can seed encrypted bytes onward: yes/no
- can open plaintext here in ordinary product flow: yes/no
- can decrypt here in ordinary product flow: yes/no
- can accept Selective Sync posture: yes/no
- strongest impossible action

Use explicit hard-ceiling language such as:

- `plaintext open unavailable on this node`
- `local decrypt absent in ordinary flow`
- `Selective Sync not supported for this encrypted node`

The operator must be able to answer: **what can this node honestly do, and what can it never do here?**

### 3) Forced-guardrails card

Show:

- read-only posture forced or not
- `Overwrite any changed files` forced or not
- whether local edits would ever become authoritative
- whether local deletion will be redownloaded from other live peers when possible
- strongest hidden default that matters operationally

The operator must be able to answer: **which safety behavior here is mandatory rather than operator-chosen?**

### 4) Onward-share / seeding card

Show:

- may share onward at all
- if so, only in encrypted form or not
- whether the node can serve unmodified ciphertext to newly arriving peers
- whether memory / CPU cost is materially elevated
- strongest current availability witness

The operator must be able to answer: **what can this node contribute to the wider graph without ever becoming plaintext authority?**

### 5) Receipt and next ladder

After any review or change, emit a receipt preserving:

- custody class
- plaintext ceiling
- forced guardrails observed
- onward-share ceiling
- next review link to **Decrypt recovery**

## Honest outputs

This page may conclude:

- `Ciphertext-only seed · can store and serve encrypted bytes but cannot open plaintext here`
- `Read-only encrypted node · overwrite guardrail is forced`
- `Onward share allowed only in encrypted format`
- `Capability uncertain because admission proof is incomplete`

It may not collapse these into one generic `Encrypted folder connected` outcome.

## Rules

### Rule 1 — ciphertext presence is not plaintext capability

Do not let the UI imply that because bytes exist here, readable restoration is therefore local and immediate.

### Rule 2 — forced guardrails must look forced

If overwrite or read-only posture is mandatory, the page must not render it as an optional preference.

### Rule 3 — impossible actions stay visible as impossible

Hide-less is better than magical optimism.
The operator should see why a tempting action is impossible on this node.

### Rule 4 — performance cost belongs with the role

If this role materially increases CPU or memory cost, that belongs on the page, not in later troubleshooting folklore.

## Non-clone reason

Current official Resilio docs still openly say the encrypted node is read-only, cannot decrypt in ordinary use, has `Overwrite any changed files` forced, lacks Selective Sync, and can only share onward in encrypted form.
That candor is good.
What should not be cloned is the way those truths still read like caveats inside an article instead of one stable custody page.
