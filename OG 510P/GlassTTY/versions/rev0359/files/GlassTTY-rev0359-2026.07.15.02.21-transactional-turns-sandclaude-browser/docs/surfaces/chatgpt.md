# ChatGPT surface notes

Current live-surface lock, derived from the rev0331 Tampermonkey userscript
reports and preserved in `validation/latest/chatgpt-live-surface-contract-rev0335-2026.06.13.json`:

| Surface role | Current selector / signal | Notes |
|---|---|---|
| Route | `/c/<conversation-id>` or `/` with composer | Submit allowed only for plain-chat posture. |
| Composer | `#prompt-textarea` | Visible contenteditable `div`, role `textbox`, aria-label `Chat with ChatGPT`. |
| Fallback composer | hidden textarea, name `prompt-textarea`, placeholder `Ask anything` | Do not prefer it while hidden. |
| Strict send | `#composer-submit-button`, `data-testid="send-button"`, aria-label `Send prompt` | Preferred submit target after write/readback. |
| Blocked composer tool | `#composer-plus-btn`, `data-testid="composer-plus-btn"`, aria-label `Add files and more` | Must never be treated as send. |
| Assistant turns | `[data-message-author-role="assistant"]` | Prefer latest explicit assistant role by DOM order. |
| User turns | `[data-message-author-role="user"]` | Prefer latest explicit user role by DOM order. |

Selector policy:

1. Prefer explicit author-role nodes for reading turns.
2. Prefer the observed strict send button when present.
3. Require write/readback and plain-chat route posture before clicking send.
4. Record blocked composer controls in fixture metadata.
5. Do not click plus, upload, dictation, model/reasoning/tools, copy/edit,
   feedback, sources, download-app, or scroll-marker controls.
