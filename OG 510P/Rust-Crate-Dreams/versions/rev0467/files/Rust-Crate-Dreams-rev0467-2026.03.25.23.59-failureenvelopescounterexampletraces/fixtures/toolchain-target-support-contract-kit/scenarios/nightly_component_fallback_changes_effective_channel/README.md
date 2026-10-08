# Scenario: nightly component fallback changes the effective channel

The project asks for `nightly` plus an extra component. On the latest nightly for the host, that component is missing, so rustup falls back to an older nightly that contains it.
The support contract must keep the requested channel, effective toolchain, and component state separate.
