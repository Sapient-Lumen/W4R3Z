# Suite topology card — template

## Proposal
- id:
- title:
- repeated downstream question:
- receiver classes:

## Recommended package family
- core package:
- schemas package:
- operator-facing CLI package:
- adapter/import packages:
- corpus/fixtures package or tree:
- optional policy/profile package:

## Why each package exists
- core:
- schemas:
- CLI:
- adapters:
- corpus:
- policy/profile:

## Release ladder
### Honest `0.1`
- packages included:
- minimum operator workflow:
- minimum embeddable API:
- minimum stable packet vocabulary:

### Strong `0.3`
- packages added:
- adapter growth:
- corpus growth:
- reuse story:

### Real `1.0`
- schema stability:
- handoff semantics:
- adapter boundary policy:
- corpus expectations:

## Refusal boundary
- what stays out of core:
- what stays out of schemas:
- what the CLI does not certify:

## Worthiness check
- why this package family helps other people:
- why one package is not enough:
- why more packages would be too many:
