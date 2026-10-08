# Rev822 installed runtime resources and startup refactor

This landing converts the riskiest rev821 audit finding from a note into working runtime behavior: a wheel or `pip --target` install can now open bundled help docs and load bundled default plugins outside a source checkout.

## What changed

- `pyproject.toml` now installs root `docs/*.md` under `share/micromax/docs`.
- `pyproject.toml` now installs bundled `plugins/core` and `plugins/capdemo` under `share/micromax/plugins`.
- `micromax_editor.resource_roots` centralizes runtime root resolution:
  - explicit `MICROMAX_DOCS` and explicit `--plugins` paths remain literal;
  - implicit docs default stays `./docs` when present, then falls back to installed `share/micromax/docs`;
  - implicit plugin default stays `./plugins` when present, then falls back to installed `share/micromax/plugins`.
- `Editor.docs_root()` now preserves the old cwd-relative default when no installed resource root exists, but can find bundled docs in a package install.
- `Editor.find_doc_path()` accepts the common repo-root spelling `docs/00-vision.md` against the installed docs root instead of requiring the user to know the internal `share/micromax/docs` path.
- `micromax_editor.startup` replaces duplicated headless/TUI startup code with one boot path for hostcalls, plugin loading, plugin-load messages, user init, capability refresh, and optional persistence loads.
- `micromax-editor --tui --help-doc TOPIC` now has a real TUI path rather than doing headless startup and then discarding the requested help doc.

## Boundary decisions

The fallback is deliberately only for implicit defaults. A user-provided `MICROMAX_DOCS`, a user-provided docs path, or an explicit `--plugins` value still means exactly that path. This avoids turning installed bundled resources into surprising precedence over a caller's configured workspace.

The installed docs are data files, not a script-readable filesystem escape. Editor commands and script hostcalls still use the default docs-root containment boundary from rev821; only the trusted CLI path can opt into arbitrary explicit markdown files.

## Regression

`tests/test_installed_runtime_resources.py` copies the source tree without stale `build/`, `dist/`, egg-info, caches, or pycs, installs it with `pip install --target`, changes to a directory with no `docs/` or `plugins/`, and checks that:

- `python -m micromax_editor --help-doc 00-vision --dump-screen ...` succeeds;
- `python -m micromax_editor --help-doc docs/00-vision.md --dump-screen ...` succeeds;
- `default_docs_root()` points at a root containing `00-vision.md`;
- `default_plugins_root()` points at a root containing `plugins/core/init.mx` and `plugins/capdemo/plugin.json`.

## Audit note

The local checkout had a stale `build/` tree that could mask source changes during local packaging probes. The new install regression copies a clean source tree before invoking pip, and the release packer already skips `build/`, `dist/`, egg-info, pycache, and archives. This is a small but important correction: package tests should prove the source, not whatever an old build directory happens to contain.
