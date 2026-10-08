# Encrypted custody seat: capability ceiling and recoverability posture interface spec

## Purpose

After encrypted custody exists, operators still need one stable page that keeps the node honest in everyday use.

This page exists to answer one ordinary operator question:

> what can this encrypted-custody seat do right now, what can it never do here, how recoverable is it if source peers fail, and what exact review should I open next?

## Core decision

Every seat participating as a ciphertext-only node must expose one first-class **Encrypted custody seat** page.
That page is the semantic home of:

- current custody role
- capability ceiling
- current recoverability posture
- strongest current risk
- next review links and recent receipts

The page must not force the operator to infer these truths from a folder row, a mode icon, and remembered help-center caveats.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. current custody verdict strip
2. capability ceiling card
3. recoverability posture card
4. current risks and missing materials
5. recent continuity-changing receipts
6. admissible next actions

### 1) Current custody verdict strip

Show:

- seat name and host
- subject or subject-family count in encrypted custody
- current verdict
- strongest current risk
- next safest action button

Allowed verdicts:

- `ciphertext custody active`
- `ciphertext custody active; recovery partially prepared`
- `ciphertext custody degraded`
- `ciphertext custody misconfigured`
- `ciphertext custody blocked / continuity lost`

The operator must be able to answer: **is this seat healthy as an opaque custody node right now?**

### 2) Capability ceiling card

Show:

- stores ciphertext only
- ordinary plaintext access (`never on this seat`)
- write authority (`read-only custody only`)
- overwrite posture
- selective-materialization availability
- onward-share ceiling

The page should use explicit statements such as:

- `ordinary plaintext unavailable here`
- `onward sharing limited to encrypted format`
- `selective sync unavailable on this custody seat`

The operator must be able to answer: **what exact powers exist here, and what powers do not exist here by design?**

### 3) Recoverability posture card

Show one ranked posture:

- `recovery prepared`
- `recovery plausible but incomplete`
- `recovery at risk`
- `recovery not prepared`
- `continuity uncertain`

For each posture, show:

- saved-key posture
- database continuity posture
- known decrypt lane
- last rehearsal or proof time
- strongest missing prerequisite

The operator must be able to answer: **if my plaintext-capable source disappears, how real is the path back from this seat?**

### 4) Current risks and missing materials

This card is mandatory whenever posture is not `recovery prepared`.

Show:

- missing RW/RO material or unknown storage location
- continuity risk from disconnect/remove/recreate operations
- archive ceiling misunderstanding risk
- stale rehearsal or never-tested recovery posture
- conflicting seat posture or path mutation risk

The page should differentiate:

- `hard blocker`
- `missing evidence`
- `operator memory risk`
- `ordinary caution only`

### 5) Recent continuity-changing receipts

Show recent receipts that materially affect later recovery:

- created encrypted custody
- changed target path
- disconnected / removed subject
- continuity-preserving rereview
- rehearsal result
- explicit abstention with reason

Receipts must preserve whether the event weakened continuity, strengthened evidence, or merely changed visibility.

### 6) Admissible next actions

Typical actions:

- `Open recovery material attestation`
- `Review target admission`
- `Generate proofpack`
- `Run recovery drill`
- `Inspect encrypted Archive limit`
- `Escalate continuity uncertainty`
- `Retire this custody seat`

The first action should be the strongest honest next move, not just `Settings`.

## Compact seat card contract

A trustworthy compact seat card should preserve the following order:

1. custody role
2. capability ceiling
3. recoverability posture
4. strongest risk
5. next honest action

Example:

- `Ciphertext custody active · Plaintext unavailable / encrypted-only onward share · Recovery plausible but incomplete · Saved keys unproven on current operator roster · Run attestation`

## Acceptance criteria

This spec is satisfied when:

- every encrypted-custody seat can explain its capabilities without article memory
- recoverability posture is visible next to capability ceiling instead of hidden in a later support lane
- continuity-changing events emit durable receipts
- the operator can tell whether the seat is valuable merely as custody, or also valuable as a prepared recovery source
