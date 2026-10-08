# Precedent docket contract sheet page: source ruling, analogy, and binding weight interface spec

## Purpose

After the archive learned how to adjudicate disputed completion, it still needed one ordinary page for the next operator question:

> this new challenge looks like an older one — are we actually bound by that earlier ruling, merely guided by it, or free to distinguish it?

## Core decision

AnonSync must expose one first-class **Precedent docket contract sheet** whenever a dispute verdict, case closure, or doctrine update is being invoked for a later materially similar case.

## Fixed page order

1. **Precedent header**
2. **Source-ruling card**
3. **Analogy card**
4. **Binding-weight card**
5. **Version and world-scope card**
6. **Requested doctrine action card**
7. **Decision sentence**

### 1) Precedent header

Show:

- precedent docket id
- source verdict id
- current case id
- doctrine owner
- opened time
- current precedent status
- strongest currently safe sentence
- superseding precedent id if any

Supported `precedent_status` values:

- `drafting`
- `pending-analogy-review`
- `pending-appeal`
- `binding-active`
- `presumptive-active`
- `persuasive-only`
- `informative-only`
- `distinguished-for-current-case`
- `superseded`
- `sunset`
- `closed`

Hard rule:

A current case may not silently claim `same as before` without naming the actual source ruling and its current doctrine status.

### 2) Source-ruling card

Required rows:

- source verdict sentence
- source case scope
- source witness basis
- source remedy or ruling class
- source residual uncertainty if any
- source appeal history if any

Hard rule:

The page must preserve enough of the original ruling to judge whether the analogy is real.
A precedent docket cannot point at a vague remembered incident.

### 3) Analogy card

Required rows:

- claimed similarity summary
- material matching facts
- material mismatching facts
- disputed mismatches
- analogy class
- weakest safe claim about sameness

Supported `analogy_class` values:

- `same-facts`
- `close-analogy`
- `same-symptom-different-world`
- `same-symptom-different-version`
- `distinguishable`
- `gap-case`

Hard rule:

The product must store both matches and mismatches.
Similarity may not erase the facts that could later justify distinction or overrule.

### 4) Binding-weight card

Required rows:

- proposed binding weight
- who may assign or lower that weight
- what evidence would strengthen the weight
- what evidence would weaken the weight
- currently blocked stronger sentence

Supported `binding_weight` values:

- `binding`
- `presumptive`
- `persuasive`
- `informative-only`
- `superseded`

Hard rule:

Binding weight must be explicit.
The interface may not force the operator to infer weight from how confidently the earlier case was described.

### 5) Version and world-scope card

Required rows:

- source version window
- source world or lane scope
- current case version and world
- known drift since source ruling
- scope mismatch verdict
- sunset trigger already known

Hard rule:

A precedent cannot silently cross version or world boundaries.
If the current case differs by version, service world, mobile lane, config world, or other material axis, the page must say whether the older ruling still travels.

### 6) Requested doctrine action card

Required rows:

- requested doctrine action
- requested exception if any
- appeal requested or not
- proposed overrule basis if any
- downstream claim effect
- review owner next step

Supported `requested_doctrine_action` values:

- `apply-as-binding`
- `apply-as-presumptive`
- `treat-as-persuasive`
- `distinguish-current-case`
- `propose-overrule`
- `create-new-precedent`
- `sunset-old-precedent`

Hard rule:

The requested action must be one explicit doctrine move.
`Looks similar` is not a doctrine action.

### 7) Decision sentence

Render one sentence only:

- `This docket compares [current case] to [source ruling], currently treats the earlier ruling as [binding_weight], and still blocks the stronger sentence that [overclaim].`

## Required interactions

- **Attach source verdict**
- **Mark matching fact**
- **Mark distinguishing fact**
- **Assign or lower binding weight**
- **Open appeal / propose overrule**
- **Create new precedent instead**

## Empty and failure states

If no prior ruling has been attached, show:

- `No source ruling attached yet. This case cannot claim precedent weight.`

If the only attached ruling is already superseded, show:

- `Attached ruling is superseded. Use it for history only or attach a newer doctrine source.`
