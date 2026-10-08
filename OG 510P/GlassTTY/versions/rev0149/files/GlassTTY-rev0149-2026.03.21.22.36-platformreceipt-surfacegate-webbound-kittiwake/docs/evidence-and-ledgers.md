# Evidence and ledgers

GlassTTY already has strong evidence instincts. This doc makes them canonical.

## Evidence families

- **state snapshot** — structured state at a point in time
- **probe capture** — bridge and browser diagnostics
- **fixture capture** — saved DOM/content interaction baseline
- **smoke run** — one workflow-oriented test attempt
- **support bundle** — compact artifact set that supports or falsifies a support claim
- **operator handoff** — packaged current-state narrative
- **operator attempt** — before/after story around one real command
- **comparison bundle** — diff between two relevant captures
- **release-gate artifact** — proof tied to a support-tier or release claim

## Ledger purpose

Ledgers should make it easy to answer:
- what evidence exists?
- what is the latest relevant artifact?
- what changed since last time?
- what should the next implementer inspect first?

## Evidence quality rules

- preserve links between artifacts
- preserve timestamps
- preserve relation to surface/workflow/lane
- preserve recommendation or next-action hints where possible
- preserve partial truth even when a run fails

## Support rule

A support claim without a named artifact ref should be treated as weak.
A support tier promotion without a named artifact family should be treated as incomplete.

## Where the artifact shapes live

Use `docs/evidence-catalog.md` and the templates under `docs/templates/` for:
- expected support-bundle contents
- release-gate checklist shape
- naming expectations

## Implementation guidance

New features should think about evidence at design time.
If a workflow exists but emits no durable evidence, support truth will stay weak.
