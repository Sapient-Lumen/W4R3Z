# Control-surface receipt page — audience, auth grade, transport, and recovery path interface spec

## Purpose

Preserve durable proof of what control-surface grade was actually achieved after a control mutation, credential recovery, certificate change, or mode shift.

The receipt exists so later operators do not have to infer from current settings whether the endpoint became broader, stronger, weaker, or merely different.

## Inputs

- seat / host identifier
- pre-change control grade
- resulting control grade
- actor and time
- chosen mutation or recovery method
- collateral class
- remaining browser / session residue
- fallback route after apply

## Receipt sections

### A. Control-grade result

Fields:

- resulting audience
- resulting auth floor
- resulting transport posture
- resulting certificate class
- resulting control modality

### B. Method and collateral

Fields:

- method used
- whether settings reset occurred
- whether sessions were revoked
- whether device-row duplication risk was introduced
- restart / reload performed or still pending

### C. Strongest safe sentence

Two explicit lines:

- strongest approved sentence
- stronger forbidden sentence

### D. Recovery and fallback

Fields:

- fallback control path now available
- browser residue still present?
- next recommended hardening action

## Guardrails

- Never issue a receipt that says only `WebUI configured`.
- Never omit whether the result is still HTTP, still self-signed, or no longer live-WebUI-administered.
- Never omit side effects of the chosen credential-reset path.

## Output

A durable control-surface attestation that later runtime, security, and support pages can cite directly.
