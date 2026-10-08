# priority reconsideration after rev0039

The current bottleneck is still label quality, not model class.

rev0039 weakens a tempting assumption:

```text
public-policy disagreement is good for frame selection
therefore vote-prioritized branch selection must be good
```

The matched audit says the second claim is not automatically true.  With a tight branch budget, diversity can still beat vote priority.

Next priority:

```text
1. hybrid branch selector: disagreement + diversity + ranker prior
2. adaptive extra rollouts on top-contender actions
3. scale decisive labels only after selector audits stay clean
4. use C++ no-choice segment batching once branch collection becomes the speed bottleneck
5. promote policies only after nontruncated payoff tables and replay/C++ gates stay clean
```
