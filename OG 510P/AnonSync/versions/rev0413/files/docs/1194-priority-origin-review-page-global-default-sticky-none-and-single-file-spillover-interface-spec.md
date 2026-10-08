# Priority-origin review page — global default, sticky `None`, and single-file spillover

## Purpose

Review any operator action that changes queue-order policy origin.
This page exists because `default`, `manual`, `reset to none`, and `single-file send` are not the same contract.

## Review questions

1. Is the operator changing the global default, a specific share, or a bounded single-file send lane?
2. Has the share ever been manually altered before?
3. If the share is being set to `None`, does that mean `no local comparator` or only `sticky local none`?
4. Will this change spill into future shares and single-file sends?
5. What subjects remain unaffected?

## Required review outcomes

### Outcome 1 — live inherited default

Show this only when the subject has never been manually altered and therefore still tracks the current global default.

### Outcome 2 — manual share override

Show this when the share now has its own explicit comparator and future global changes will not retune it.

### Outcome 3 — sticky local `None`

Show this when a share was manually changed in the past and later set to `None`, but still remains outside future global-default propagation.
This is the most important anti-confusion state.

### Outcome 4 — global-default propagation

Show this when the operator changes `folder_defaults.transfer_priority` and the change will affect all still-inheriting shares and future new shares, including single-file sharing.

### Outcome 5 — single-file inherited lane

Show this when the queue policy comes from the global default because the send has no post-start per-transfer retuning surface.

## Review obligations

The page must show:

- current origin
- proposed origin
- propagation scope
- unaffected subjects
- spillover into new shares
- spillover into single-file sends
- blocked stronger sentence

## Mandatory language

Use language like:

- `This share still inherits the current global default.`
- `This share now carries its own local queue policy.`
- `Setting this share back to None does not restore future inheritance.`
- `Single-file sends will use the global default active at send start.`

Do not use language like:

- `Reset to default` unless future inheritance will in fact resume
- `No priority` if the more precise truth is `sticky local none`
- `Global` if the scope is only `new shares plus currently inheriting shares`
