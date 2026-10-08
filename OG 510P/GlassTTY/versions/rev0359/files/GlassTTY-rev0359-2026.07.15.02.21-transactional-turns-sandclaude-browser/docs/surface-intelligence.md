# Surface intelligence (rev0354)

ChatGPT's UI changes without telling anyone. When it does, GlassTTY breaks — and
the failure looks like *your* bug. This wing exists so that a UI change becomes a
diagnosis instead of an evening.

## The problem with the old surface contract

The pre-existing `surface-contract-*` tooling asks: *"are the things I already
know about still there?"*

That question is necessary and structurally blind. It can never see a control
that did not exist when the contract was written — and **every ChatGPT change
that has ever broken this project arrived as something new**. A new model picker.
A new "Add files and more" button that scored as send. A nag dialog over the
composer. The contract can only report that a known signal went missing; it can't
tell you what replaced it, when it happened, or what to do next.

## What this wing adds

```text
probe    → inventory EVERY control on the page, classify each one,
           and report what it could not classify   (the oddity hunter)
snapshot → store it, so the UI has a history
diff     → what changed between two moments
triage   → which GlassTTY capabilities that change breaks, and how badly
repair   → a concrete replacement selector, applied live
```

## The commands

```bash
glassttyd surface-snapshot --promote     # record today's UI as known-good
glassttyd surface-triage --pretty        # what's wrong right now?
glassttyd surface-diff                   # baseline vs live
glassttyd surface-history                # when did the UI change?
glassttyd surface-watch --interval 300   # early warning: alert the moment it drifts
glassttyd surface-repair --apply         # fix it, live, without a rebuild
glassttyd surface-overrides              # what patches are currently in force?
```

And the one you'll actually use:

```bash
glassttyd ask "hello" --diagnose
```

## Auto-diagnosis: the payoff

A failed turn used to be a dead end — *"submit was blocked"*, by what? Now the
failure itself triggers a live probe, a diff against the last known-good surface,
and a correlation between the two:

```console
$ glassttyd ask "hello?" --diagnose
[glassttyd] diagnosis: surface-drift-blocking
[glassttyd] likely cause: submit was refused because the send control no longer
                          matches the expected surface
[glassttyd]   [critical] capability-lost: a prompt can be staged but never sent
[glassttyd]   [critical] anchor-substituted: the adapter is about to act on a node
                          it did not expect; this is how a wrong click happens
[glassttyd]   [critical] regression: 'submit_prompt' worked in the baseline and does not now
[glassttyd]   repair (confident): send -> [data-testid="composer-send-v2"]
[glassttyd]   next: apply repair (glassttyd surface-repair --apply)
```

Not *"something changed"*. **"Your submit did nothing because the send button is
now `[data-testid=composer-send-v2]`, and here is the fix."**

## Repair without a rebuild

When ChatGPT moves a control, the honest options used to be (a) ship a new
extension build, or (b) stay broken until someone does. Neither is acceptable for
a tool you use daily.

So the adapter consults a **runtime override** before its compiled selectors:

```bash
glassttyd surface-repair --apply    # writes the override into extension storage
glassttyd ask "hello"               # works immediately — no rebuild, no reload
```

Overrides live in `chrome.storage.local`, so they survive reloads and apply to
every ChatGPT tab at once. Fold them into the adapter when convenient; until
then, you are not blocked.

### The override is a hint, not a bypass

This is the load-bearing safety property. An overridden node still has to be
visible, still has to be a real control, and still has to pass the same send-intent
scoring that rejects the "Add files" decoy. **A wrong override degrades to the
normal search; it can never make GlassTTY click something it would otherwise
refuse to click.** There is a test for exactly this
(`test_a_wrong_override_cannot_make_a_broken_tab_pretend_to_work`).

### And a repair is never proposed unless it is *identified*

An early version of the repair scorer confidently proposed
`send -> #prompt-textarea` — the text editor itself — because it was an unknown,
visible thing sitting in the composer. A repair engine that can tell the adapter
to click the text box is worse than no repair engine at all.

So the rules are now hard:

- a send candidate **must** be a real control (`button`, `role=button`, `type=submit`);
- anything that looks like attach/upload/dictate/model-picker is **disqualified**, not merely penalised;
- `confident` requires the candidate to be **positively classified** as the role it replaces — outscoring a bad field is not the same as being right.

When the real send is gone and only a decoy remains, GlassTTY proposes **nothing**
and stays broken. That is the correct answer.

## Rehearsing a drift before it happens

You cannot test drift resilience by waiting for OpenAI to break something. So the
mock tab can *become* a drifted ChatGPT on demand:

```bash
glassttyd surface-scenarios              # list them
glassttyd mock-tab --drift send-renamed  # then run ask/triage/repair against it
```

| scenario | what it simulates |
|---|---|
| `send-renamed` | send still works, but its id/testid changed |
| `send-removed` | the send control is gone entirely |
| `decoy-send` | send is gone and an "Add files" control sits in its place |
| `composer-removed` | the prompt editor is gone |
| `nag-dialog` | a modal covers the page; submit "works" and nothing generates |
| `rate-limit-banner` | an alert banner is up and generation never starts |
| `new-composer-control` | an unrecognised new control appears in the composer |
| `no-generation-signal` | the page stops reporting a lifecycle; the engine must fall back |

Each scenario changes what the probe **sees** *and* how the tab **behaves** —
behaviour is derived from the same capability map the probe reports, so the mock
can never look broken while secretly working. A diagnosis is graded against a real
failure, not a fake one.

This is also how you develop *ahead* of a change: when you see something new in
ChatGPT, add a scenario, watch the wing fail to handle it, then fix it.

## The oddity hunter

The probe classifies every control against a role atlas (send, stop, continue,
attach, dictate, model-picker, tools, …). Anything it cannot name in a
load-bearing region is reported as an **oddity**:

- an **unknown control in the composer** — this is how a new picker, a new mode
  toggle, or a new decoy send button first appears, *before* it breaks anything;
- an **open modal dialog** — likely intercepting your clicks;
- a **live/alert region** — often a rate limit or an error notice.

`surface-watch` turns this into an early-warning system: it catches a UI change
before it silently ruins a long `run`.

```bash
glassttyd surface-watch --interval 300 --json >> surface-log.jsonl &
```

## Keeping the atlas honest

When the wing reports an unknown composer control, that is a request for one line
of work: add the control to `ROLE_ATLAS` in
`extension/src/adapters/surface-probe.ts`. Each addition makes the next drift
quieter — the atlas is how the tool *learns the UI over time*, and the history
store is the record of that learning.
