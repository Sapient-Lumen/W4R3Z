# docsrs_all_features_vs_minimal_default

A crate advertises a small recommended default scenario, but its docs.rs build turns on `all-features` and exposes extra integrations and API slices.

This fixture exists to force the pack to keep separate:

- the **recommended default** scenario,
- the **docs.rs documentation surface**,
- and the **matrix fidelity** of what was actually checked locally.

Expected outputs:
- `scenario_class = recommended_default` for the ordinary lane
- `docs_surface_changed` or `docs_only` notes for the docs.rs lane
- explicit origin receipts showing docs.rs metadata as the source of the wider surface
