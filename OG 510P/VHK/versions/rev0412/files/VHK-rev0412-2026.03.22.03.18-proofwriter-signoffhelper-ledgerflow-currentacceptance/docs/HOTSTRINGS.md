# Hotstrings (text expansion) via Espanso

VHK intentionally **does not** try to implement global keyboard interception itself.

- On **Wayland**, global key interception/injection is compositor-controlled for security reasons, and apps can't reliably “just grab” all keystrokes.
- On **X11**, it’s possible, but it’s still easy to get wrong (keyboard grabs, IME, focus races, etc.).

Instead, VHK treats hotstrings as a **project-level intent** that can be exported to a dedicated hotstring engine.

Today, the first supported exporter is **Espanso**.

## Why Espanso?

Espanso is a cross‑platform text expander driven by YAML match files. A match can run a shell command and inject its stdout as the replacement text (via the `shell` extension).

That’s a great fit for VHK:

- You type a trigger like `:sig`.
- Espanso runs `vhk run ... --print-return`.
- VHK prints the macro’s return value to stdout.
- Espanso injects it into the focused app.

This avoids brittle “simulate typing” approaches and works well for multi‑line expansions when using `force_mode: clipboard`.

## Project format

Add a `hotstrings:` section to your `project.yaml`:

```yaml
hotstrings:
  - trigger: ":sig"
    description: "Insert my email signature"
    macro: signature
    mode: return
    force_mode: clipboard
```

### Macro design

In `macros/signature.yaml`, return the text you want to insert:

```yaml
name: signature
steps:
  - type: Return
    value_expr: "\"Best,\\nJane Doe\\n(555) 555‑5555\""
```

`Return.value_expr` uses VHK’s expression language.

## Exporting to Espanso

Generate an Espanso match file:

```bash
vhk gen-espanso /path/to/project --out /tmp/vhk_project.yml
```

Then copy it into Espanso’s match directory (commonly `$CONFIG/match/`).

## Context-sensitive hotstrings

Espanso can scope *sets of matches* to a specific application using
**app-specific configurations** and **include rules**.

> Caveat: Espanso's app-specific configs are not yet supported on Wayland.

VHK supports this pattern via `hotstrings[].when`.

Example:

```yaml
hotstrings:
  - trigger: ":jira"
    macro: jira_link
    description: "Insert a JIRA link (only in Firefox)"
    when:
      class: Firefox
```

Generate an Espanso *package directory* (match/ + config/):

```bash
vhk gen-espanso /path/to/project --package-dir /tmp/espanso_vhk
```

Then copy the generated folders into your Espanso config root (or merge them),
and restart Espanso.

VHK now makes that package export more explicit about Espanso's config model:

- config files are prefixed by **specificity order** so more-specific filters sort earlier
- VHK generates **synthetic composite configs** when simple scoped filter sets can overlap cleanly (for example `class=Firefox` plus `title=Inbox`)
- those composite configs include the less-specific match files they subsume, so one active Espanso config can still expose all applicable VHK hotstrings
- the package now includes a local `README.md` and `pack.json` describing the generated precedence/include structure

## Forms (prompted expansions)

Espanso supports lightweight input forms. VHK can generate these when you set
`form_layout`.

```yaml
hotstrings:
  - trigger: ":hello"
    macro: hello
    description: "Prompt for a name and insert a greeting"
    form_layout: |
      Hello [[name]]
      Company [[company]]
```

VHK will parse the `[[field]]` placeholders and pass them into the macro as
initial vars (alongside `hotstrings[].vars`).

## Notes

- Hotstring macros should be **fast**. If a hotstring blocks on UI automation or waits, it will feel laggy.
- If you want a trigger that runs automation *without* inserting text, set `mode: side_effect`.

## Alternatives

- **AutoKey** is a popular X11 automation/hotstring tool with Python scripting, but (like many X11 automation tools) it doesn’t work properly on Wayland.

## Export honesty / linting

`vhk lint-project` now warns about a few hotstring-adapter mismatches before you generate any files:

- `ESPANSO_APP_SCOPE_WAYLAND` when the project asks Espanso for app-scoped hotstrings on a Wayland target
- `ESPANSO_SCOPE_EXPORT_GAP` when a hotstring `when:` selector uses fields Espanso cannot export as app/title filters
- `ESPANSO_SCOPE_COMPOSITE_CONFIG` when `vhk gen-espanso --package-dir` will need synthetic composite configs so overlapping scopes stay active under Espanso's one-app-config rule
- `AUTOKEY_SCOPE_APPROXIMATION_REQUIRED` / `AUTOKEY_SCOPE_EXPORT_GAP` when the same hotstring scope would be widened or dropped in the AutoKey/X11 adapter lane

Treat those warnings as a design review step: sometimes the right answer is still to export, but VHK now makes the lossiness explicit instead of burying it in generated artifacts.
