# Minimal adversarial publication test (MAPT) — bounded checklist

**Track:** Shared (cross-cutting)


This checklist is a **defense against “legibility theater”**: publishing something that is technically “public”
but operationally useless under dispute conditions.

**Goal:** the **least-effort compliant** publication is still useful.

**Related:** `docs/187`, `docs/200–206`, `docs/221–222`, `docs/234–236`.

---

## A) Pointer surfaces (must be fast + machine-checkable)

For each official pointer surface:

- [ ] Response is **JSON** (not HTML/PDF; not a JS app that requires execution).
- [ ] `Content-Type` is unambiguous (`application/json` or equivalent).
- [ ] Size is bounded (rule of thumb: **< 1 MB** for pointer surfaces; justify exceptions).
- [ ] Cache policy is explicit and revalidation works (`ETag`/`Last-Modified`). (`docs/205`)
- [ ] Surface includes (or links to) **digests** for what it points to.

Surfaces (typical):
- `/.well-known/election-stack.json` (discovery)
- official channel directory
- PublicNotice feed
- signing keyset pointer for PublicNotice

---

## B) “Official statement” publications (must be digest-first)

For each incident-relevant statement:

- [ ] Published as `PublicNotice` (digest-bearing; copy/pasteable).
- [ ] At least two independent mirrors/witnesses/monitors have observed the same digest (or a parity snapshot exists).
- [ ] A human can check authenticity **without** screenshots (digest card + lookup path).

---

## C) Data publications (must be mirrorable + indexable)

For each dataset (ENR, results objects, audit logs, etc.):

- [ ] Machine-checkable format (JSON/CSV with declared schema) — **not** a scan.
- [ ] There is a small **index/manifest** that lists parts + digests.
- [ ] Large datasets are sharded (predictable naming; no “single 50k‑page file”).
- [ ] There is a link‑forward/correction story (prior versions remain fetchable; corrections are labeled). (`docs/234–236`)
- [ ] A third party can diff versions using digests without downloading everything.

---

## D) Stress posture

- [ ] Low-bandwidth fallback exists for critical surfaces (`docs/206`).
- [ ] Missed publication deadlines become measurable evidence (TriggerEvents + CoverageReport). (`docs/187`)
- [ ] There is an explicit “what to do when the official site is down” instruction for monitors/mirrors (`docs/221–222`).

---

## Result

- [ ] MAPT PASS
- [ ] MAPT FAIL (treat as publication incident; document what failed and how)
