# Certificate posture page — endpoint origin, warning class, and durable fix interface spec

## Purpose

Answer one ordinary operator question:

- why is this browser or client warning happening
- what endpoint identity is actually being presented
- is this only a self-signed bootstrap condition, broader browser residue, or a more serious mismatch
- what temporary bypass means
- what durable fix will actually improve control-surface grade

This page is narrower than general browser-trust recovery.
It is the certificate/trust posture page that the control-grade family links to directly.

## Inputs

- endpoint / seat identifier
- current transport posture
- presented certificate fingerprint / origin class
- hostname / interface context
- browser warning class
- prior trust history if known
- available durable fixes
- whether config-mode material is required

## Primary questions this page must answer

1. What certificate class is being presented?
2. Why is the client warning happening?
3. Is the warning expected for this endpoint and audience?
4. What does a temporary bypass actually do?
5. What durable fix best matches the intended control grade?

## Layout

### A. Presented endpoint card

Fields:

- endpoint address
- audience class
- transport posture
- certificate origin (`self-signed`, `operator-supplied`, `unknown`, `not-present`)
- fingerprint handle

### B. Warning-class card

Allowed classes:

- `expected self-signed bootstrap`
- `browser residue / HSTS pressure`
- `hostname or interface mismatch`
- `expired / rotated / stale cert`
- `unexpected endpoint identity`
- `warning absent`

### C. Temporary bypass meaning card

Fields:

- bypass available? (`yes`, `no`, `not-recommended`)
- scope (`this browser`, `this session`, `browser-profile residue`, `unknown`)
- what it changes
- what it does not change

### D. Durable fix ladder

Rows such as:

- `return to local HTTP only`
- `clear browser residue for the expected local endpoint`
- `install or reference a trusted certificate`
- `move control to a safer endpoint`

Each row shows:

- resulting control grade improvement
- config / restart need
- remaining caveats

### E. Trust receipt preview

Shows what the durable receipt will say after action:

- endpoint
- warning class
- chosen action
- resulting certificate posture
- remaining weaker claims

## Guardrails

- Never call a self-signed HTTPS endpoint `trusted`.
- Never conflate browser residue with endpoint rotation.
- Never present bypass as a durable hardening step.
- Never hide the fact that trusted-cert posture may require config-owned material and restart review.

## Output

A typed certificate/trust posture verdict and a ranked durable-fix ladder that feeds the control-grade family.
