# Queue-governance lineage receipt page — policy origin, window scope, and visible-order trust

## Purpose

Emit one durable receipt after any serious queue-policy action or review.
The receipt must preserve what governed order, what scope that order actually covered, and what stronger sentence the product refused to make.

## Receipt fields

### Identity

- subject / share / transfer identifier
- timestamp
- actor / source of mutation or review

### Policy provenance

- current origin
- previous origin
- comparator in force
- inheritance status

### Scope truth

- active-window membership
- active-window ceiling status
- admitted / waiting / exception-bearing class

### Visible-order truth

- UI order class
- scheduler-order proof class

### Strongest safe sentence

Examples:

- `This share still inherits the global newer-first policy.`
- `This share is manually pinned to larger-first and no longer follows later global changes.`
- `This item is outside the active prioritized window.`
- `Visible list order is not proof of scheduler order.`

### Blocked stronger sentence

Examples:

- `this share has fully reset to default`
- `this file will download next`
- `the displayed queue is the executed queue`

## Use cases

The receipt must be durable enough for:

- later debugging
- policy-audit review
- explaining sticky `None`
- distinguishing active-priority scope from whole-backlog myth
