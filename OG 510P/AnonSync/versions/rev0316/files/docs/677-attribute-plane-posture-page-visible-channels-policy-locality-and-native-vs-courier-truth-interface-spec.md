# Attribute-plane posture page — visible channels, policy locality, and native-vs-courier truth interface spec

## Purpose

The product needs one stable page that answers a small but load-bearing question:

> for this subject, what metadata channels belong to the meaning plane, and what kind of seat am I right now for those channels?

Without that page, `supported`, `synced`, or `xattrs on` stays too vague.

## Core decision

AnonSync should expose an **Attribute-plane posture** page for any subject whose meaning depends on metadata beyond ordinary file bytes.

The page must distinguish:

- channel set in scope
- policy source
- seat class per channel
- object families at risk
- strongest safe sentence

## Fixed page order

1. **Channels in scope now**
2. **Policy basis and locality**
3. **Seat class now**
4. **Object-shape consequences**
5. **Next safe actions**

### 1) Channels in scope now

Show each channel in scope, such as xattrs, alternate streams, forks, comments, tags, or bundle-defining metadata.
For each one, show whether it is `required`, `optional`, `legacy-carried`, or `out-of-scope`.

The operator must be able to answer: **what meaning-plane channels are active here at all?**

### 2) Policy basis and locality

Show where the rule comes from:

- reviewed product policy
- inherited subject policy
- imported legacy state pending review
- platform-imposed narrowing

The operator must be able to answer: **did I choose this, inherit this, or merely discover it?**

### 3) Seat class now

For the current seat and every other visible seat, show one of:

- `native preserver`
- `courier-only relay`
- `reduced-fidelity holder`
- `blocked for this channel`

The operator must be able to answer: **is this seat a true home for meaning, or only a transit lane?**

### 4) Object-shape consequences

Show whether any current narrowing risks:

- bundle decomposition
- invisible-but-retained metadata
- metadata loss on local edit
- failure of shell/provider affordances

The operator must be able to answer: **could visible object behavior change under this posture?**

### 5) Next safe actions

Offer only actions that preserve truth, such as:

- `Review policy change`
- `Require native preservation for this subject`
- `Permit courier-only relay with waiver`
- `Migrate subject to a native-capable seat`

## Receipt sentence

This page must always be able to emit one plain sentence such as:

- `This seat preserves all required metadata channels natively.`
- `This seat carries metadata onward but does not store all required channels natively.`
- `This subject is present here under reduced meaning fidelity.`
