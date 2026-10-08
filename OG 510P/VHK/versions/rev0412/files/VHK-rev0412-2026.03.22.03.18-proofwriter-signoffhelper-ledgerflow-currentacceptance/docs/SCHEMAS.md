# JSON Schemas + Editor Autocomplete

VHK's YAML files (`project.yaml` and `macros/*.yaml`) are backed by pydantic
models. The CLI can generate JSON Schemas so editors can validate and autocomplete
your files.

## Generate schemas for a project

```bash
vhk schemas ./my_project --patch-modelines
```

This writes:

- `schemas/vhk_project.schema.json`
- `schemas/vhk_macro.schema.json`

Optionally, it also writes `.vscode/settings.json` with `yaml.schemas` mappings
and injects the `# yaml-language-server: $schema=...` modeline into YAML files.

## Print a schema (stdout)

```bash
vhk schema --kind macro > vhk_macro.schema.json
vhk schema --kind project > vhk_project.schema.json
```

### Draft compatibility

The default `--draft 7` output is intended to work with the popular
yaml-language-server ecosystem.

If you prefer the raw pydantic output (uses `$defs`), use:

```bash
vhk schema --kind macro --draft pydantic
```
