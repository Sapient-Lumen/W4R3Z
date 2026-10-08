# Control-state detachment page — inline spine detachment, export, and clean-branch interface spec

## Purpose

Some trees should remain managed subjects.
Some should become plain payload branches.
This page exists for the high-risk middle case:

> can I keep the bytes but deliberately stop carrying the old controller state?

## Core decision

Whenever a reviewed action would detach hidden controller state from a copied-looking tree, AnonSync must open one first-class **Control-state detachment** page.

The page must make a durable distinction between:

- removing disposable residue
- detaching continuity-bearing spine material
- exporting recovery witnesses before detachment
- creating a clean payload branch after controller-state removal

## Fixed page order

1. **Detachment target**
2. **Witnesses that would be lost or preserved**
3. **Resulting branch posture**
4. **Detachment receipt promise**

### 1) Detachment target

Show exactly which hidden families are proposed for detachment:

- subject spine / ID witness
- local recovery/history store
- controller policy material
- ambiguous residue

### 2) Witnesses that would be lost or preserved

Show:

- continuity witnesses preserved elsewhere
- witnesses that would be exported now
- witnesses that would be lost after detachment
- claim ceiling after detachment

The operator must be able to answer:

> what proof dies if I strip the control state out of this tree?

### 3) Resulting branch posture

Show the post-detach sentence as one of:

- `clean payload branch`
- `payload branch with exported continuity packet`
- `still ambiguous; detach insufficient`
- `blocked; detachment would overclaim cleanliness`

The operator must be able to answer:

> after detachment, what am I honestly allowed to call this tree?

### 4) Detachment receipt promise

The receipt must preserve:

- detached control families
- exported witnesses if any
- resulting branch posture
- rejected stronger sentence

## Non-goal

This page does not itself attach or publish the resulting tree.
It only governs the semantic boundary where hidden controller state stops traveling with the payload tree.
