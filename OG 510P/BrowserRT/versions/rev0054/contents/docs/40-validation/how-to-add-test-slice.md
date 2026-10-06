# How to add a BrowserRT test slice

Revision: rev0028

## Checklist

1. Name one claim and one proof boundary.
2. Add a Manifest task in `test/manifest.json` with id, lane, areas, tags, size, isolation, flakiness, risk, estimate, timeout, inputs, outputs, capabilities, cache policy, and evidence.
3. Add Impact map coverage in `test/impact-map.json`.
4. Add or update `test/surface-inventory.json`.
5. Write an Artifact under `artifacts/validation/`, `artifacts/proof/`, or `artifacts/audit/` using the current `REV####` prefix.
6. Add docs with Non-claims in `docs/40-validation/` or the appropriate architecture lane.
7. Run the narrow `--id` first, then release.

## Manifest task

The manifest should make the slice understandable without reading the whole repo. Browser tasks use `parallelGroup: browser-process` and should not join broad release by default.

## Artifact

The artifact should state revision, status, observations, counts, trace/event evidence, and non-claims. It should be enough for a future session to know what was earned.

## Non-claims

Every slice must say what it does not prove. Non-claims are how BrowserRT keeps ambition from becoming overclaiming.

## Impact map

If editing the source or doc for a slice would not select its test, the slice is not integrated.
