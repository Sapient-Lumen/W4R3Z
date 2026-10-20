# Contributing to IoTox

IoTox is at its founding boundary. Changes should keep the product's claims no stronger than its
executable evidence and preserve the separation between friendship, transport, authorization, and
durable effects.

## Development loop

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
ctest --preset gcc-debug --output-on-failure
```

Warnings are errors. Add or update tests with behavior changes. Security-sensitive changes should
also update the threat model and, when they establish a lasting constraint, add an ADR under
`docs/decisions/`.

The independently buildable `components/toxsync` line has its own test registry. Until its newer
core is reconciled with the IoTox rev0015 foundation, changes must not imply that it is linked into
the default `iotox` product.

## Before opening a change

- Run the relevant CTest preset.
- Do not commit identities, savedata, ledgers, command stores, runtime trees, or received files.
- Keep generated build trees and fetched dependencies outside version control.
- Explain the evidence boundary for network, cryptographic, and durability claims.

By submitting a contribution, you agree that it may be distributed under the project's MIT
License and that you have the right to provide it under those terms.
