# Revision 0349

This revision takes two ideas that showed up repeatedly across comparison datacubes and applies them to VHK's flagship lane without broadening the product surface.

## 1. Control-plane surfaces now declare authority and mutability

The generated i3/X11 warm-runtime `control-plane.json` now classifies every helper as one of:

- canonical editable project source
- generated review surface
- runtime snapshot
- runtime actuation
- runtime observability

Each class also declares authority, refresh expectations, and guidance for a private LLM. Individual script entries now carry `surface_class` and `llm_mode`.

This sharpens the repo's emerging control-plane story: the warm stack is not just a bag of helper scripts, it is a typed operational surface.

## 2. Macro review queue now has stable issue codes and evidence

`vhk macro-review-queue-json` now emits a stable issue taxonomy and per-item evidence fields. Queue items carry `issue_code`, `status_label`, `severity`, `action_lane`, and `evidence`.

This turns recorder debt into something a private LLM or operator can triage with less guesswork and better provenance.

## Why these changes were worth taking

The comparison datacubes were strongest when they made three things explicit:

- what is canonical vs generated vs transient
- what state or issue code a caller is looking at
- what evidence supports the recommendation

Those ideas fit VHK directly because VHK is already converging on a warm-stack control plane and a recorder-review queue. The right move was to sharpen those surfaces, not to add new product lanes.
