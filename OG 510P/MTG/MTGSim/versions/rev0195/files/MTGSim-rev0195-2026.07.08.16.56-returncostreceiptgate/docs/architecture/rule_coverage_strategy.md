# Rule coverage strategy through rev0011

MTGSim does not claim full Magic support. It turns completeness into an auditable inventory.

## Source posture

The cube keeps source manifests, fetch tools, and local/private diff/index tools. It does not redistribute Wizards' full rules text. The official rules page remains the canonical source for Comprehensive Rules downloads.

## Metadata-only ledger

`data/rules/coverage/rules_ledger.json` stores coarse rule buckets with:

- rule ID or range;
- title;
- status;
- implementation notes;
- linked C++/scenario/fuzz test refs;
- known gaps.

`tools/check_rule_coverage.py` validates ledger structure and cross-links. `tools/rules_progress.py` computes trend metrics.

## rev0009 snapshot

- conservative full-rules proxy: **0.986%**;
- ledger-weighted internal progress: **77.031%**;
- ledger rows: **32**;
- tested rows: **24**;
- executable/scaffold-or-better rows: **27**;
- linked test refs: **191**.

The conservative proxy is the headline number. The ledger-weighted number is only useful inside the small current inventory.

## New rev0009 coverage

rev0009 adds metadata rows and tests for:

- `603`: triggered abilities scaffold;
- `603.3`: putting pending triggered abilities on the stack scaffold;
- `603.6`: zone-change/dies trigger scaffold.

These rows are marked as tested scaffolds, not full rules. The known-gaps fields remain important because rule 603 is large and depends on choices, conditions, ordering, targets, delayed/reflexive triggers, and last-known-information.

## rev0010 ledger changes

rev0010 adds metadata-only rows for `614` replacement effects and `615` prevention effects. The `615` row is marked tested for finite damage-prevention shields. The `614` row is only scaffolded, because the current engine has a replacement/prevention hook around damage events but not a general replacement-effect system.

This distinction matters: having tests that mention `614` means the hook exists and is visible in the ledger; it does not mean MTGSim implements replacement effects generally.

## rev0011 coverage note: counters are cross-cutting

Rule `122` is now tracked as a dedicated metadata-only row, but counter work also touches rows for objects, zone changes, effects, casting, combat damage, SBAs, and layers. The ledger should keep both views: a direct row for counter primitives and cross-links on behaviors that would regress if counter math drifted.

The conservative full-rules proxy is **1.080%** in rev0011. This is still a trend metric, not proof of rules completeness.

## rev0012 keyword coverage decomposition

Rule 702 is now represented as a broad keyword-abilities row plus narrow tested rows for flying, reach, deathtouch, lifelink, and vigilance. This avoids the trap of claiming a whole chapter from one bitmask: each keyword gets its own row, notes, limitations, and linked tests.

## rev0013 keyword ledger split

rev0013 adds separate metadata-only ledger rows for first strike, double strike, trample, and indestructible. These are intentionally narrow rows. They are not evidence that rule 702 is complete; they are evidence that specific C++ behaviors and scenarios are linked to specific rule IDs.

The rule-ledger strategy remains: never mark a broad chapter complete from one scaffold. Add a row for each behavior, link it to C++ and scenario tests, document missing interactions, and let the conservative full-rules progress estimator stay harsh.


## rev0015 ledger expansion

The ledger now tracks `105` colors, `109` object/source characteristics, `202` simple mana-cost-derived color metadata, `702.16` protection, and `702.111` menace. These are marked tested only for the narrow scaffolds implemented locally; the conservative rules-progress estimate remains the headline completeness number.

## rev0016 ledger refinement

rev0016 adds exact metadata rows for `701.8` destroy, `701.19` regenerate, and the SBA subrules `704.5f`, `704.5g`, and `704.5h`. The important coverage distinction is that tests now prove regeneration is connected to destroy-style events, not to every graveyard movement. This is an example of how the ledger should evolve: split a coarse bucket into exact rows when the engine has executable behavior and focused regression tests.

## rev0017 attachment coverage rows

The rules ledger now tracks attachment-specific metadata rows for `301.5`, `303.4`, `303.4a`, `303.4b`, `303.4g`, `701.3`, `704.5m`, and `704.5n`. These rows intentionally do not copy official rule text. They link local implementation seams and tests to the rule IDs most affected by the Aura/Equipment scaffold.

## rev0018 token/exile/sacrifice coverage rows

