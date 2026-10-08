# Rematch worlds should plan width-only service relaxations by residual axis budgets

The recent local witness, slack-lead, and axis-persistence cards explain what happens **next** from a current positive-service weakening SLA state.
The tighter inheritor question is what future relaxation capacity still remains overall.

The archive should answer that with one small residual budget triple attached to the current staircase signature `E_i_S_j`:

- `exact_only_remaining`
- `suffix_only_remaining`
- `shared_diagonal_remaining`

where the unique shared diagonal is the one audited coupled step `E3_S8 -> E4_S9`.

## Claim

From any current positive-service service target, the entire remaining staircase to terminal `E6_S11` is fully summarized by this residual budget triple.
There is no extra hidden geometry once those three numbers are known.

## Current law

- total future exact support still available is `6 - i`
- total future suffix support still available is `11 - j`
- one future coupled step remains **iff** the current state still lies before the diagonal gate, i.e. before `E4_S9`
- therefore:
  - `exact_only_remaining = (6 - i) - shared_diagonal_remaining`
  - `suffix_only_remaining = (11 - j) - shared_diagonal_remaining`
  - `total_relaxation_steps_remaining = exact_only_remaining + suffix_only_remaining + shared_diagonal_remaining`

That total matches the audited staircase distance to terminal exactly.

## Operational use

When an inheritor is handed a current width-only weakening SLA target:

1. map it to the current signature `E_i_S_j`
2. compute the residual budget triple
3. treat `shared_diagonal_remaining = 1` as “future growth still contains one coupled kink”
4. treat `shared_diagonal_remaining = 0` as “future growth is now a pure single-axis countdown”

This turns the future from a catalog of thresholds into a countdown budget.

## Consequence

The current archive now has an exact local completion card:

- first `12` positive-service states are **pre-diagonal** and still carry the one shared coupon,
- the last `4` nonterminal states are **post-diagonal** and purely axis-separable,
- terminal `E6_S11` has zero remaining budget.

So future service relaxation planning can be governed as residual budget depletion, not by rereading the whole staircase.
