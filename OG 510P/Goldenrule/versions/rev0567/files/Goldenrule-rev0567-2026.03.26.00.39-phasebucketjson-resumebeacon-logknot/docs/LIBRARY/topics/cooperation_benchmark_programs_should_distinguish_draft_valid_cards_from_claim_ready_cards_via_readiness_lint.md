# Cooperation benchmark programs should distinguish draft-valid cards from claim-ready cards via readiness lint

Once the archive already has a machine-checkable schema, a scaffold, and a canonical renderer, one subtle loophole remains: a card can be **schema-valid** while still being unfit to carry an inheritor-facing claim.

That happens when the card still contains draft placeholders, unreviewed `TODO` text, or vacuous `not applicable` fields that do not say *why* the row is inapplicable.

So the benchmark program should distinguish two states explicitly:

1. **draft-valid**: the card is structurally valid against the schema;
2. **claim-ready**: the card is structurally valid *and* passes a small readiness lint that rejects unresolved placeholders and empty inapplicability language.

Why this belongs in the archive:

- `RS-GR-111` says benchmark documentation should follow a standardized structure, which supports machine-checkable validation but does not by itself guarantee substantive completion.
- `RS-GR-114` says machine-actionable metadata should be easy for both people and software to reuse, which points toward compact automated readiness checks rather than manual inheritor guesswork.
- `RS-GR-115` says standards-driven metadata templates benefit from quantitative and verifiable measures of whether descriptors meet community requirements, which supports a tiny local quality gate over compact cooperation cards.
- `RS-GR-116` says quality gates can turn raw evidence into promote/hold decisions, which supports keeping one explicit local distinction between a card that merely parses and a card that is ready to support a retained claim.

So the archive should not treat JSON-schema validity as the end of the story.
It should also ship one **small readiness lint** for compact cooperation cards.

Keep the lint compact and narrow:

- reject unresolved `TODO` placeholders;
- reject bare `not applicable` strings that do not explain why the row is inapplicable;
- keep the rules local and deterministic;
- let scaffold output remain draft-valid, while making claim-readiness an explicit second gate.

This gives future inheritors one tiny but important protection: a compact card can stay easy to scaffold, while the archive still refuses to mistake a half-filled draft for a claim-ready publication object.
