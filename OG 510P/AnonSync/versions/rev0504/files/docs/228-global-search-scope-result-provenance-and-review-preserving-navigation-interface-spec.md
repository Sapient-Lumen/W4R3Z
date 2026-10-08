# Global search scope, result provenance, and review-preserving navigation interface spec

## Purpose

The archive already had shell, navigation, and command-palette doctrine.
What it still lacked was one tighter interface contract for a simpler operator need:

> I want one search box that can find the thing I mean, tell me what kind of thing it is, and open it without losing proof context or starting a dangerous action by accident.

Current Resilio docs still make this seam concrete.
They still say search exists in the main view for folders/files, separately in the peer list, separately in license users, and on iOS only at the current subfolder level.
That means the operator still has to know *which pane* contains the right search affordance before they can even look.

AnonSync should not clone pane-bound search.

## Core decision

AnonSync should provide one **global search** that spans:

- subjects
- files
- peers / seats
- users / identities
- receipts / reviews
- capability envelopes and seats when relevant

Every result must declare:

- what object family it belongs to
- whether it is current state or historical receipt
- what scope filters are currently applied
- whether opening it preserves or discards current proof context

## Why this matters

Current Resilio behavior still leaves search fragmented by page family and platform.
That creates three avoidable problems:

- users must remember where to search rather than what to search for
- different object families have different affordances and result semantics
- opening a result can quietly drop the explanatory context that made the result meaningful

AnonSync should therefore keep one stronger rule:

> search is a navigation and interpretation surface, not just a text filter attached to whatever list happens to be open.

## Fixed result anatomy

Every global-search result row should show, in the same order:

1. **Label**
2. **Object family**
3. **Current vs historical posture**
4. **Scope / seat / subject context**
5. **Next action**

### 1) Label

Examples:

- `Subject: Tax Records`
- `Peer: Laptop-ED25519-7F2…`
- `Receipt: relay-cost override expired`
- `File: photos/2024/raw/IMG_1042.nef`

### 2) Object family

Possible values include:

- `subject`
- `file`
- `peer`
- `seat`
- `identity`
- `review`
- `receipt`
- `capability-envelope`

### 3) Current vs historical posture

Each row must say whether it opens:

- live state
- draft review
- closed receipt
- historical alias match
- mixed (current object with historical aliases)

### 4) Scope / seat / subject context

Show the minimum disambiguators needed to avoid wrong-click ambiguity:

- acting seat
- parent subject
- lane / queue when relevant
- alias match versus canonical label match

### 5) Next action

Examples:

- `Open live detail`
- `Open proof drawer`
- `Open closed receipt`
- `Open compare review`
- `Filter results further`

Search results should not be direct dangerous-action buttons.

## Main surface behavior

The shell search box should support:

- free-text lookup
- type filters like `type:receipt`, `type:subject`, `type:file`
- alias matches and canonical matches
- scoped searches like `within:subject`
- exact-handle jumps when known

Selecting a result should preserve review context when honest to do so.
If preserving current proof context would mislead, the product should say so before opening the new page.

## Review-preserving navigation rules

When a search result opens from inside a review or proof drawer, AnonSync should choose among three explicit behaviors:

- `open inline and preserve current review`
- `open side-by-side and preserve current review`
- `leave current review and open result as new focus`

The chosen behavior must be visible, not implicit.

## Object model implications

### Search result row

Fields:

- `search_result_row_id`
- `query_text`
- `matched_object_ref`
- `object_family`
- `match_kind` (`canonical`, `alias`, `historical`, `path`, `receipt-text`)
- `state_posture` (`live`, `draft`, `closed-receipt`, `mixed`)
- `scope_summary`
- `open_behavior`
- `recommended_action`

### Search session

Fields:

- `search_session_id`
- `query_text`
- `active_filters[]`
- `origin_surface`
- `preserve_context_mode`
- `result_refs[]`

### Search-open receipt

Fields:

- `search_open_receipt_id`
- `search_session_ref`
- `opened_result_ref`
- `context_preserved` boolean
- `context_transition_kind`
- `recorded_at`

## Explicit non-goals

AnonSync should not:

- require users to search separate panes for subjects, peers, seats, and receipts
- hide whether a result is live state or historical record
- let a search result silently bypass review surfaces for dangerous actions
- discard current proof context without warning

## Relationship to nearby specs

This spec narrows and operationalizes:

- `149-interface-shell-navigation-and-persistent-context-spec.md`
- `152-command-palette-bulk-review-and-apply-boundary-interface-spec.md`

Those documents already define shell and command-palette doctrine.
This one fixes the global-search contract so lookup remains truthful across object families and historical state.
