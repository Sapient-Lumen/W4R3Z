# Meta: Source Atlas Protocol (rev0436)

## Purpose
Use this protocol when the archive needs one shared answer to:
> which upstream sources should be maintained as recurring authority lanes, what claim families are they fit for, and what caveats must travel with them?

This protocol is **not** the same as:
- evidence renewal,
- a bibliography dump,
- a hypothesis ledger,
- or seam-local citation style.

It exists for the narrower question:
> what minimum fields and coverage rules should a small maintained source atlas require so future revisions stop re-deriving their evidentiary basis ad hoc?

Read with:
- `design/portfolio-source-atlas-2026Q1.md`
- `design/portfolio-evidence-renewal-2026Q1.md`
- `design/portfolio-hypothesis-ledger-2026Q1.md`
- `atlases/portfolio-source-atlas-v0/README.md`

## Required atlas fields
Every shared source-atlas card should include:
- `source_id`
- `title`
- `url`
- `authority_lane`
- `source_kind`
- `drift_horizon`
- `scope`
- `preferred_claim_classes`
- `preferred_uses`
- `known_caveats`
- `refresh_signals`
- `related_assets`

## Required lane coverage
The first shared atlas should cover at least these lanes:
- `official_blog`
- `inside_rust_blog`
- `project_goals`
- `cargo_reference`
- `service_docs`

These lanes are intentionally broad enough to stay small but narrow enough to stop the archive from treating every citation as interchangeable.

## Required claim-class coverage
The first shared atlas should cover at least these recurring claim classes:
- `ecosystem_pain`
- `roadmap_and_priorities`
- `machine_usable_tooling`
- `service_behavior`
- `security_and_registry`

## Allowed drift horizons
A source-atlas card should use one of:
- `hot`
- `warm`
- `cool`
- `cold`

Interpretation guideline:
- `hot` = recent service, incident, or implementation updates that may move quickly;
- `warm` = active but reasonably stable project/roadmap or service pages;
- `cool` = reference-like pages that still deserve periodic review;
- `cold` = stable background sources that rarely need attention.

## Checker scope
A thin checker may enforce:
- top-level schema family and revision;
- unique source IDs;
- allowed drift horizons;
- required lane coverage;
- required claim-class coverage;
- non-empty caveats and preferred-use lists;
- and existence of referenced canon assets.

A thin checker must **not** claim:
- that the source is currently fresh;
- that every claim inferred from it is correct;
- or that the source atlas replaces a real renewal pass.

## Card-writing rules
A good shared source-atlas card should:
- say what claim families the source is best at supporting;
- say what the source is *not* good evidence for;
- carry the most important caveats explicitly;
- and point to the canon assets that repeatedly rely on it.

A bad card:
- is just a title and URL;
- pretends one source supports every type of claim;
- or omits the caveats that matter most in practice.

## Update rule
If a revision materially changes the atlas model, it should update together:
- `design/portfolio-source-atlas-2026Q1.md`
- `meta/SOURCE_ATLAS_PROTOCOL.md`
- `atlases/portfolio-source-atlas-v0/sources.json`
- `tools/check_source_atlas.py`

If none of those changed, say so rather than silently treating the atlas as current.
