# Regression fixture coherence refactor — rev0067

rev0067 adds a fixture-contract layer and deliberately keeps it separate from the adjacent gates.

## Split map

```text
rev0062 positive clean-room replay:
  proves copied kit can replay fixed regressions after patching extracted archived source.

rev0063 clean-room contract/tamper gate:
  proves the kit has required files and fails closed for tampered kit/source states.

rev0066 patch hunk/preimage gate:
  proves rev0059 split patch hunks match uploaded-source preimages and allowed file scope.

rev0067 regression fixture contract:
  proves copied clean-room tests and patches are byte-for-byte the intended artifacts, statically hygienic, runtime-backed by inherited clean-room evidence, and runner-isolated.
```

## Non-claims

rev0067 does not add a new private packet, does not expand any minimum claim, does not replace current-source checkout proof, and does not blend public path traversal work into the strict/front packets.

## Refactor rows

See `data/rev0067_fixture_contract_refactor.csv` for the row-level split.
