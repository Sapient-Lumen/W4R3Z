# ChatGPT page-world rest probe

`tools/chatgpt-pageworld-restprobe.js` is a small DevTools console script for
facts a userscript sandbox may not expose in the same way. It is optional and
passive.

It prints:

```text
GLASSTTY_PAGEWORLD_REST_JSON={...}
```

The report includes page-world global key signatures, Next.js metadata summary,
React DevTools hook presence, sanitized resource timing, script nonce presence,
editing API support, and a DOM crosscheck for the prompt, role nodes, send
button, and composer-plus control.

The script does not read cookies or browser storage, does not send network
requests, and does not write or submit prompts. It is a fallback complement to
the Tampermonkey userscript, not the main capture path.
