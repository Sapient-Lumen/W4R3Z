# Public trace live prompt manifest audit — REV0130

Status: `pass`  
Promotion allowed: `false`

Prompt manifest: `artifacts/prompts/REV0130_PUBLIC_TRACE_PROMPTS.txt`  
Prompt count: `2`

## Errors

- none

## Interpretation

A correct one-shot default is insufficient if the parent run wrapper exports PROMPT_MANIFEST to a missing path. The prompt manifest must be a single visible file consumed by the live capture command, or the real trace can fail after all earlier gates pass.