rev0018 adds metadata-only rows for `111` tokens, `406` exile, `701.7` create, `701.13` exile, `701.21` sacrifice, and `704.5d` token ceased-to-exist cleanup. These are marked tested only for the local scaffolds: simple token creation from a definition index, targeted exile of battlefield permanents, controller sacrifice of controlled permanents, and token tombstone cleanup during SBAs.

This revision is a good example of why the conservative full-rules proxy remains the headline number. The ledger-weighted percentage is high because the internal inventory is increasingly well linked, but full Magic still needs token copy characteristics, linked exile durations, full LKI, real card text, and replacement-effect choices.


## rev0019 rule-ledger update

The ledger adds metadata-only rows for planeswalker and loyalty rules: `306`, `306.5`, `306.6`, `306.8`, `606`, `606.3`, `606.4`, `606.6`, and `704.5i`. Each row links to focused C++ cases and/or scenario fixtures. This is coverage bookkeeping, not a claim of complete planeswalker support.


## rev0020 battle ledger rows

Battle support adds metadata-only rows for rules around battles, defense counters, battle attacks, damage-to-defense, protectors, and zero-defense state-based actions. These rows are tested scaffolds, not full coverage of battle subtypes or Siege transformation.


## rev0021 modal ledger split

The modal slice split exact metadata-only rows for `115.8`, `700.2`, `700.2a`, `700.2c`, and `700.2f`. This keeps the high-level `700-733` inventory bucket from becoming a fake proof of coverage while still letting C++ test rule refs be mechanically checked against a ledger row.

## rev0022 timing and land-play ledger rows

rev0022 adds metadata-only rows for `116`, `117.1a`, `304`, `305`, `305.1`, `305.2`, `305.2a`, `305.2b`, `305.3`, `305.9`, `307`, and `702.8`. The split is intentional: “timing works” is too broad to mark as one claim. The current tests prove only narrow local behaviors: instant/flash timing, ordinary noninstant sorcery-speed gating, stack-free land play, one-land-per-turn accounting, land-play reset, and the rule that lands are not cast as spells.

## Rev0023 rule-602 coverage posture

The ledger now has metadata-only rows for `602`, `602.1`, `602.2`, `602.2a`, `602.2b`, `602.2g`, and `117.1b`. These rows are marked tested for the narrow scaffold only; they are not a claim of complete activated ability coverage.


## rev0024 exact mana subrules

The ledger now splits several mana-payment footholds out of the old coarse `605` row: `601.2g`, `601.2h`, `605.1a`, `605.3a`, `605.3b`, and `405.6c`. This gives future rule-change diffs a smaller blast radius: if the Comprehensive Rules alter mana-ability timing or payment ordering, the changed subrule rows point directly at the auto-payment tests and scenario fixtures.

## rev0025 ledger additions

The ledger now has metadata-only rows for static abilities and continuous-effect/layer seams: `604`, `611`, `613`, `613.1f`, `613.1g`, and `613.4c`. These rows are marked tested only for the narrow scaffolds implemented here, not for full layer completeness.


## rev0026 control-change coverage rows

rev0026 adds metadata-only rows for `108.4`, `109.4`, `110.2`, and `613.1b`. These rows are marked tested only for MTGSim's narrow permanent-control scaffold: owner identity is preserved, controller battlefield containers are updated, combat metadata is cleared, control-start timestamps refresh, and controller-scoped static effects recompute.

This is still not a full layer-2 implementation. The ledger should treat `613.1b` as an executable seam that future timestamp/dependency/duration work can plug into, not as evidence that continuous control-changing effects are complete.


## rev0027 type/color layer coverage rows

rev0027 adds metadata-only rows for `205`, `613.1d`, and `613.1e`, and extends the existing `105`, `109`, `611`, and `613` rows. The tested scaffold is intentionally narrow: static battlefield effects can add/remove coarse card-type bits and set/add/remove colors, and consumers use `object_type_mask(...)` / `object_color_mask(...)` for current derived answers. Full timestamps, dependencies, subtypes, supertypes, and Oracle text remain future work.

## rev0028 ledger delta

rev0028 adds metadata-only rows for `208.4` and `613.4b`, expands `613.1f` from ability-grant-only to ability add/remove coverage, and links the new static ability-removal and base-P/T scenario fixtures. This still does not prove rule-613 completeness: timestamps, dependencies, characteristic-defining abilities, copy/text effects, and duration-bearing continuous effects remain roadmap rows.
## rev0029 ledger slice

The rules ledger now has metadata-only rows for `611.2a`, `611.2c`, `613.7`, and `514.2`. The row status reflects focused executable fixtures for a tiny until-cleanup generated-effect seam; it is not a claim that continuous effects or layers are complete.
