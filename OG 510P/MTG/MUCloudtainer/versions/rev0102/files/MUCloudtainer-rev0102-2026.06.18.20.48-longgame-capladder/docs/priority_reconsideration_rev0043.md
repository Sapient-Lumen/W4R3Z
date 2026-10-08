# Priority reconsideration rev0043

The priority after rev0043 is:

```text
1. Margin-seeking hard-frame screen: predict decisive labels per rollout.
2. Keep online adaptive allocation; do not revert to fixed branch matrices except for audits.
3. Use matched audits to compare screeners/selectors on the same situations.
4. Attach C++ shadow checks to every branch-heavy collector.
5. Delay policy promotion until label yield and nontruncated payoff gates are stronger.
```

The biggest lesson is that the system is label-limited, not model-limited. The online collector works, but now we need better public-only frame selection.
