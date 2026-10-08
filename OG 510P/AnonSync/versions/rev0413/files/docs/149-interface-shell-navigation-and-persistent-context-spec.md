# Interface shell, navigation, and persistent context spec

## Purpose

This document decides the stable frame for AnonSync.
The question is not merely `which pages exist?`
The question is:

> what interface shell must every projection preserve so operators do not reconstruct truth from scattered screens, hidden modals, or remembered support ritual?

`38-operator-workbench-interface-spec.md` names the page families.
This document fixes the shell that holds them together.

## Why this matters now

The current Resilio evidence is useful precisely because it is not caricature.
It shows a real product with a main view, a share dialog, desktop-only folder preferences, sync preferences, power-user preferences, configuration mode, and support pages that together explain the operator model.

AnonSync should not repeat that split.
A page hierarchy can be rich.
The shell must still feel like one product.

## Core decision

Every interactive AnonSync projection should preserve six conceptual regions:

1. **navigation chooser**  
   section rail, section tabs, or textual section selector
2. **scope strip**  
   acting seat, current subject family, current lane/filter, and any active baseline/exception context relevant to the page
3. **primary pane**  
   list, board, detail page, compare view, or plan/review surface
4. **proof drawer**  
   expandable evidence/explanation region tied to the currently selected card, row, or action
5. **action tray**  
   the next safe actions for the current page or selected rows, clearly separated from danger actions
6. **queue context**  
   lane placement, acknowledgement/snooze posture, and any active review/attention state for the subject

A projection may stack, collapse, or alternate these regions.
It may not silently drop their semantics.

## Default landing behavior

The default landing is intentionally conservative.
It should show:

- every `Now` item
- `Soon` items that are newly promoted or within the due horizon
- a collapsed `Quiet` summary with counts and one-line explanation

This is a deliberate answer to the noise question.
The default shell should not behave like a raw event firehose.
It should also not hide near-due truth behind an extra click.

## Navigation rules

### Top-level navigation

Top-level navigation follows the page catalog in `38-operator-workbench-interface-spec.md`.
The shell should keep the top level small enough that operators can predict where a subject will live.
It should not promote every object family into its own permanent first-tier tab.

### Cross-page transitions

When the operator moves between adjacent pages, the shell should preserve context if preserving it is still honest:

- current acting seat
- current subject or filter if the destination page still supports that scope
- currently open proof/report drawer target when the destination still references the same subject
- sort mode and lane filter

The shell should drop context when keeping it would be misleading, such as:

- jumping from one acting seat to a review flow whose main point is choosing a different acting seat
- moving from a current subject page to an older receipt page where fresh proof context would look falsely current
- moving from one subject family to an unrelated danger flow where the old filter would falsely imply relevance

## Deep-link rules

Every substantial page, report, review object, and receipt should have a stable deep-linkable handle.
The handle must survive:

- shell reload
- CLI-to-workbench handoff
- workbench-to-CLI copy/paste
- browser refresh in the local web projection

A deep link should restore at least:

- page family
- subject ID
- selected tab or subview where meaningful
- report/proof drawer selection when still valid

A deep link should never silently apply an action.
At most it may reopen a draft or staged review object.

## Search and command entry

The shell should offer one omnibox or command/search field that can:

- jump to a subject
- open a report
- open an explanation
- create a draft review flow
- invoke safe read actions

It should not become a hidden bypass around page context.
High-risk mutations may be started from the omnibox, but they should still open the relevant review object inside the normal shell.

## Projection mapping

### Wide GUI / local web

- navigation chooser in a left rail or top rail
- scope strip under the global header
- primary pane center
- proof drawer on the right or as an anchored expansion
- action tray beneath the answer strip or at the bottom edge of the primary pane
- queue context as chips/strip near the subject header or page header

### Narrow GUI / mobile-like web

- navigation chooser collapses into section switcher
- scope strip stays visible above primary content
- proof drawer becomes an in-page sheet
- action tray becomes a sticky bottom region or explicit action sheet
- queue context stays near the answer strip rather than disappearing into badges alone

### TUI / richer CLI summaries

- navigation chooser is a section selector or command namespace
- scope strip is a fixed header block
- primary pane is a table/card/text summary
- proof drawer becomes an expandable secondary section
- action tray is a labeled action block with safe/default action first
- queue context is rendered as lane/reason lines, not only colors or terse badges

## Things the shell should refuse

- modals that hide which subject is being acted on
- action sheets that omit proof freshness for risky work
- navigation that forgets the acting seat just when trust scope matters most
- summary boards that flatten queue reason and subject reason into the same vague badge
- page-local vocabulary that contradicts the global action grammar

## Result

The shell should make AnonSync feel like one inspectable product even when there are many pages, many reports, and many object families.
The operator should not need to ask:

- `which screen owns the truth?`
- `did I just leave the subject page and lose the evidence?`
- `why did this action button appear here but not there?`
- `is this still the same acting seat and the same review context?`

If those questions arise regularly, the shell is not doing its job.
