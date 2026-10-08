# Text Layout & Shaping Conformance Kit fixtures

This pack freezes the receiver-facing artifact surface for `textlayoutkit`.

## Schemas
- `manifest.schema.json` — `textlayoutbundle` manifest contract.
- `layout-case.schema.json` — stable semantic request model.
- `layout-profile.schema.json` — pinned Unicode/data/policy interpretation contract.
- `fontset-lock.schema.json` — pinned font and fallback provenance.
- `corpus-import.receipt.schema.json` — normative/curated corpus import receipt.
- `backend-capability.receipt.schema.json` — runner/backend truth surface.
- `decision-origin.receipt.schema.json` — where important decisions came from.
- `font-resolution.receipt.schema.json` — what fonts actually resolved at runtime.
- `layout-output.schema.json` — normalized semantic layout IR.
- `layout-diff.report.schema.json` — semantic diff report.
- `diagnosis.report.schema.json` — likely failure-family explanation.

## Scenarios
- `thai_emoji_wrap_upgrade/` — Unicode-data and break-policy drift with emoji/ZWJ content.
- `arabic_latin_bidi_fallback_regression/` — bidi/fallback/measurement interaction drift.
- `cjk_unknown_lang_linebreak_policy/` — same text under distinct interpretation profiles (`unicode_default` vs `css_text_like`).
