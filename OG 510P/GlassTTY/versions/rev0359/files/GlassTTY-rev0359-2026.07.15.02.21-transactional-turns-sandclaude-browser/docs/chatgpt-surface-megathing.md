# ChatGPT surface inspection tools

The cube now has two local-only DevTools console inspectors for the live
`chatgpt.com` surface.

- `tools/chatgpt-surface-capsule.js` is the small paste-first tool. Use this
  when the console, chat, or browser makes it annoying to move a large report.
- `tools/chatgpt-surface-megathing.js` is the full structural inspector. Use it
  when a complete selector-drift fixture is needed.

Both tools avoid network writes, storage reads, prompt submission, `eval`,
`new Function`, and script-tag injection. Package verification fails if either
console tool contains U+2028/U+2029 separators, known CSP-hostile constructs,
or lines above the paste-safe limit.

## rev0329 export-hardening notes

The first paste failed before inspection because rendered source was wrapped
inside JavaScript strings/selectors. The rev0328 tool fixed that. The next live
run reached `schema_version: 2`, created the report object, and stored the JSON
on `window`, but Firefox/DevTools did not auto-copy the full JSON. rev0329 keeps
the full report and adds a smaller capsule export path.

The megathing now emits and stores:

```js
window.__GLASSTTY_CHATGPT_SURFACE_REPORT__
window.__GLASSTTY_CHATGPT_SURFACE_REPORT_JSON__
window.__GLASSTTY_CHATGPT_SURFACE_CAPSULE__
window.__GLASSTTY_CHATGPT_SURFACE_CAPSULE_JSON__
```

It also installs fallback helpers:

```js
__GLASSTTY_PRINT_SURFACE_CAPSULE__()
__GLASSTTY_PROMPT_SURFACE_CAPSULE__()
__GLASSTTY_COPY_SURFACE_REPORT__('capsule')
__GLASSTTY_COPY_SURFACE_REPORT__('full')
__GLASSTTY_DOWNLOAD_SURFACE_REPORT__('capsule')
__GLASSTTY_DOWNLOAD_SURFACE_REPORT__('full')
```

The capsule tool stores:

```js
window.__GLASSTTY_CHATGPT_SURFACE_CAPSULE__
window.__GLASSTTY_CHATGPT_SURFACE_CAPSULE_JSON__
```

and installs:

```js
__GLASSTTY_PRINT_SURFACE_CAPSULE__()
__GLASSTTY_PROMPT_SURFACE_CAPSULE__()
__GLASSTTY_COPY_SURFACE_CAPSULE__()
__GLASSTTY_DOWNLOAD_SURFACE_CAPSULE__()
```

## Recommended run path

1. Open `https://chatgpt.com/` or an existing `https://chatgpt.com/c/...` chat.
2. Open DevTools / F12.
3. Paste `tools/chatgpt-surface-capsule.js` first.
4. Copy back the line beginning with:

```text
GLASSTTY_SURFACE_CAPSULE_JSON=
```

If that line is hard to copy, run one of the fallback helpers above. After the
capsule looks useful, run `tools/chatgpt-surface-megathing.js` for a complete
fixture.

## Privacy defaults

By default, message and composer text are not sampled. The full report records
text length and hashes so selector behavior can be debugged without exposing
chat content. UI labels and placeholders may appear because they distinguish
Send from model/tools/search/upload controls.

Optional samples can be enabled before running the megathing:

```js
window.GLASSTTY_SURFACE_INSPECTOR_OPTIONS = {
  includeMessageTextSamples: true,
  includeEditableTextSamples: true,
  includeGenericTextSamples: true
};
```

Only enable those options in a throwaway or already-redacted conversation.

## Report audit

Save a capsule line or full JSON report and run:

```bash
python scripts/chatgpt-surface-report-audit.py path/to/surface.json --pretty
```

The audit checks host, route posture, prompt/send candidate availability,
explicit author-role nodes, and latest-turn witness availability. It is a quick
preflight before spending time on a live checkpoint proof attempt.
