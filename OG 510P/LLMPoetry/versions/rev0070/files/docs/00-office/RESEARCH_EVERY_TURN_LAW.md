# Research every turn law

## Law text

Every LLMPoetry turn begins with a web research pulse. This applies to poem-making, refactoring, packaging, validation, discussion, evaluation, and housekeeping. There is no purely local exception inside the project.

## Enforcement added in rev0011

The law is now part of validation. A packaged revision should contain at least one pulse in `registries/research_entropy_ledger.json` whose `revision` matches `STATE.json` and whose `turn` matches `STATE.json.turn.last_completed`. The validator also checks that the pulse's source IDs exist in `registries/source_registry.json`.

## Why this exists

The web pulse is not only for facts. It is also an entropy valve. It interrupts the model prior with current nouns, live standards, source textures, bureaucratic forms, counterarguments, material measurements, dates, places, and ugly particulars.

## Allowed pulse modes

- **Authority pulse**: official, primary, peer-reviewed, archival, or standard-setting source.
- **Adversarial pulse**: critique, failure report, bias paper, skeptical review, or contrary example.
- **Source-health pulse**: checks whether a cited source, standard, law, dataset, or tool has changed.
- **Entropy pulse**: deliberately weird or concrete search used to disturb diction.
- **Receipt pulse**: quote-search, source capture, DOI/URL verification, or provenance check.

## Logging requirement

Every pulse must record query/source, access date, role, what changed, and whether it affected a poem, registry, validator, or only atmosphere. For packaged revisions, append to `registries/research_entropy_ledger.json`.

## Blocked browsing

If browsing is blocked by the host environment or explicitly disabled by the human, write `WEB-PULSE-BLOCKED`, state what could not be checked, and do not make currentness claims. Blocking the pulse does not silently waive the law.
