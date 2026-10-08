# 0001 — System context

## Intent

Establish the first stable shape of the AnonSync system before protocol details harden.

## Proposed layers

1. **sync core**
   - manifests
   - chunking
   - reconciliation
   - scheduling
   - conflict handling

2. **identity and capability layer**
   - peer identity
   - folder capabilities
   - invite objects
   - local trust decisions
   - key persistence

3. **transport providers**
   - bundled `i2pd` + SAM adapter
   - bundled tor-daemon provider
   - mixed-mode routing strategy
   - future test transports
   - future Arti provider

4. **runtime orchestration**
   - config loading
   - child-process lifecycle
   - runtime checks
   - provider lifecycle
   - shutdown and recovery

5. **product surface**
   - CLI
   - logs/status
   - packaging
   - updater story
   - mobile ergonomics

## Main rule

The sync core must not directly depend on Tor or I2P implementation details.
