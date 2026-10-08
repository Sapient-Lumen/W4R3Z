# Revision 0281 — kitty remote-control pack

This revision turns the first app-native protocol lane into a concrete export.

## Added

- `vhk gen-kitty-pack`
- `src/vhk/project/kitty_pack.py`
- `tests/test_kitty_pack_cli.py`
- planner command wiring so kitty-targeted app-native lanes now point at a real pack

## What the new pack writes

- `vhk.kitty.routes.yml` — reviewable route catalog for kitty-targeted `TypeText` routes
- `vhk.kitty.commands.json` — machine-readable command ledger and skipped-route list
- `bin/*.sh` — thin wrappers around `kitten @ send-text --match ... --stdin`
- `README.md` — operator-facing explanation of assumptions and limits

## Design stance

This pack stays deliberately conservative:

- it only exports macros that already target kitty and contain `TypeText`
- it currently needs explicit title/title-regex selector evidence to generate an honest kitty `--match`
- class/app_id-only kitty routes are recorded as skipped instead of being widened into folklore
