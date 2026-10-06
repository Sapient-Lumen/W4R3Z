# RFC-0109: Specialisations and variants

Status: Draft

## Problem

Operators and users need “safe mode” and “role mode” toggles that do not require rebuilding the base generation.

## Proposal

Introduce **variants** as a derived artifact that is bound to a base generation.

* variants change activation targets, policy-composed networking, extensions, and workload enablement
* variants do not mutate the immutable store closure of the base generation

## Evidence

* `variant.switch.receipt`

## References

See `docs/174-specialisations-and-variants.md`.
