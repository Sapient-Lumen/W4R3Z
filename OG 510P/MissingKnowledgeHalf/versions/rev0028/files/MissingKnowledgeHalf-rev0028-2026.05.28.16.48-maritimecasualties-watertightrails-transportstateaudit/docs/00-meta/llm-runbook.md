# LLM runbook

## Startup

Read `START_HERE.md`, `SURFACE-STATUS.json`, `REVISION-RECEIPT.json`, and `context-pack.json` before editing. Then read the narrow method document relevant to the requested move.

## During a revision

- Keep a small scope.
- State what is not being claimed.
- Prefer one well-supported record over ten weak records.
- Do not treat familiar examples as verified without sources.
- Update ledgers and receipt as part of the work, not as an afterthought.
- Run `make lint` before packaging.

## Source handling

When live source acquisition begins, every source pass should log:

- query or route used,
- sources opened,
- sources used,
- sources rejected and why,
- sources not reached,
- retrieval date,
- permanence token,
- copyability/sensitivity.

## Record handling

When adding a record, separate:

- what happened or was claimed,
- who claimed it,
- what source carries it,
- what the current status is,
- what would defeat or change the status,
- how it links to other records,
- what ethical cautions apply.
