# rev0059 patch-layer attribution and split-bundle independence gate

rev0059 continues from rev0058 without opening a new private packet. The revision keeps the strict/front lane frozen at seven production-gated maintainer packets and adds a layer-attribution gate for the selected strict/front patch stack.

## Why this revision exists

rev0057 generated a lane-specific combined selected-stack patch. rev0058 proved that those combined patch files apply cleanly and preserve the fixed-regression gates. rev0059 splits the same selected stack into four reviewer-facing filing-bundle patches and checks two properties that were not explicit before:

1. **Attribution:** each packet's fixed regression is satisfied by its intended bundle patch.
2. **Independence/necessity:** when every other bundle patch is applied but the target bundle patch is omitted, the target fixed regression remains nonzero as expected.

This is an archived-source proof against the uploaded `Nicotine-source(1).zip`, not live-current filing proof.

## Source bundle used

```text
source zip: /mnt/data/Nicotine-source(1).zip
source zip sha256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
lanes: github-tag-3.3.10; github-branch-3.3.x; github-branch-master
```

## Split bundle patches

rev0059 creates 12 bundle patch files:

```text
3 archived source lanes × 4 filing-bundle patches = 12 patch files
```

The four bundle patches are:

```text
U-123
PB-01
SEARCH-RESP-SOURCE-ADMISSION
SEARCH-RESP-PARSER-BUDGET
```

The generated patches are under:

```text
handoff/rev0059/patches/<lane>/
```

## Verification summary

```text
bundle patch files: 12
bundle patch file-hash rows: 15
bundle patch roundtrip rows: 48/48 pass
attribution rows: 42/42 pass
split-bundle stack rows: 21/21 pass
new private packets: 0
fresh current checkout completed: no
```

## Attribution scenarios

For every packet and lane, rev0059 records two attribution cases:

```text
target-bundle-only:
  apply only the intended bundle patch and run the packet's fixed regression;
  expected rc = 0.

all-except-target-bundle:
  apply all other bundle patches while omitting the intended bundle patch;
  expected rc = nonzero.
```

The all-except rows intentionally count expected failing regressions as a **passing gate** when the observed return code is nonzero. This confirms that unrelated patches are not silently satisfying the target regression.

## Stack compatibility

After attribution, rev0059 applies all four split bundle patches together and reruns all seven fixed regressions on each source lane:

```text
3 source lanes × 7 fixed-regression gates = 21/21 pass
```

This demonstrates that the split patches remain stack-compatible after being decomposed from the rev0057/rev0058 combined patch file.

## Primary data files

```text
data/rev0059_bundle_patch_manifest.csv
data/rev0059_bundle_patch_file_hashes.csv
data/rev0059_bundle_patch_roundtrip_matrix.csv
data/rev0059_bundle_attribution_matrix.csv
data/rev0059_bundle_stack_regression_matrix.csv
data/rev0059_bundle_attribution_summary.csv
```

## Helper

```bash
python tools/probe_rev0059_patch_layer_attribution.py --source-zip /mnt/data/Nicotine-source\(1\).zip
```

The default helper validates the recorded rev0059 gate, the uploaded-source identity, inherited handoff manifest, and package hygiene.
