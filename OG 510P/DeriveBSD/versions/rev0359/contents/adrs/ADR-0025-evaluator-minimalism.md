# ADR-0025: No general-purpose evaluator in core Derive (proposed)

- Status: proposed
- Date: 2026-02-23

## Decision
The Derive core does not execute user code during evaluation. Specs are data; computation is limited to explicit frontend compilation and controlled resolvers/builders.

## Consequences
- evaluation remains deterministic and auditable
- smaller trusted computing base
- avoids Nix-style “evaluation language becomes the ecosystem”
