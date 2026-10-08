# Support bundle transition

`python scripts/support-bundle-transition.py ...` moves one support-bundle manifest between queue states and keeps `bundle_status` plus `publication_decision.decision` aligned.

## Why this exists

Directory motion alone is too easy to misread. GlassTTY now treats support-bundle state changes as explicit queue actions rather than silent file moves.

## Command

```bash
python scripts/support-bundle-transition.py \
  --bundle claude-reference-chromium-live-rev0128 \
  --to-state published-ready \
  --why "live route/history bundle exists" \
  --publish-when "bundle is ready to execute into published state"
```

## States

- `candidate` — shaped enough to review
- `hold` — named evidence exists, but publication is intentionally blocked
- `published-ready` — reviewed and ready to execute into citable state
- `published` — citable support bundle; may appear on the published support surface

## Working rule

Use `published-ready` as the last review stop. Use `published` only after the bundle is deliberately executed into citable support truth.


## Fail-closed promotion

After rev0130, transitions into `published-ready` or `published` run through `support-publish-gate`. By default the transition stops if the gate fails or if the requested queue edge is not allowed. Use `--allow-failed-gate` only when you intentionally want an exception recorded in the transition receipt.

Every transition now writes a receipt under `validation/latest/support-bundle-transition/` and appends to `validation/support-bundle-transition-receipts.json`.
