# Install receipt

`python scripts/install-receipt.py --pretty` answers a narrow but high-value question: **is GlassTTY merely present on disk, or is it actually installed, registered, and live enough to blame runtime behavior instead of bootstrap drift?**

## Why this exists

GlassTTY has several distinct bootstrap layers:

- extension materialization (`extension/manifest.json`, side panel, service worker path)
- native-host registration (browser-specific manifest placement, extension ID allowlist, wrapper path)
- runtime state (broker socket, owner metadata, lock state)
- operator reachability (best known attach-ready profile and the next readiness action)

Before rev0125, those truths were scattered across `doctor.py`, `native-host-report.py`, and `readiness-report.py`. The install receipt turns them into one typed object and one freezeable artifact.

## What it reports

- `bootstrap.stage` — one concise stage such as `native-host-registration-missing`, `registered-runtime-idle`, or `runtime-reachable`
- `materialization` — extension/native-host assets that should exist on disk
- `registration` — recommended browser targets, ready vs missing manifests, mismatch details, and install commands
- `runtime` — broker socket / owner metadata state plus the current readiness next action
- `reachability` — whether the best saved profile is actually attach-ready

## Commands

```bash
python scripts/install-receipt.py --pretty
python scripts/install-receipt.py capture --output-dir validation/latest/install-receipt-capture
python scripts/install-receipt.py history --pretty
```

## Working rule

Use the install receipt before spending time on MV3 or adapter debugging. If bootstrap truth is still blocked at materialization or registration, runtime explanations are usually premature.
