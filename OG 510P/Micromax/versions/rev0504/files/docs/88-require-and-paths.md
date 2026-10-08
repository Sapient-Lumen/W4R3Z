# `include` / `require` path resolution (rev64)

Micromax has small file-loading primitives:

- `include` `( "path" -- )` — load and eval a file
- `require` `( "path" -- )` — load once (deduped by resolved absolute path)
- `reload` `( "path" -- )` — load even if previously `require`d
- `unrequire` `( "path" -- )` — forget a previously `require`d file

## Search convention

For **relative** paths, Micromax resolves the first existing file from:

1. **directory of the calling source file** (best-effort via `vm.last_span`)
2. **current working directory**
3. host-provided `vm.load_paths` (Python embedding API)
4. `$MICROMAX_PATH` entries (split by `os.pathsep`)

Absolute paths are used as-is.

If no file is found, `include/require/reload` raise an error that includes a
short “searched:” preview of candidate paths.

## Examples

Relative to the current file:

```forth
\ In plugins/myplugin/init.mx
"lib/util.mx" require
```

With a global search path:

```sh
export MICROMAX_PATH="$HOME/.config/micromax/lib:$PWD/vendor"
```

```forth
"statusline.mx" require
```

## Embedding hooks

The Python host can set additional roots:

- `vm.load_paths.append("/some/root")`

This is intentionally a *host-owned* knob so different embeddings can choose
safe defaults.
