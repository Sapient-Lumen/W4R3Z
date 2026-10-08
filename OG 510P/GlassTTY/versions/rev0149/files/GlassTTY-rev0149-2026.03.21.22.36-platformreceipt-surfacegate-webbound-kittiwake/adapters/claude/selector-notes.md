# Claude selector notes

## Bootstrap heuristics

Prompt candidates:
- `textarea`
- `[contenteditable="true"]`
- `[role="textbox"]`

Output candidates:
- `main`
- `article`
- `[role="main"]`

## Expectations

These are only first-pass heuristics. Real fixtures from Claude.ai should replace hand-wavy assumptions quickly.

## Breakage discipline

When Claude UI changes:
- capture a fixture
- update this file with what broke
- note whether the breakage was in input detection, output detection, or delta watching
