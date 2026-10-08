# 10 — Profile reference strength

## Rule

Use the weakest profile reference strong enough to identify or bind the validation rules at the consuming boundary.

## Tiers

| Tier | Shape | Use when |
|---:|---|---|
| 0 | implicit sealed context | one authenticated/configured profile encloses all assessed state |
| 1 | `id + version/revision` | public, stable, unambiguous profile |
| 2 | `authority + id + version/revision` | names can collide across operators or deployments |
| 3 | `authority + id + version/revision + digest` | exact retained rules matter for audit, safety, compliance, mutable stores, or long retention |
| 4 | signed profile-binding record | receiver must independently verify who bound the profile reference |

## Digest semantics

The digest binds the normative profile rules used for assessment.

It does not bind:

```text
source packet
PDF artifact
operator alias
request bundle
clock certificate
compliance verdict
whole standards catalog
```

## Signed binding semantics

A signed binding lets a receiver verify who bound the profile id/version/revision/digest. It is not proof that the assessed clock was good, and it is not a conformance certificate unless a separate profile says so.

## Export consequence

Name-only references are too weak for most exported actionable conformance. Detached or retained assessment should normally use at least Tier 3.
