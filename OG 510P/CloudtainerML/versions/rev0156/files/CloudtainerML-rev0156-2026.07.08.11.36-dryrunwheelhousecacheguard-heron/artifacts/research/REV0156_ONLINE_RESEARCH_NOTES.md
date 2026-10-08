# Online research notes — REV0156

Status: `pass`  
Promotion allowed: `false`

- Hugging Face Hub docs say env vars are read at `huggingface_hub` import time and define the cache/offline controls used by this runner. Source: https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables
- The same Hub docs state `HF_HUB_OFFLINE=1` prevents Hub HTTP calls and note that `HF_HUB_DISABLE_SYMLINKS=1` can duplicate or move huge files into snapshot directories. Source: https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables
- Transformers docs state offline use requires downloaded/cached files ahead of time and show local-directory `from_pretrained(..., local_files_only=True)`. Source: https://huggingface.co/docs/transformers/en/installation

Implementation consequence: REV0156 fixes the one-command bootstrap dry-run path, adds optional wheelhouse/no-index runtime bootstrap, and hard-gates the cache duplication footgun before a large TinyLlama snapshot is materialized.
