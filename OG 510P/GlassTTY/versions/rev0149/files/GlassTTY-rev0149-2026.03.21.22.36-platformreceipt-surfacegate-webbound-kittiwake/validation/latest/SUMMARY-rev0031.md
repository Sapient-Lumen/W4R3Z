# rev0031 summary

- Added a browser-target watch lane in `scripts/cdp_inspect.py` using `Target.setDiscoverTargets`, so GlassTTY can preserve extension target lifecycle events over a bounded window instead of relying only on static snapshots.
- Focused tests passed for the new CDP watch path, the fixture-lab helpers, and release validation.
- Manual validation in this container proved a headless-new Chromium run where the browser-target watch observed a real `Target.targetCreated` event for the unpacked extension probe page; see `manual-service-worker-watch-cdp-rev0031.json`.
- This still does not prove any MV3 service-worker target, native-host socket availability, or a full live bridge round-trip in this container.
