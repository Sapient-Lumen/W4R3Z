# Public trace digest acceptance audit — REV0129

Status: `pass`  
Promotion allowed: `false`

## Errors

- none

## Warnings

- none

## Interpretation

This is a substance guard, not a new paperwork lane: public capture can only self-promote after the local or cached `model.safetensors` bytes match the pinned TinyLlama SHA-256, and the capture wrapper must not invoke network downloads. Structural safetensors parsing still catches fake/truncated files cheaply; digest acceptance closes the wrong-weight local snapshot gap while local-only capture avoids run-to-run network drift.
