# Public trace cache duplication guard audit — REV0156

Status: `pass`  
Promotion allowed: `false`

Guards two high-risk/wasteful operational edges before the first real TinyLlama trace: bootstrap dry-run must be safe/no-pip, and HF_HUB_DISABLE_SYMLINKS must not silently duplicate large Hub snapshot files unless the operator explicitly opts in.

## Errors

- none

## Warnings

- none
