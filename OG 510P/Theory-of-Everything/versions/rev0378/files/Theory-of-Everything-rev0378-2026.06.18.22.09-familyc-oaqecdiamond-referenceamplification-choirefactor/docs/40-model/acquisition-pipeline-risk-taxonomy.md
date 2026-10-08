# Acquisition-pipeline risk taxonomy

## Purpose

This surface names the recurring ways a route can acquire a public-looking record without acquiring the target claim.

## Risk classes

| Risk | Pattern | Typical affected routes |
|---|---|---|
| pointer-public | URL, DOI, repository, or release page exists but no replayable target artifact is frozen | all routes |
| paper-public | derivation is inspectable but not experimentally or computationally acquired | formal and thermodynamic routes |
| benchmark-public | code/data replay works for a surrogate or narrow code space | Family C, learned inverse, simulations |
| catalog-public | public catalog exists but inverse to candidate identity is many-to-one | GW, cosmology, HEP/EFT |
| lab-public | lab record exists but nuisance or subsystem controls remain unresolved | GIE/BMV, single-graviton access |
| frame-public | a frame-relative fact exists but same-record transport is not established | QRF / relational routes |
| metadata-public | FAIR/PROV/DataCite discipline exists but does not itself carry the physical target | all routes |

## Use

When a future source is added, classify its acquisition risk before changing any route state. A risk classification can be useful progress, but it should usually lower or preserve the maximum credit rather than raise it.
