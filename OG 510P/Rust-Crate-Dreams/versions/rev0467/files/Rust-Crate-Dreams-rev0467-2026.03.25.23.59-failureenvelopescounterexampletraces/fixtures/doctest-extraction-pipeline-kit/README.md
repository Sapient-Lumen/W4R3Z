# Doctest Extraction & Support Contract Kit fixtures

This fixture family is for `P-0455 Doctest Extraction & Support Contract Kit`.

Core artifact families:
- `doctest.manifest.json`
- `extraction-basis.receipt.json`
- `rewrite-lineage.receipt.json`
- `execution-mode.receipt.json`
- `docs-example-support.report.json`
- `grouping-comparison.report.json`
- `docs-example-drift.diff.json`
- `doctest-support-bundle.manifest.json`

Suggested fixture cases:
- hidden setup plus environment-specific harness rewrites
- nightly rustdoc JSON basis versus Markdown-fallback extraction authority
- merged vs standalone doctest execution
- host-run vs cross-target vs docs.rs-render-only support classes
- grouping or attribute drift without prose edits
- portable bundle inventory for issue/review handoff
