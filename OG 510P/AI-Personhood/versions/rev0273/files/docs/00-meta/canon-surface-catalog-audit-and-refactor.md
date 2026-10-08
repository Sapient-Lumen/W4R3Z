# Canon surface catalog audit and refactor

## Problem

The cube now contains hundreds of markdown, schema, example, fixture, and tool surfaces. File presence alone is no longer enough. A surface can be present but practically lost if it is not cataloged, indexed, assigned an owner role, or linked to the release state that admitted it.

rev0177 therefore adds a first-pass catalog for current-release surfaces. This is deliberately narrower than a whole-archive index. The goal is to make the release boundary auditable now, then backfill earlier layers once the shape proves useful.

## Catalog object

The catalog records:

- surface id;
- file path;
- surface class;
- lifecycle axes;
- owner role;
- supersession posture;
- dependency notes;
- review cadence;
- title found in the markdown file, where applicable.

The catalog is not a bibliography, legal index, or table of contents. It is an operational surface map.

## Audit checks

The rev0177 audit checks that:

1. every cataloged path exists;
2. every surface id is unique;
3. every cataloged markdown file begins with a level-one title;
4. every path listed in `SURFACE-STATUS.json` for the current release is cataloged;
5. every cataloged schema, example, fixture, or tool path uses the expected directory;
6. the catalog summary counts match the catalog entries.

## Refactor posture

This is a light refactor, not a rewrite. It does not rename legacy files. It does not flatten the archive. It creates an admission gate for new surfaces and a future route for backfilling older families.

## Future backfill

The next catalog pass should add release bands for rev0160 through rev0176, then mark which surfaces are canonical, transitional, quarantine, superseded, or implementation-only. After that, the archive can begin enforcing that release heads, docs index, archive index, schema registry, fixture suite, and catalog agree.
