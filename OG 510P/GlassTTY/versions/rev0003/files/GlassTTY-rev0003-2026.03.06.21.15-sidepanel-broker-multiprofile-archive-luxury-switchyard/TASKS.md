# TASKS

## Next sharp tasks

- [ ] Load the unpacked extension into an isolated Chromium profile and record the real extension ID
- [ ] Install the native-host manifest for that extension ID
- [ ] Verify `python -m glassttyd.cli socket-status`
- [ ] Verify `python -m glassttyd.cli read-prompt --wait` on a live Claude tab
- [ ] Save one or more Claude DOM fixtures under `fixtures/claude/`
- [ ] Improve Claude output extraction beyond `main/article/[role="main"]`

## Short backlog

- [ ] Add `prompt.submit` CLI command
- [ ] Add a second adapter example
- [ ] Add adapter capability reporting to the side panel
- [ ] Add per-profile manifest install helpers
- [ ] Add Playwright smoke tests for the extension in bundled Chromium

## Things to watch

- transcript deltas may be noisy
- Claude selectors may drift quickly
- native-host path quoting can be annoying across environments
