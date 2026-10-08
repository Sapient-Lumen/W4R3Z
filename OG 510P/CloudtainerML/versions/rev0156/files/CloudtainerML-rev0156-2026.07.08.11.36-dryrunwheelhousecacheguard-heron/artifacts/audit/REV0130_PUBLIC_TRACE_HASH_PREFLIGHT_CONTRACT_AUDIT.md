# Public trace hash preflight contract audit — REV0130

Status: `pass`  
Promotion allowed: `false`

## Errors

- none

## Interpretation

A valid safetensors header is useful structural evidence, but the live public trace must not advance to capture unless the pinned TinyLlama weight digest is checked on the same local snapshot that will be loaded. Rev0130 also separates long snapshot/download/hash work from the short generic probe timeout.
