
# Birth-commitment review page: frozen fields, empty targets, and creation assumptions interface spec

## Purpose

This page exists because some settings are not merely preferences; they are commitments made at the moment an object is created.

The operator should be able to answer:

> what assumptions am I baking into this object right now that later operators should not mistake for ordinary editable settings?

## Required sections

1. **Object being born**
2. **Frozen-at-birth fields**
3. **Creation preconditions**
4. **Later-change honesty**
5. **Receipt promise**

### 1) Object being born

Show:

- new object type
- acting seat
- chosen subject kind / topology / authority substrate
- intended role

### 2) Frozen-at-birth fields

Show each field that later becomes `birth-locked` or `successor-required`, including:

- field name
- chosen value
- why this value is birth-bound rather than live-editable
- what later change would require

### 3) Creation preconditions

Show:

- empty-target requirements
- path-class requirements
- privilege / authority assumptions
- runtime topology assumptions
- portability or substrate assumptions

### 4) Later-change honesty

Render plain sentences such as:

- `This value may be edited in place later.`
- `This value can change only for future descendants.`
- `Changing this value later requires a successor object and cutover.`
- `Changing this value later replays initial indexing / admission work.`

### 5) Receipt promise

The page must promise a receipt that preserves:

- birth-time field choices
- satisfied preconditions
- stronger rejected sentence
- successor-required boundaries

## Rules

- never hide birth commitments behind `Advanced settings`
- never let an empty-target requirement appear only after creation fails
- never treat later recreate cost as a support concern rather than an interface concern
