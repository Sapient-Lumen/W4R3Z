# Setup pack

`vhk gen-setup-pack <project_dir>` is the first setup-aware generator built on
planner `setup_recipes`.

It closes a gap the repo had been documenting for a while:

- `setup_recipes` already described **what** an operator or author should do
- but they were still stuck inside planner JSON and prose
- there was no stable way to turn them into repeatable docs + scripts

The setup pack turns those recipes into generated artifacts under `docs/` and
`scripts/`. It also now folds planner `toolchain_choices` into a best-effort
package bootstrap lane so authors can see likely distro install commands next
to the higher-level recipe docs.

## Generated artifacts

By default the command writes:

- `docs/VHK_SETUP_GUIDE.md`
- `docs/VHK_SETUP_MATRIX.md`
- `docs/VHK_SETUP_PLAN.json`
- `scripts/vhk_apply_setup_recipes.sh`
- `scripts/vhk_verify_setup_recipes.sh`
- `scripts/vhk_install_toolchain_packages.sh`

## Why this exists

Linux-native automation rarely has a single universal installer.

Projects usually need a reviewable sequence such as:

- generate launcher/menu entrypoints
- stage WM/remapper snippets
- verify capability fit against the current session
- keep rollback notes visible while testing a new lane

The planner already knew those steps via `setup_recipes`, but authors still had
to manually translate them into shell history.

This pack makes setup more executable without pretending every recipe can be
fully automated.

## Script behavior

The generated scripts are intentionally conservative:

- they only auto-run strings that look like shell commands
- narrative validation/install notes stay in the docs instead of being executed
- apply/verify scripts accept `RECIPE_FILTER=<recipe-id>` to limit execution to
  one or more recipe ids
- the package bootstrap helper defaults to a dry run and only executes when
  `RUN_INSTALL=1` is set explicitly

Example:

```bash
vhk gen-setup-pack ./myproj
cd ./myproj
RECIPE_FILTER=launcher-entrypoint-install ./scripts/vhk_apply_setup_recipes.sh
RECIPE_FILTER=launcher-entrypoint-install ./scripts/vhk_verify_setup_recipes.sh
```

## Design goal

The goal is not a fake one-click installer.

The goal is to let planner-backed setup guidance become:

- reviewable
- repeatable
- shell-runnable where honest
- caveated where Linux session/tooling boundaries still require human judgment
