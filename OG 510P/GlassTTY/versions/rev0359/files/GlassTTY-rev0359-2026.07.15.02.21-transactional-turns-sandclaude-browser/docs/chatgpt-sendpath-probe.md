# ChatGPT sendpath probe

`tools/chatgpt-sendpath-probe.js` is a focused DevTools console probe for the
send path. It is retained as a narrow fallback now that the preferred capture
path is the Tampermonkey surface oracle.

It reports strict send candidates separately from blocked composer controls such
as upload, tools, voice, model picker, and `#composer-plus-btn`. Use it when the
full userscript drill is unnecessary or unavailable.

The probe is local-only, does not read cookies or storage, does not send network
requests, and does not submit prompts.
