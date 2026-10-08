# Doctrine dependency map and overlap refactor

## Thesis

Identity, domicile, family, association, public services, and civic participation are tightly coupled. A new rule in one area can silently change another. rev0178 therefore adds `examples/doctrine-dependency-map-rev0178.json` and `tools/audit_doctrine_dependency_map.py`.

## Dependency classes

- **Depends on** — a doctrine cannot be understood or safely applied without the prior surface.
- **Overlaps with** — two surfaces govern adjacent facts and must be harmonized.
- **Supersedes** — a surface narrows, replaces, or operationalizes an earlier surface.
- **Refactor risk** — ambiguity, duplication, obsolete vocabulary, or conflicting reliance effect.

## First-map scope

The first dependency map covers rev0178 surfaces and links them to older surfaces on legal identity, domicile packets, family status, assembly, public legitimacy, legal aid, accommodation, communication access, schema registry, and canon catalog.

## Audit rule

The audit tool checks that mapped paths exist, that current-release markdown surfaces are represented, that dependencies and overlaps point to real files, and that dependency cycles are not introduced among mapped surfaces.

## Follow-through

Backfill should proceed by release band:

1. identity and recognition;
2. continuity and migration;
3. safety/emergency and sealed evidence;
4. commerce and labor;
5. care/accessibility;
6. treaty and cross-border transfer.

Only after that backfill should the archive mark old surfaces as superseded or merge overlapping files.
