# Scenario — PR head versus last green `main` needs an explicit comparison window

This scenario exists so the archive can say **why** a baseline/head pair was selected instead of implying that any two comparable sessions automatically define the same review object.

The key truth here is that:

- the audience is **PR review**,
- the baseline is the **last green session on the base branch**,
- and the excluded sessions include a newer local experiment that should not silently replace the review baseline.
