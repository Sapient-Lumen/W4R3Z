# Scaffold macros

`vhk scaffold` is an **authoring helper**: it inserts *non-breaking* TODOs into a
macro so you can upgrade a raw recording into a robust automation script.

## Why scaffolding exists

Raw recordings often contain:

- **Fixed sleeps** (`Delay`) that become flaky as UI timing varies.
- **Absolute coordinate clicks** (`MouseClickAt`) that break when DPI/layout/
  window positions change.

Across mature automation ecosystems, the consistent recommendation is to wait on
**conditions** instead of sleeping:

- Selenium explicitly calls out explicit waits as loops that poll for a
  condition before continuing: https://www.selenium.dev/documentation/webdriver/waits/
- SikuliX tutorials show waiting for an image pattern with a timeout rather
  than sleeping: https://sikulix-2014.readthedocs.io/en/latest/tutorials/surveillance/surveillance.html

VHK already has the primitives (e.g. `WaitForImage`, `WaitForText`,
`WaitForWindow`, `ClickNeedle`). Scaffolding helps you **wire them in faster**.

## What it does

Depending on what it finds, scaffolding will:

- Add `comment:` hints to brittle steps.
- Insert disabled (non-executing) TODO stubs like:
  - `WaitForImage` before a long `Delay`
  - `ClickNeedle` before a `MouseClickAt`

The key idea: **your macro behavior does not change** until you enable the
inserted steps.

## Usage

### Scaffold a single macro

```bash
vhk scaffold macros/login.yaml --in-place
```

### Review mode (like code formatters)

`--check` exits non-zero if changes would be made.
`--diff` prints a unified diff.

```bash
vhk scaffold macros/login.yaml --check
vhk scaffold macros/login.yaml --diff
```

This mirrors common formatter UX such as Black's `--check` and `--diff`:
https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html

### Bulk scaffold a project

```bash
vhk scaffold-project . --out-dir macros_scaffolded
# or
vhk scaffold-project . --in-place
```

## Tips

- Prefer `ClickNeedle` over `MouseClickAt` by capturing a stable needle and
  (optionally) a click point via openQA-style metadata.
- Prefer `WaitForImage`/`WaitForText` over long `Delay` blocks.
- Keep regions tight for faster vision/OCR and fewer false matches.
