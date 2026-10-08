# Contribution shape protocol (rev0437)

If the archive now keeps a **shared contribution-shape atlas**, every card in that atlas should answer the same narrow question:

> what kind of thing should this worthy contribution become first, and what artifacts or failure modes come with that choice?

## Required files
A minimal shared contribution-shape packet includes:
- `design/portfolio-contribution-shapes-2026Q1.md`
- `meta/CONTRIBUTION_SHAPE_PROTOCOL.md`
- `morphologies/README.md`
- `morphologies/portfolio-contribution-shapes-v0/README.md`
- `morphologies/portfolio-contribution-shapes-v0/shapes.json`
- `tools/check_contribution_shapes.py`

## Required top-level fields
`shapes.json` must contain:
- `schema_family`
- `revision`
- `shapes`

## Required card fields
Each shape card must contain:
- `shape_id`
- `shape_class`
- `label`
- `one_sentence`
- `truth_location`
- `best_for`
- `required_artifacts`
- `common_failure_modes`
- `prefer_when`
- `avoid_when`
- `related_assets`

## Required class coverage
The first shared atlas must cover at least these classes:
- `protocol_contract`
- `evidence_collector`
- `reference_layer`
- `report_command`
- `service_surface`
- `corpus_atlas`
- `checker_validator`
- `bridge_adapter`
- `pilot_program`
- `stewarded_program`

## Machine-checkable rules
A checker may enforce:
- correct top-level schema family and revision presence;
- `shapes` is a list;
- unique `shape_id` values;
- required class coverage;
- non-empty string/list fields;
- at least one related canon asset per card;
- existence of referenced assets.

A checker should **not** try to prove:
- that the shape choice is strategically optimal;
- that the seam itself deserves promotion;
- that every worthy contribution only has one valid shape;
- or that a passed corpus proves product-market fit.

## Editorial rules
When using the atlas in prose:
- say which shape is primary **now**, not which every future evolution must follow forever;
- keep **shape choice** separate from **seam ranking**;
- keep **shape choice** separate from **pilot verdict**;
- and keep **shape choice** separate from **funding posture**, even when a stewarded-program card becomes relevant.

## Update rule
If a revision materially changes the atlas's hard rules, update the design note, the protocol, the corpus, and the checker in the same revision, or explicitly say why not.
