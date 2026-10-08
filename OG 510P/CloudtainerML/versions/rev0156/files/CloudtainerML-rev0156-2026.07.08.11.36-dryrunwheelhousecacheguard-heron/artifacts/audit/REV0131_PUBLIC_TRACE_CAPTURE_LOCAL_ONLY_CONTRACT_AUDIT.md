# Public trace capture local-only contract audit — REV0131

Status: `pass`  
Promotion allowed: `false`

## Errors

- none

## Interpretation

This audit prevents a wasteful capture path: `ALLOW_DOWNLOAD=1` may be useful while preparing a snapshot, but the public evidence capture wrapper intentionally does not pass `--allow-download` to the Hugging Face loader. Therefore capture preflight must require the digest-verified local snapshot.
