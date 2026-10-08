# Diagnostic send page: bundle membership, redaction, and transport commit review interface spec

## Purpose

`Send logs` is not a harmless button.
It is an outbound evidence transfer.

## Core decision

AnonSync should therefore model every outbound support / feedback transfer as a reviewed **diagnostic send page**.

The page must answer:

1. what exact bundle members are included
2. what still remains local-only
3. what redaction or omission choices exist
4. where the bundle is going
5. when the send is complete enough to close the page

## Required sections

1. **Destination and purpose**
2. **Bundle membership**
3. **Excluded local artifacts**
4. **Redaction / omission controls**
5. **Transport progress and completion**
6. **Receipt**

## Bundle membership

List each family explicitly:

- debug logs
- profiler traces
- crash artifacts
- configuration snapshot
- operator note / repro note
- selected share or file names if included

Do not permit one vague `logs included` sentence.

## Excluded local artifacts

The page must also say what is not being sent, such as:

- older rotated logs
- large crash dumps
- raw content files
- manually copied attachments not yet selected

## Redaction / omission controls

Where redaction is possible, show it.
Where it is not possible, say that plainly.

Operators must be able to choose:

- send all selected evidence
- omit a family
- export locally instead of sending
- cancel without changing local retention

## Transport progress and completion

The page must reflect:

- bytes prepared
- bytes sent
- waiting for operator / network / server acknowledgment
- safe-to-close versus not-yet-safe-to-close

## Receipt

On success, emit a receipt with:

- send time
- destination class
- bundle family summary
- local artifact disposition (`retained`, `rotating`, `queued for expiry`)

## Anti-clone rule

Do not make outbound evidence transfer a one-click side effect with no bundle preview.
