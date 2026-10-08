# Data-driven macros

VHK v0.10 adds a small but useful "data table" slice:

- `ReadCsv(path, has_header=true)` loads rows into a variable
- `WriteCsv(path, rows_expr, append=false)` persists list-of-dicts or list-of-lists
- `ReadJson(path)` / `WriteJson(path, value_expr)` handle structured files
- `ForEach(items_expr, item_var, steps)` iterates lists/tuples/dicts
- text transforms (`RegexReplace`, `TrimText`, `SplitText`, `JoinText`) let macros clean data without shelling out

## Example

```yaml
name: greet_rows
steps:
  - type: ReadCsv
    path: data/users.csv
    out_var: rows
  - type: ForEach
    items_expr: rows
    item_var: row
    steps:
      - type: WriteFile
        path: logs/${row.id}.txt
        text: "Hello ${row.name}\n"
```

Because `row` is a dict, interpolation supports dotted paths like `${row.id}` and `${row.name}`.

## Notes

- `ForEach` over a dict sets `item_var` to the value. If you need the key too, set `key_var`.
- `JoinText` and `WriteCsv` use expression fields (`items_expr`, `rows_expr`) so they can consume lists/dicts already stored in variables.
- This is intentionally small. The next natural step is a higher-level Studio data-table panel and row-aware templates.
