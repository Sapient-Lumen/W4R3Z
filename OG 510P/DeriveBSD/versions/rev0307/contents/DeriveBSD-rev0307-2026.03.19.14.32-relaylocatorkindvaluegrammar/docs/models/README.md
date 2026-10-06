# Models

This folder contains **tiny, finite models** used to sanity-check DeriveBSD state machines.

Rules of thumb:
- Keep models *small and finite* (TLC is an explicit-state checker).
- Prefer modeling **authority + state transitions**, not implementation details.
- A model belongs to an ADR/RFC if it is used to justify a decision.

Starter model:
- `docs/models/bootenv_switch.tla` + `docs/models/bootenv_switch.cfg` — a toy bootenv switcher model.
