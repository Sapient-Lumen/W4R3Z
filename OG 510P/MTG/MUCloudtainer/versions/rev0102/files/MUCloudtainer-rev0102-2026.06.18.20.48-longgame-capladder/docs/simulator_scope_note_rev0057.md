# Simulator scope note — rev0057

MUC-5 intentionally diverges from tournament Magic.

Current local scope:

```text
five cards only
40-card or 60-card decks
unlimited copies of the five cards
starting life dial: 20 or 40
compressed but exact local macro-actions
hidden information preserved in observations
```

This is appropriate for a closed-world research instrument, but all claims must be phrased as MUC-5 claims, not general Magic claims.

Recommended wording:

```text
In the MUC-5 microgame, under the current public-decision-frame simulator and terminal-clean gate, ...
```

Avoid wording like:

```text
This Magic deck beats that Magic deck.
```

The official Magic rules have different format-specific deck-construction constraints, starting life defaults, and many more card/rule interactions than MUC-5 models.
