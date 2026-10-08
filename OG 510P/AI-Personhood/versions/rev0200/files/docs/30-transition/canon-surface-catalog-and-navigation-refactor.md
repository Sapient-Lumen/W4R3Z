# Canon surface catalog and navigation refactor

## Thesis

The archive now needs navigation controls as much as content controls. rev0177 adds a current-release surface catalog and audit tool so the next version of the cube can tell which surfaces were admitted, what they own, what they depend on, and whether they are findable.

## What the catalog changes

The catalog creates a release-local map of:

- doctrine surfaces;
- schema surfaces;
- example filings;
- negative fixtures;
- audit tools;
- owner roles;
- lifecycle axes;
- supersession state;
- review cadence.

This lets a later release ask: did a support rule enter the archive without an object? Did an object enter without a fixture? Did a tool enter without being wired into lint? Did a release status surface cite a path that is not cataloged?

## Current scope

rev0177 catalogs only its new surfaces. That limited scope is intentional. The next refactor should add release-band catalog files for rev0160-rev0176, then build a consolidated graph.

## Failure effects

A missing current-release catalog entry is a lint failure. A missing legacy catalog entry is not yet a failure but should be recorded as a backfill task until the catalog reaches whole-archive coverage.
