# rev0092 focused validation

- baseline: `GlassTTY-rev0091-2026.03.17.16.25-deferredintent-secondarytruth-lazybroker-tern.zip`
- focus: native-lane diagnosis plus opportunistic persistent reconnect from explicit status/probe diagnostics
- passed: `npm run typecheck`, `npm run build`, `node extension/scripts/native-lane-check.mjs`, `python scripts/archive-audit.py --pretty`
- final package verification was run against the exact `GlassTTY-rev0092-2026.03.17.16.35-nativelane-selfheal-probetruth-avocet.zip` artifact after the validation summary and archive manifest were refreshed
- not proven: no fresh live Chromium/native-host/browser round-trip in this container; no full smoke/full pytest rerun for rev0092
