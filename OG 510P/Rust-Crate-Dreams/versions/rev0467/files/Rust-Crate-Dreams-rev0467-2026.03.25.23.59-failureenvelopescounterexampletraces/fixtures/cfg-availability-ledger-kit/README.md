# Cfg Availability Ledger Kit fixtures

This fixture pack is for **P-0451 Cfg Availability Ledger Kit**.
It exists to keep item-level conditional availability honest when docs, features, targets, docs.rs settings, and re-exported public paths all tell slightly different stories.

The most important review objects in this fixture pack are:

- **availability class** — what kind of availability claim is being made
- **origin receipt** — where the claim came from
- **slice witness** — which target/feature/docs slice was actually observed
- **gate normalization** — how a raw `cfg` expression was simplified for people
- **re-export lineage** — whether effective availability was inherited from another path
- **fidelity report** — how much of the matrix is directly observed versus inferred or imported
- **usability witness** — whether docs-visible, doctest-usable, and downstream-usable truth actually match
- **default-surface drift** — whether hosted defaults changed what readers see without proving new support

The fixture families are deliberately biased toward cases where a coarse “the docs show it” or “the public path exists” interpretation would be wrong.
