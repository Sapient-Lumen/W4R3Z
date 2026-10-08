# Validator facet smoke report

Rev0022 adds a correction-office validator facet and records a static smoke report for validator modules. The stable command remains `make lint`; the monolithic validator still owns the full release gate while facet modules gradually take over office-specific checks.

This is a refactor, not a weakening of validation.

