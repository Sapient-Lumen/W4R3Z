# Provider compatibility refactor

The cube has two provider-poison surfaces:

```text
src/i2p_dht_lab/providerpoison.py   # rev0011 legacy behavior-pinning surface
src/i2p_dht_lab/provider_poison.py  # canonical local memory/quarantine/refusal surface
```

The easy cleanup would be deletion. The safer cleanup is a visible compatibility plan.

`provider_compat.py` classifies public names as:

```text
reexport_canonical
adapt_legacy_name
keep_historical_only
needs_manual_decision
```

The current report has no active legacy imports, but it still has historical imports and adapter-worthy legacy names. That means the legacy module should not yet become a silent alias. The next cleanup should either write explicit adapters or move the historical tests to compatibility fixtures.
