# Revision 0325 — X11-first datacube reshape and vault pass

## Summary

Revision 0325 makes the repo's product truth explicit:
VHK is now framed as an **i3/X11-first desktop automation engine + future studio**.
The active story is narrowed around a **session-bound long-lived runtime**,
**ad hoc CLI support**, **recorder/cleanup/replay**, and **private-LLM-authored
macro workflows**.

Wayland/portal/app-native work is preserved, but demoted out of the active
headline datacube and into the vault/historical lane.

## Code changes

- no live runtime code paths were removed in this pass
- vaulting is currently a **repo-shape/documentation** demotion, not a code-pruning pass

## Docs

- rewrote `README.md` around the X11-first product statement
- added `docs/DATACUBE_2026.03.19_X11_FIRST.md`
- added `docs/DECISION_2026.03.19_X11_FIRST_PRODUCT.md`
- added `docs/DECISION_2026.03.19_RUNTIME_AND_LLM_CONTROL.md`
- added `docs/ROADMAP_2026.03.19_X11_FIRST.md`
- added `docs/VAULT_POLICY_2026.03.19.md`
- added `vault/README.md`
- moved portal/Wayland/app-native research docs into `vault/docs/`
- left forwarding stubs in `docs/` for the moved documents

## Tests

- `python -m compileall -q src/vhk tests`
