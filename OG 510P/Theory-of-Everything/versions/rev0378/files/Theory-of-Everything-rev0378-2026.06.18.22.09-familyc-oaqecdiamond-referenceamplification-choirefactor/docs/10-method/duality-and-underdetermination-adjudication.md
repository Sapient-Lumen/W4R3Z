# Duality and underdetermination adjudication

## Purpose

The archive needs a way to decide when two candidate descriptions are genuinely different candidates, merely different presentations, or empirically indistinguishable under the current record denominator. This surface opens that pressure explicitly as `OQ-0058`.

## Adjudication states

| State | Meaning | Promotion consequence |
|---|---|---|
| `presentation-same` | notational, gauge, coordinate, regulator, frame, or dictionary variation only | no candidate distinction |
| `duality-same` | descriptions are equivalent under a declared duality or functorial equivalence | score the quotient, not both sides separately |
| `operationally-same` | public record experiments cannot distinguish them at the declared target grain | carry residual cap; no uniqueness claim |
| `regime-split` | descriptions agree in one regime and disagree outside it | local partial credit only |
| `candidate-different` | invariant carrier, target quotient, and public experiment distinguish them | possible discriminator credit |
| `unknown` | quotient or record denominator is incomplete | no same/different promotion |

## Required adjudication row

```yaml
comparison_id:
route_ids:
descriptions_compared:
claimed_difference:
invariant_carrier:
duality_or_equivalence_map:
public_record_experiment:
regime_boundary:
known_degeneracies:
negative_controls:
adjudication_state:
residual_cap:
```

A route cannot claim candidate uniqueness until its strongest duality and underdetermination decoys are survived.

## Speculative view

For a mature ToE program, “candidate identity” may be a quotient object, not a presentation object. The archive should therefore ask whether the sought theory is a unique formalism, a class of dual presentations, an operational equivalence class, or a deeper object whose public record functor forgets some structure. `OQ-0058` keeps that distinction from being smuggled into `OQ-0057`.
