# Validator facet refactor — rev0020

`tools/validate_surfaces.py` is still the single `make lint` entrypoint, but it
has become monolithic. Rev0020 begins a non-destructive validator refactor by
adding a facet registry and a first small module under `tools/validators/` for
review-packet checks.

This keeps the operational behavior stable while giving future sessions a path
to split checks by office: release identity, no-live-data guard, source custody,
claim lifecycle, claim workbench, source-family atlas, review packet operations,
public display, privacy/legal, audit/refactor, and schema/record-kind coverage.

No existing validator entrypoint was removed.
