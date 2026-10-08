# FT-0181 end-of-window readout disposition gate

A terminal live-window card can source only a bounded aggregate readout. The
readout can classify the window as stopped, rolled back, continuing within the
same ceiling, rerun narrower, quarantined, or no-change/trimmed. It cannot mutate
service records, public language, lifecycle state, custody, acceptance, or
closure.

Rev0301 chain:

```text
terminal card
→ owner-live-window-readout-brief
→ human-recorded owner-live-window-readout
→ owner-post-readout-action-brief
→ human-recorded owner-post-readout-action
→ wait until due_or_recheck_date
→ owner-post-readout-recheck
→ stop, or route actual new owner context through owner-field-next
```

The readout brief is a scratch-local execution bridge only. It validates the
terminal card and prepares state-matched command skeletons; it is not a readout,
not post-readout dispatch, not evidence, and not closure.

The post-readout action brief is also scratch-local. It validates the terminal
readout and prepares the dispatch command skeleton; it is not the dispatch, not
owner action, not a recheck, not post-readout context receipt, not evidence, and
not closure.

The disposition gate protects against turning an end-of-window summary into
evidence. It is a routing control only.

Metadata anchor: this gate is part of the real import evidence grade path, not a
closure shortcut.
