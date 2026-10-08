# What the live surface report of 2026-07-11 taught us

An operator-captured Surface Oracle report from a real ChatGPT session (Firefox
149, `/c/…` plain chat, empty composer). It is the first ground truth this project
has had in a while, and it invalidated two shipped assumptions immediately.

## 1. The send button does not exist until you type

```
"#composer-submit-button"            count: 0
"button[data-testid=\"send-button\"]"  count: 0
"button[aria-label*=\"Send\" i]"       count: 0
```

On a **perfectly healthy page**. The oracle's own warnings even say so —
*"No strict send button found; this is expected when empty."* — and then the drift
contract returns `verdict: surface-drift-blocker` anyway, on the strength of
`strict_send_contract_mismatch`.

That is a false positive on a working page, and rev0354's triage inherited it
(`submit_prompt: Boolean(composer && send)` → `false`).

**Fix (rev0355):** capabilities are now tri-state — `true` / `false` / `null`.
`null` means *unknowable right now*, which is a different thing from broken and is
never reported as damage. `glassttyd surface-triage --probe-with-draft` stages a
harmless draft (never submitted, then restored) so send is actually rendered and
the reading is definitive.

This also closes a task that had been sitting in `TASK_QUEUE.md`:
*"Use the after-write strict send selector to finalize send scoring."*

## 2. Two thirds of the page's ids are garbage

```
[id^="radix-"]   count: 65
```

Including the composer's own effort pill, `#radix-_r_ds_` (text: "Pro"). Radix
generates these at runtime; they change on **every page load**.

rev0354's repair engine preferred `#id` above all other selectors, so it would
have written `#radix-_r_ds_` into a persistent override. It would have worked
once, then silently stopped matching — which is worse than never repairing
anything, because you believe it is fixed.

**Fix (rev0355):** volatile ids are blacklisted (`radix-*`, `:r7:`,
`headlessui-*`, `mui-*`, `react-aria-*`), anywhere in a selector — `button#radix-_r_ds_`
is exactly as worthless as `#radix-_r_ds_`. Structural paths (`div:nth-of-type(1) > …`)
are rejected too. A repair with no durable selector is never marked confident.

## 3. The composer's real furniture

Now in the role atlas, so it stops being reported as unknown:

| control | identity |
|---|---|
| attach | `#composer-plus-btn`, aria "Add files and more" |
| effort pill | `.__composer-pill`, text "Pro" (id is volatile — matched by class/text) |
| dictate | aria "Start dictation" |
| new chat | `[data-testid="create-new-chat-button"]` → now `glassttyd new-chat` |
| copy / feedback | `copy-turn-action-button`, `good|bad-response-turn-action-button` |
| turns | `[data-testid="conversation-turn-N"]`, `[data-message-author-role]` |

## 4. A fallback textarea exists

`textarea[name="prompt-textarea"]`, `display: none`, placeholder "Ask ChatGPT",
class `wcDTda_fallbackTextarea`. A second write path if ProseMirror ever moves.
Not used yet; worth remembering.

## 5. The prompt editor is stable

`#prompt-textarea` — a ProseMirror `div[contenteditable=true][role=textbox]`,
score 1.36. No change needed.

## Method note

Every one of these was found by *reading a capture of the real thing*. The drift
wing exists so this stops being a manual, once-in-a-while exercise: `surface-watch`
polls, `surface-history` records, and `--diagnose` correlates a failure with what
actually changed. But the atlas still only knows what it has been shown — so when
a new control appears, add it.
