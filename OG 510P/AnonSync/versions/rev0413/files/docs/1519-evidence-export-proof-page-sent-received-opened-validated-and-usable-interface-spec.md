# Evidence export proof page: sent, received, opened, validated, and usable interface spec

## Purpose

Once the chosen packet is exported, the product still needs one page that answers:

> what exactly left, did anyone receive it, did they actually open and validate it, and what evidentiary ceiling now survives that export path?

## Core decision

AnonSync must expose one first-class **Evidence export proof** page whenever a packet is exported, uploaded, attached, transferred, recalled, or superseded in a materially meaningful way.

## Fixed page order

1. **Export header**
2. **Packet-and-path card**
3. **Transport-result card**
4. **Destination-validation card**
5. **Integrity-ceiling card**
6. **Proof sentence**

### 1) Export header

Show:

- export proof id
- source packet sheet id
- source packet form
- export state
- current strongest safe post-export sentence
- strongest blocked post-export sentence

Supported `export_state` values:

- `sent-not-confirmed`
- `received-not-opened`
- `opened-not-validated`
- `validated-not-acted-on`
- `usable-for-stated-purpose`
- `delivery-failed`
- `recalled`
- `superseded`

Hard rule:

The page must not jump from `sent` to `usable` silently.
Each rung is product truth.

### 2) Packet-and-path card

Required rows:

- exported packet id
- exported packet form
- destination audience
- transport path
- size or artifact constraints encountered
- retained source packet pointer
- superseding packet pointer if any

Supported `transport_path` values:

- `in-product-upload`
- `manual-attachment`
- `secure-link`
- `local-file-drop`
- `public-staging-path`
- `api-export`
- `narrative-only-channel`

Hard rule:

Transport path must stay visible because it changes the integrity ceiling and recall options.

### 3) Transport-result card

Required rows:

- send result
- receive acknowledgement
- open acknowledgement
- checksum or integrity witness if any
- transport failure notes
- resend or alternate-path decision

Hard rule:

Receive acknowledgement and open acknowledgement must remain separate.
A mailbox or upload service can acknowledge receipt without proving the packet was read.

### 4) Destination-validation card

Required rows:

- destination validation state
- validation method
- packet usable for stated purpose or not
- missing context still requested
- audience challenge or rejection state

Supported `destination_validation_state` values:

- `not-yet-attempted`
- `format-opened`
- `integrity-checked`
- `context-sufficient`
- `usable-for-purpose`
- `usable-but-narrow`
- `rejected-or-corrupt`

Hard rule:

Format readability is weaker than validation.
A packet that opens but cannot support the requested task stays weaker.

### 5) Integrity-ceiling card

Required rows:

- highest safe statement supported by this export event
- highest blocked statement
- reason still blocked
- event that would upgrade the ceiling
- recall or supersession consequence if stale

Hard rule:

The integrity ceiling must consider packet form, transport path, and destination validation together.

### 6) Proof sentence

Render one sentence only:

- `This export is [export_state] via [transport path]; destination validation is [validation state], so the strongest safe post-export sentence is [sentence].`

## Required interactions

- **Acknowledge receipt**
- **Record open or validation result**
- **Attach resend or alternate path**
- **Recall packet**
- **Supersede with stronger packet**

## Failure state

If transport or validation fails, show:

- `The packet left the source boundary but did not yet become usable evidence at destination. The prior export ceiling survives until receipt, validation, or stronger resend.`
