# Instance namespace receipt page — runtime lineage, storage root, and overlap verdict interface spec

## Purpose

Issue a durable receipt after any reviewed same-host launch, switch, or attach so later operators do not have to reconstruct which namespace became active and what branch was chosen.

## Inputs

- host identifier
- requested action
- executed action class
- resulting namespace label
- principal / service account
- storage root
- config path if any
- control endpoint
- lineage verdict after apply
- subjects carried forward
- subjects blocked or reset
- overlap verdict if relevant
- strongest safe sentence
- stronger forbidden sentence
- rollback / follow-up route

## Layout

### A. Receipt verdict strip

Fields:

- active namespace now
- storage root now
- lineage verdict now
- overlap verdict now
- strongest safe sentence
- next review point

### B. What changed / what did not

Two lists:

- changed now
- preserved or explicitly not preserved

Examples:

- `service account changed`
- `storage root changed`
- `share roster preserved`
- `share roster not preserved; sibling namespace active`
- `subject attach blocked`
- `subject reset requires witness preservation follow-up`

### C. Namespace lineage card

Fields:

- prior namespace reference
- resulting relationship (`continued`, `sibling`, `fresh`, `uncertain`)
- evidence basis
- remaining uncertainty

### D. Subject admission card

Fields:

- subjects reopened safely
- subjects blocked for overlap
- subjects forced into new epoch / reset
- witness-preservation obligations still open

### E. Language block

Four lines:

- requested phrase
- approved phrase
- forbidden stronger phrase
- reason stronger phrase stays blocked

## Guardrails

- Never issue a receipt that records only the executable or mode flag.
- Never hide a changed storage root or principal.
- Never blur `same host` into `same seat preserved`.
- Never omit blocked or reset subjects from the receipt.

## Output

A durable namespace receipt that preserves which runtime world became active, how it relates to earlier worlds on the same host, and what continuity claim the product is honestly allowed to make.
