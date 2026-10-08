# Native messaging

The native host remains provider-neutral infrastructure used by the ChatGPT browser extension.

Install for the recommended local Chromium-family target:

```bash
./scripts/install-native-host.sh --target auto --extension-id auto
```


For deterministic target resolution during tests or unusual local installs, set `GLASSTTY_BROWSER_BIN` before running report/install commands:

```bash
GLASSTTY_BROWSER_BIN=/usr/bin/chromium ./scripts/install-native-host.sh --target auto --extension-id auto
```

The reporter still accepts an explicit CLI override when called directly:

```bash
python scripts/native-host-report.py resolve-targets --target auto --browser-bin /usr/bin/chromium --print-targets
```

The host message-size budget is still enforced. Oversized host-to-extension payloads spill to `GLASSTTY_HOME/state/fixtures/` with a compact browser-visible report.
