# Investigation-evidence lineage receipt page: support lane, capture basis, and blocked stronger sentences interface spec

## Purpose

The archive repeatedly chooses receipts whenever a later operator may need to prove not just *what evidence was collected*, but *what the product was willing to claim that evidence could support at the time*.
This receipt is the durable output for the investigation-evidence family.

## Core decision

AnonSync must emit one **Investigation-evidence lineage receipt** whenever a user-visible troubleshooting sentence depends on support lane, capture posture, artifact class, rotation survivorship, cleanup risk, or runtime-stopped benchmarking.

## Receipt layout

1. **Receipt header**
2. **Lane and posture block**
3. **Artifact basis block**
4. **Survival and sharing block**
5. **Blocked stronger sentences block**

### 1) Receipt header

Show:

- `investigation_receipt_id`
- incident ref
- subject ref if any
- issued-at time
- receipt freshness horizon
- strongest safe sentence
- blocked stronger sentence

### 2) Lane and posture block

Must preserve:

- support-lane verdict
- receiver class
- intake path
- capture posture
- whether runtime was live or stopped
- whether restart was still needed
- whether the repro window was sufficient

### 3) Artifact basis block

Must preserve:

- artifact classes collected
- source paths or path classes
- whether service-account or vendor-specific path indirection applied
- whether crash residue, core dump, or benchmark evidence was used
- which strongest claim each artifact class supported

This block exists so future readers do not misread historical `sent logs` or `captured evidence` language as stronger than what was actually preserved.

### 4) Survival and sharing block

Must preserve:

- rotation posture
- cleanup threat at issue time
- whether export completed before loss risk
- redaction posture
- whether the final artifact remained source-grade or became summary-only
- whether the artifact was merely locally retained or actually submitted through a proven lane

### 5) Blocked stronger sentences block

Each receipt must preserve at least one blocked stronger sentence, for example:

- `Direct support will review this artifact.`
- `Debug logging was definitely active during the failure.`
- `The current logs contain the whole incident.`
- `This stopped-runtime benchmark proves the live runtime fault.`

## Hard rules

- receipts may never serialize `support available` without reviewed receiver meaning
- receipts must preserve both lane truth and capture truth
- receipts must state whether the strongest sentence depended on live runtime evidence, residue-only evidence, or stopped-runtime benchmark evidence
- receipts must remain readable without cross-referencing the full sheet
