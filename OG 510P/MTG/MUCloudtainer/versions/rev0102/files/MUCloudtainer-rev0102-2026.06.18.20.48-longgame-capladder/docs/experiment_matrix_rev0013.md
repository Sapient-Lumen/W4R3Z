# rev0013 experiment matrix update

## New axis: policy implementation form

```text
trusted_state_scripted
public_profile_scripted
public_readable_code_policy
public_random
future_public_neural
future_public_search
future_public_code_generated
```

Promotion-facing experiments should prefer public interfaces. Trusted-state scripted agents may remain debugging baselines.

## New strategy-bundle fields

```text
strategy_id
deck_name
deck_vector
agent_name / policy_id
mulligan_policy
life construction context
simulator_revision
interface
reward_convention
```

## New minimum for future payoff rows

Before a row can be used for promotion, it should record:

```text
simulator_revision
interface
reward_convention
starting_life
starting_player
mulligan0 / mulligan1
agent0 / agent1
deck0 / deck1
truncation status
terminal win columns
seed
```

## Next high-value builds

1. Confidence intervals for payoff tables.
2. Public action-feature encoder for neural/imitation policies.
3. First MAP-Elites archive over deck descriptors.
4. First Alpha-Rank adapter over promoted payoff tables.
5. Determinized search agent with explicit belief-sampling label.
6. Stall/adversary policy to test truncation-reward robustness.
