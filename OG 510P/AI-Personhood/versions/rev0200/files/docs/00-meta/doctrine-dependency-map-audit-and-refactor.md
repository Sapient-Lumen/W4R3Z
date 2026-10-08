# Doctrine dependency map audit and refactor

## Thesis

The cube is now too large for path lists alone. A surface catalog answers “does the file exist?” A schema registry answers “does the object family parse and have fixtures?” A doctrine-dependency map answers a different question: **which canon surfaces rely on, overlap with, or supersede one another?**

rev0178 introduces a release-local dependency map and an audit tool. This is a refactor layer, not just a new artifact.

## What the map records

Each mapped surface records:

- path;
- layer;
- direct dependencies;
- overlapping surfaces;
- supersession candidates;
- owner role;
- review cadence;
- refactor risk.

The first map focuses on the civil-status / domicile / civic-participation band. It intentionally links back to older identity, domicile, family, assembly, public-legitimacy, and legal-aid surfaces instead of pretending rev0178 starts from a blank slate.

## Audit rule

`tools/audit_doctrine_dependency_map.py` validates the map, checks that referenced paths exist, checks that current-release markdown surfaces are represented, and rejects dependency cycles among mapped surfaces. This catches a class of defect the earlier catalog could not catch: a new doctrine may be present and indexed but still disconnected from the doctrine it quietly changes.

## Refactor posture

This is a release-local proof of method. The follow-through task is to backfill dependency maps across identity, continuity, capacity, emergency, commerce, labor, care, and treaty bands, then use those maps to mark superseded or duplicative surfaces.
