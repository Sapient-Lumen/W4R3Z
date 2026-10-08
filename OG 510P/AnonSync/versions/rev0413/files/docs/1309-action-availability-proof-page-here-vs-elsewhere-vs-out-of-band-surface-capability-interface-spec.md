## Action-availability proof

### Goal
Prove the strongest honest sentence about where a requested action can actually be completed.

### Proof rungs

#### Rung 1 — documented somewhere
Evidence:
- the verb family exists in product or support material
- no surface-locality proof yet for this runtime

Safe sentence:
- `this product family has a lane for this action`

Blocked sentence:
- `you can complete it from here`

#### Rung 2 — elsewhere in-product lane known
Evidence:
- the stronger execution surface is known
- the current surface cannot execute it or cannot witness it strongly enough

Safe sentence:
- `this action is available, but not on this current surface`

Blocked sentence:
- `this surface supports it`

#### Rung 3 — out-of-band recovery identified
Evidence:
- the strongest truthful remediation requires file browser, shell, config file, or service manager
- the semantic loss of leaving the product has been published

Safe sentence:
- `recovery exists, but part of it lives outside the product surface`

Blocked sentence:
- `the product itself contains the full recovery lane`

#### Rung 4 — here / witnessed / recoverable contract proven
Evidence:
- the current surface can execute the verb
- the current surface can witness success/failure with adequate proof
- the current surface can complete the strongest honest recovery without leaving its reviewed lane

Safe sentence:
- `this action is executable, witnessable, and recoverable from the current surface`

Blocked sentence:
- `all runtimes and surfaces support it equally`

### Key product rule
**Presence of a button never outranks surface-locality truth.**
The product must always prefer proven execution/witness/recovery locality over superficial affordance parity.
