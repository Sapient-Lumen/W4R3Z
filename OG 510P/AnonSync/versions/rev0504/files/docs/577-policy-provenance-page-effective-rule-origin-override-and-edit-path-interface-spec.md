# Policy provenance page — effective rule, override chain, and edit-path interface spec

## Purpose

Give the operator one reviewed answer to:

- what rule is effective right now
- where that rule came from
- what other candidate rules exist but are losing
- which surface is authoritative for changing it
- whether the visible control is truthful, shadowed, or descriptive-only
- what stronger claim the product must not let the operator make

This page is the policy-plane companion to control-surface grade, runtime profile, destination world, bind outcome, and delivery diagnosis pages.
It should appear whenever behavior can be shaped by more than one rule surface.

## Inputs

- seat / host identifier
- subject identifier (share, seat, network rule, cleanup rule, retention rule, control surface)
- effective rule summary
- rule scope (`global`, `folder`, `seat`, `runtime-profile`, `config-owned`, `policy-bundle`, `unknown`)
- origin chain, ordered strongest to weakest
- shadowed rules still present
- authoritative edit surfaces
- required restart / reload / reconnect conditions
- visibility posture (`fully-visible`, `partly-hidden`, `hidden-critical`, `descriptive-only-ui`, `unknown`)
- last mutation actor and surface if known
- strongest safe sentence
- stronger forbidden sentence

## Primary questions this page must answer

1. What rule is actually winning right now?
2. Where did it come from?
3. What other rules are present but losing?
4. Which surface is truly authoritative for changing it?
5. Will editing the visible control actually change behavior?
6. What stronger sentence is unsafe because provenance is still mixed?

## Layout

### A. Effective rule verdict strip

Fields:

- effective rule label
- origin label
- edit authority label
- strongest safe sentence
- stronger forbidden sentence
- next safest action

Example labels:

- `Folder rule active; no deeper override detected`
- `Power-user override shadowing visible toggle`
- `Config-owned rule; WebUI descriptive only`
- `Runtime-profile split; active store differs from expected seat`

### B. Rule origin chain card

Show a stacked chain, strongest first:

- winning rule
- shadowed rule(s)
- defaults beneath them
- missing / unknown hops

Each row should include:

- origin surface
- scope
- strength class
- editability from current surface

### C. Authority and edit-path card

Fields:

- authoritative surface now
- non-authoritative visible controls
- whether restart / reload / reconnect is required
- whether apply would change product mode

### D. Shadow and residue card

Fields:

- shadowed rules still stored
- future reactivation risk
- rules that only affect newly created subjects
- rules that will survive current apply

### E. Provenance sentence block

Three stacked lines:

- **What rule currently governs behavior**
- **Why that rule is in force**
- **What the visible surface must not imply**

Example:

- `Placeholder deletion is currently prevented on this share.`
- `A deeper override is active beneath the visible share row.`
- `The product must not imply that local placeholder removal will propagate as an ordinary delete.`

## Required interactions

- `Review override mutation`
- `Surface hidden overrides`
- `Jump to authoritative edit surface`
- `Export policy provenance receipt`

## Guardrails

- Never show a mutable-looking control without stating whether it is authoritative.
- Never flatten global, folder, power-user, and config-owned rules into one anonymous `setting` noun.
- Never hide surviving shadow rules just because a higher rule currently wins.
- Never imply that editing a visible toggle changes behavior when a deeper origin still governs.
- Never hide mode substitution (`config-owned`, `restart-required`, `new-runtime-store`) behind a successful save toast.

## Output

A reviewed provenance verdict that downstream pages inherit without re-deriving rule origin from scattered settings.
