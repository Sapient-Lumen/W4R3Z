# rev0084 focused validation

- focused pytest subset: PASS (`6 passed`)
- Python compile check: PASS
- extension typecheck: PASS
- extension build: PASS
- archive audit saved: `archive-audit.json`
- real temp-root marker-survival proof: after `import-archive`, a later raw `python -m playwright install chromium` still left `chromium-1208` visible in `install --list`; the install itself still failed here on FFmpeg DNS, which is preserved in `marker-survival-install.stderr`
- packaged zip verification: PASS
