# rev0004 research notes — life dials, masking, and population tests

## Life total as a tournament variable

The 2026 Comprehensive Rules state that each player begins with a starting life total of 20, while variant games can specify different starting life totals. The same rule section lists Commander as 40 life. MUC-5 is not Commander, but `[20, 40]` is interpretable rather than arbitrary.

Relevant references checked during this revision:

- Wizards Comprehensive Rules page: https://magic.wizards.com/en/rules
- Wizards TXT Comprehensive Rules, effective April 17, 2026: https://media.wizards.com/2026/downloads/MagicCompRules%2020260417.txt
- Wizards Commander format page: https://magic.wizards.com/en/formats/commander

## Why this is a good tiny experiment

Life total is a rare dial that changes payoff pressure without expanding the legal-action grammar.

It does not add new actions. It changes valuation:

```text
Force pitch cost
Overlord damage clock
Jace protection urgency
risk of dying while using Force
relative importance of decking/library pressure
```

That is exactly the kind of setting where we can ask whether a constructor/pilot actually responds to context.

## Known vs unknown construction

The more interesting ML question is not "20 or 40?" alone. It is:

```text
Can a constructor exploit known tournament context?
Can a different constructor build a robust deck when the context is hidden until gameplay?
```

This is related to environment/domain randomization: train or select under randomized environment parameters, then test whether policies are robust across those dimensions. In rev0004 the randomized parameter is just `starting_life`.

Future evaluation:

```text
known-20 constructor vs robust-unknown constructor at 20
known-40 constructor vs robust-unknown constructor at 40
cross-play all produced decks
measure exploitability and regret
```

## Static prior added before learned constructors

`src/muc5/life_constructor.py` creates weak static deck-construction priors:

```text
known_life20
known_life40
unknown_robust
```

The static prior is intentionally disposable. It exists so we can wire the tournament axis, generate artifacts, and later replace it with enumeration, evolution, neural construction, or PSRO-style best responses.

## Population methods stay attractive

PSRO remains attractive because the object is not one champion bot. It is a growing population of deck+pilot strategies and best responses. A life dial gives PSRO another way to expose brittle policies.

Reference:

- Policy Space Response Oracles survey: https://arxiv.org/html/2403.02227v1

## Action masking still matters

The life dial does not change the action-mask thesis. MUC-5 still has a dynamic legal action set: response frames, pitch choices, Jace choices, attack counts, block counts, and discard choices. The environment should continue to expose only legal macro-actions.

References:

- PettingZoo AEC API/action masking docs: https://pettingzoo.farama.org/api/aec/
- PettingZoo custom action masking tutorial: https://pettingzoo.farama.org/tutorials/custom_environment/3-action-masking/
- Huang & Ontañón, invalid action masking: https://arxiv.org/abs/2006.14171

## Imperfect-information methods

The five-card game is still hidden-information because hands and libraries are hidden. Deep CFR/NFSP/ReBeL-style branches remain later options. The life dial should be part of the information state when known during gameplay, but not necessarily known at construction time.

Reference:

- Deep Counterfactual Regret Minimization: https://proceedings.mlr.press/v97/brown19b.html

## rev0004 recommendation

Keep the life dial, but do not let it distract from simulator correctness.

The dial earns its place because it is cheap and asks a clean context-adaptation question. It should be discarded or demoted later if tournament data shows no meaningful construction/pilot response beyond noise.

## Static constructor priors added

rev0004 includes a weak static constructor prior to make the known/unknown-life question testable immediately. It should be treated like a scaffold, not as a final model. The next learned/evolved constructor should try to beat these shortlists under the same four tournament contexts.

The constructor arena is intentionally small: top four static decks per construction label, mirror cross-play, and the current public-info heuristic pilot. This is enough to find obvious plumbing regressions and some early deck-shape smells.
