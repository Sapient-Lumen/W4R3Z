# Parser hold: Python-owned hostile-byte parsing

The parser hold lane records that parseguard and other hostile-byte decoders remain Python-owned. A native parser proposal is not accepted merely because the native runtime and dispatch lanes exist.

`parserhold.py` rejects digest drift, replay, rollback, same-sequence forks, previous-link mismatch, low diversity, and any native parser request touching untrusted bytes.

The current policy is conservative: native leaf kernels may compare already-bounded byte arrays, but they may not decide how hostile network bytes become typed protocol data.
