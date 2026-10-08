# Public trace hash preflight contract audit — REV0131

Status: `pass`  
Promotion allowed: `false`

## Errors

- none

## Interpretation

A valid safetensors header is useful structural evidence, but the live public trace must not advance to capture unless the pinned TinyLlama weight digest is checked on the same local snapshot that will be loaded. Rev0131 also ensures capture remains local-files-only even if ALLOW_DOWNLOAD=1 is set, and separates long snapshot/download/hash work from the short generic probe timeout.
