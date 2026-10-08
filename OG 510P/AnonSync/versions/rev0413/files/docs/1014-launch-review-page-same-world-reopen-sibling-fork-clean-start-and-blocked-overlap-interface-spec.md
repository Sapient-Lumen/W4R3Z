# Launch review page — same-world reopen, sibling fork, clean start, and blocked overlap

## Purpose

Review a non-trivial launch before the product starts a runtime whose world, exposure, or continuity would otherwise be easy to misread.

This page exists to answer:

- `is this the same world or a different one?`
- `will launch preserve current continuity?`
- `is this a safe sibling runtime or a dangerous overlap?`
- `what exactly changes if I proceed?`

## Trigger classes

Open this review when any of the following is true:

- the chosen state root differs from the last reviewed root
- config authority outranks the current interactive world
- launch changes visibility and control exposure together
- service/user switch changes reachable storage or roster basis
- the target world is absent and would be created fresh
- the target world risks overlap with an already-running runtime

## Required sections

### 1. Requested launch

Must show:

- launch verb and origin surface
- requested invocation family
- requested state root or root-selection rule
- requested exposure posture
- whether the operator asked for same-world continuity explicitly

### 2. World comparison

Must compare current reviewed world and candidate world across:

- state root
- identity lineage
- subject roster basis
- config ownership
- runtime principal / service profile

The page must classify the candidate as exactly one of:

- `same-world reopen`
- `same-world quieter projection`
- `same-world exposure change`
- `sibling world`
- `clean world`
- `blocked overlap`
- `unknown; proof insufficient`

### 3. Continuity and fallout

Must publish:

- what continuity survives automatically
- what continuity weakens and why
- whether rebind, relink, or rereview will be required
- whether any existing receipts become weaker or stale

### 4. Exposure and visibility delta

Must show:

- before / after visibility
- before / after listener posture
- before / after auth floor and transport posture
- whether the change creates a wider observer class

### 5. Safe options

Must offer typed actions such as:

- `Proceed as same-world reopen`
- `Proceed and record sibling-world receipt`
- `Create clean world intentionally`
- `Narrow to inspect-only`
- `Abort and reopen current reviewed world`
- `Repair overlap before launch`

### 6. Strongest safe sentence

Examples:

- `Proceeding will create a sibling runtime world; it will not inherit current subject continuity automatically.`
- `Proceeding keeps the same world but widens control exposure and therefore needs a launch receipt.`
- `Launch is blocked until overlap with the existing runtime is resolved.`

### 7. Blocked stronger sentence

Examples:

- `This is just starting the app again.`
- `A different root still means the same node.`
- `Silent launch is harmless because no UI appears.`
- `A clean world can be treated as the same seat once it starts.`

## Action semantics

- `Proceed` must always emit a receipt
- `Abort` may emit a refusal receipt when the case was materially risky
- `Inspect only` must not silently widen exposure or create a fresh mutable world
- `Repair overlap` must route into the overlap / namespace family, not a generic settings editor

## CLI contract

```text
anonsync launch review --profile srv-lan-headless --root /srv/anonsync/state
anonsync launch explain --candidate maintenance-shell
anonsync launch adopt-root --receipt invr_01J...
anonsync launch receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- the operator can create a sibling world without seeing that lineage break
- a visibility-only change and a world-switch look identical
- a blocked overlap still looks like an ordinary `start` button
- exposure widening rides along with launch without a typed delta section
