# Product plan — Safety Contract Consumer Kit, authority/coverage/semantics refinement (2026-03-23)

## Why this refinement is worth doing

The std-contracts goal now makes a two-lane future explicit:

- the same contract substrate should support opt-in runtime checking,
- and external tools should be able to retrieve annotated contracts.

The ecosystem around `verify-rust-std` makes a broader multi-lane future visible as well.
A consumer crate that only snapshots contracts but cannot say which clauses were consumed by which tool/mode is still too weak for real review.

## Main `0.1` refinement

Keep the earlier snapshot, diff, runtime-check, receipt, and bundle ideas.
Add three more first-class artifacts:

- `contract-authority.receipt.json`
- `consumer-coverage.matrix.json`
- `semantic-lane.report.json`

## What `0.1` should classify now

### `contract-authority.receipt.json`

This is the compact answer to:

> “Where did these contract clauses come from?”

It should classify at least:

- subject,
- contract snapshot id,
- clause id,
- authority kind,
- source location,
- extraction route,
- normalization notes,
- and authority confidence.

Good initial authority kinds:

- `compiler_native_attribute`,
- `imported_std_snapshot`,
- `tool_specific_annotation`,
- `manual_contract_note`,
- `derived_runtime_assertion`.

### `consumer-coverage.matrix.json`

This is the compact answer to:

> “Which consumer or mode actually used which clauses?”

It should classify at least:

- consumer id,
- semantic lane,
- clause set or clause ids,
- coverage status,
- import route,
- excluded clauses,
- and short caveats.

Good initial coverage statuses:

- `full_for_lane`,
- `partial`,
- `abstracted`,
- `ignored`,
- `manual_review_required`.

### `semantic-lane.report.json`

This is the compact answer to:

> “What kind of result are we looking at, and what does it still not mean?”

It should classify at least:

- consumer id,
- lane kind,
- claim class,
- boundedness/assumption notes,
- soundness caveats,
- target/config scope,
- and bridge notes.

Good initial lane kinds:

- `runtime_checks`,
- `bounded_model_checking`,
- `deductive_verification`,
- `refinement_typing`,
- `separation_logic`,
- `manual_contract_review`.

## Recommended proving grounds

### std-contract source + Kani runtime/proof split

Use one tiny function whose contracts are imported from a standard-like attribute surface and then consumed in two Kani-shaped modes:

- runtime-check-style harnessing,
- and proof/stubbing-style abstraction.

This proves that one consumer can already have multiple semantic lanes.

### `verify-rust-std` plurality proving ground

Use the accepted-tool list as the simplest public proof that one contract corpus can serve multiple tools without implying uniform clause coverage.

### cross-tool caveat proving ground

Use Flux / Creusot / VeriFast as examples of clearly different semantic styles.
Do **not** pretend to translate all of them in `0.1`.
Instead, make the semantic-lane report the first-class honesty mechanism.

## Suggested workspace split after this refinement

- `contracts_consumer_model`
- `contracts_consumer_extract`
- `contracts_consumer_authority`
- `contracts_consumer_coverage`
- `contracts_consumer_semantics`
- `contracts_consumer_runtime`
- `contracts_consumer_pack`
- `cargo-contracts-consume`

## `0.1` adoption story after refinement

1. maintainer extracts one contract snapshot,
2. tool records clause authority and normalization route,
3. maintainer runs one or more consumer lanes,
4. tool emits consumer coverage and semantic-lane reports,
5. `doctor` warns when a bundle claims “verified” without naming the semantic lane or clause coverage gaps,
6. `pack` exports one portable bundle with authority, coverage, semantics, runtime results, and diffs together.

That is still compact enough for a real crate, but much closer to the hidden review contract other people actually need.
